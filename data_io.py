"""데이터 입출력 — 시세, 마스터 파일, 옵션 체인 수집(파일 우선 / API 보조).

[V29] 같은 Quote Date 에 대해 두 스냅샷이 뒤섞이던 문제 방지.
[V30] 야후 파이낸스 차단 대응 전면 개편
      1) 엑셀/CSV 로 내려받은 옵션 체인을 그대로 파이프라인에 태우는 경로를 신설.
         → 야후가 죽어도 IV/Delta 산출까지 100% 동일하게 동작합니다.
      2) CBOE 와이드 포맷(한 행에 콜/풋 동시), 롱 포맷, 컬럼명 변형을 자동 인식.
      3) 시세도 야후 실패 시 stooq → 업로드 파일 → 수동입력 순으로 폴백.
      4) yfinance 신버전(0.2.5x+)에 requests.Session 을 주입하면 터지던 버그 수정.
         (신버전은 curl_cffi 세션을 요구합니다. requests.Session 주입은 예외를 냅니다.)
      5) Option Type 을 'C'/'P' 로 넣든 'Call'/'Put' 으로 넣든 IV 계산이 동일하게 동작.
"""
from __future__ import annotations

import io
import os
import re
import time
from typing import Any

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

from config import (DEFAULT_SOFR, DIVIDEND_YIELD, MASTER_FILE, PRICE_COL,
                    SYMBOL, TH)
from pricing import bs_delta_batch, solve_iv_batch

MASTER_KEYS = ["Quote Date", "Expiration Date", "Option Type", "Strike"]

# app.py 가 구버전 data_io.py 배포를 감지하는 데 쓰는 표식입니다.
IO_VERSION = "V31"

FINAL_COLS = ["Contract Name", "Quote Date", "Expiration Date", "Option Type",
              "Strike", "Bid", "Ask", "Last Price", "Volume", "Open Interest",
              "Secured Overnight Financing Rate", PRICE_COL,
              "Implied Volatility", "Delta"]

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")


# ═══════════════════════════════════════════════════════════════════
# 0. 컬럼명 정규화 — 벤더마다 다른 헤더를 하나의 표준으로 흡수
# ═══════════════════════════════════════════════════════════════════
def _nk(s: Any) -> str:
    """컬럼명 비교용 키. 공백·특수문자·대소문자 무시."""
    return re.sub(r"[^a-z0-9가-힣]", "", str(s).lower())


_ALIASES: dict[str, tuple[str, ...]] = {
    "Contract Name": ("contractname", "contractsymbol", "optionsymbol", "symbol",
                      "calls", "puts", "옵션코드", "종목코드", "종목명", "계약명"),
    "Quote Date": ("quotedate", "date", "tradedate", "datadate", "asofdate",
                   "기준일", "기준일자", "일자", "조회일", "거래일"),
    "Expiration Date": ("expirationdate", "expiration", "expiry", "expdate",
                        "exp", "만기일", "만기"),
    "Option Type": ("optiontype", "type", "callput", "putcall", "cp", "cporp",
                    "구분", "옵션구분", "콜풋"),
    "Strike": ("strike", "strikeprice", "행사가", "행사가격"),
    "Bid": ("bid", "bidprice", "매수호가"),
    "Ask": ("ask", "askprice", "매도호가"),
    "Last Price": ("lastprice", "last", "lastsale", "lasttradeprice",
                   "종가", "현재가", "최종가"),
    "Volume": ("volume", "vol", "거래량"),
    "Open Interest": ("openinterest", "openint", "oi", "미결제약정", "미결제"),
    "Implied Volatility": ("impliedvolatility", "iv", "impvol", "내재변동성"),
    "Delta": ("delta", "델타"),
    "Secured Overnight Financing Rate": (
        "securedovernightfinancingrate", "sofr", "riskfreerate", "rate", "rf",
        "무위험이자율", "금리"),
}

# 기초자산 가격 컬럼(PRICE_COL)은 config 값에 따라 달라지므로 동적으로 붙입니다.
_ALIASES[PRICE_COL] = tuple(set((
    _nk(PRICE_COL), "underlyingprice", "underlying", "stockprice", "spot",
    "spotprice", "etfprice", "closeprice", "기초자산가격", "현물가", "기초자산",
)))

# 역인덱스: 정규화키 → 표준 컬럼명
_ALIAS_INDEX: dict[str, str] = {}
for _canon, _keys in _ALIASES.items():
    _ALIAS_INDEX.setdefault(_nk(_canon), _canon)
    for _k in _keys:
        _ALIAS_INDEX.setdefault(_nk(_k), _canon)


