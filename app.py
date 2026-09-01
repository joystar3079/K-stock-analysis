"""EWY Quant Analytics V30 — Streamlit UI.
 
[V29 8개 파일 모듈화 전용 UI]
수학 연산과 판정 로직은 완벽히 분리되어 다른 파일에서 불러옵니다.
새창 열기 동기화 우회, 퀵링크, 우측 쌍둥이 버튼 정렬, 마스터 최신 다운로드 기능이 적용되었습니다.
 
[V30] 야후 파이낸스 차단 무관 운영
  · 옵션 체인: 엑셀/CSV 업로드 경로가 기본, 야후 자동수집은 보조
  · 시세: 야후 → stooq 자동 폴백, 둘 다 막히면 시세 파일 업로드로 대체
  · 자동 인식 실패 시 종가·기준일·SOFR 를 수동 보정할 수 있는 입력란 제공
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
 
from config import (DEFAULT_SOFR, DISPLAY_COLS, ENGINES, MAX_HISTORY,
                    PRICE_HISTORY_START, SYMBOL)
from data_io import (diagnose_quote_date, extract_daily_options,
                     fetch_etf_history, load_master_data, merge_master,
                     merge_report, push_master_to_github)
 
# ── V30 신규 함수 ────────────────────────────────────────────────────
# 저장소에 구버전 data_io.py 가 남아 있어도 앱 전체가 죽지 않도록 방어합니다.
# (ImportError 로 앱이 통째로 멈추면 원인 파악이 어렵기 때문입니다.)
try:
    from data_io import extract_options_from_file, load_price_history_from_file
    IO_OK, IO_ERR = True, ""
except ImportError as _e:
    IO_OK, IO_ERR = False, str(_e)
    extract_options_from_file = None
    load_price_history_from_file = None
 
try:
    from data_io import IO_VERSION
except ImportError:
    IO_VERSION = "구버전(V29 이하)"
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns
 
warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V30",
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
st.session_state.setdefault("price_history_override", None)
 
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
 
    # 시세: 업로드 파일이 있으면 최우선, 없으면 야후 → stooq 폴백
    end_date = (datetime.today() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    px = st.session_state.get("price_history_override")
    if px is not None and not px.empty:
        meta["price_source"] = "업로드 파일"
        mask = ((px["Date"] >= pd.to_datetime(PRICE_HISTORY_START))
                & (px["Date"] <= pd.to_datetime(end_date)))
        px = px[mask].reset_index(drop=True)
    else:
        px = fetch_etf_history(SYMBOL, PRICE_HISTORY_START, end_date)
        meta["price_source"] = "야후/stooq"
 
    if px is None or px.empty:
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
    st.title(f"📈 {SYMBOL} Quant Analytics V30")
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
 
    if not IO_OK:
        st.error(
            f"⚠️ **data_io.py 가 구버전입니다** ({IO_VERSION})\n\n"
            "저장소의 `data_io.py` 를 V30 파일로 교체한 뒤 앱을 재부팅하세요. "
            "그 전까지는 야후 자동 수집만 동작합니다.")
        with st.expander("상세 오류"):
            st.code(IO_ERR)
        source_mode = "🌐 야후 자동 수집"
    else:
        source_mode = st.radio(
            "수집 방식",
            ("📁 엑셀/CSV 업로드", "🌐 야후 자동 수집"),
            label_visibility="collapsed", key="source_mode",
            help="야후가 차단된 서버에서는 업로드 경로를 사용하세요. 산출 결과는 동일합니다.")
 
    # ── 경로 A: 파일 업로드 (야후 차단과 무관) ─────────────────────
    if IO_OK and source_mode.startswith("📁"):
        up_file = st.file_uploader(
            "옵션 체인 파일", type=["csv", "xlsx", "xls", "xlsm"],
            label_visibility="collapsed", key="chain_uploader")
        st.caption("CBOE 원본(콜·풋 한 행) · 일반 롱 포맷 · 컬럼명 변형 자동 인식")
 
        with st.expander("⚙️ 수동 보정 (자동 인식 실패 시)"):
            use_price = st.checkbox("기초자산 종가 직접 입력", key="use_manual_price")
            manual_price = st.number_input(
                f"{SYMBOL} 종가 ($)", min_value=0.0, value=0.0, step=0.01,
                format="%.2f", disabled=not use_price, key="manual_price")
 
            use_date = st.checkbox("기준일 직접 지정", key="use_manual_date")
            manual_date = st.date_input(
                "기준일 (Quote Date)", datetime.today(),
                disabled=not use_date, key="manual_qdate")
 
            use_sofr = st.checkbox("SOFR 직접 입력", key="use_manual_sofr")
            manual_sofr = st.number_input(
                "SOFR (%)", min_value=0.0, value=float(DEFAULT_SOFR), step=0.01,
                format="%.2f", disabled=not use_sofr, key="manual_sofr")
 
        if st.button("📄 업로드 파일 변환", type="primary",
                     use_container_width=True, disabled=up_file is None):
            with st.spinner("파일 파싱 및 IV/Delta 벡터 연산 중..."):
                df_ext, err, stats = extract_options_from_file(
                    up_file,
                    filename=getattr(up_file, "name", None),
                    etf_price=(manual_price if use_price and manual_price > 0 else None),
                    quote_date=(manual_date if use_date else None),
                    sofr=(manual_sofr if use_sofr else None),
                )
            if err:
                st.error(err)
                st.session_state["extract_error_stats"] = stats
                st.session_state["extract_error_msg"] = err
            else:
                st.session_state.pop("extract_error_stats", None)
                st.session_state.pop("extract_error_msg", None)
                st.session_state["recent_extracted_data"] = df_ext
                st.session_state["extract_stats"] = stats
                st.rerun()
 
    # ── 경로 B: 야후 자동 수집 (보조) ──────────────────────────────
    else:
        st.caption("서버 IP가 차단되면 실패할 수 있습니다. 실패 시 업로드 경로를 쓰세요.")
        if st.button("Daily 옵션데이터 추출", use_container_width=True):
            with st.spinner("옵션 체인 수집 및 IV/Delta 벡터 연산 중..."):
                df_ext, err, stats = extract_daily_options()
            if err:
                st.error(err)
                st.session_state["extract_error_stats"] = stats
                st.session_state["extract_error_msg"] = err
            else:
                st.session_state.pop("extract_error_stats", None)
                st.session_state.pop("extract_error_msg", None)
                st.session_state["recent_extracted_data"] = df_ext
                st.session_state["extract_stats"] = stats
                st.rerun()
 
    if "recent_extracted_data" in st.session_state:
        if st.button("↩️ 추출본 버리기 (마스터만 사용)", use_container_width=True):
            st.session_state.pop("recent_extracted_data", None)
            st.session_state.pop("extract_stats", None)
            st.rerun()
 
    # ── 시세 폴백 ────────────────────────────────────────────────
    if IO_OK:
        with st.expander("📉 시세 파일 (야후 시세까지 막힐 때)"):
            px_now = st.session_state.get("price_history_override")
            if px_now is not None and not px_now.empty:
                st.success(f"적용 중 — {len(px_now):,}일 "
                           f"({px_now['Date'].min():%Y-%m-%d} ~ {px_now['Date'].max():%Y-%m-%d})")
                if st.button("시세 파일 해제", use_container_width=True):
                    st.session_state["price_history_override"] = None
                    st.rerun()
            else:
                px_file = st.file_uploader(
                    f"{SYMBOL} 일봉 (Date / Close 컬럼)",
                    type=["csv", "xlsx", "xls"], key="px_uploader")
                if px_file is not None and st.button("시세 적용", use_container_width=True):
                    try:
                        px_df = load_price_history_from_file(
                            px_file, getattr(px_file, "name", None))
                    except Exception as e:
                        px_df = pd.DataFrame()
                        st.error(f"시세 파일 읽기 실패: {e}")
                    if px_df.empty:
                        st.error("Date / Close 컬럼을 찾지 못했습니다.")
                    else:
                        st.session_state["price_history_override"] = px_df
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
 
    st.caption(f"data_io: {IO_VERSION}")
 
# =====================================================================
# [결과 화면 1] 추출 완료 + 마스터 최신 다운로드 + 병합 정책
# =====================================================================
if st.session_state.get("extract_error_stats") is not None:
    with st.expander("🩺 수집 실패 진단 — 파일에서 무엇을 읽었는지 확인", expanded=True):
        est = st.session_state["extract_error_stats"]
        st.error(st.session_state.get("extract_error_msg", "수집에 실패했습니다."))
        cols = est.get("detected_columns")
        if cols:
            st.write("**인식된 컬럼:** " + ", ".join(str(c) for c in cols))
            st.caption("Strike / Expiration Date / Option Type 중 빠진 게 있으면 "
                       "원본 파일의 헤더를 확인하거나 수동 보정 입력란을 사용하세요.")
        else:
            st.caption("헤더 자체를 찾지 못했습니다. 파일 상단의 안내문이 너무 길거나 "
                       "옵션 체인이 아닌 시트일 수 있습니다.")
        st.json(est)
 
if "recent_extracted_data" in st.session_state:
    df_ext = st.session_state["recent_extracted_data"]
    stats = st.session_state.get("extract_stats", {})
    total = stats.get("total_rows", len(df_ext))
    priced = stats.get("priced_rows", 0)
    src_label = "📁 업로드 파일" if stats.get("source") == "file" else "🌐 야후 API"
    price_txt = stats.get("etf_price", "-")
    st.success(f"✅ 연산 완료 [{src_label}] — 전체 {total:,}행 중 유동성 있는 {priced:,}행만 IV 계산 "
               f"(기준일 {stats.get('quote_date', '-')}, {SYMBOL} ${price_txt}, "
               f"SOFR {stats.get('sofr', '-')}%)")
 
    if stats.get("multi_quote_dates"):
        st.warning(
            f"⚠️ 업로드 파일에 날짜가 여러 개 섞여 있습니다 "
            f"({', '.join(str(d) for d in stats['multi_quote_dates'])}). "
            f"가장 최근 날짜 **{stats.get('quote_date')}** 만 사용했습니다. "
            "다른 날짜를 쓰려면 사이드바의 '기준일 직접 지정'으로 골라 다시 변환하세요.")
 
    if stats.get("price_source"):
        st.caption(f"기초자산 종가 출처: {stats['price_source']} "
                   "(파일에 종가 컬럼이 없어 외부에서 보충했습니다)")
 
    filled_iv = stats.get("filled_from_file_Implied Volatility", 0)
    if filled_iv:
        st.caption(f"IV 산출이 실패한 {filled_iv:,}행은 파일에 들어있던 벤더 IV로 채웠습니다.")
 
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
        if meta.get("price_error"):
            st.error("❌ 시세를 가져오지 못했습니다 (야후·stooq 모두 실패). "
                     "사이드바 **📉 시세 파일** 에 일봉 CSV를 올린 뒤 다시 실행하세요.")
        else:
            st.error("❌ 조회 결과가 없습니다. 날짜 범위와 마스터 데이터를 확인하세요.")
    else:
        anchor = meta.get("anchor_date")
        anchor_str = pd.to_datetime(anchor).strftime("%Y-%m-%d") if anchor is not None else "-"
        st.success(f"✅ 연산 완료 ({mode_selection}) · **기준일 {anchor_str}** · "
                   f"누적 {meta.get('n_dates', 0)}일")
 
        if meta.get("merged_extraction"):
            pol = "기존 유지" if meta.get("merge_policy") == "skip" else "새 추출본으로 교체"
            st.info(f"💡 업로드 전 추출본이 결합되었습니다 (중복 날짜 처리: {pol})")
 
        if meta.get("price_source"):
            st.caption(f"시세 출처: {meta['price_source']}")
 
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
