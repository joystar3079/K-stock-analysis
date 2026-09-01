"""데이터 입출력 — 파일 업로드 전용 모듈 (API 자동 수집 폐기)

[V34 경량화 최종본] 
  1) 야후 파이낸스 옵션 API 수집 경로 완전 삭제 (로컬 CSV 업로드 전용)
  2) [오류 수정] 429 Too Many Requests (트래픽 초과) 방어 로직 추가
     - 옵션 크롤링이 빠졌으므로, 시세(history) 조회 전용 브라우저 위장 세션 재투입
     - 차단 시 지연 재시도(Exponential Backoff) 알고리즘 탑재
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
IO_VERSION = "V34_File_Only_Final"

FINAL_COLS = ["Contract Name", "Quote Date", "Expiration Date", "Option Type",
              "Strike", "Bid", "Ask", "Last Price", "Volume", "Open Interest",
              "Secured Overnight Financing Rate", PRICE_COL,
              "Implied Volatility", "Delta"]

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# ═══════════════════════════════════════════════════════════════════
# 0. 컬럼명 정규화
# ═══════════════════════════════════════════════════════════════════
def _nk(s: Any) -> str:
    return re.sub(r"[^a-z0-9가-힣]", "", str(s).lower())

_ALIASES: dict[str, tuple[str, ...]] = {
    "Contract Name": ("contractname", "contractsymbol", "optionsymbol", "symbol", "calls", "puts", "옵션코드", "종목코드", "종목명", "계약명"),
    "Quote Date": ("quotedate", "date", "tradedate", "datadate", "asofdate", "기준일", "기준일자", "일자", "조회일", "거래일"),
    "Expiration Date": ("expirationdate", "expiration", "expiry", "expdate", "exp", "만기일", "만기"),
    "Option Type": ("optiontype", "type", "callput", "putcall", "cp", "cporp", "구분", "옵션구분", "콜풋"),
    "Strike": ("strike", "strikeprice", "행사가", "행사가격"),
    "Bid": ("bid", "bidprice", "매수호가"),
    "Ask": ("ask", "askprice", "매도호가"),
    "Last Price": ("lastprice", "last", "lastsale", "lasttradeprice", "종가", "현재가", "최종가"),
    "Volume": ("volume", "vol", "거래량"),
    "Open Interest": ("openinterest", "openint", "oi", "미결제약정", "미결제"),
    "Implied Volatility": ("impliedvolatility", "iv", "impvol", "내재변동성"),
    "Delta": ("delta", "델타"),
    "Secured Overnight Financing Rate": ("securedovernightfinancingrate", "sofr", "riskfreerate", "rate", "rf", "무위험이자율", "금리"),
}
_ALIASES[PRICE_COL] = tuple(set((_nk(PRICE_COL), "underlyingprice", "underlying", "stockprice", "spot", "spotprice", "etfprice", "closeprice", "기초자산가격", "현물가", "기초자산")))

_ALIAS_INDEX: dict[str, str] = {}
for _canon, _keys in _ALIASES.items():
    _ALIAS_INDEX.setdefault(_nk(_canon), _canon)
    for _k in _keys:
        _ALIAS_INDEX.setdefault(_nk(_k), _canon)

def _dedupe(names: list[str]) -> list[str]:
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
    return re.sub(r"\.\d+$", "", str(col))

# ═══════════════════════════════════════════════════════════════════
# 1. 파일 읽기 및 메타데이터 탐지
# ═══════════════════════════════════════════════════════════════════
def _read_raw(src, filename: str | None = None) -> list[pd.DataFrame]:
    name = (filename or getattr(src, "name", "") or str(src)).lower()
    if hasattr(src, "seek"):
        try: src.seek(0)
        except Exception: pass
    if name.endswith((".xlsx", ".xlsm", ".xls", ".xltx")):
        sheets = pd.read_excel(src, sheet_name=None, header=None, dtype=object)
        return list(sheets.values())
    for kwargs in ({"sep": None, "engine": "python"}, {"sep": ","}, {"sep": "\t"}, {"sep": ";"}):
        try:
            if hasattr(src, "seek"): src.seek(0)
            df = pd.read_csv(src, header=None, dtype=object, on_bad_lines="skip", **kwargs)
            if df.shape[1] >= 3: return [df]
        except Exception: continue
    raise ValueError("파일을 읽지 못했습니다. CSV 또는 XLSX 인지 확인해 주세요.")

def _find_header_row(raw: pd.DataFrame, scan: int = 30) -> int:
    best_row, best_hit = 0, 0
    for i in range(min(scan, len(raw))):
        cells = [_nk(v) for v in raw.iloc[i].tolist() if pd.notna(v)]
        hit = sum(1 for c in cells if c in _ALIAS_INDEX)
        has_strike = any(_ALIAS_INDEX.get(c) == "Strike" for c in cells)
        score = hit + (3 if has_strike else 0)
        if score > best_hit: best_row, best_hit = i, score
    if best_hit < 3:
        raise ValueError("옵션 체인 헤더를 찾지 못했습니다.")
    return best_row

def _scan_metadata(raw: pd.DataFrame, header_row: int) -> dict:
    meta: dict = {}
    if header_row <= 0: return meta
    text = " ".join(str(v) for v in raw.iloc[:header_row].to_numpy().ravel() if pd.notna(v))
    m = re.search(r"last[:\s]+\$?\s*([0-9]+\.?[0-9]*)", text, re.I)
    if m:
        try: meta["etf_price"] = float(m.group(1))
        except ValueError: pass
    m = re.search(r"date[:\s]+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", text, re.I)
    if not m: m = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", text)
    if m:
        d = pd.to_datetime(m.group(1), errors="coerce")
        if pd.notna(d): meta["quote_date"] = d.normalize()
    return meta

def _promote_header(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    hdr = _find_header_row(raw)
    meta = _scan_metadata(raw, hdr)
    body = raw.iloc[hdr + 1:].copy()
    body.columns = _dedupe([str(c) for c in raw.iloc[hdr].tolist()])
    body = body.dropna(how="all").reset_index(drop=True)
    body = body.loc[:, [c for c in body.columns if not str(c).lower().startswith(("unnamed", "nan", "none"))]]
    return body, meta

def standardize_option_columns(df: pd.DataFrame) -> pd.DataFrame:
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
    if s.dtype.kind in "if": return s
    cleaned = (s.astype(str).str.replace(r"[,\s$₩]", "", regex=True)
               .str.replace("%", "", regex=False).replace({"": np.nan, "-": np.nan, "nan": np.nan, "None": np.nan}))
    return pd.to_numeric(cleaned, errors="coerce")

# ═══════════════════════════════════════════════════════════════════
# 2. IV / Delta 산출 (결측치 발생 시 보완)
# ═══════════════════════════════════════════════════════════════════
def enrich_option_frame(df: pd.DataFrame, etf_price: float, quote_date,
                        sofr: float, stats: dict | None = None,
                        keep_file_greeks: bool = True) -> pd.DataFrame:
    stats = stats if stats is not None else {}
    d = df.copy()

    if "Contract Name" not in d.columns: d["Contract Name"] = ""
    for col in ("Bid", "Ask", "Last Price", "Volume", "Open Interest"):
        d[col] = _to_num(d[col]) if col in d.columns else 0.0
        d[col] = d[col].fillna(0)

    d["Strike"] = _to_num(d["Strike"])
    d = d.dropna(subset=["Strike"])
    d["Option Type"] = _norm_option_type(d["Option Type"])

    d["Quote Date"] = pd.to_datetime(quote_date).normalize()
    d["Expiration Date"] = pd.to_datetime(d["Expiration Date"], errors="coerce").dt.normalize()
    d = d.dropna(subset=["Expiration Date"])
    if d.empty: raise ValueError("유효한 만기일이 있는 행이 없습니다.")

    d["Secured Overnight Financing Rate"] = sofr
    d[PRICE_COL] = float(etf_price)

    bus = np.busday_count(d["Quote Date"].values.astype("datetime64[D]"), d["Expiration Date"].values.astype("datetime64[D]"))
    d["T"] = np.maximum(bus, TH.MIN_T_DAYS) / TH.TRADING_DAYS

    mid = (d["Bid"] + d["Ask"]) / 2.0
    has_quote = (d["Bid"] > 0) & (d["Ask"] > 0)
    target = np.where(has_quote, mid, d["Last Price"])
    liquid = (target > 0) & (d["Open Interest"] > 0) & (d["T"] > 0)

    stats["total_rows"] = len(d)
    stats["priced_rows"] = int(liquid.sum())

    iv = np.full(len(d), np.nan)
    delta = np.full(len(d), np.nan)
    if liquid.any() and not keep_file_greeks:
        idx = np.flatnonzero(np.asarray(liquid))
        is_call = d["Option Type"].to_numpy()[idx] == "Call"
        r = sofr / 100.0
        iv_sub = solve_iv_batch(np.asarray(target)[idx], d[PRICE_COL].to_numpy()[idx], d["Strike"].to_numpy()[idx], d["T"].to_numpy()[idx], r, DIVIDEND_YIELD, is_call)
        iv[idx] = iv_sub
        delta[idx] = bs_delta_batch(d[PRICE_COL].to_numpy()[idx], d["Strike"].to_numpy()[idx], d["T"].to_numpy()[idx], r, DIVIDEND_YIELD, iv_sub, is_call)

    if keep_file_greeks:
        for col, arr in (("Implied Volatility", iv), ("Delta", delta)):
            if col in df.columns:
                vend = _to_num(df.loc[d.index, col]).to_numpy(dtype=float)
                if col == "Implied Volatility":
                    with np.errstate(invalid="ignore"):
                        vend = np.where(vend > 3.0, vend / 100.0, vend) 
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
# 3. 파일 추출 전용 경로 (핵심)
# ═══════════════════════════════════════════════════════════════════
def extract_options_from_file(src, *, filename: str | None = None) -> tuple[pd.DataFrame | None, str | None, dict]:
    stats: dict = {"source": "file", "filename": filename or getattr(src, "name", "")}
    try: candidates = _read_raw(src, filename)
    except Exception as e: return None, f"파일 읽기 실패: {e}", stats

    best, meta, err = None, {}, None
    for raw in candidates:
        try:
            body, m = _promote_header(raw)
            std = standardize_option_columns(body)
            if "Strike" not in std.columns or "Expiration Date" not in std.columns: continue
            if best is None or len(std) > len(best):
                best, meta = std, m
        except Exception as e:
            err = str(e)
            continue

    if best is None:
        return None, f"옵션 체인으로 인식할 수 없습니다. ({err or '헤더 불일치'})", stats

    std = best
    stats["detected_columns"] = list(std.columns)
    
    qd = meta.get("quote_date")
    if qd is None and "Quote Date" in std.columns:
        parsed = pd.to_datetime(std["Quote Date"], errors="coerce").dropna()
        if not parsed.empty:
            uniq = parsed.dt.normalize().unique()
            qd = pd.Timestamp(sorted(uniq)[-1])
            
    if qd is None: return None, "기준일(Quote Date) 컬럼을 찾을 수 없습니다.", stats
    qd = pd.Timestamp(qd).normalize()
    stats["quote_date"] = qd.date()

    if "Quote Date" in std.columns:
        col = pd.to_datetime(std["Quote Date"], errors="coerce").dt.normalize()
        if col.notna().any(): std = std[col == qd]

    price = meta.get("etf_price")
    if price is None and PRICE_COL in std.columns:
        v = _to_num(std[PRICE_COL]).dropna()
        if not v.empty: price = float(v.median())
    if price is None or not np.isfinite(price) or price <= 0:
        return None, "기초자산 종가(EWY Price) 컬럼을 찾을 수 없습니다.", stats
    stats["etf_price"] = round(float(price), 4)

    sofr = DEFAULT_SOFR
    if "Secured Overnight Financing Rate" in std.columns:
        v = _to_num(std["Secured Overnight Financing Rate"]).dropna()
        if not v.empty: sofr = float(v.median())
    stats["sofr"] = sofr

    try:
        final = enrich_option_frame(std, float(price), qd, float(sofr), stats, keep_file_greeks=True)
    except Exception as e:
        return None, f"데이터 처리 실패: {e}", stats

    if final.empty: return None, "변환 후 남은 행이 없습니다.", stats
    return final, None, stats

# ═══════════════════════════════════════════════════════════════════
# 4. 기초자산 시세 수집 (MA 연산용 / 429 방어 로직 적용)
# ═══════════════════════════════════════════════════════════════════
def _stooq_history(symbol: str) -> pd.DataFrame:
    tick = symbol.lower()
    if not tick.endswith(".us") and "." not in tick and "^" not in tick: tick += ".us"
    url = f"https://stooq.com/q/d/l/?s={tick}&i=d"
    r = requests.get(url, timeout=20, headers={"User-Agent": _UA})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if df.empty or "Close" not in df.columns: return pd.DataFrame()
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    return df.rename(columns={"Close": "Close Price"})[["Date", "Close Price"]]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """야후 → stooq 폴백 시세 수집.
    옵션 조회가 빠졌으므로, 429(Too Many Requests) 트래픽 차단을 뚫기 위해 
    강력한 브라우저 위장 세션을 시세 전용으로 다시 투입합니다.
    """
    empty = pd.DataFrame(columns=["Date", "Close Price"])
    last_err = ""
    
    # 💡 [핵심 방어막] 시세 조회 전용 위장 세션 구축 (429 차단 우회)
    s = requests.Session()
    s.headers.update({
        "User-Agent": _UA,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"
    })

    # 지연 재시도 (Exponential Backoff)
    for attempt in range(3):
        try:
            tk = yf.Ticker(symbol, session=s)
            px = tk.history(start=start_date, end=end_date).reset_index()
            
            if not px.empty:
                if "Datetime" in px.columns:
                    px = px.rename(columns={"Datetime": "Date"})
                    
                if "Close" in px.columns:
                    px = px.rename(columns={"Close": "Close Price"})
                    px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None).dt.normalize()
                    return px.sort_values("Date").dropna(subset=["Close Price"]).reset_index(drop=True)[["Date", "Close Price"]]
                    
        except Exception as e:
            last_err = str(e)
            # 429 에러(트래픽 초과) 발생 시 약간 대기 후 재시도
            if "429" in last_err or "Too Many Requests" in last_err:
                time.sleep(1.5 * (attempt + 1))
                continue
            else:
                break # 다른 형태의 오류면 즉시 루프 탈출
                
    st.info(f"야후 시세 실패 — stooq 폴백 시도 ({last_err[:60]})")

    try:
        px = _stooq_history(symbol)
        if not px.empty:
            mask = ((px["Date"] >= pd.to_datetime(start_date)) & (px["Date"] <= pd.to_datetime(end_date)))
            return px[mask].sort_values("Date").reset_index(drop=True)
    except Exception:
        pass
    
    return empty

# ═══════════════════════════════════════════════════════════════════
# 5. 마스터 파일 및 다중 병합
# ═══════════════════════════════════════════════════════════════════
DOWNLOAD_FOLDER = "EWY Option"

def latest_data_date(*frames) -> pd.Timestamp | None:
    dates = []
    for df in frames:
        if df is None or getattr(df, "empty", True): continue
        if "Quote Date" not in df.columns: continue
        s = pd.to_datetime(df["Quote Date"], errors="coerce").dropna()
        if not s.empty: dates.append(s.max())
    return max(dates) if dates else None

def build_filename(data_date=None, kind: str = "분석데이터", ext: str = "csv", symbol: str = SYMBOL) -> str:
    d = pd.to_datetime(data_date, errors="coerce") if data_date is not None else None
    stamp = d.strftime("%Y%m%d") if d is not None and pd.notna(d) else "날짜미상"
    return f"{symbol} Option {kind}_{stamp}.{ext}"

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

def to_zip_bytes(files: dict[str, bytes], folder: str = DOWNLOAD_FOLDER) -> bytes:
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(f"{folder}/{name}", data)
    return buf.getvalue()

def _repo_name() -> str | None:
    try: return st.secrets["GITHUB_REPO"]
    except Exception: return None

@st.cache_data(ttl=600, show_spinner=False)
def load_master_data(cache_bust: str = "") -> pd.DataFrame:
    repo = _repo_name()
    if repo:
        url = f"https://raw.githubusercontent.com/{repo}/main/{MASTER_FILE}"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return pd.read_pickle(io.BytesIO(resp.content), compression="gzip")
        except Exception as e: pass
    if os.path.exists(MASTER_FILE):
        try: return pd.read_pickle(MASTER_FILE)
        except Exception: pass
    return pd.DataFrame()

def normalize_option_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Quote Date"] = pd.to_datetime(out["Quote Date"]).dt.normalize()
    out["Expiration Date"] = pd.to_datetime(out["Expiration Date"]).dt.normalize()
    out["Option Type"] = np.where(out["Option Type"].astype(str).str.upper().str.startswith("C"), "C", "P")
    return out

def quote_dates(df: pd.DataFrame) -> set[pd.Timestamp]:
    if df.empty or "Quote Date" not in df.columns: return set()
    return set(pd.to_datetime(df["Quote Date"]).dt.normalize().unique())

def merge_report(current: pd.DataFrame, new: pd.DataFrame) -> dict:
    cur_d, new_d = quote_dates(current), quote_dates(new)
    dup = sorted(new_d & cur_d)
    add = sorted(new_d - cur_d)
    return {"new_dates": [d.date() for d in add], "conflict_dates": [d.date() for d in dup],
            "master_rows": len(current), "new_rows": len(new),
            "conflict_rows_in_master": int(pd.to_datetime(current["Quote Date"]).dt.normalize().isin(dup).sum()) if dup and not current.empty else 0}

def merge_master(current: pd.DataFrame, new: pd.DataFrame, on_conflict: str = "skip") -> pd.DataFrame:
    new_n = normalize_option_frame(new)
    if current is None or current.empty: return new_n.sort_values("Quote Date").reset_index(drop=True)
    cur = normalize_option_frame(current)
    dup = quote_dates(new_n) & quote_dates(cur)
    if dup:
        if on_conflict == "skip": new_n = new_n[~new_n["Quote Date"].isin(dup)]
        else: cur = cur[~cur["Quote Date"].isin(dup)]
    if new_n.empty: return cur.sort_values("Quote Date").reset_index(drop=True)
    merged = pd.concat([cur, new_n], ignore_index=True)
    return merged.drop_duplicates(subset=MASTER_KEYS, keep="last").sort_values("Quote Date").reset_index(drop=True)

def push_master_to_github(merged: pd.DataFrame, quote_date) -> int:
    from github import Github
    buffer = io.BytesIO()
    merged.to_pickle(buffer, compression="gzip")
    payload = buffer.getvalue()
    repo = Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["GITHUB_REPO"])
    msg = f"Auto-update master data: {quote_date}"
    try:
        contents = repo.get_contents(MASTER_FILE)
        repo.update_file(contents.path, msg, payload, contents.sha)
    except Exception:
        repo.create_file(MASTER_FILE, f"Create master data: {quote_date}", payload)
    return len(merged)

def master_summary(df: pd.DataFrame) -> dict:
    if df is None or df.empty: return {"rows": 0, "days": 0, "start": None, "end": None}
    d = pd.to_datetime(df["Quote Date"], errors="coerce").dropna()
    return {"rows": len(df), "days": int(d.dt.normalize().nunique()), "start": d.min(), "end": d.max()}

def auto_update_master(current: pd.DataFrame, new: pd.DataFrame, on_conflict: str = "skip") -> dict:
    before = master_summary(current)
    rep = merge_report(current if current is not None else pd.DataFrame(), new)
    merged = merge_master(current, new, on_conflict=on_conflict)
    rows = push_master_to_github(merged, latest_data_date(new))
    after = master_summary(merged)
    return {"file": MASTER_FILE, "policy": on_conflict, "before": before, "after": after,
            "added_rows": rows - before["rows"], "added_days": after["days"] - before["days"], "report": rep}

def merge_many(current: pd.DataFrame, frames: list[pd.DataFrame], on_conflict: str = "skip") -> tuple[pd.DataFrame, list[dict]]:
    merged = current.copy() if current is not None and not current.empty else pd.DataFrame()
    reports: list[dict] = []
    for i, new in enumerate(frames):
        if new is None or new.empty: continue
        rep = merge_report(merged, new)
        rep["step"] = i + 1
        merged = merge_master(merged, new, on_conflict=on_conflict)
        rep["rows_after"] = len(merged)
        reports.append(rep)
    return merged, reports

def extract_options_from_files(files, *, on_conflict: str = "skip", **kwargs) -> tuple[pd.DataFrame | None, list[dict]]:
    frames, results = [], []
    for f in files:
        name = getattr(f, "name", str(f))
        df, err, stats = extract_options_from_file(f, filename=name)
        results.append({"filename": name, "rows": 0 if df is None else len(df),
                        "quote_date": stats.get("quote_date"), "priced_rows": stats.get("priced_rows", 0),
                        "error": err, "stats": stats})
        if df is not None and not df.empty: frames.append(df)
    if not frames: return None, results
    combined, reports = merge_many(pd.DataFrame(), frames, on_conflict=on_conflict)
    for r, rep in zip([x for x in results if not x["error"]], reports): r["merge"] = rep
    return combined, results

def diagnose_quote_date(master: pd.DataFrame, extracted: pd.DataFrame | None, target) -> pd.DataFrame:
    t = pd.to_datetime(target).normalize()
    rows = []
    def summarize(df, label):
        blank = {"출처": label, "행수": 0, "만기수": 0, "OI합": 0, "OI=0 비율": "-", "행사가 범위": "-", "IV 결측률": "-"}
        if df is None or df.empty:
            rows.append(blank)
            return
        d = normalize_option_frame(df)
        d = d[d["Quote Date"] == t]
        if d.empty:
            rows.append(blank)
            return
        iv_na = d["Implied Volatility"].isna().mean() if "Implied Volatility" in d.columns else np.nan
        rows.append({"출처": label, "행수": len(d), "만기수": d["Expiration Date"].nunique(),
                     "OI합": int(d["Open Interest"].sum()), "OI=0 비율": f"{(d['Open Interest'] <= 0).mean():.0%}",
                     "행사가 범위": f"{d['Strike'].min():.0f}~{d['Strike'].max():.0f}",
                     "IV 결측률": "-" if pd.isna(iv_na) else f"{iv_na:.0%}"})
    summarize(master, "마스터")
    summarize(extracted, "신규 추출")
    if extracted is not None and not extracted.empty:
        summarize(merge_master(master, extracted, "skip"), "병합(skip)")
        summarize(merge_master(master, extracted, "replace"), "병합(replace)")
    return pd.DataFrame(rows)