def _dedupe(names: list[str]) -> list[str]:
    """pandas 와 동일한 방식으로 중복 컬럼에 .1 .2 를 붙입니다."""
    seen: dict[str, int] = {}
    out = []
    for n in names:
        n = str(n).strip()
        if n in seen:
            seen[n] += 1
            out.append(f"{n}.{seen[n]}")
        else:
            seen[n] = 0
            out.append(n)
    return out


def _base_name(col: str) -> str:
    """'Bid.1' → 'Bid'"""
    return re.sub(r"\.\d+$", "", str(col))


# ═══════════════════════════════════════════════════════════════════
# 1. 파일 읽기 (CSV / XLSX) — 헤더 위치·메타데이터 자동 탐지
# ═══════════════════════════════════════════════════════════════════
def _read_raw(src, filename: str | None = None) -> list[pd.DataFrame]:
    """헤더 없이 통째로 읽어 후보 시트 목록을 반환합니다."""
    name = (filename or getattr(src, "name", "") or str(src)).lower()

    if hasattr(src, "seek"):
        try:
            src.seek(0)
        except Exception:
            pass

    if name.endswith((".xlsx", ".xlsm", ".xls", ".xltx")):
        sheets = pd.read_excel(src, sheet_name=None, header=None, dtype=object)
        return list(sheets.values())

    # CSV / TSV — 구분자 자동 추론
    for kwargs in ({"sep": None, "engine": "python"},
                   {"sep": ","}, {"sep": "\t"}, {"sep": ";"}):
        try:
            if hasattr(src, "seek"):
                src.seek(0)
            df = pd.read_csv(src, header=None, dtype=object,
                             on_bad_lines="skip", **kwargs)
            if df.shape[1] >= 3:
                return [df]
        except Exception:
            continue
    raise ValueError("파일을 읽지 못했습니다. CSV 또는 XLSX 인지 확인해 주세요.")


def _find_header_row(raw: pd.DataFrame, scan: int = 30) -> int:
    """알려진 컬럼명이 가장 많이 걸리는 행을 헤더로 판단합니다."""
    best_row, best_hit = 0, 0
    for i in range(min(scan, len(raw))):
        cells = [_nk(v) for v in raw.iloc[i].tolist() if pd.notna(v)]
        hit = sum(1 for c in cells if c in _ALIAS_INDEX)
        has_strike = any(_ALIAS_INDEX.get(c) == "Strike" for c in cells)
        score = hit + (3 if has_strike else 0)
        if score > best_hit:
            best_row, best_hit = i, score
    if best_hit < 3:
        raise ValueError(
            "옵션 체인 헤더를 찾지 못했습니다. "
            "Strike / Expiration / Bid / Ask 같은 컬럼이 있는지 확인해 주세요.")
    return best_row


def _scan_metadata(raw: pd.DataFrame, header_row: int) -> dict:
    """헤더 위쪽 안내문에서 기초자산 가격·기준일을 긁어옵니다 (CBOE 형식 등)."""
    meta: dict = {}
    if header_row <= 0:
        return meta
    text = " ".join(
        str(v) for v in raw.iloc[:header_row].to_numpy().ravel() if pd.notna(v))

    m = re.search(r"last[:\s]+\$?\s*([0-9]+\.?[0-9]*)", text, re.I)
    if m:
        try:
            meta["etf_price"] = float(m.group(1))
        except ValueError:
            pass

    m = re.search(r"date[:\s]+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", text, re.I)
    if not m:
        m = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", text)
    if m:
        d = pd.to_datetime(m.group(1), errors="coerce")
        if pd.notna(d):
            meta["quote_date"] = d.normalize()
    return meta


