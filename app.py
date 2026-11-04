"""EWY Quant Analytics V34 — Streamlit UI.

[V34 파일 업로드 전용 경량화 & 다중 분석 모듈 탑재] 
  · 야후 API 의존성 완전 제거 (마스터 파일 내장 주가 자체 추출)
  · 사이드바 메뉴 분기: [옵션 가격(방어벽) 분석] vs [옵션 거래량(레짐) 분석]
  · [오류 수정] 삼성 갤럭시 One UI 최신버전 '내 파일' 강제 호출 패치 완료
  · [오류 수정] st.dataframe 동적 JS 모듈 로드 실패 원천 차단 패치
"""
from __future__ import annotations

import base64
import html
import json
import uuid
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from github import Github

from config import (
    DEFAULT_SOFR,
    DISPLAY_COLS,
    ENGINES,
    MASTER_FILE,
    MAX_HISTORY,
    PRICE_HISTORY_START,
    SYMBOL,
)
from data_io import (
    DOWNLOAD_FOLDER,
    IO_VERSION,
    auto_update_master,
    build_filename,
    diagnose_quote_date,
    extract_options_from_files,
    latest_data_date,
    load_master_data,
    merge_master,
    merge_report,
    push_master_to_github,
    to_csv_bytes,
    to_zip_bytes,
)
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns
from volume_analysis import run_volume_analysis

warnings.filterwarnings("ignore")
st.set_page_config(
    page_title=f"{SYMBOL} Quant Analytics V34",
    page_icon="📈",
    layout="wide",
)

