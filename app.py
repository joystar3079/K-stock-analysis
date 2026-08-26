"""EWY Quant Analytics V29 — Streamlit UI.

[V29 8개 파일 모듈화 전용 UI]
수학 연산과 판정 로직은 완벽히 분리되어 다른 파일에서 불러옵니다.
새창 열기 동기화 우회, 퀵링크, 우측 쌍둥이 버튼 정렬, 마스터 최신 다운로드 기능이 적용되었습니다.
"""
from __future__ import annotations

import json
import uuid
import warnings
from datetime import datetime
import base64

import pandas as pd
import streamlit as st
from github import Github

from config import (DISPLAY_COLS, ENGINES, MAX_HISTORY, PRICE_HISTORY_START,
                    SYMBOL)
from data_io import (diagnose_quote_date, extract_daily_options,
                     fetch_etf_history, load_master_data, merge_master,
                     merge_report, push_master_to_github)
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns

warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V29",
                   page_icon="📈", layout="wide")

# =====================================================================
# [웹 UI 전용 CSS] 버튼 크기, 디자인 완벽 쌍둥이 통일
# =====================================================================
st.markdown("""
<style>
/* 삭제버튼 (Secondary) 크기/포맷 통일 */
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

/* 새창열기 HTML 버튼을 삭제버튼과 100% 동일하게 맞춤 */
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

/* 마크다운 여백 제거 (버튼 상하 정렬용) */
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

if "quick_links" not in st.session_state:
    st.session_state["quick_links"] = load_quick_links()

def toggle_edit():
    st.session_state["edit_links_mode"] = not st.session_state["edit_links_mode"]

def remove_history_item(item_id: str) -> None:
    st.session_state["analysis_history"] = [
        r for r in st.session_state["analysis_history"] if r["id"] != item_id]

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
    btn_html = f"""
    <a href="javascript:void(0);" onclick="var w=window.open(); w.document.write(decodeURIComponent(escape(atob('{b64}')))); w.document.close();" class="custom-new-window-btn">
        ↗️ 새창 열기
    </a>
    """
    return btn_html

# =====================================================================
# [엔진 실행 코어]
# =====================================================================
def build_full_frame(version: str) -> tuple[pd.DataFrame, dict]:
    cfg = ENGINES[version]
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

    if master_df.empty:
        return pd.DataFrame(), meta

    end_date = (datetime.today() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    px = fetch_etf_history(SYMBOL, PRICE_HISTORY_START, end_date)

    opt_df = aggregate_oi_features(master_df, px)
    if opt_df.empty:
        return pd.DataFrame(), meta

    df = attach_price(opt_df, px, master_df)
    df = assign_phases(df, cfg)
    df = add_display_columns(df, cfg)
    meta["latest_date"] = df["Date"].max()
    meta["n_dates"] = len(df)
    return df, meta

def run_quant_engine(version: str, mode: str, target_date=None,
                     target_start=None, target_end=None) -> tuple[pd.DataFrame, dict]:
    df, meta = build_full_frame(version)
    if df.empty:
        return pd.DataFrame(), meta

    if mode == "구간 조회" and target_start and target_end:
        sel = df[(df["Date"] >= pd.to_datetime(target_start))
                 & (df["Date"] <= pd.to_datetime(target_end))].copy()
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
    return sel.rename(columns={"Close Price": f"{SYMBOL}($)",
                               "Phase": "현재 시장 국면 진단"}), meta

# =====================================================================
# [상단 UI]
# =====================================================================
col_header, col_links = st.columns([0.65, 0.35])
with col_header:
    st.title(f"📈 {SYMBOL} Quant Analytics V29")
    st.markdown("**3-in-1 다중 전략 엔진 · 벡터화 연산 엔진 탑재**")

with col_links:
    h1, h2 = st.columns([0.85, 0.15])
    with h1:
        st.write("🔗 **Quick Links**")
    with h2:
        st.button("⚙️", on_click=toggle_edit, key="link_edit_btn", help="링크 편집")

    link_cols = st.columns(3)
    for i, link in enumerate(st.session_state["quick_links"][:3]):
        with link_cols[i]:
            st.markdown(
                f"<a href='{link['url']}' target='_blank' style='text-decoration:none;'>"
                f"<button style='width:100%;background-color:#FF4B4B;color:white;border:none;"
                f"border-radius:4px;font-size:11px;padding:6px 2px;cursor:pointer;"
                f"font-weight:bold;'>{link['name']}</button></a>",
                unsafe_allow_html=True)

    if st.session_state.get("show_link_success", False):
        st.success("✅ 링크 영구 저장 완료!")
        st.session_state["show_link_success"] = False

    if st.session_state["edit_links_mode"]:
        st.markdown("<br>", unsafe_allow_html=True)
        for i in range(3):
            c1, c2 = st.columns([0.4, 0.6])
            c1.text_input(f"이름 {i+1}", value=st.session_state["quick_links"][i]["name"],
                          key=f"edit_name_{i}")
            c2.text_input(f"URL {i+1}", value=st.session_state["quick_links"][i]["url"],
                          key=f"edit_url_{i}")
        if st.button("적용하기", type="primary", use_container_width=True):
            with st.spinner("클라우드에 링크 설정 저장 중..."):
                for i in range(3):
                    st.session_state["quick_links"][i]["name"] = st.session_state[f"edit_name_{i}"]
                    st.session_state["quick_links"][i]["url"] = st.session_state[f"edit_url_{i}"]
                save_quick_links(st.session_state["quick_links"])
                st.session_state["edit_links_mode"] = False
                st.session_state["show_link_success"] = True
                st.rerun()

st.divider()

# =====================================================================
# [사이드바]
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

    if "recent_extracted_data" in st.session_state:
        if st.button("↩️ 추출본 버리기 (마스터만 사용)", use_container_width=True):
            st.session_state.pop("recent_extracted_data", None)
            st.session_state.pop("extract_stats", None)
            st.rerun()

    st.divider()
    st.markdown("#### ⎈ 퀀트 엔진 버젼 선택")
    engine_version = st.radio("버전", list(ENGINES.keys()), label_visibility="collapsed")

    st.divider()
    st.markdown("#### ◱ 분석 모드")
    mode_selection = st.selectbox(
        "조회 방식", ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회"),
        label_visibility="collapsed")

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
# [결과 화면 1] 추출 완료 + 마스터 최신 다운로드 + 병합 정책
# =====================================================================
if "recent_extracted_data" in st.session_state:
    df_ext = st.session_state["recent_extracted_data"]
    stats = st.session_state.get("extract_stats", {})
    total = stats.get("total_rows", len(df_ext))
    priced = stats.get("priced_rows", 0)
    st.success(f"✅ 연산 완료 — 전체 {total:,}행 중 유동성 있는 {priced:,}행만 IV 계산 "
               f"(SOFR {stats.get('sofr', '-')}%, 기준일 {stats.get('quote_date', '-')})")

    master_info = load_master_data(st.session_state["master_version"])
    rep = merge_report(master_info, df_ext)

    if rep["conflict_dates"]:
        st.warning(
            f"⚠️ 추출본의 날짜 **{', '.join(str(d) for d in rep['conflict_dates'])}** 가 "
            f"이미 마스터에 있습니다 (해당 날짜 마스터 {rep['conflict_rows_in_master']:,}행).\n\n"
            "라이브 옵션 체인은 만기 구성과 미결제약정이 과거 기록과 다릅니다. "
            "두 스냅샷을 섞으면 그 날짜의 지표가 왜곡되므로, 아래에서 하나를 고르세요.")
        policy_label = st.radio(
            "중복 날짜 처리",
            ("기존 기록 유지 (권장)", "새 추출본으로 통째 교체"),
            horizontal=True, key="policy_radio")
        st.session_state["merge_policy"] = (
            "skip" if policy_label.startswith("기존") else "replace")
    else:
        st.session_state["merge_policy"] = "skip"
        if rep["new_dates"]:
            st.info(f"🆕 마스터에 없는 새 날짜: "
                    f"{', '.join(str(d) for d in rep['new_dates'])}")

    if not master_info.empty:
        start_dt = master_info["Quote Date"].min().strftime("%Y-%m-%d")
        end_dt = master_info["Quote Date"].max().strftime("%Y-%m-%d")
        st.info(f"📅 **클라우드 누적 현황:** {start_dt} ~ {end_dt} ({len(master_info):,}행)")

        latest = master_info["Quote Date"].max()
        latest_df = master_info[master_info["Quote Date"] == latest]
        st.download_button(
            label=f"📥 {latest.strftime('%Y-%m-%d')} 마스터(최근) 다운로드",
            data=latest_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"{SYMBOL}_Master_Latest_{latest.strftime('%Y%m%d')}.csv",
            mime="text/csv")
    else:
        quote_str = pd.to_datetime(df_ext["Quote Date"].iloc[0]).strftime("%Y%m%d")
        csv_data = df_ext.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 CSV 파일 임시 다운로드 (PC 백업용)",
            data=csv_data,
            file_name=f"{SYMBOL} Option 분석데이터_{quote_str}.csv", 
            mime="text/csv"
        )

    if stats.get("skipped_expirations"):
        st.warning(f"수집 실패 만기: {', '.join(stats['skipped_expirations'][:5])}")

    with st.expander("🔬 날짜 구성 진단 — 마스터 vs 추출본 비교"):
        diag_date = st.date_input(
            "진단할 날짜",
            pd.to_datetime(stats.get("quote_date", datetime.today())),
            key="diag_date")
        st.dataframe(diagnose_quote_date(master_info, df_ext, diag_date),
                     use_container_width=True, hide_index=True)
        st.caption("행수·만기수·행사가 범위가 다르면 두 스냅샷은 서로 다른 자료입니다. "
                   "OI=0 비율이 높으면 라이브 체인의 미결제약정이 아직 갱신되지 않은 상태입니다.")

    st.dataframe(df_ext.head(5), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### ☁️ 클라우드 마스터 데이터베이스 업데이트")
    if st.button("🚀 옵션데이터 누적관리", type="primary"):
        with st.spinner("GitHub 마스터 파일에 병합 중..."):
            try:
                merged = merge_master(master_info, df_ext,
                                      on_conflict=st.session_state["merge_policy"])
                n = push_master_to_github(merged, df_ext["Quote Date"].iloc[0])
                st.success(f"🎉 업데이트 완료 (정책: {st.session_state['merge_policy']}, "
                           f"총 누적 {n:,}행)")
                st.session_state.pop("recent_extracted_data", None)
                st.session_state.pop("extract_stats", None)
                st.session_state["master_version"] = uuid.uuid4().hex[:8]
                load_master_data.clear()
                st.info("GitHub raw 캐시 반영에 최대 5분 걸릴 수 있습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"업데이트 실패: {e}")

# =====================================================================
# [결과 화면 2] 분석 실행
# =====================================================================
if run_button:
    with st.spinner(f"[{engine_version}] 연산 중..."):
        result_df, meta = run_quant_engine(engine_version, mode_selection,
                                           target_date, target_start, target_end)
    if result_df.empty:
        st.error("❌ 조회 결과가 없습니다. 날짜 범위와 마스터 데이터를 확인하세요.")
    else:
        anchor = meta.get("anchor_date")
        anchor_str = pd.to_datetime(anchor).strftime("%Y-%m-%d") if anchor is not None else "-"
        st.success(f"✅ 연산 완료 ({mode_selection}) · **기준일 {anchor_str}** · "
                   f"누적 {meta.get('n_dates', 0)}일")

        if meta.get("merged_extraction"):
            pol = "기존 유지" if meta.get("merge_policy") == "skip" else "새 추출본으로 교체"
            st.info(f"💡 업로드 전 추출본이 결합되었습니다 (중복 날짜 처리: {pol})")

        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detail = mode_selection
        if mode_selection == "타임머신 (특정일)":
            detail += f" ({target_date})"
        elif mode_selection == "구간 조회":
            detail += f" ({target_start} ~ {target_end})"

        st.session_state["analysis_history"].insert(0, {
            "id": uuid.uuid4().hex[:8],
            "title": f"📌 [{stamp}] {engine_version} | {detail} | 기준일 {anchor_str}",
            "data": result_df,
        })
        st.session_state["analysis_history"] = \
            st.session_state["analysis_history"][:MAX_HISTORY]

# =====================================================================
# [결과 화면 3] 히스토리 (오른쪽 정렬 완벽 쌍둥이 통일)
# =====================================================================
if st.session_state["analysis_history"]:
    st.divider()
    st.header(f"📊 분석 결과 비교 히스토리 (최근 {MAX_HISTORY}건)")
    for record in st.session_state["analysis_history"]:
        with st.container():
            st.markdown(f"**{record['title']}**")
            
            # [새창 열기]와 [삭제] 버튼을 오른쪽 끝에 나란히 배치 [8 : 1 : 1 비율]
            _, btn_col1, btn_col2 = st.columns([8, 1, 1])
            with btn_col1:
                new_window_html = generate_new_window_link(record['data'], record['title'])
                st.markdown(new_window_html, unsafe_allow_html=True)
            with btn_col2:
                st.button("❌ 삭제", key=f"del_{record['id']}",
                          on_click=remove_history_item, args=(record["id"],),
                          use_container_width=True)
                          
            st.dataframe(record["data"], use_container_width=True, hide_index=True)
            st.write("")