def _promote_header(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    hdr = _find_header_row(raw)
    meta = _scan_metadata(raw, hdr)
    body = raw.iloc[hdr + 1:].copy()
    body.columns = _dedupe([str(c) for c in raw.iloc[hdr].tolist()])
    body = body.dropna(how="all").reset_index(drop=True)
    # 이름 없는 잉여 컬럼 제거
    body = body.loc[:, [c for c in body.columns
                        if not str(c).lower().startswith(("unnamed", "nan", "none"))]]
    return body, meta


# ═══════════════════════════════════════════════════════════════════
# 2. 와이드(콜/풋 한 행) → 롱 변환
# ═══════════════════════════════════════════════════════════════════
def _is_wide_chain(df: pd.DataFrame) -> bool:
    cols = list(df.columns)
    strike_at = [i for i, c in enumerate(cols) if _ALIAS_INDEX.get(_nk(_base_name(c))) == "Strike"]
    if not strike_at:
        return False
    i = strike_at[0]
    right_bases = {_base_name(c) for c in cols[i + 1:]}
    left_bases = {_base_name(c) for c in cols[:i]}
    return len(right_bases & left_bases) >= 2


def _split_wide_chain(df: pd.DataFrame) -> pd.DataFrame:
    """CBOE 형태(… Calls | Bid Ask … | Strike | Puts | Bid Ask … )를 롱으로 펼칩니다."""
    cols = list(df.columns)
    i = next(k for k, c in enumerate(cols)
             if _ALIAS_INDEX.get(_nk(_base_name(c))) == "Strike")
    strike_col = cols[i]
    left, right = cols[:i], cols[i + 1:]

    right_bases = {_base_name(c): c for c in right}
    call_specific = [c for c in left if _base_name(c) in right_bases]
    shared = [c for c in left
              if c not in call_specific and _nk(_base_name(c)) not in ("calls", "puts")]

    call_name = next((c for c in left if _nk(_base_name(c)) == "calls"), None)
    put_name = next((c for c in right if _nk(_base_name(c)) == "puts"), None)

    def side(specific, ident, tag):
        take = shared + specific + [strike_col] + ([ident] if ident else [])
        s = df[take].copy()
        s.columns = [_base_name(c) for c in take]
        if ident:
            s = s.rename(columns={_base_name(ident): "Contract Name"})
        s["Option Type"] = tag
        return s

    calls = side(call_specific, call_name, "Call")
    puts = side([right_bases[_base_name(c)] for c in call_specific], put_name, "Put")
    return pd.concat([calls, puts], ignore_index=True)


# ═══════════════════════════════════════════════════════════════════
# 3. 표준화
# ═══════════════════════════════════════════════════════════════════
def standardize_option_columns(df: pd.DataFrame) -> pd.DataFrame:
    """어떤 벤더 포맷이든 표준 컬럼명으로 바꿉니다."""
    if _is_wide_chain(df):
        df = _split_wide_chain(df)

    mapping: dict[str, str] = {}
    used: set[str] = set()
    for c in df.columns:
        canon = _ALIAS_INDEX.get(_nk(_base_name(c)))
        if canon and canon not in used:
            mapping[c] = canon
            used.add(canon)
    out = df.rename(columns=mapping)
    return out.loc[:, ~out.columns.duplicated()].copy()


def _norm_option_type(s: pd.Series) -> pd.Series:
    u = s.astype(str).str.strip().str.upper()
    return np.where(u.str.startswith("C"), "Call", "Put")


def _to_num(s: pd.Series) -> pd.Series:
    """'1,234' '62.10%' '$3.20' 같은 문자열도 숫자로 흡수합니다."""
    if s.dtype.kind in "if":
        return s
    cleaned = (s.astype(str)
                .str.replace(r"[,\s$₩]", "", regex=True)
                .str.replace("%", "", regex=False)
                .replace({"": np.nan, "-": np.nan, "nan": np.nan, "None": np.nan}))
    return pd.to_numeric(cleaned, errors="coerce")


# ═══════════════════════════════════════════════════════════════════
# 4. IV / Delta 산출 — 야후 경로와 파일 경로가 공유하는 핵심 로직
# ═══════════════════════════════════════════════════════════════════
def enrich_option_frame(df: pd.DataFrame, etf_price: float, quote_date,
                        sofr: float, stats: dict | None = None,
                        keep_file_greeks: bool = True) -> pd.DataFrame:
    """표준화된 옵션 프레임에 T·IV·Delta 를 채워 최종 형태로 만듭니다."""
    stats = stats if stats is not None else {}
    d = df.copy()

    if "Contract Name" not in d.columns:
        d["Contract Name"] = ""
    for col in ("Bid", "Ask", "Last Price", "Volume", "Open Interest"):
        d[col] = _to_num(d[col]) if col in d.columns else 0.0
        d[col] = d[col].fillna(0)

    d["Strike"] = _to_num(d["Strike"])
    d = d.dropna(subset=["Strike"])
    d["Option Type"] = _norm_option_type(d["Option Type"])

    d["Quote Date"] = pd.to_datetime(quote_date).normalize()
    d["Expiration Date"] = pd.to_datetime(d["Expiration Date"], errors="coerce").dt.normalize()
    d = d.dropna(subset=["Expiration Date"])
    if d.empty:
        raise ValueError("유효한 만기일이 있는 행이 없습니다.")

    d["Secured Overnight Financing Rate"] = sofr
    d[PRICE_COL] = float(etf_price)

    bus = np.busday_count(
        d["Quote Date"].values.astype("datetime64[D]"),
        d["Expiration Date"].values.astype("datetime64[D]"))
    d["T"] = np.maximum(bus, TH.MIN_T_DAYS) / TH.TRADING_DAYS

    # 유동성 필터 — 호가도 미결제도 없는 계약은 IV를 구할 이유가 없습니다
    mid = (d["Bid"] + d["Ask"]) / 2.0
    has_quote = (d["Bid"] > 0) & (d["Ask"] > 0)
    target = np.where(has_quote, mid, d["Last Price"])
    liquid = (target > 0) & (d["Open Interest"] > 0) & (d["T"] > 0)

    stats["total_rows"] = len(d)
    stats["priced_rows"] = int(liquid.sum())
    stats["zero_oi_rows"] = int((d["Open Interest"] <= 0).sum())

    iv = np.full(len(d), np.nan)
    delta = np.full(len(d), np.nan)
    if liquid.any():
        idx = np.flatnonzero(np.asarray(liquid))
        is_call = d["Option Type"].to_numpy()[idx] == "Call"
        r = sofr / 100.0
        iv_sub = solve_iv_batch(
            np.asarray(target)[idx], d[PRICE_COL].to_numpy()[idx],
            d["Strike"].to_numpy()[idx], d["T"].to_numpy()[idx],
            r, DIVIDEND_YIELD, is_call)
        iv[idx] = iv_sub
        delta[idx] = bs_delta_batch(
            d[PRICE_COL].to_numpy()[idx], d["Strike"].to_numpy()[idx],
            d["T"].to_numpy()[idx], r, DIVIDEND_YIELD, iv_sub, is_call)

    # 파일에 벤더 IV/Delta 가 있으면 우리 계산이 실패한 자리만 메웁니다
    if keep_file_greeks:
        for col, arr in (("Implied Volatility", iv), ("Delta", delta)):
            if col in df.columns:
                vend = _to_num(df.loc[d.index, col]).to_numpy(dtype=float)
                if col == "Implied Volatility":
                    with np.errstate(invalid="ignore"):
                        vend = np.where(vend > 3.0, vend / 100.0, vend)  # 퍼센트 표기 흡수
                gap = np.isnan(arr) & ~np.isnan(vend)
                arr[gap] = vend[gap]
                stats[f"filled_from_file_{col}"] = int(gap.sum())

    d["Implied Volatility"] = np.round(iv, 4)
    d["Delta"] = np.round(delta, 4)

    d["Quote Date"] = d["Quote Date"].dt.date
    d["Expiration Date"] = d["Expiration Date"].dt.date

    final = d[FINAL_COLS].copy()
    final["Volume"] = final["Volume"].astype(float).round().astype(int)
    final["Open Interest"] = final["Open Interest"].astype(float).round().astype(int)
    return final.reset_index(drop=True)


# ═══════════════════════════════════════════════════════════════════
# 5. ★ 파일 경로 — 야후와 완전히 무관한 메인 수집 경로
# ═══════════════════════════════════════════════════════════════════
def extract_options_from_file(
    src, *, filename: str | None = None, etf_price: float | None = None,
    quote_date=None, sofr: float | None = None, symbol: str = SYMBOL,
) -> tuple[pd.DataFrame | None, str | None, dict]:
    """엑셀/CSV 로 받은 옵션 체인 → 마스터 병합 가능한 형태로 변환.

    반환 형식은 extract_daily_options() 와 동일합니다: (데이터, 오류메시지, 통계)
    etf_price / quote_date 를 넘기지 않으면 파일 컬럼 → 파일 메타 → 야후 순으로
    찾고, 그래도 없으면 오류를 돌려주어 사용자가 직접 입력하게 합니다.
    """
    stats: dict = {"source": "file", "filename": filename or getattr(src, "name", "")}

    try:
        candidates = _read_raw(src, filename)
    except Exception as e:
        return None, f"파일 읽기 실패: {e}", stats

    best, meta, err = None, {}, None
    for raw in candidates:
        try:
            body, m = _promote_header(raw)
            std = standardize_option_columns(body)
            if "Strike" not in std.columns or "Expiration Date" not in std.columns:
                continue
            if best is None or len(std) > len(best):
                best, meta = std, m
        except Exception as e:
            err = str(e)
            continue

    if best is None:
        return None, f"옵션 체인으로 인식할 수 있는 시트가 없습니다. ({err or '헤더 불일치'})", stats

    std = best
    if "Option Type" not in std.columns:
        return None, ("Call/Put 구분 컬럼을 찾지 못했습니다. "
                      "'Option Type' 컬럼을 추가하거나 CBOE 원본 형식으로 받아주세요."), stats

    stats["detected_columns"] = list(std.columns)
    stats["raw_rows"] = len(std)

    # ── 기준일 결정
    qd = quote_date or meta.get("quote_date")
    if qd is None and "Quote Date" in std.columns:
        parsed = pd.to_datetime(std["Quote Date"], errors="coerce").dropna()
        if not parsed.empty:
            uniq = parsed.dt.normalize().unique()
            if len(uniq) > 1:
                stats["multi_quote_dates"] = [pd.Timestamp(u).date() for u in sorted(uniq)]
            qd = pd.Timestamp(sorted(uniq)[-1])
    if qd is None:
        return None, ("기준일(Quote Date)을 찾지 못했습니다. 화면에서 날짜를 직접 지정해 주세요."), stats
    qd = pd.Timestamp(qd).normalize()
    stats["quote_date"] = qd.date()

    # 파일에 여러 날짜가 섞여 있으면 해당 날짜만 남깁니다 (V29 원칙 유지)
    if "Quote Date" in std.columns:
        col = pd.to_datetime(std["Quote Date"], errors="coerce").dt.normalize()
        if col.notna().any():
            std = std[col == qd]
            if std.empty:
                return None, f"{qd.date()} 에 해당하는 행이 파일에 없습니다.", stats

    # ── 기초자산 가격 결정
    price = etf_price or meta.get("etf_price")
    if price is None and PRICE_COL in std.columns:
        v = _to_num(std[PRICE_COL]).dropna()
        if not v.empty:
            price = float(v.median())
    if price is None:
        price, note = _price_fallback(symbol, qd)
        if note:
            stats["price_source"] = note
    if price is None or not np.isfinite(price) or price <= 0:
        return None, ("기초자산 종가를 확인할 수 없습니다. "
                      "화면에서 EWY 종가를 직접 입력해 주세요."), stats
    stats["etf_price"] = round(float(price), 4)

    # ── 금리
    rate = sofr if sofr is not None else _fetch_sofr()
    stats["sofr"] = rate

    try:
        final = enrich_option_frame(std, float(price), qd, float(rate), stats)
    except Exception as e:
        return None, f"IV/Delta 계산 실패: {e}", stats

    if final.empty:
        return None, "변환 후 남은 행이 없습니다. 파일 내용을 확인해 주세요.", stats
    return final, None, stats


# ═══════════════════════════════════════════════════════════════════
# 6. 시세 — 야후 → stooq → 파일 → 수동
# ═══════════════════════════════════════════════════════════════════
def _make_sessions() -> list:
    """yfinance 버전별로 먹히는 세션 후보를 순서대로 만듭니다.

    yfinance 0.2.5x 이후는 curl_cffi 세션을 요구하며, requests.Session 을 넣으면
    바로 예외가 납니다. 그래서 curl_cffi → requests → 세션없음 순으로 시도합니다.
    """
    sessions: list = []
    try:
        from curl_cffi import requests as cffi
        sessions.append(cffi.Session(impersonate="chrome"))
    except Exception:
        pass
    s = requests.Session()
    s.headers.update({"User-Agent": _UA, "Accept": "*/*"})
    sessions.append(s)
    sessions.append(None)
    return sessions


def _yahoo_history(symbol: str, **kw) -> pd.DataFrame:
    last_err = None
    for sess in _make_sessions():
        try:
            tk = yf.Ticker(symbol, session=sess) if sess is not None else yf.Ticker(symbol)
            hist = tk.history(**kw)
            if hist is not None and not hist.empty:
                return hist
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return pd.DataFrame()


def _stooq_history(symbol: str) -> pd.DataFrame:
    """야후가 막혔을 때의 무료 대체 소스. 미국 ETF 는 티커.us 형식."""
    tick = symbol.lower()
    if not tick.endswith(".us") and "." not in tick and "^" not in tick:
        tick += ".us"
    url = f"https://stooq.com/q/d/l/?s={tick}&i=d"
    r = requests.get(url, timeout=20, headers={"User-Agent": _UA})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    return df.rename(columns={"Close": "Close Price"})[["Date", "Close Price"]]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """야후 → stooq 폴백. 둘 다 실패해도 예외 대신 빈 프레임을 돌려줍니다."""
    empty = pd.DataFrame(columns=["Date", "Close Price"])

    try:
        px = yf.download(symbol, start=start_date, end=end_date,
                         progress=False, auto_adjust=False).reset_index()
        if not px.empty:
            if isinstance(px.columns, pd.MultiIndex):
                px.columns = [c[0] for c in px.columns]
            px = px.rename(columns={"Close": "Close Price"})
            px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None).dt.normalize()
            return (px.sort_values("Date").dropna(subset=["Close Price"])
                      .reset_index(drop=True)[["Date", "Close Price"]])
    except Exception as e:
        st.info(f"야후 시세 실패 — stooq 폴백 시도 ({str(e)[:60]})")

    try:
        px = _stooq_history(symbol)
        if not px.empty:
            mask = ((px["Date"] >= pd.to_datetime(start_date)) &
                    (px["Date"] <= pd.to_datetime(end_date)))
            st.caption("시세 출처: stooq (야후 폴백)")
            return px[mask].sort_values("Date").reset_index(drop=True)
    except Exception as e:
        st.warning(f"시세 조회 실패(야후·stooq 모두): {str(e)[:80]}")

    return empty


