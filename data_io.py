"""데이터 입출력 — 시세, 마스터 파일, 일일 옵션 추출.

[V29 수정] 같은 Quote Date 에 대해 두 스냅샷이 뒤섞이던 문제를 막습니다.

기존 merge_master 는 (Quote Date, Expiration Date, Option Type, Strike) 키가
겹치는 행만 교체했습니다. 라이브 옵션 체인은 과거 기록과 만기 구성·행사가
범위가 다르고 당일 미결제약정이 아직 0인 경우가 많아서, 이미 존재하는 날짜를
재추출하면 옛 행과 새 행이 뒤섞인 '혼종'이 만들어졌습니다. 그 날짜의 OI 집계
지표가 통째로 왜곡되고, 세션에 추출 데이터가 남아 있는 한 모든 분석에 계속
반영되었습니다.

이제 병합은 항상 '날짜 단위'로 처리합니다.
  skip    : 이미 있는 날짜는 건너뜁니다 (기본 — 기록 보존)
  replace : 해당 날짜의 기존 행을 전부 지우고 새 스냅샷으로 통째 교체
어느 쪽이든 한 날짜 안에 두 스냅샷이 섞이는 일은 발생하지 않습니다.
"""
from __future__ import annotations

import io
import os

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
    """마스터 병합용 표준 형태로 변환. Quote Date 는 자정으로 정규화합니다."""
    out = df.copy()
    out["Quote Date"] = pd.to_datetime(out["Quote Date"]).dt.normalize()
    out["Expiration Date"] = pd.to_datetime(out["Expiration Date"]).dt.normalize()
    out["Option Type"] = np.where(
        out["Option Type"].astype(str).str.upper().str.startswith("C"), "C", "P")
    return out


def quote_dates(df: pd.DataFrame) -> set[pd.Timestamp]:
    if df.empty or "Quote Date" not in df.columns:
        return set()
    return set(pd.to_datetime(df["Quote Date"]).dt.normalize().unique())


def merge_report(current: pd.DataFrame, new: pd.DataFrame) -> dict:
    """병합 전에 무엇이 벌어질지 미리 보여줍니다. 부작용 없음."""
    cur_d, new_d = quote_dates(current), quote_dates(new)
    dup = sorted(new_d & cur_d)
    add = sorted(new_d - cur_d)
    return {
        "new_dates": [d.date() for d in add],
        "conflict_dates": [d.date() for d in dup],
        "master_rows": len(current),
        "new_rows": len(new),
        "conflict_rows_in_master": (
            int(current["Quote Date"].isin(dup).sum()) if dup and not current.empty else 0),
    }


def merge_master(current: pd.DataFrame, new: pd.DataFrame,
                 on_conflict: str = "skip") -> pd.DataFrame:
    """날짜 단위 병합.

    on_conflict
      "skip"    : 마스터에 이미 있는 Quote Date 는 신규분을 버립니다 (기본)
      "replace" : 해당 날짜의 마스터 행을 전부 제거하고 신규분으로 대체합니다

    두 경우 모두 한 날짜 안에서 옛 스냅샷과 새 스냅샷이 섞이지 않습니다.
    """
    if on_conflict not in ("skip", "replace"):
        raise ValueError(f"on_conflict 는 'skip' 또는 'replace' — 받은 값: {on_conflict}")

    new_n = normalize_option_frame(new)
    if current is None or current.empty:
        return new_n.sort_values("Quote Date").reset_index(drop=True)

    cur = current.copy()
    cur["Quote Date"] = pd.to_datetime(cur["Quote Date"]).dt.normalize()

    dup = quote_dates(new_n) & quote_dates(cur)
    if dup:
        if on_conflict == "skip":
            new_n = new_n[~new_n["Quote Date"].isin(dup)]
        else:
            cur = cur[~cur["Quote Date"].isin(dup)]

    if new_n.empty:
        return cur.sort_values("Quote Date").reset_index(drop=True)

    merged = pd.concat([cur, new_n], ignore_index=True)
    # 같은 날짜 안에서는 이제 한 출처만 존재하므로, 이 단계는 순수 안전장치입니다
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
        hist = ticker.history(period="5d")
        etf_price = round(float(hist["Close"].iloc[-1]), 2)
        quote_date = hist.index[-1].date()
    except Exception as e:
        return None, f"주가 데이터를 불러올 수 없습니다: {e}", stats

    stats["quote_date"] = quote_date

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

    # 유동성 필터 — 호가도 미결제도 없는 종목은 IV를 구할 이유가 없습니다
    mid = (df["Bid"] + df["Ask"]) / 2.0
    has_quote = (df["Bid"] > 0) & (df["Ask"] > 0)
    target = np.where(has_quote, mid, df["Last Price"])
    liquid = (target > 0) & (df["Open Interest"] > 0) & (df["T"] > 0)

    stats["total_rows"] = len(df)
    stats["priced_rows"] = int(liquid.sum())
    stats["zero_oi_rows"] = int((df["Open Interest"] <= 0).sum())

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


# ─── 진단 ────────────────────────────────────────────────────────────
def diagnose_quote_date(master: pd.DataFrame, extracted: pd.DataFrame | None,
                        target) -> pd.DataFrame:
    """특정 날짜가 마스터/추출본에서 어떻게 구성되는지 비교합니다."""
    t = pd.to_datetime(target).normalize()
    rows = []

    def summarize(df, label):
        if df is None or df.empty:
            rows.append({"출처": label, "행수": 0, "만기수": 0,
                         "OI합": 0, "OI=0 비율": "-", "행사가 범위": "-"})
            return
        d = normalize_option_frame(df)
        d = d[d["Quote Date"] == t]
        if d.empty:
            rows.append({"출처": label, "행수": 0, "만기수": 0,
                         "OI합": 0, "OI=0 비율": "-", "행사가 범위": "-"})
            return
        rows.append({
            "출처": label,
            "행수": len(d),
            "만기수": d["Expiration Date"].nunique(),
            "OI합": int(d["Open Interest"].sum()),
            "OI=0 비율": f"{(d['Open Interest'] <= 0).mean():.0%}",
            "행사가 범위": f"{d['Strike'].min():.0f}~{d['Strike'].max():.0f}",
        })

    summarize(master, "마스터")
    summarize(extracted, "신규 추출")
    if extracted is not None and not extracted.empty:
        summarize(merge_master(master, extracted, "skip"), "병합(skip)")
        summarize(merge_master(master, extracted, "replace"), "병합(replace)")
    return pd.DataFrame(rows)
