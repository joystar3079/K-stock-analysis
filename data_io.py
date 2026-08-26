"""데이터 입출력 — 시세, 마스터 파일, 일일 옵션 추출.

기존 구조는 GitHub에 쓰고 로컬 파일에서 읽었습니다. Streamlit Cloud에서
로컬 파일은 배포 시점 스냅샷이라 업로드해도 재배포 전까지 반영되지 않았고,
캐시를 비워도 같은 옛 데이터를 다시 읽었습니다. 여기서는 읽기/쓰기를
모두 GitHub 기준으로 통일하고, 로컬 파일은 폴백으로만 씁니다.
"""
from __future__ import annotations

import io
import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

from config import (DEFAULT_SOFR, DIVIDEND_YIELD, MASTER_FILE, PRICE_COL,
                    SYMBOL, TH)
from pricing import bs_delta_batch, solve_iv_batch

MASTER_KEYS = ["Quote Date", "Expiration Date", "Option Type", "Strike"]


# ─── 시세 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    try:
        px = yf.download(symbol, start=start_date, end=end_date,
                         progress=False, auto_adjust=False).reset_index()
    except Exception as e:
        st.warning(f"시세 조회 실패: {e}")
        return pd.DataFrame(columns=["Date", "Close Price"])

    if px.empty:
        return pd.DataFrame(columns=["Date", "Close Price"])
    if isinstance(px.columns, pd.MultiIndex):
        px.columns = [c[0] for c in px.columns]
    px = px.rename(columns={"Close": "Close Price"})
    px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None).dt.normalize()
    return (px.sort_values("Date").dropna(subset=["Close Price"])
              .reset_index(drop=True)[["Date", "Close Price"]])


# ─── 마스터 파일 ─────────────────────────────────────────────────────
def _repo_name() -> str | None:
    try:
        return st.secrets["GITHUB_REPO"]
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def load_master_data(cache_bust: str = "") -> pd.DataFrame:
    """GitHub raw 우선, 실패 시 로컬 파일 폴백."""
    repo = _repo_name()
    if repo:
        url = f"https://raw.githubusercontent.com/{repo}/main/{MASTER_FILE}"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return pd.read_pickle(io.BytesIO(resp.content), compression="gzip")
        except Exception as e:
            st.info(f"GitHub 마스터 로드 실패 — 로컬 폴백 시도 ({str(e)[:60]})")
    if os.path.exists(MASTER_FILE):
        try:
            return pd.read_pickle(MASTER_FILE)
        except Exception as e:
            st.warning(f"로컬 마스터 로드 실패: {e}")
    return pd.DataFrame()


def normalize_option_frame(df: pd.DataFrame) -> pd.DataFrame:
    """마스터 병합용 표준 형태로 변환."""
    out = df.copy()
    out["Quote Date"] = pd.to_datetime(out["Quote Date"])
    out["Expiration Date"] = pd.to_datetime(out["Expiration Date"])
    out["Option Type"] = np.where(
        out["Option Type"].astype(str).str.upper().str.startswith("C"), "C", "P")
    return out


def merge_master(current: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    merged = pd.concat([current, normalize_option_frame(new)], ignore_index=True)
    return (merged.drop_duplicates(subset=MASTER_KEYS, keep="last")
                  .sort_values("Quote Date").reset_index(drop=True))


def push_master_to_github(merged: pd.DataFrame, quote_date) -> int:
    """GitHub에 마스터 파일 덮어쓰기. 실패 시 예외를 그대로 올립니다."""
    from github import Github

    missing = [k for k in ("GITHUB_TOKEN", "GITHUB_REPO") if k not in st.secrets]
    if missing:
        raise KeyError(f"secrets 누락: {', '.join(missing)}")

    buffer = io.BytesIO()
    merged.to_pickle(buffer, compression="gzip")

    repo = Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["GITHUB_REPO"])
    contents = repo.get_contents(MASTER_FILE)
    repo.update_file(contents.path, f"Auto-update master data: {quote_date}",
                     buffer.getvalue(), contents.sha)
    return len(merged)


# ─── 일일 옵션 추출 ──────────────────────────────────────────────────
def _fetch_sofr() -> float:
    try:
        import pandas_datareader as pdr
        return round(float(pdr.DataReader("SOFR", "fred")["SOFR"].dropna().iloc[-1]), 2)
    except Exception:
        return DEFAULT_SOFR