def load_price_history_from_file(src, filename: str | None = None) -> pd.DataFrame:
    """EWY_Historical_Data_01.csv 같은 시세 파일을 표준 형태로 읽습니다."""
    raws = _read_raw(src, filename)
    for raw in raws:
        try:
            body, _ = _promote_header(raw)
        except Exception:
            body = raw.copy()
            body.columns = _dedupe([str(c) for c in raw.iloc[0].tolist()])
            body = body.iloc[1:]
        cols = {_nk(c): c for c in body.columns}
        dcol = next((cols[k] for k in cols if k in ("date", "일자", "날짜", "기준일")), None)
        ccol = next((cols[k] for k in cols if k in ("close", "closeprice", "종가", "adjclose")), None)
        if dcol and ccol:
            out = pd.DataFrame({
                "Date": pd.to_datetime(body[dcol], errors="coerce").dt.normalize(),
                "Close Price": _to_num(body[ccol]),
            }).dropna()
            return out.sort_values("Date").reset_index(drop=True)
    return pd.DataFrame(columns=["Date", "Close Price"])


def _price_fallback(symbol: str, quote_date: pd.Timestamp) -> tuple[float | None, str | None]:
    """해당 날짜의 종가를 야후 → stooq 순으로 조용히 찾아봅니다."""
    try:
        hist = _yahoo_history(symbol, period="1mo")
        if not hist.empty:
            idx = pd.to_datetime(hist.index).tz_localize(None).normalize()
            hit = hist[idx <= quote_date]
            if not hit.empty:
                return round(float(hit["Close"].iloc[-1]), 4), "yahoo"
    except Exception:
        pass
    try:
        px = _stooq_history(symbol)
        hit = px[px["Date"] <= quote_date]
        if not hit.empty:
            return round(float(hit["Close Price"].iloc[-1]), 4), "stooq"
    except Exception:
        pass
    return None, None


