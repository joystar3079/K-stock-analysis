"""옵션 미결제약정 집계 — 마스터가 같으면 결과가 같으므로 캐싱합니다."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from config import PRICE_COL, TH


def _bunker_price(otm_puts: pd.DataFrame) -> float:
    """OI 상위 10개 행사가의 가중평균. nlargest를 한 번만 호출합니다."""
    if otm_puts.empty:
        return 0.0
    top = otm_puts.nlargest(10, "Open Interest")
    total = top["Open Interest"].sum()
    if total <= 0:
        return 0.0
    return float((top["Strike"] * top["Open Interest"]).sum() / total)


def _ratio(numer_df: pd.DataFrame, denom: float) -> float:
    return float(numer_df["Open Interest"].sum() / denom) if denom > 0 else 0.0


@st.cache_data(show_spinner=False)
def aggregate_oi_features(master_df: pd.DataFrame, px: pd.DataFrame) -> pd.DataFrame:
    """일자별 미결제약정 구조 지표를 만듭니다."""
    if master_df.empty:
        return pd.DataFrame()

    op = master_df.copy()
    op["DTE"] = (op["Expiration Date"] - op["Quote Date"]).dt.days
    op = op[op["DTE"] >= TH.MIN_DTE]
    if op.empty:
        return pd.DataFrame()

    px_map = (px.set_index("Date")["Close Price"].to_dict()
              if not px.empty else {})

    rows = []
    for dt, g in op.groupby("Quote Date"):
        spot = float(g[PRICE_COL].iloc[0])
        if not np.isfinite(spot) or spot <= 0:
            spot = float(px_map.get(dt, np.nan))
        if not np.isfinite(spot) or spot <= 0:
            continue  # 스팟을 모르면 비율이 무의미 — 기존의 spot=1 폴백은 위험

        lo, hi = spot * (1 - TH.ATM_BAND), spot * (1 + TH.ATM_BAND)
        c, p = g[g["Option Type"] == "C"], g[g["Option Type"] == "P"]
        near_c = c[c["DTE"] <= TH.NEAR_DTE_MAX]
        near_p = p[p["DTE"] <= TH.NEAR_DTE_MAX]
        long_p = p[p["DTE"] >= TH.LONG_DTE_MIN]

        n_c_atm = near_c[near_c["Strike"].between(lo, hi)]["Open Interest"].sum()
        n_p_atm = near_p[near_p["Strike"].between(lo, hi)]["Open Interest"].sum()
        l_p_atm = long_p[long_p["Strike"].between(lo, hi)]["Open Interest"].sum()
        long_p_oi = long_p["Open Interest"].sum()

        rows.append({
            "Date": dt,
            "Near_C_Ratio": _ratio(near_c[near_c["Strike"] > hi], n_c_atm),
            "Near_P_Ratio": _ratio(near_p[near_p["Strike"] < lo], n_p_atm),
            "Long_P_Ratio": _ratio(long_p[long_p["Strike"] < lo], l_p_atm),
            "Long_P_OI": float(long_p_oi),
            "Bunker_Price": _bunker_price(long_p[long_p["Strike"] < spot]),
            "Long_P_Wgt": (float((long_p["Strike"] * long_p["Open Interest"]).sum()
                                 / long_p_oi) if long_p_oi > 0 else spot),
            "Total_P_OI": float(p["Open Interest"].sum()),
            "ATM_Put_Dominance": (float(n_p_atm / (n_p_atm + n_c_atm) * 100)
                                  if (n_p_atm + n_c_atm) > 0 else 50.0),
        })

    if not rows:
        return pd.DataFrame()

    opt = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    opt["Total_P_OI_Lag"] = opt["Total_P_OI"].shift(1)
    opt["Near_C_Ratio_Drop"] = opt["Near_C_Ratio"].shift(1) - opt["Near_C_Ratio"]
    opt["Long_P_OI_Growth"] = (
        opt["Long_P_OI"] / opt["Long_P_OI"].shift(1).replace(0, np.nan) - 1) * 100
    opt["Long_P_Wgt_Rollup"] = opt["Long_P_Wgt"] - opt["Long_P_Wgt"].shift(1)
    return opt


def attach_price(opt_df: pd.DataFrame, px: pd.DataFrame,
                 master_df: pd.DataFrame) -> pd.DataFrame:
    """시세 결합 + 결측 보정. 루프 안 스캔(O(n^2))을 map으로 대체했습니다."""
    df = pd.merge(px, opt_df, on="Date", how="right").sort_values("Date").reset_index(drop=True)

    if PRICE_COL in master_df.columns:
        fallback = master_df.groupby("Quote Date")[PRICE_COL].first()
        filled = df["Date"].map(fallback)
        need = df["Close Price"].isna() | (df["Close Price"] == 0)
        df.loc[need, "Close Price"] = filled[need]

    df["Close Price"] = df["Close Price"].ffill()
    df["10MA"] = df["Close Price"].rolling(TH.MA_SHORT, min_periods=1).mean()
    df["20MA"] = df["Close Price"].rolling(TH.MA_LONG, min_periods=1).mean()
    return df