def extract_daily_options() -> tuple[pd.DataFrame | None, str | None, dict]:
    """옵션 체인 수집 + IV/Delta 연산. (데이터, 오류메시지, 통계) 반환."""
    stats: dict = {}
    sofr = _fetch_sofr()
    stats["sofr"] = sofr

    ticker = yf.Ticker(SYMBOL)
    try:
        hist = ticker.history(period="1d")
        etf_price = round(float(hist["Close"].iloc[-1]), 2)
        quote_date = hist.index[-1].date()
    except Exception as e:
        return None, f"주가 데이터를 불러올 수 없습니다: {e}", stats

    try:
        expirations = ticker.options
    except Exception as e:
        return None, f"만기일 데이터를 가져올 수 없습니다: {e}", stats

    frames, skipped = [], []
    for exp in expirations:
        try:
            chain = ticker.option_chain(exp)
            for side, tag in ((chain.calls, "Call"), (chain.puts, "Put")):
                part = side.copy()
                part["Option Type"] = tag
                part["Expiration Date"] = exp
                frames.append(part)
        except Exception as e:
            skipped.append(f"{exp}({str(e)[:30]})")
    if skipped:
        stats["skipped_expirations"] = skipped
    if not frames:
        return None, "옵션 데이터가 없습니다.", stats

    df = pd.concat(frames, ignore_index=True).rename(columns={
        "contractSymbol": "Contract Name", "strike": "Strike", "bid": "Bid",
        "ask": "Ask", "lastPrice": "Last Price", "volume": "Volume",
        "openInterest": "Open Interest"})
    for col in ["Bid", "Ask", "Last Price", "Volume", "Open Interest"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Quote Date"] = quote_date
    df["Secured Overnight Financing Rate"] = sofr
    df[PRICE_COL] = etf_price
    df["Expiration Date"] = pd.to_datetime(df["Expiration Date"]).dt.date

    bus = np.busday_count(
        pd.to_datetime(df["Quote Date"]).values.astype("datetime64[D]"),
        pd.to_datetime(df["Expiration Date"]).values.astype("datetime64[D]"))
    df["T"] = np.maximum(bus, TH.MIN_T_DAYS) / TH.TRADING_DAYS

    # ── 유동성 필터: 호가도 미결제도 없는 종목은 IV를 구할 이유가 없습니다 ──
    mid = (df["Bid"] + df["Ask"]) / 2.0
    has_quote = (df["Bid"] > 0) & (df["Ask"] > 0)
    target = np.where(has_quote, mid, df["Last Price"])
    liquid = (target > 0) & (df["Open Interest"] > 0) & (df["T"] > 0)

    stats["total_rows"] = len(df)
    stats["priced_rows"] = int(liquid.sum())

    iv = np.full(len(df), np.nan)
    delta = np.full(len(df), np.nan)
    if liquid.any():
        idx = np.flatnonzero(liquid.to_numpy())
        is_call = df["Option Type"].to_numpy()[idx] == "Call"
        r = sofr / 100.0
        iv_sub = solve_iv_batch(
            np.asarray(target)[idx], df[PRICE_COL].to_numpy()[idx],
            df["Strike"].to_numpy()[idx], df["T"].to_numpy()[idx],
            r, DIVIDEND_YIELD, is_call)
        iv[idx] = iv_sub
        delta[idx] = bs_delta_batch(
            df[PRICE_COL].to_numpy()[idx], df["Strike"].to_numpy()[idx],
            df["T"].to_numpy()[idx], r, DIVIDEND_YIELD, iv_sub, is_call)

    # NaN 유지 — 빈 문자열을 섞으면 dtype이 object가 되어 이후 연산이 막힙니다
    df["Implied Volatility"] = np.round(iv, 4)
    df["Delta"] = np.round(delta, 4)

    cols = ["Contract Name", "Quote Date", "Expiration Date", "Option Type",
            "Strike", "Bid", "Ask", "Last Price", "Volume", "Open Interest",
            "Secured Overnight Financing Rate", PRICE_COL,
            "Implied Volatility", "Delta"]
    final = df[cols].copy()
    final["Volume"] = final["Volume"].astype(int)
    final["Open Interest"] = final["Open Interest"].astype(int)
    return final, None, stats