# ═══════════════════════════════════════════════════════════════════
# 7. 마스터 파일 (기존 로직 유지)
# ═══════════════════════════════════════════════════════════════════
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
            int(pd.to_datetime(current["Quote Date"]).dt.normalize().isin(dup).sum())
            if dup and not current.empty else 0),
    }


def merge_master(current: pd.DataFrame, new: pd.DataFrame,
                 on_conflict: str = "skip") -> pd.DataFrame:
    """날짜 단위 병합."""
    if on_conflict not in ("skip", "replace"):
        raise ValueError(f"on_conflict 는 'skip' 또는 'replace' — 받은 값: {on_conflict}")

    new_n = normalize_option_frame(new)
    if current is None or current.empty:
        return new_n.sort_values("Quote Date").reset_index(drop=True)

    cur = normalize_option_frame(current)

    dup = quote_dates(new_n) & quote_dates(cur)
    if dup:
        if on_conflict == "skip":
            new_n = new_n[~new_n["Quote Date"].isin(dup)]
        else:
            cur = cur[~cur["Quote Date"].isin(dup)]

    if new_n.empty:
        return cur.sort_values("Quote Date").reset_index(drop=True)

    merged = pd.concat([cur, new_n], ignore_index=True)
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


# ═══════════════════════════════════════════════════════════════════
# 8. 야후 경로 (보조) — 실패해도 파일 경로가 있으므로 치명적이지 않습니다
# ═══════════════════════════════════════════════════════════════════
def _fetch_sofr() -> float:
    try:
        import pandas_datareader as pdr
        return round(float(pdr.DataReader("SOFR", "fred")["SOFR"].dropna().iloc[-1]), 2)
    except Exception:
        return DEFAULT_SOFR


