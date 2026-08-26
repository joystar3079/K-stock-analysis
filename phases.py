"""국면 판정 — 버전 분기를 EngineConfig로 몰아 조건문 중첩을 줄였습니다.

시그널 로직 자체는 원본과 동일하게 유지했습니다. 바뀐 것은 구조뿐입니다.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import TH, EngineConfig


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """스코어와 백분위 — 전부 벡터 연산(기존 iterrows 제거)."""
    out = df.copy()

    out["Near_C_Pct"] = out["Near_C_Ratio"].rolling(TH.WIN_NEAR, min_periods=1).rank(pct=True) * 100
    out["Near_P_Pct"] = out["Near_P_Ratio"].rolling(TH.WIN_NEAR, min_periods=1).rank(pct=True) * 100

    capped = out["Long_P_OI_Growth"].fillna(0).clip(upper=TH.GROWTH_CAP)
    out["Raw_Bunker_Score"] = out["Long_P_Ratio"] * TH.LONG_RATIO_WEIGHT + capped * TH.LONG_GROWTH_WEIGHT
    out["Bunker_Pct"] = out["Raw_Bunker_Score"].rolling(TH.WIN_BUNKER, min_periods=1).rank(pct=True) * 100

    out["Recent_5D_Near_C_Pct"] = out["Near_C_Pct"].rolling(TH.WIN_RECENT, min_periods=1).max()
    out["Recent_5D_Bunker_Pct"] = out["Bunker_Pct"].rolling(TH.WIN_RECENT, min_periods=1).max()

    nc_drop = out["Near_C_Ratio_Drop"].fillna(0)
    lp_growth = out["Long_P_OI_Growth"].fillna(0).clip(upper=TH.GROWTH_CAP)
    out["Near_Score"] = np.maximum(
        0, out["Near_C_Ratio"] * TH.NEAR_RATIO_WEIGHT + nc_drop * TH.NEAR_DROP_WEIGHT).astype(int)
    out["Long_Score"] = np.maximum(
        0, out["Long_P_Ratio"] * TH.LONG_RATIO_WEIGHT + lp_growth * TH.LONG_GROWTH_WEIGHT).astype(int)
    out["Hybrid_Score"] = ((out["Near_Score"] + out["Long_Score"]) / 2).astype(int)
    return out


def _bottom_probability(r: pd.Series, close: float) -> tuple[float, float]:
    """4차원 바닥 에너지. (종합확률, 낙폭점수)"""
    n_prob = min(100.0, (r.get("Recent_5D_Near_C_Pct", 0) or 0) / TH.PROB_DIVISOR_PCT * 100.0)
    l_prob = min(100.0, (r.get("Recent_5D_Bunker_Pct", 0) or 0) / TH.PROB_DIVISOR_PCT * 100.0)
    ma20 = r["20MA"]
    depth_raw = (close / ma20) * 100.0 if ma20 > 0 else 100.0
    p_prob = max(0.0, min(100.0, (TH.PROB_DEPTH_BASE - depth_raw) / TH.PROB_DEPTH_SPAN * 100.0))
    atm = r["ATM_Put_Dominance"] if pd.notna(r["ATM_Put_Dominance"]) else 50.0
    a_prob = max(0.0, min(100.0, (100.0 - atm) / TH.PROB_ATM_SPAN * 100.0))
    return (n_prob + l_prob + p_prob + a_prob) / 4.0, p_prob


def _phase_uptrend(r, cfg, ceiling_active, close, prev_close, is_g_down):
    """상승 추세 구간 판정. (phase, ceiling_active) 반환."""
    is_warning = r["Recent_Top_Warning"] > 0
    rollup = r["Long_P_Wgt_Rollup"]
    is_rollup = pd.notna(rollup) and rollup > TH.ROLLUP_CONFIRM

    if is_warning and is_rollup:
        return "⛔ 대천장(Ceiling) 확정 (전량 익절)", True
    # prev_close 초기값을 NaN으로 두어 첫 행이 무조건 참이 되던 문제를 막습니다
    if ceiling_active and pd.notna(prev_close) and close > prev_close:
        return ("⛔ 대천장 가짜 랠리 (익절 유지)" if is_g_down
                else "⛔ 대천장 유지 / 가짜 랠리"), True
    if is_warning:
        return ("⚠️ 상승장 고점 경계령 (비중축소)" if is_g_down
                else "⚠️ 상승장 속 고점 경계령 (단기 풋 투매 폭발 / 비중축소)"), False
    if r["10MA"] > r["20MA"]:
        return "📈 대세 상승 추세 진행 중", False
    if is_g_down and r.get("Recent_Bottom", 0) > 0:
        return "🚀 하락 멈춤 상승 전환", False
    return "🚀 하락 멈춤 / 단기 상승 전환", False


def _phase_downtrend_score(r) -> str:
    """G하락 버전 — 스코어 기반."""
    mid_up = r["10MA"] > r["20MA"]
    h, n, l = r["Hybrid_Score"], r["Near_Score"], r["Long_Score"]
    if h >= TH.SCORE_TRIGGER:
        return "⚡ 일시 급락 눌림목" if mid_up else "🔥 찐바닥 포착"
    if n >= TH.SCORE_TRIGGER > l:
        return "🔪 단기 투매 (칼날 주의)"
    if l >= TH.SCORE_TRIGGER > n:
        return "🛡️ 세력 하방경직 구축"
    return "📉 본격 하락 추세 진행 중"


def _phase_downtrend_4d(r, close) -> tuple[str, bool]:
    """C / G상승 버전 — 4차원 확률 기반. (phase, bottom_flag) 반환."""
    mid_up = r["10MA"] > r["20MA"]
    n_pct = r["Near_C_Pct"] if pd.notna(r["Near_C_Pct"]) else 0
    l_pct = r["Bunker_Pct"] if pd.notna(r["Bunker_Pct"]) else 0
    atm = r["ATM_Put_Dominance"] if pd.notna(r["ATM_Put_Dominance"]) else 50.0

    prob, p_prob = _bottom_probability(r, close)
    suffix = f" 🔋[에너지: {prob:.1f}% | 낙폭: {p_prob:.0f}점]"
    bottom = False

    if l_pct < TH.PCT_STRONG:
        if n_pct >= TH.PCT_STRONG:
            phase = "🔪 단기 투매 발생 (방어벽 부재)" if mid_up else "🔪 개미 패닉셀 발생"
        else:
            phase = "📉 단기 조정 진행 중" if mid_up else "📉 본격 하락 추세 진행 중"
    elif n_pct < TH.PCT_STRONG:
        phase = "🛡️ 강력 세력 방어벽 셋업" if mid_up else "🛡️ 강력 세력 벙커 구축 중"
    else:
        bottom = True
        if atm >= TH.ATM_DOM_WATCH:
            phase = "⚠️ 섣부른 눌림목 주의" if mid_up else "⚠️ 가짜 반등 주의 (기관 ATM 숏 지속)"
        else:
            phase = "🔥 퍼펙트 눌림목 포착" if mid_up else "🔥 퍼펙트 찐바닥 포착"

    if "퍼펙트" not in phase:
        if prob >= TH.PROB_SETUP_MAX and "가짜 반등" not in phase and "압박" not in phase:
            phase = "⏳ 눌림목 셋업 극대화" if mid_up else "⏳ 찐바닥 셋업 극대화"
        elif prob >= TH.PROB_SETUP_HIGH and ("본격 하락" in phase or "조정" in phase):
            phase = "🟡 견조한 조정 진행 중" if mid_up else "🟡 바닥 다지기 진행 중"
    return phase + suffix, bottom


def assign_phases(df: pd.DataFrame, cfg: EngineConfig) -> pd.DataFrame:
    """국면 판정. 입력을 복사해 캐시 오염을 막습니다."""
    out = compute_scores(df)
    is_g_down = not cfg.use_4d_probability

    warn = (out["Near_P_Ratio"] > TH.NEAR_P_RAW_WARNING if cfg.top_warning_uses_raw
            else out["Near_P_Pct"] >= TH.PCT_STRONG)
    out["Top_Warning_Flag"] = warn.astype(int)
    out["Recent_Top_Warning"] = out["Top_Warning_Flag"].rolling(TH.WIN_WARNING, min_periods=1).max()

    if is_g_down:
        out["Bottom_Flag"] = ((out["Hybrid_Score"] >= TH.SCORE_TRIGGER) |
                              (out["Long_Score"] >= TH.SCORE_TRIGGER)).astype(int)
        out["Recent_Bottom"] = out["Bottom_Flag"].rolling(TH.WIN_RECENT, min_periods=1).max()
    else:
        out["Bottom_Flag"] = 0
        out["Recent_Bottom"] = 0

    phases, ceiling_active, prev_close = [], False, np.nan
    for i, r in out.iterrows():
        close = r["Close Price"]
        if close > r["10MA"]:
            if is_g_down:
                out.at[i, "Bottom_Flag"] = 0
            phase, ceiling_active = _phase_uptrend(
                r, cfg, ceiling_active, close, prev_close, is_g_down)
        else:
            ceiling_active = False
            if is_g_down:
                phase = _phase_downtrend_score(r)
            else:
                phase, bottom = _phase_downtrend_4d(r, close)
                if bottom:
                    out.at[i, "Bottom_Flag"] = 1
        prev_close = close
        phases.append(phase)

    if not is_g_down:
        out["Recent_Bottom"] = out["Bottom_Flag"].rolling(TH.WIN_RECENT, min_periods=1).max()
    out["Phase"] = phases
    return out
