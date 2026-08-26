"""EWY Quant Analytics V28 — Streamlit UI.

UI만 담당합니다. 수학은 pricing.py, 집계는 features.py, 판정은 phases.py,
표시 문자열은 presenters.py 에 있습니다.
"""
from __future__ import annotations

import uuid
import warnings
from datetime import datetime

import pandas as pd
import streamlit as st

from config import (DISPLAY_COLS, ENGINES, MAX_HISTORY, PRICE_HISTORY_START,
                    SYMBOL)
from data_io import (extract_daily_options, fetch_etf_history, load_master_data,
                     merge_master, normalize_option_frame, push_master_to_github)
from features import aggregate_oi_features, attach_price
from phases import assign_phases
from presenters import add_display_columns

warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V28",
                   page_icon="📈", layout="wide")

st.session_state.setdefault("analysis_history", [])
st.session_state.setdefault("master_version", "")


def remove_history_item(item_id: str) -> None:
    """인덱스가 아니라 id로 지웁니다. 콜백 실행 시점에 목록이 바뀌어도 안전합니다."""
    st.session_state["analysis_history"] = [
        r for r in st.session_state["analysis_history"] if r["id"] != item_id]


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


# ─── 사이드바 ────────────────────────────────────────────────────────
st.title(f"📈 {SYMBOL} Quant Analytics V28")
st.markdown("**3-in-1 다중 전략 엔진 · 벡터화 연산 엔진 탑재**")

with st.sidebar:
    st.header("📥 데이터 관리")
    # 플래그 없이 바로 실행 — rerun 왕복을 한 번 줄입니다
    if st.button("Daily 옵션데이터 추출", use_container_width=True):
        with st.spinner("옵션 체인 수집 및 IV/Delta 벡터 연산 중..."):
            df_ext, err, stats = extract_daily_options()
        if err:
            st.error(err)
        else:
            st.session_state["recent_extracted_data"] = df_ext
            st.session_state["extract_stats"] = stats

    st.divider()
    st.header("⚙️ 퀀트 엔진 버젼 선택")
    engine_version = st.radio("버전", list(ENGINES.keys()))

    st.divider()
    st.header("▶ 분석 모드")
    mode_selection = st.selectbox(
        "조회 방식을 선택하세요",
        ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회"))

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

# ─── 추출 결과 ───────────────────────────────────────────────────────
if "recent_extracted_data" in st.session_state:
    df_ext = st.session_state["recent_extracted_data"]
    stats = st.session_state.get("extract_stats", {})
    total, priced = stats.get("total_rows", len(df_ext)), stats.get("priced_rows", 0)
    st.success(f"✅ 연산 완료 — 전체 {total:,}행 중 유동성 있는 {priced:,}행만 IV 계산 "
               f"(SOFR {stats.get('sofr', '-')}%)")
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
                # 업로드가 끝난 데이터를 세션에 남겨두면 이후 분석에 계속 재병합됩니다
                st.session_state.pop("recent_extracted_data", None)
                st.session_state.pop("extract_stats", None)
                st.session_state["master_version"] = uuid.uuid4().hex[:8]
                load_master_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"업데이트 실패: {e}")

# ─── 엔진 실행 ───────────────────────────────────────────────────────
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
        if mode_selection == "타임머신 (특정일)":
            detail += f" ({target_date})"
        elif mode_selection == "구간 조회":
            detail += f" ({target_start} ~ {target_end})"

        st.session_state["analysis_history"].insert(0, {
            "id": uuid.uuid4().hex[:8],          # 초 단위 타임스탬프는 키 충돌 위험
            "title": f"📌 [{stamp}] {engine_version} | {detail}",
            "data": result_df,
        })
        # 세션 메모리가 무한히 늘지 않도록 상한을 둡니다
        st.session_state["analysis_history"] = \
            st.session_state["analysis_history"][:MAX_HISTORY]

# ─── 히스토리 ────────────────────────────────────────────────────────
if st.session_state["analysis_history"]:
    st.divider()
    c_title, c_clear = st.columns([0.85, 0.15])
    with c_title:
        st.header(f"📊 분석 결과 비교 히스토리 (최근 {MAX_HISTORY}건)")
    with c_clear:
        if st.button("🗑️ 전체 삭제", use_container_width=True):
            st.session_state["analysis_history"] = []
            st.rerun()

    for record in st.session_state["analysis_history"]:
        with st.container():
            c1, c2 = st.columns([0.9, 0.1])
            with c1:
                st.markdown(f"**{record['title']}**")
            with c2:
                st.button("❌ 삭제", key=f"del_{record['id']}",
                          on_click=remove_history_item, args=(record["id"],),
                          use_container_width=True)
            st.dataframe(record["data"], use_container_width=True, hide_index=True)
            st.write("")
