"""EWY Quant Analytics V34 — Streamlit UI.

[V34 파일 업로드 전용 경량화 & 다중 분석 모듈 탑재] 
  · 야후 API 의존성 완전 제거 (마스터 파일 내장 주가 자체 추출)
  · 사이드바 메뉴 분기: [옵션 가격(방어벽) 분석] vs [옵션 거래량(레짐) 분석]
  · [오류 수정] 삼성 갤럭시 One UI 최신버전 '내 파일' 강제 호출 패치 완료
  · [오류 수정] st.dataframe 동적 JS 모듈(DataFrame.*.js) 로드 실패(Failed to fetch) 원천 차단 패치
"""
from __future__ import annotations

import json
import uuid
import warnings
from datetime import datetime
import base64
import html

import pandas as pd
import numpy as np
import streamlit as st
from github import Github

from config import (DEFAULT_SOFR, DISPLAY_COLS, ENGINES, MASTER_FILE,
                    MAX_HISTORY, PRICE_HISTORY_START, SYMBOL)
from data_io import (DOWNLOAD_FOLDER, auto_update_master, build_filename,
                     extract_options_from_files, latest_data_date, load_master_data,
                     merge_master, merge_report, push_master_to_github, to_csv_bytes,
                     to_zip_bytes, diagnose_quote_date, IO_VERSION)
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns

from volume_analysis import run_volume_analysis

warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V34", page_icon="📈", layout="wide")

# =====================================================================
# [웹 UI 전용 CSS] - 최신 Streamlit DOM 업데이트 & 커스텀 테이블 반영
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
    display: flex; align-items: center; justify-content: center; box-sizing: border-box; text-decoration: none;
}
.custom-new-window-btn:hover { border-color: #FF4B4B; color: #FF4B4B; }
div[data-testid="stMarkdownContainer"] > p { margin-bottom: 0px !important; }

/* 💡 DataFrame.*.js 동적 로드 오류 원천 차단용 반응형 테이블 스타일 */
.quant-table-wrapper {
    width: 100%;
    max-height: 460px;
    overflow-x: auto;
    overflow-y: auto;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 8px;
    margin-top: 6px;
    margin-bottom: 14px;
}
.quant-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    text-align: center;
    white-space: nowrap;
}
.quant-table thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background-color: var(--secondary-background-color, #f0f2f6);
    color: var(--text-color, #31333F);
    font-weight: 600;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}
.quant-table tbody td {
    padding: 7px 12px;
    color: var(--text-color, #31333F);
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
        repo = Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["GITHUB_REPO"])
        return json.loads(repo.get_contents("quick_links.json").decoded_content.decode("utf-8"))
    except Exception:
        return [
            {"name": "Google Finance", "url": "https://www.google.com/finance"},
            {"name": "CME FedWatch", "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"},
            {"name": "TradingView", "url": "https://kr.tradingview.com/"},
        ]

def save_quick_links(links):
    try:
        repo = Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["GITHUB_REPO"])
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
    st.session_state["edit_links_mode"] = not