# =====================================================================
# [웹 UI 전용 CSS]
# =====================================================================
st.markdown("""
<style>
div[data-testid="column"] button[kind="secondary"],
div[data-testid="column"] button[data-testid="baseButton-secondary"],
div[data-testid="column"] button[data-testid="stBaseButton-secondary"] {
    width: 100% !important; height: 32px !important; min-height: 32px !important;
    padding: 0px !important; border-radius: 6px !important;
    border: 1px solid rgba(128, 128, 128, 0.4) !important;
    background-color: transparent !important; color: var(--text-color) !important;
}
div[data-testid="column"] button[kind="secondary"] p,
div[data-testid="column"] button[data-testid="baseButton-secondary"] p,
div[data-testid="column"] button[data-testid="stBaseButton-secondary"] p {
    font-size: 13px !important; margin: 0px !important; font-weight: 500 !important;
}
div[data-testid="column"] button[kind="secondary"]:hover,
div[data-testid="column"] button[data-testid="baseButton-secondary"]:hover,
div[data-testid="column"] button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #FF4B4B !important; color: #FF4B4B !important;
}
.custom-new-window-btn {
    width: 100%; height: 32px; min-height: 32px; padding: 0px; border-radius: 6px;
    border: 1px solid rgba(128, 128, 128, 0.4); background-color: transparent;
    color: var(--text-color); font-size: 13px; font-weight: 500; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    box-sizing: border-box; text-decoration: none;
}
.custom-new-window-btn:hover { border-color: #FF4B4B; color: #FF4B4B; }
div[data-testid="stMarkdownContainer"] > p { margin-bottom: 0px !important; }

.quant-table-wrapper {
    width: 100%; max-height: 460px; overflow-x: auto; overflow-y: auto;
    border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px;
    margin-top: 6px; margin-bottom: 14px;
}
.quant-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
    text-align: center; white-space: nowrap;
}
.quant-table thead th {
    position: sticky; top: 0; z-index: 2;
    background-color: var(--secondary-background-color, #f0f2f6);
    color: var(--text-color, #31333F); font-weight: 600; padding: 8px 12px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}
.quant-table tbody td {
    padding: 7px 12px; color: var(--text-color, #31333F);
    border-bottom: 1px solid rgba(128, 128, 128, 0.15);
    border-right: 1px solid rgba(128, 128, 128, 0.1);
}
.quant-table tbody tr:hover {
    background-color: rgba(128, 128, 128, 0.08);
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# [클라우드 저장소] 퀵링크 영구 저장/불러오기
# =====================================================================
def load_quick_links():
    try:
        gh = Github(st.secrets["GITHUB_TOKEN"])
        repo = gh.get_repo(st.secrets["GITHUB_REPO"])
        raw = repo.get_contents("quick_links.json").decoded_content
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return [
            {"name": "Google Finance", "url": "https://www.google.com/finance"},
            {"name": "CME FedWatch", "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"},
            {"name": "TradingView", "url": "https://kr.tradingview.com/"},
        ]

def save_quick_links(links):
    try:
        gh = Github(st.secrets["GITHUB_TOKEN"])
        repo = gh.get_repo(st.secrets["GITHUB_REPO"])
        body = json.dumps(links, ensure_ascii=False, indent=2).encode("utf-8")
        try:
            c = repo.get_contents("quick_links.json")
            repo.update_file(c.path, "Update quick links", body, c.sha)
        except Exception:
            repo.create_file("quick_links.json", "Create quick links", body)
        return True
    except Exception as e:
        st.error(f"링크 저장 오류: {e}")
        return False

# =====================================================================
# [세션 상태 관리]
# =====================================================================
st.session_state.setdefault("analysis_history", [])
st.session_state.setdefault("master_version", "")
st.session_state.setdefault("merge_policy", "skip")
st.session_state.setdefault("edit_links_mode", False)
st.session_state.setdefault("show_vol_explanation", True)

if "quick_links" not in st.session_state:
    st.session_state["quick_links"] = load_quick_links()

def toggle_edit():
    curr = st.session_state.get("edit_links_mode", False)
    st.session_state["edit_links_mode"] = not curr

def remove_history_item(item_id: str) -> None:
    hist = st.session_state["analysis_history"]
    st.session_state["analysis_history"] = [r for r in hist if r["id"] != item_id]

def hide_vol_explanation():
    st.session_state["show_vol_explanation"] = False

# =====================================================================
# [지표 설명자료 MD]
# =====================================================================
VOLUME_EXPLANATION_MD = """
#### 1. 산출 원리 (2단계 연산 구조)
코드 내부에서는 다음 두 단계를 거쳐 **Put_Skew_Pct**를 산출합니다.

**① 원천 하방 스큐 (Put_Skew) 계산:**
> **Put_Skew_t = IV_{OTM Put, t} - IV_{ATM, t}**

* **IV_{OTM Put} (외가격 풋옵션 IV):** 현재 주가보다 5% 이상 낮은 행사가에 위치한 풋옵션들의 거래량 가중평균 내재변동성입니다. (급락에 베팅하거나 방어하려는 *'폭락 보험료'*)
* **IV_{ATM} (등가격 옵션 IV):** 현재 주가 ±5% 이내 옵션들의 가중평균 내재변동성입니다. (시장의 *기본 변동성*)

💡 **즉, Put_Skew가 클수록 시장 참여자들이 평상시 변동성 대비 하방 폭락 가능성에 훨씬 비싼 프리미엄(웃돈)을 지불하며 풋옵션을 사들이고 있음을 의미합니다.**

**② 60영업일 롤링 백분위 (Put_Skew_Pct) 변환:**
시장의 기본 변동성 레벨은 시기마다 달라지므로 절대값만으로는 과열 여부를 판단하기 어렵습니다. 따라서 직전 **60영업일(약 3개월)** 동안의 Put_Skew 값들을 줄 세운 뒤, 오늘의 수치가 차지하는 순위를 백분율(0% ~ 100%)로 환산합니다.

📌 **예시:** Put_Skew_Pct = 95.0%라면, 최근 60영업일 중 오늘보다 풋옵션 웃돈이 더 비쌌던 날이 단 3일(상위 5%)뿐일 정도로 **하방 헤지 수요가 극에 달했다는 뜻**입니다.

---

#### 2. 구간별 수치 해석 및 실전 매매 활용법

| Put_Skew_Pct 구간 | 시장 미시구조 상태 | 주가 위치별 실전 해석 및 전략 |
| :--- | :--- | :--- |
| **90% ~ 100%** *(극단적 왜곡/패닉)* | 딜러들의 숏 베가(Short Vega) 한계 도달. 대중과 기관이 OTM 풋옵션을 시장가로 쓸어 담는 상태 | **• 급락장 바닥권 (Regime 1):** 대중의 투매가 끝자락에 도달한 역발상 매수 타점 ➔ **• 상승장 고점권:** 스마트 머니가 폭락 직전 풋옵션을 선취매하는 발작 경보 |
| **75% ~ 89%** *(하방 경계심 고조)* | OTM 풋옵션 수요가 뚜렷하게 증가하며 스큐가 가팔라지는 구간 | **• 조정 구간 (DD_10 ≤ -6%):** 기간구조 역전(Backwardation)과 결합 시 Regime 1 진입 조건 충족 |
| **25% ~ 74%** *(중립 / 평상시)* | 콜/풋옵션의 수급 균형이 유지되는 일반적인 시장 상태 | **• 중립 구간:** 스큐 단독으로는 특이 시그널 없음 (거래량 및 미결제약정 증감으로 방향성 판별) |
| **0% ~ 24%** *(극단적 안도/과열)* | 하방 보험 수요가 완전히 소멸하거나, 상방 콜옵션 수요가 몰린 상태 | **• 고점 부근:** 하락 공포를 잊은 FOMO 구간. 기관의 OI 청산 동반 시 Regime 2(고점 엑시트) 위험 급증 |
"""

def generate_new_window_link(df, title):
    html_content = df.to_html(index=False, justify='center')
    html_template = f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>{title}</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; padding: 20px; color: #333; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 13px; text-align: center; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
    </style></head><body>
    <h2>{title}</h2>
    {html_content}
    </body></html>
    """
    b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8').replace('\n', '')
    js_cmd = (
        f"var w=window.open();"
        f"w.document.write(decodeURIComponent(escape(atob('{b64}'))));"
        f"w.document.close();"
    )
    return f'<a href="javascript:void(0);" onclick="{js_cmd}" class="custom-new-window-btn">↗️ 새창 열기</a>'

def render_safe_table(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("표시할 데이터가 없습니다.")
        return

    headers = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows_html = []
    for _, row in df.iterrows():
        cells = "".join(
            f"<td>{'' if pd.isna(v) else html.escape(str(v))}</td>"
            for v in row
        )
        rows_html.append(f"<tr>{cells}</tr>")

    table_html = (
        f'<div class="quant-table-wrapper">'
        f'<table class="quant-table">'
        f'<thead><tr>{headers}</tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'</table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

# =====================================================================
# [엔진 실행 코어]
# =====================================================================
def get_ready_master() -> tuple[pd.DataFrame, dict]:
    meta: dict = {}
    master_df = load_master_data(st.session_state["master_version"])
    meta["master_rows"] = len(master_df)
    meta["merged_extraction"] = False

    new = st.session_state.get("recent_extracted_data")
    if new is not None and not new.empty:
        rep = merge_report(master_df, new)
        meta["merge_report"] = rep
        policy = st.session_state["merge_policy"]
        if rep["new_dates"] or policy == "replace":
            master_df = merge_master(master_df, new, on_conflict=policy)
            meta["merged_extraction"] = True
        meta["merge_policy"] = policy
    return master_df, meta

def build_full_frame(version: str) -> tuple[pd.DataFrame, dict]:
    master_df, meta = get_ready_master()
    if master_df.empty:
        return pd.DataFrame(), meta

    cfg = ENGINES[version]

    if "EWY Price" in master_df.columns:
        px = master_df[["Quote Date", "EWY Price"]].drop_duplicates(subset=["Quote Date"]).copy()
        px.rename(columns={"Quote Date": "Date", "EWY Price": "Close Price"}, inplace=True)
        px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None).dt.normalize()
        px = px.sort_values("Date").dropna(subset=["Close Price"]).reset_index(drop=True)
        meta["price_source"] = "마스터 파일 내장 시세 (오프라인 모드)"
    else:
        meta["price_error"] = True
        return pd.DataFrame(), meta

    if px.empty:
        meta["price_error"] = True
        return pd.DataFrame(), meta

    opt_df = aggregate_oi_features(master_df, px)
    if opt_df.empty:
        return pd.DataFrame(), meta

    df = attach_price(opt_df, px, master_df)
    df = assign_phases(df, cfg)
    df = add_display_columns(df, cfg)
    meta["latest_date"] = df["Date"].max()
    meta["n_dates"] = len(df)
    return df, meta

def store_extraction(df_ext, stats, file_results=None) -> None:
    keys_to_clear = (
        "extract_error_stats",
        "extract_error_msg",
        "accumulated_steps",
        "push_result",
        "push_error",
    )
    for k in keys_to_clear:
        st.session_state.pop(k, None)
    st.session_state["recent_extracted_data"] = df_ext
    st.session_state["extract_stats"] = stats
    st.session_state["file_results"] = file_results

    if not st.session_state.get("auto_push", False):
        return
    try:
        current = load_master_data(st.session_state["master_version"])
        st.session_state["push_result"] = auto_update_master(current, df_ext, on_conflict="skip")
        st.session_state["master_version"] = uuid.uuid4().hex[:8]
        load_master_data.clear()
    except Exception as e:
        st.session_state["push_error"] = str(e)

def run_quant_engine(
    version: str,
    mode: str,
    target_date=None,
    target_start=None,
    target_end=None,
) -> tuple[pd.DataFrame, dict]:
    df, meta = build_full_frame(version)
    if df.empty:
        return pd.DataFrame(), meta
    if mode == "구간 조회" and target_start and target_end:
        cond = (df["Date"] >= pd.to_datetime(target_start)) & (df["Date"] <= pd.to_datetime(target_end))
        sel = df[cond].copy()
    elif mode == "타임머신 (특정일)" and target_date:
        sel = df[df["Date"] <= pd.to_datetime(target_date)].tail(10).copy()
    else:
        sel = df.tail(10).copy()
    if sel.empty:
        return pd.DataFrame(), meta
    meta["anchor_date"] = sel["Date"].max()
    sel = sel[DISPLAY_COLS].copy()
    sel["Date"] = sel["Date"].dt.strftime("%m/%d")
    sel["Close Price"] = sel["Close Price"].round(2)
    return sel.rename(columns={"Close Price":
