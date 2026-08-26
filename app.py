"""EWY Quant Analytics V28 — Streamlit UI.

모듈화된 구조 위에서 UI, 퀵링크, 새창 열기, 누적 기간, 우측 정렬이 완벽하게 반영된 최종 버전입니다.
수학 연산과 로직은 다른 .py 파일들에서 불러옵니다.
"""
from __future__ import annotations

import uuid
import warnings
from datetime import datetime
import json
import base64

import pandas as pd
import streamlit as st
from github import Github

from config import (DISPLAY_COLS, ENGINES, MAX_HISTORY, PRICE_HISTORY_START,
                    SYMBOL)
from data_io import (extract_daily_options, fetch_etf_history, load_master_data,
                     merge_master, push_master_to_github)
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns

warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V28",
                   page_icon="📈", layout="wide")

# =====================================================================
# [웹 UI 전용 CSS] 버튼 크기, 디자인 완벽 쌍둥이 통일
# =====================================================================
st.markdown("""
<style>
/* 1. 삭제버튼 (Secondary) 크기/포맷 통일 */
div[data-testid="column"] button[kind="secondary"] {
    width: 100% !important;
    height: 32px !important;
    min-height: 32px !important;
    padding: 0px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(128, 128, 128, 0.4) !important;
    background-color: transparent !important;
    color: var(--text-color) !important;
}
div[data-testid="column"] button[kind="secondary"] p {
    font-size: 13px !important;
    margin: 0px !important;
    font-weight: 500 !important;
}
div[data-testid="column"] button[kind="secondary"]:hover {
    border-color: #FF4B4B !important;
    color: #FF4B4B !important;
}

/* 2. 새창열기 HTML 버튼을 삭제버튼과 100% 동일하게 맞춤 */
.custom-new-window-btn {
    width: 100%;
    height: 32px;
    min-height: 32px;
    padding: 0px;
    border-radius: 6px;
    border: 1px solid rgba(128, 128, 128, 0.4);
    background-color: transparent;
    color: var(--text-color);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    text-decoration: none;
}
.custom-new-window-btn:hover {
    border-color: #FF4B4B;
    color: #FF4B4B;
}

/* 3. 마크다운 컨테이너 기본 여백 제거 (상하 높이 정렬용) */
div[data-testid="stMarkdownContainer"] > p {
    margin-bottom: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# [클라우드 저장소] 퀵링크 영구 저장/불러오기 로직
# =====================================================================
def load_quick_links():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["GITHUB_REPO"])
        contents = repo.get_contents("quick_links.json")
        return json.loads(contents.decoded_content.decode('utf-8'))
    except:
        return [
            {"name": "Google Finance", "url": "https://www.google.com/finance"},
            {"name": "CME FedWatch", "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"},
            {"name": "TradingView", "url": "https://kr.tradingview.com/"}
        ]

def save_quick_links(links):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["GITHUB_REPO"])
        content_bytes = json.dumps(links, ensure_ascii=False, indent=2).encode('utf-8')
        try:
            contents = repo.get_contents("quick_links.json")
            repo.update_file(contents.path, "Update quick links", content_bytes, contents.sha)
        except:
            repo.create_file("quick_links.json", "Create quick links", content_bytes)
        return True
    except Exception as e:
        st.error(f"링크 저장 오류: {e}")
        return False

# =====================================================================
# [세션 상태 관리 및 UI 헬퍼 함수]
# =====================================================================
st.session_state.setdefault("analysis_history", [])
st.session_state.setdefault("master_version", "")

if 'quick_links' not in st.session_state:
    st.session_state['quick_links'] = load_quick_links()
if 'edit_links_mode' not in st.session_state:
    st.session_state['edit_links_mode'] = False

def toggle_edit():
    st.session_state['edit_links_mode'] = not st.session_state['edit_links_mode']

def remove_history_item(item_id: str) -> None:
    st.session_state["analysis_history"] = [
        r for r in st.session_state["analysis_history"] if r["id"] != item_id]

# 팝업 차단을 완벽하게 우회하는 동기화(Synchronous) 새 탭 기술
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
    # 줄바꿈 문자를 확실히 제거하여 자바스크립트 오류 방지
    b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8').replace('\n', '')
    
    btn_html = f"""
    <a href="javascript:void(0);" onclick="var w=window.open(); w.document.write(decodeURIComponent(escape(atob('{b64}')))); w.document.close();" class="custom-new-window-btn">
        ↗️ 새창 열기
    </a>
    """
    return btn_html

# =====================================================================
# [엔진 실행 코어 로직] 
# =====================================================================
def run_quant_engine(version: str, mode: str, target_date=None,
                     target_start=None, target_end=None) -> pd.DataFrame:
    cfg = ENGINES[version]
    master_df = load_master_data(st.session_state["master_version"])

    if "recent_extracted_data" in st.session_state:
        master_df = merge_master(master_df, st.session_state["recent_extracted_data"])

    if master_df.empty:
        st.error("❌ 처리할 데이터가 없습니다.")
        return pd.DataFrame()

    end_date = (datetime.today() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    px = fetch_etf_history(SYMBOL, PRICE_HISTORY_START, end_date)

    opt_df = aggregate_oi_features(master_df, px)
    if opt_df.empty:
        st.error("❌ 집계 가능한 옵션 데이터가 없습니다.")
        return pd.DataFrame()

    df = attach_price(opt_df, px, master_df)
    df = assign_phases(df, cfg)
    df = add_display_columns(df, cfg)

    if mode == "구간 조회" and target_start and target_end:
        sel = df[(df["Date"] >= pd.to_datetime(target_start))
                 & (df["Date"] <= pd.to_datetime(target_end))].copy()
    elif mode == "타임머신 (특정일)" and target_date:
        sel = df[df["Date"] <= pd.to_datetime(target_date)].tail(10).copy()
    else:
        sel = df.tail(10).copy()

    if sel.empty:
        return pd.DataFrame()

    sel = sel[DISPLAY_COLS].copy()
    sel["Date"] = sel["Date"].dt.strftime("%m/%d")
    sel["Close Price"] = sel["Close Price"].round(2)
    return sel.rename(columns={"Close Price": f"{SYMBOL}($)",
                               "Phase": "현재 시장 국면 진단"})


# =====================================================================
# [화면 상단 UI] 타이틀 및 퀵 링크 
# =====================================================================
col_header, col_links = st.columns([0.65, 0.35])

with col_header:
    st.title(f"📈 {SYMBOL} Quant Analytics V28")
    st.markdown("**3-in-1 다중 전략 엔진 · 벡터화 연산 엔진 탑재**")

with col_links:
    head_c1, head_c2 = st.columns([0.85, 0.15])
    with head_c1:
        st.write("🔗 **Quick Links**")
    with head_c2:
        st.button("⚙️", on_click=toggle_edit, key="link_edit_btn", help="링크 편집")
        
    link_cols = st.columns(3)
    for i, link in enumerate(st.session_state['quick_links']):
        with link_cols[i]:
            btn_html = f"""
            <a href='{link['url']}' target='_blank' style='text-decoration:none;'>
                <button style='width:100%; background-color:#FF4B4B; color:white; border:none; border-radius:4px; font-size:11px; padding:6px 2px; cursor:pointer; font-weight:bold; box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 2px;'>
                    {link['name']}
                </button>
            </a>
            """
            st.markdown(btn_html, unsafe_allow_html=True)
            
    if st.session_state.get('show_link_success', False):
        st.success("✅ 링크 영구 저장 완료!")
        st.session_state['show_link_success'] = False
    
    if st.session_state['edit_links_mode']:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            for i in range(3):
                c1, c2 = st.columns([0.4, 0.6])
                c1.text_input(f"이름 {i+1}", value=st.session_state['quick_links'][i]['name'], key=f"edit_name_{i}")
                c2.text_input(f"URL {i+1}", value=st.session_state['quick_links'][i]['url'], key=f"edit_url_{i}")
            
            if st.button("적용하기", type="primary", use_container_width=True):
                with st.spinner("클라우드에 링크 설정 저장 중..."):
                    for i in range(3):
                        st.session_state['quick_links'][i]['name'] = st.session_state[f"edit_name_{i}"]
                        st.session_state['quick_links'][i]['url'] = st.session_state[f"edit_url_{i}"]
                    
                    save_quick_links(st.session_state['quick_links'])
                    st.session_state['edit_links_mode'] = False
                    st.session_state['show_link_success'] = True
                    st.rerun()

st.divider()

# =====================================================================
# [사이드바] 데이터 관리 및 조회 (깃허브 스타일 모던 UI 복원)
# =====================================================================
with st.sidebar:
    st.markdown("#### ⛁ 데이터 관리")
    if st.button("Daily 옵션데이터 추출", use_container_width=True):
        with st.spinner("옵션 체인 수집 및 IV/Delta 벡터 연산 중..."):
            df_ext, err, stats = extract_daily_options()
        if err:
            st.error(err)
        else:
            st.session_state["recent_extracted_data"] = df_ext
            st.session_state["extract_stats"] = stats
            
    # 마스터 데이터 가장 최근 일자 다운로드 기능 추가
    master_info_sb = load_master_data(st.session_state["master_version"])
    if not master_info_sb.empty:
        latest_date_sb = master_info_sb['Quote Date'].max()
        latest_date_str_sb = pd.to_datetime(latest_date_sb).strftime('%Y-%m-%d')
        latest_df_sb = master_info_sb[master_info_sb['Quote Date'] == latest_date_sb]
        csv_sb = latest_df_sb.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        
        st.download_button(
            label=f"📥 {latest_date_str_sb} 마스터(최근) 다운로드",
            data=csv_sb,
            file_name=f"{SYMBOL}_Master_Latest_{pd.to_datetime(latest_date_sb).strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()
    st.markdown("#### ⎈ 퀀트 엔진 버젼 선택")
    engine_version = st.radio("버전", list(ENGINES.keys()), label_visibility="collapsed")

    st.divider()
    st.markdown("#### ◱ 분석 모드")
    mode_selection = st.selectbox(
        "조회 방식을 선택하세요",
        ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회"), label_visibility="collapsed")

    target_date = target_start = target_end = None
    if mode_selection == "타임머신 (특정일)":
        target_date = st.date_input("기준일 선택", datetime.today())
    elif mode_selection == "구간 조회":
        c1, c2 = st.columns(2)
        with c1:
            target_start = st.date_input("시작일", datetime(2026, 6, 1))
        with c2:
            target_end = st.date_input("종료일", datetime(2026, 6, 30))

    run_button = st.button("🚀 분석 엔진 가동", type="primary", use_container_width=True)

# =====================================================================
# [결과 화면 1] 데이터 추출 완료 화면 (누적 기간 표시 복원)
# =====================================================================
if "recent_extracted_data" in st.session_state:
    df_ext = st.session_state["recent_extracted_data"]
    stats = st.session_state.get("extract_stats", {})
    total, priced = stats.get("total_rows", len(df_ext)), stats.get("priced_rows", 0)
    st.success(f"✅ 연산 완료 — 전체 {total:,}행 중 유동성 있는 {priced:,}행만 IV 계산 "
               f"(SOFR {stats.get('sofr', '-')}%)")
               
    # 누적 데이터 기간 계산 표시 완벽 복원
    master_info = load_master_data(st.session_state["master_version"])
    if not master_info.empty:
        start_dt = master_info['Quote Date'].min().strftime('%Y-%m-%d')
        end_dt = max(master_info['Quote Date'].max(), pd.to_datetime(df_ext['Quote Date'].iloc[0])).strftime('%Y-%m-%d')
        total_len = len(master_info) + len(df_ext)
        st.info(f"📅 **클라우드 데이터베이스 누적 현황:** {start_dt} ~ {end_dt} (예상 총 {total_len:,}행)")
    else:
        st.info(f"📅 **신규 데이터 기간:** {pd.to_datetime(df_ext['Quote Date'].iloc[0]).strftime('%Y-%m-%d')}")

    if stats.get("skipped_expirations"):
        st.warning(f"수집 실패 만기: {', '.join(stats['skipped_expirations'][:5])}")

    quote_str = pd.to_datetime(df_ext["Quote Date"].iloc[0]).strftime("%Y%m%d")
    st.download_button(
        "📥 CSV 파일 임시 다운로드 (PC 백업용)",
        df_ext.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"{SYMBOL} Option 분석데이터_{quote_str}.csv", mime="text/csv")
    st.dataframe(df_ext.head(5), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### ☁️ 클라우드 마스터 데이터베이스 업데이트")
    if st.button("🚀 옵션데이터 누적관리", type="primary"):
        with st.spinner("GitHub 마스터 파일에 병합 중..."):
            try:
                merged = merge_master(load_master_data(st.session_state["master_version"]),
                                      df_ext)
                n = push_master_to_github(merged, df_ext["Quote Date"].iloc[0])
                st.success(f"🎉 업데이트 완료 (총 누적 {n:,}행)")
                st.session_state.pop("recent_extracted_data", None)
                st.session_state.pop("extract_stats", None)
                st.session_state["master_version"] = uuid.uuid4().hex[:8]
                load_master_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"업데이트 실패: {e}")

# =====================================================================
# [결과 화면 2] 분석 엔진 가동 결과 누적 로직 
# =====================================================================
if run_button:
    with st.spinner(f"[{engine_version}] 연산 중..."):
        result_df = run_quant_engine(engine_version, mode_selection,
                                     target_date, target_start, target_end)
    if not result_df.empty:
        st.success(f"✅ 연산 완료 ({mode_selection})")
        if "recent_extracted_data" in st.session_state:
            st.info("💡 아직 업로드하지 않은 최신 추출 데이터가 결합되어 진단되었습니다.")

        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detail = mode_selection
        if mode_selection == "타임머신 (특정일)": detail += f" ({target_date})"
        elif mode_selection == "구간 조회": detail += f" ({target_start} ~ {target_end})"

        st.session_state["analysis_history"].insert(0, {
            "id": uuid.uuid4().hex[:8],
            "title": f"📌 [{stamp}] {engine_version} | {detail}",
            "data": result_df,
        })
        st.session_state["analysis_history"] = st.session_state["analysis_history"][:MAX_HISTORY]

# =====================================================================
# [결과 화면 3] 분석 결과 비교 히스토리 화면 (오른쪽 정렬 완벽 쌍둥이 통일)
# =====================================================================
if st.session_state["analysis_history"]:
    st.divider()
    st.header(f"📊 분석 결과 비교 히스토리 (최근 {MAX_HISTORY}건)")

    for record in st.session_state["analysis_history"]:
        with st.container():
            st.markdown(f"**{record['title']}**")
            
            # [새창 열기]와 [삭제] 버튼을 오른쪽 끝에 나란히 배치 [7.6 : 1.2 : 1.2 비율]
            _, btn_col1, btn_col2 = st.columns([7.6, 1.2, 1.2])
            with btn_col1:
                new_window_html = generate_new_window_link(record['data'], record['title'])
                st.markdown(new_window_html, unsafe_allow_html=True)
            with btn_col2:
                st.button("❌ 삭제", key=f"del_{record['id']}",
                          on_click=remove_history_item, args=(record["id"],),
                          use_container_width=True)
            
            st.dataframe(record["data"], use_container_width=True, hide_index=True)
            st.write("")
