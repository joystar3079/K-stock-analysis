"""V34 가격(방어벽) · 거래량(레짐) 엔진 실행 — 스트림잇 원본(app.py)의 build_full_frame · run_quant_engine ·
거래량 메뉴와 같은 계산·선택·표시 규칙. 계산 모듈(features · phases · presenters · volume_analysis)은 원본 그대로 씁니다."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import DISPLAY_COLS, ENGINES, PRICE_COL, SYMBOL
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns
from volume_analysis import run_volume_analysis

PRICE_MODES = ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회")
VOLUME_MODES = ("최근 시그널 분석 (15일)", "구간 조회")
VOLUME_VERSION = "V35.0"


class QuantError(Exception):
    """화면에 그대로 보여 줄 오류"""


def price_base(master_df):
    """버전과 무관한 부분 (원본 build_full_frame의 attach_price까지)"""
    if master_df is None or master_df.empty:
        raise QuantError("❌ 마스터 데이터가 비어 있습니다. [⛁ 데이터 관리]에서 데이터를 수집하세요.")
    if PRICE_COL not in master_df.columns:
        raise QuantError("❌ 기초자산 시세(EWY Price) 정보를 찾지 못했습니다. 마스터 파일 데이터를 확인하세요.")
    px = master_df[["Quote Date", PRICE_COL]].drop_duplicates(subset=["Quote Date"]).copy()
    px.rename(columns={"Quote Date": "Date", PRICE_COL: "Close Price"}, inplace=True)
    px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None).dt.normalize()
    px = px.sort_values("Date").dropna(subset=["Close Price"]).reset_index(drop=True)
    if px.empty:
        raise QuantError("❌ 기초자산 시세(EWY Price) 정보를 찾지 못했습니다. 마스터 파일 데이터를 확인하세요.")
    opt_df = aggregate_oi_features(master_df, px)
    if opt_df.empty:
        raise QuantError("❌ 조회 결과가 없습니다. 마스터 데이터를 확인하세요.")
    return attach_price(opt_df, px, master_df)


def volume_frame(master_df):
    vol = run_volume_analysis(master_df)
    if vol.empty:
        raise QuantError("❌ 거래량 모델 연산 실패 (데이터 부족)")
    return vol


def _day(v, what):
    d = pd.to_datetime(v, errors="coerce")
    if pd.isna(d):
        raise QuantError(f"❌ {what}을(를) 고르세요.")
    return pd.Timestamp(d).normalize()


def run_price(base, version, mode, target_date=None, start=None, end=None):
    """-> (표 DataFrame, 기준일 Timestamp, 누적 일수, detail 글)"""
    cfg = ENGINES[version]
    df = add_display_columns(assign_phases(base, cfg), cfg)
    detail = mode
    if mode == "구간 조회":
        a, z = sorted([_day(start, "시작일"), _day(end, "종료일")])
        sel = df[(df["Date"] >= a) & (df["Date"] <= z)].copy()
        detail += f" ({a:%Y-%m-%d} ~ {z:%Y-%m-%d})"
    elif mode == "타임머신 (특정일)":
        t = _day(target_date, "기준일")
        sel = df[df["Date"] <= t].tail(10).copy()
        detail += f" ({t:%Y-%m-%d})"
    else:
        sel = df.tail(10).copy()
    if sel.empty:
        raise QuantError("❌ 조회 결과가 없습니다. 기간이나 데이터를 확인하세요.")
    anchor = pd.to_datetime(sel["Date"].max())
    sel = sel[DISPLAY_COLS].copy()
    sel["Date"] = sel["Date"].dt.strftime("%m/%d")
    sel["Close Price"] = sel["Close Price"].round(2)
    sel = sel.rename(columns={"Close Price": f"{SYMBOL}($)", "Phase": "현재 시장 국면 진단"})
    return sel.reset_index(drop=True), anchor, len(df), detail


def run_volume(vol_df, mode, start=None, end=None):
    """-> (표 DataFrame, 기준일 Timestamp, detail 글)"""
    detail = mode
    if mode == "구간 조회":
        a, z = sorted([_day(start, "시작일"), _day(end, "종료일")])
        sel = vol_df[(vol_df["Quote Date"] >= a) & (vol_df["Quote Date"] <= z)].copy()
        detail += f" ({a:%Y-%m-%d} ~ {z:%Y-%m-%d})"
    else:
        sel = vol_df.tail(15).copy()
    if sel.empty:
        raise QuantError("⚠️ 선택하신 기간에 데이터가 없습니다.")
    cols = ["Quote Date", "EWY_Price", "DD_10", "Pos_20D", "Backwardation_Flag", "Put_Skew_진단", "Regime"]
    out = sel[cols].copy()
    anchor = pd.to_datetime(out["Quote Date"].max())
    out["Quote Date"] = out["Quote Date"].dt.strftime("%m-%d")
    out["EWY_Price"] = pd.to_numeric(out["EWY_Price"], errors="coerce").round(2)
    dd_s = pd.to_numeric(out["DD_10"], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    pos_s = pd.to_numeric(out["Pos_20D"], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.5)
    out["DD_10"] = dd_s.round(1).astype(str) + "%"
    out["Pos_20D"] = (pos_s * 100).round(0).astype(int).astype(str) + "%"
    out = out.rename(columns={"Quote Date": "Date", "EWY_Price": f"{SYMBOL}($)", "Backwardation_Flag": "Backward(역조)"})
    return out.reset_index(drop=True), anchor, detail
