"""표시 문자열 — 계산 결과를 사람이 읽는 형태로만 변환합니다.

기존에는 이 로직이 국면 판정 한복판에 섞여 있어서, 표시 형식을 바꾸려면
계산부를 건드려야 했고 로직 단위 테스트도 불가능했습니다.
"""
from __future__ import annotations

import pandas as pd

from config import TH, EngineConfig


def _pick(value: float, bands: list[tuple[float, str]], default: str) -> str:
    for threshold, text in bands:
        if value >= threshold:
            return text
    return default


def near_put_label(np_val: float, np_raw: float, cfg: EngineConfig) -> str:
    """[상승장] 단기 풋발작."""
    if cfg.top_warning_uses_raw:
        return _pick(np_val, [
            (TH.NEAR_P_RAW_MANIA, f"{np_val:.1f}배 🚨 광기"),
            (TH.NEAR_P_RAW_WARNING, f"{np_val:.1f}배 ⚠️ 고점"),
            (TH.NEAR_P_RAW_HEDGE, f"{np_val:.1f}배 🟡 헷징"),
        ], f"{np_val:.1f}배 ➖ 안정적")
    return _pick(np_val, [
        (TH.PCT_EXTREME, f"[{np_val:.0f}점] 🚨 풋 투매 ({np_raw:.1f}배)"),
        (TH.PCT_STRONG, f"[{np_val:.0f}점] ⚠️ 고점 발작 ({np_raw:.1f}배)"),
        (TH.PCT_WATCH, f"[{np_val:.0f}점] 🟡 헷징 증가 ({np_raw:.1f}배)"),
    ], f"[{np_val:.0f}점] ➖ 안정적")


def rollup_label(rollup: float) -> str:
    """[상승장] 세력 롤업."""
    return _pick(rollup, [
        (TH.ROLLUP_CEILING, f"+${rollup:.2f} 💀 대천장"),
        (TH.ROLLUP_CONFIRM, f"+${rollup:.2f} ⛔ 롤업 확정"),
        (TH.ROLLUP_HINT, f"+${rollup:.2f} 🟡 조짐"),
    ], f"{rollup:+.2f} ➖ 평상시")


def _atm_suffix(atm: float) -> str:
    level = _pick(atm, [
        (TH.ATM_DOM_MAX, "(MAX 🚨)"),
        (TH.ATM_DOM_RISK, "(위험 ⚠️)"),
        (TH.ATM_DOM_CAUTION, "(경계 🟡)"),
    ], "(해제 🟢)")
    return f" [하방: {atm:.0f}% {level}]"


def near_call_label(r: pd.Series, cfg: EngineConfig) -> str:
    """[하락장] 단기 콜투매."""
    if cfg.top_warning_uses_raw:
        n = int(r["Near_Score"])
        return _pick(n, [
            (TH.SCORE_CAPITULATION, f"{n} 🚨 항복 선언"),
            (TH.SCORE_PANIC, f"{n} 🩸 패닉 셀링"),
            (TH.SCORE_TRIGGER, f"{n} 🟡 투매 발생"),
        ], f"{n} ➖ 소화 중")

    atm = _atm_suffix(r["ATM_Put_Dominance"])
    raw = r["Near_C_Ratio"]
    pct = r["Near_C_Pct"] if pd.notna(r["Near_C_Pct"]) else 0
    px = cfg.prefix_near
    return _pick(pct, [
        (TH.PCT_EXTREME, f"[{px} {raw:.1f}배] 🚨 항복 선언{atm}"),
        (TH.PCT_STRONG, f"[{px} {raw:.1f}배] 🩸 패닉 셀링{atm}"),
        (TH.PCT_WATCH, f"[{px} {raw:.1f}배] 🟡 투매 발생{atm}"),
    ], f"[{px} {raw:.1f}배] ➖ 평상시{atm}")


def bunker_label(r: pd.Series, cfg: EngineConfig) -> str:
    """[하락장] 세력 벙커."""
    bunker = r["Bunker_Price"]
    raw = r["Long_P_Ratio"]

    if cfg.top_warning_uses_raw:
        suffix = f" (${bunker:.1f})" if bunker > 0 else ""
        l = int(r["Long_Score"])
        return _pick(l, [
            (TH.SCORE_CAPITULATION, f"{l} 🚨 극단치{suffix}"),
            (TH.SCORE_PANIC, f"{l} 🛡️ 세력개입{suffix}"),
            (TH.SCORE_TRIGGER, f"{l} 🏗️ 방어벽{suffix}"),
        ], f"{l} ➖ 방어없음")

    suffix = (f" (벽: ${bunker:.1f} / {raw:.1f}배)" if bunker > 0
              else f" (규모: {raw:.1f}배)")
    pct = r["Bunker_Pct"] if pd.notna(r["Bunker_Pct"]) else 0
    px = cfg.prefix_long
    return _pick(pct, [
        (TH.PCT_EXTREME, f"[{px} {raw:.1f}배] 🚨 역사적 벙커{suffix}"),
        (TH.PCT_STRONG, f"[{px} {raw:.1f}배] 🛡️ 강력 방어벽{suffix}"),
        (TH.PCT_WATCH, f"[{px} {raw:.1f}배] 🏗️ 일반 방어벽{suffix}"),
    ], f"[{px} {raw:.1f}배] ➖ 평상시{suffix}")


def add_display_columns(df: pd.DataFrame, cfg: EngineConfig) -> pd.DataFrame:
    """추세 방향에 따라 상단/하단 표시 컬럼을 채웁니다."""
    out = df.copy()
    tops_s, tops_l, bots_s, bots_l = [], [], [], []

    for _, r in out.iterrows():
        up = r["Close Price"] > r["10MA"]
        if up:
            np_val = r["Near_P_Ratio"] if cfg.top_warning_uses_raw else r["Near_P_Pct"]
            rollup = r["Long_P_Wgt_Rollup"] if pd.notna(r["Long_P_Wgt_Rollup"]) else 0.0
            tops_s.append(near_put_label(np_val, r["Near_P_Ratio"], cfg))
            tops_l.append(rollup_label(rollup))
            bots_s.append("-"); bots_l.append("-")
        else:
            tops_s.append("-"); tops_l.append("-")
            bots_s.append(near_call_label(r, cfg))
            bots_l.append(bunker_label(r, cfg))

    out["[상승장] 단기(풋발작)"] = tops_s
    out["[상승장] 세력(롤업)"] = tops_l
    out["[하락장] 단기(콜투매/ATM)"] = bots_s
    out["[하락장] 세력(벙커)"] = bots_l
    return out