def extract_daily_options(retries: int = 2) -> tuple[pd.DataFrame | None, str | None, dict]:
    """야후 옵션 체인 수집 + IV/Delta 연산. (데이터, 오류메시지, 통계) 반환."""
    stats: dict = {"source": "yahoo"}
    sofr = _fetch_sofr()
    stats["sofr"] = sofr

    ticker = None
    hist = pd.DataFrame()
    last_err = None
    for sess in _make_sessions():
        try:
            tk = yf.Ticker(SYMBOL, session=sess) if sess is not None else yf.Ticker(SYMBOL)
            h = tk.history(period="5d")
            if h is not None and not h.empty:
                ticker, hist = tk, h
                break
        except Exception as e:
            last_err = e
            continue

    if ticker is None or hist.empty:
        return None, (f"야후에서 주가를 불러오지 못했습니다 ({str(last_err)[:60]}). "
                      "엑셀/CSV 업로드 경로를 사용해 주세요."), stats

    etf_price = round(float(hist["Close"].iloc[-1]), 2)
    quote_date = hist.index[-1].date()
    stats["quote_date"] = quote_date
    stats["etf_price"] = etf_price

    expirations: tuple = ()
    for attempt in range(max(1, retries) + 1):
        try:
            expirations = tuple(ticker.options or ())
        except Exception as e:
            last_err = e
            expirations = ()
        if expirations:
            break
        time.sleep(1.5 * (attempt + 1))

    if not expirations:
        return None, ("야후가 만기일 목록을 주지 않습니다 (차단 의심). "
                      "엑셀/CSV 업로드 경로를 사용해 주세요."), stats

    frames, skipped = [], []
    for exp in expirations:
        try:
            chain = ticker.option_chain(exp)
            for side, tag in ((chain.calls, "Call"), (chain.puts, "Put")):
                if side is None or side.empty:
                    continue
                part = side.copy()
                part["Option Type"] = tag
                part["Expiration Date"] = exp
                frames.append(part)
        except Exception as e:
            skipped.append(f"{exp}({str(e)[:30]})")

    if skipped:
        stats["skipped_expirations"] = skipped
    if not frames:
        return None, ("수집 가능한 옵션 데이터가 없습니다 (API 차단 의심). "
                      "엑셀/CSV 업로드 경로를 사용해 주세요."), stats

    df = standardize_option_columns(pd.concat(frames, ignore_index=True))
    if df.empty:
        return None, "병합된 옵션 데이터의 행(Row)이 존재하지 않습니다.", stats

    try:
        final = enrich_option_frame(df, etf_price, quote_date, sofr, stats)
    except Exception as e:
        return None, f"IV/Delta 계산 실패: {e}", stats
    return final, None, stats


