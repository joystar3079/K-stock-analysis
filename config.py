"""전역 설정 — 매직넘버와 버전 분기를 한곳에 모읍니다."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# ─── 기본 ────────────────────────────────────────────────────────────
SYMBOL: Final = "EWY"
DIVIDEND_YIELD: Final = 0.02
DEFAULT_SOFR: Final = 3.65
MASTER_FILE: Final = "EWY_Options_V27_App_Master.pkl.gz"
PRICE_COL: Final = f"{SYMBOL} Price"
PRICE_HISTORY_START: Final = "2024-01-01"


# ─── 임계값 (튜닝 대상은 전부 여기) ──────────────────────────────────
class TH:
    # 옵션 체인 분류
    ATM_BAND: Final = 0.05          # ATM 밴드 ±5%
    NEAR_DTE_MAX: Final = 30        # 근월물 상한
    LONG_DTE_MIN: Final = 91        # 원월물 하한
    MIN_DTE: Final = 10             # 이보다 짧은 건 제외

    # 백분위 윈도우
    WIN_NEAR: Final = 60
    WIN_BUNKER: Final = 252
    WIN_RECENT: Final = 5
    WIN_WARNING: Final = 3

    # 시그널 문턱
    PCT_WATCH: Final = 90.0
    PCT_STRONG: Final = 95.0
    PCT_EXTREME: Final = 99.0
    SCORE_TRIGGER: Final = 100.0
    SCORE_PANIC: Final = 300.0
    SCORE_CAPITULATION: Final = 500.0

    # 스코어 가중치
    NEAR_RATIO_WEIGHT: Final = 3.33
    NEAR_DROP_WEIGHT: Final = 10.0
    LONG_RATIO_WEIGHT: Final = 10.0
    LONG_GROWTH_WEIGHT: Final = 2.0
    GROWTH_CAP: Final = 200.0

    # 롤업 / 고점 경계
    ROLLUP_HINT: Final = 0.5
    ROLLUP_CONFIRM: Final = 2.0
    ROLLUP_CEILING: Final = 4.0
    NEAR_P_RAW_WARNING: Final = 30.0
    NEAR_P_RAW_MANIA: Final = 100.0
    NEAR_P_RAW_HEDGE: Final = 15.0

    # ATM 하방 압력
    ATM_DOM_MAX: Final = 85.0
    ATM_DOM_RISK: Final = 70.0
    ATM_DOM_WATCH: Final = 60.0
    ATM_DOM_CAUTION: Final = 55.0

    # 4차원 확률 모형
    PROB_DIVISOR_PCT: Final = 95.0
    PROB_DEPTH_BASE: Final = 98.0
    PROB_DEPTH_SPAN: Final = 8.0
    PROB_ATM_SPAN: Final = 40.0
    PROB_SETUP_MAX: Final = 90.0
    PROB_SETUP_HIGH: Final = 80.0

    # 이동평균
    MA_SHORT: Final = 10
    MA_LONG: Final = 20

    # 가격 모형
    TREE_STEPS: Final = 50
    BISECTION_ITER: Final = 32
    VOL_LO: Final = 1e-4
    VOL_HI: Final = 5.0
    TRADING_DAYS: Final = 252.0
    MIN_T_DAYS: Final = 0.5


# ─── 버전별 엔진 설정 ────────────────────────────────────────────────
@dataclass(frozen=True)
class EngineConfig:
    key: str
    label: str
    top_warning_uses_raw: bool   # True: Near_P_Ratio>30, False: Near_P_Pct>=95
    use_4d_probability: bool     # True: C/G상승 4차원, False: G하락 스코어
    prefix_near: str
    prefix_long: str


ENGINES: Final[dict[str, EngineConfig]] = {
    "G버젼_하락추세조정": EngineConfig(
        "g_down", "G버젼_하락추세조정", True, False, "투매강도:", "매집강도:"),
    "C버젼_하락특화": EngineConfig(
        "c_down", "C버젼_하락특화", False, True, "투매강도:", "매집강도:"),
    "G버젼_상승특화": EngineConfig(
        "g_up", "G버젼_상승특화", False, True, "강도:", "강도:"),
}

# ─── UI ──────────────────────────────────────────────────────────────
MAX_HISTORY: Final = 10
DISPLAY_COLS: Final = [
    "Date", "Close Price",
    "[상승장] 단기(풋발작)", "[상승장] 세력(롤업)",
    "[하락장] 단기(콜투매/ATM)", "[하락장] 세력(벙커)", "Phase",
]