# ═══════════════════════════════════════════════════════════════════
# 10. 다운로드 · 로컬 저장 · 다중 병합
# ═══════════════════════════════════════════════════════════════════
DOWNLOAD_FOLDER = "EWY Option"


def latest_data_date(*frames) -> pd.Timestamp | None:
    """넘긴 프레임들 중 가장 마지막 Quote Date.

    오늘 날짜가 아니라 '데이터의 최종 일자'입니다. 장 마감 전 조회나 휴장일
    조회에서 파일명이 실제 데이터와 어긋나지 않게 하려는 목적입니다.
    """
    dates = []
    for df in frames:
        if df is None or getattr(df, "empty", True):
            continue
        if "Quote Date" not in df.columns:
            continue
        s = pd.to_datetime(df["Quote Date"], errors="coerce").dropna()
        if not s.empty:
            dates.append(s.max())
    return max(dates) if dates else None


def build_filename(data_date=None, kind: str = "분석데이터", ext: str = "csv",
                   symbol: str = SYMBOL) -> str:
    """'EWY Option 분석데이터_20260831.csv' 형태의 파일명을 만듭니다."""
    d = pd.to_datetime(data_date, errors="coerce") if data_date is not None else None
    stamp = d.strftime("%Y%m%d") if d is not None and pd.notna(d) else "날짜미상"
    return f"{symbol} Option {kind}_{stamp}.{ext}"


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """엑셀에서 한글이 깨지지 않도록 BOM 을 붙인 UTF-8 바이트."""
    return df.to_csv(index=False).encode("utf-8-sig")


def to_zip_bytes(files: dict[str, bytes], folder: str = DOWNLOAD_FOLDER) -> bytes:
    """폴더 구조를 가진 zip 을 만듭니다.

    브라우저는 보안상 다운로드 경로를 지정할 수 없어서, 'EWY Option' 폴더로
    받으려면 폴더를 품은 zip 을 내려주는 방법밖에 없습니다. 압축을 풀면
    'EWY Option/파일명.csv' 로 생성됩니다.
    """
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(f"{folder}/{name}", data)
    return buf.getvalue()


def save_to_local_folder(data: bytes, filename: str,
                         folder: str = DOWNLOAD_FOLDER,
                         base_dir: str | None = None) -> str:
    """실행 중인 머신의 <base_dir>/<folder>/ 에 직접 저장하고 경로를 돌려줍니다.

    로컬에서 streamlit 을 돌릴 때만 의미가 있습니다. Streamlit Cloud 에서는
    서버 컨테이너에 쓰이므로 PC 에는 남지 않습니다.
    """
    root = os.path.expanduser(base_dir) if base_dir else os.getcwd()
    target = os.path.join(root, folder)
    os.makedirs(target, exist_ok=True)
    path = os.path.join(target, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path


def merge_many(current: pd.DataFrame, frames: list[pd.DataFrame],
               on_conflict: str = "skip") -> tuple[pd.DataFrame, list[dict]]:
    """여러 추출본을 순서대로 누적 병합합니다. 각 단계의 리포트도 함께 반환."""
    merged = (current.copy() if current is not None and not current.empty
              else pd.DataFrame())
    reports: list[dict] = []
    for i, new in enumerate(frames):
        if new is None or new.empty:
            continue
        rep = merge_report(merged, new)
        rep["step"] = i + 1
        merged = merge_master(merged, new, on_conflict=on_conflict)
        rep["rows_after"] = len(merged)
        reports.append(rep)
    return merged, reports


def extract_options_from_files(
    files, *, on_conflict: str = "skip", **kwargs,
) -> tuple[pd.DataFrame | None, list[dict]]:
    """여러 파일을 한 번에 변환하고 하나로 누적 병합합니다.

    반환: (병합된 데이터 또는 None, 파일별 결과 목록)
    """
    frames, results = [], []
    for f in files:
        name = getattr(f, "name", str(f))
        df, err, stats = extract_options_from_file(f, filename=name, **kwargs)
        results.append({
            "filename": name,
            "rows": 0 if df is None else len(df),
            "quote_date": stats.get("quote_date"),
            "priced_rows": stats.get("priced_rows", 0),
            "error": err,
            "stats": stats,
        })
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        return None, results

    combined, reports = merge_many(pd.DataFrame(), frames, on_conflict=on_conflict)
    for r, rep in zip([x for x in results if not x["error"]], reports):
        r["merge"] = rep
    return combined, results


# ═══════════════════════════════════════════════════════════════════
# 11. 진단
# ═══════════════════════════════════════════════════════════════════
def diagnose_quote_date(master: pd.DataFrame, extracted: pd.DataFrame | None,
                        target) -> pd.DataFrame:
    """특정 날짜가 마스터/추출본에서 어떻게 구성되는지 비교합니다."""
    t = pd.to_datetime(target).normalize()
    rows = []

    def summarize(df, label):
        blank = {"출처": label, "행수": 0, "만기수": 0,
                 "OI합": 0, "OI=0 비율": "-", "행사가 범위": "-", "IV 결측률": "-"}
        if df is None or df.empty:
            rows.append(blank)
            return
        d = normalize_option_frame(df)
        d = d[d["Quote Date"] == t]
        if d.empty:
            rows.append(blank)
            return
        iv_na = (d["Implied Volatility"].isna().mean()
                 if "Implied Volatility" in d.columns else np.nan)
        rows.append({
            "출처": label,
            "행수": len(d),
            "만기수": d["Expiration Date"].nunique(),
            "OI합": int(d["Open Interest"].sum()),
            "OI=0 비율": f"{(d['Open Interest'] <= 0).mean():.0%}",
            "행사가 범위": f"{d['Strike'].min():.0f}~{d['Strike'].max():.0f}",
            "IV 결측률": "-" if pd.isna(iv_na) else f"{iv_na:.0%}",
        })

    summarize(master, "마스터")
    summarize(extracted, "신규 추출")
    if extracted is not None and not extracted.empty:
        summarize(merge_master(master, extracted, "skip"), "병합(skip)")
        summarize(merge_master(master, extracted, "replace"), "병합(replace)")
    return pd.DataFrame(rows)
