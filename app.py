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

from config import (DEFAULT_SOFR, DISPLAY_COLS, ENGINES, MASTER_FILE,
                    MAX_HISTORY, PRICE_HISTORY_START, SYMBOL)
from data_io import (diagnose_quote_date, extract_daily_options,
                     fetch_etf_history, load_master_data, merge_master,
                     merge_report, push_master_to_github)

# ── V30 신규 함수 ────────────────────────────────────────────────────
# 저장소에 구버전 data_io.py 가 남아 있어도 앱 전체가 죽지 않도록 방어합니다.
# (ImportError 로 앱이 통째로 멈추면 원인 파악이 어렵기 때문입니다.)
try:
    from data_io import (DOWNLOAD_FOLDER, auto_update_master, build_filename,
                         extract_options_from_file, extract_options_from_files,
                         latest_data_date, load_price_history_from_file,
                         master_summary, merge_many, save_to_local_folder,
                         to_csv_bytes, to_zip_bytes)
    IO_OK, IO_ERR = True, ""
except ImportError as _e:
    IO_OK, IO_ERR = False, str(_e)
    # 파서 계열은 대체 불가 — 업로드 경로만 비활성화합니다.
    extract_options_from_file = None
    extract_options_from_files = None
    load_price_history_from_file = None

    # 아래는 순수 유틸이라 앱 안에서 그대로 재현합니다.
    # 구버전 data_io.py 가 올라가 있어도 다운로드·병합은 계속 동작합니다.
    DOWNLOAD_FOLDER = "EWY Option"

    def latest_data_date(*frames):
        dates = []
        for df in frames:
            if df is None or getattr(df, "empty", True):
                continue
            if "Quote Date" not in df.columns:
                continue
            s = pd.to_datetime(df["Quote Date"], errors="coerce").dropna()
            if not s.empty:
                dates.append(s.max())
        return max(dates) if dates else None

    def build_filename(data_date=None, kind="분석데이터", ext="csv", symbol=SYMBOL):
        d = pd.to_datetime(data_date, errors="coerce") if data_date is not None else None
        stamp = d.strftime("%Y%m%d") if d is not None and pd.notna(d) else "날짜미상"
        return f"{symbol} Option {kind}_{stamp}.{ext}"

    def to_csv_bytes(df):
        return df.to_csv(index=False).encode("utf-8-sig")

    def to_zip_bytes(files, folder=DOWNLOAD_FOLDER):
        import io as _io
        import zipfile as _zipfile
        buf = _io.BytesIO()
        with _zipfile.ZipFile(buf, "w", _zipfile.ZIP_DEFLATED) as z:
            for name, data in files.items():
                z.writestr(f"{folder}/{name}", data)
        return buf.getvalue()

    def save_to_local_folder(data, filename, folder=DOWNLOAD_FOLDER, base_dir=None):
        import os as _os
        root = _os.path.expanduser(base_dir) if base_dir else _os.getcwd()
        target = _os.path.join(root, folder)
        _os.makedirs(target, exist_ok=True)
        path = _os.path.join(target, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def merge_many(current, frames, on_conflict="skip"):
        merged = (current.copy() if current is not None and not current.empty
                  else pd.DataFrame())
        reports = []
        for i, new in enumerate(frames):
            if new is None or new.empty:
                continue
            rep = merge_report(merged, new)
            rep["step"] = i + 1
            merged = merge_master(merged, new, on_conflict=on_conflict)
            rep["rows_after"] = len(merged)
            reports.append(rep)
        return merged, reports

    def master_summary(df):
        if df is None or df.empty:
            return {"rows": 0, "days": 0, "start": None, "end": None}
        d = pd.to_datetime(df["Quote Date"], errors="coerce").dropna()
        return {"rows": len(df), "days": int(d.dt.normalize().nunique()),
                "start": d.min(), "end": d.max()}

    def auto_update_master(current, new, on_conflict="skip"):
        before = master_summary(current)
        base = current if current is not None else pd.DataFrame()
        rep = merge_report(base, new)
        merged = merge_master(base, new, on_conflict=on_conflict)
        rows = push_master_to_github(merged, latest_data_date(new))
        after = master_summary(merged)
        return {"file": MASTER_FILE, "policy": on_conflict,
                "before": before, "after": after,
                "added_rows": rows - before["rows"],
                "added_days": after["days"] - before["days"], "report": rep}

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

def store_extraction(df_ext, stats, file_results=None) -> None:
    """추출 결과를 세션에 담고, 자동 반영이 켜져 있으면 GitHub 마스터까지 갱신합니다.

    저장 위치는 config 의 MASTER_FILE 로 고정이라 폴더를 고를 필요가 없습니다.
    중복 날짜는 skip — 이미 쌓인 기록을 자동 갱신이 덮어쓰는 일은 없습니다.
    """
    for k in ("extract_error_stats", "extract_error_msg", "accumulated_preview",
              "accumulated_steps", "push_result", "push_error"):
        st.session_state.pop(k, None)
    st.session_state["recent_extracted_data"] = df_ext
    st.session_state["extract_stats"] = stats
    st.session_state["file_results"] = file_results

    if not st.session_state.get("auto_push", False):
        return
    try:
        current = load_master_data(st.session_state["master_version"])
        st.session_state["push_result"] = auto_update_master(
            current, df_ext, on_conflict="skip")
        st.session_state["master_version"] = uuid.uuid4().hex[:8]
        load_master_data.clear()
    except Exception as e:
        st.session_state["push_error"] = str(e)


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
            "저장소의 `data_io.py` 를 최신 파일로 교체한 뒤 앱을 재부팅하세요. "
            "그 전까지는 파일 업로드 경로만 막히고, 야후 수집·다운로드·누적 병합은 "
            "그대로 동작합니다.")
        with st.expander("상세 오류"):
            st.code(IO_ERR)
        source_mode = "🌐 야후 자동 수집"
    else:
        source_mode = st.radio(
            "수집 방식",
            ("📁 엑셀/CSV 업로드", "🌐 야후 자동 수집"),
            label_visibility="collapsed", key="source_mode",
            help="야후가 차단된 서버에서는 업로드 경로를 사용하세요. 산출 결과는 동일합니다.")

    st.checkbox(f"변환 즉시 GitHub 마스터 자동 반영 (`{MASTER_FILE}`)",
                value=True, key="auto_push",
                help="추출/변환이 끝나면 곧바로 GitHub 마스터에 병합·커밋합니다. "
                     "중복 날짜는 기존 기록을 유지(skip)하므로 덮어쓸 위험이 없습니다.")

    # ── 경로 A: 파일 업로드 (야후 차단과 무관) ─────────────────────
    if IO_OK and source_mode.startswith("📁"):
        up_files = st.file_uploader(
            "옵션 체인 파일", type=["csv", "xlsx", "xls", "xlsm"],
            accept_multiple_files=True,
            label_visibility="collapsed", key="chain_uploader")
        st.caption("CBOE 원본(콜·풋 한 행) · 일반 롱 포맷 · 컬럼명 변형 자동 인식")
        if up_files:
            st.caption(f"선택된 파일 {len(up_files)}개 — 여러 날짜를 한 번에 누적 병합합니다.")

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
                     use_container_width=True, disabled=not up_files):
            kw = dict(
                etf_price=(manual_price if use_price and manual_price > 0 else None),
                quote_date=(manual_date if use_date else None),
                sofr=(manual_sofr if use_sofr else None),
            )

            # 파일 1개 — 기존 경로 그대로
            if len(up_files) == 1:
                with st.spinner("파일 파싱 및 IV/Delta 벡터 연산 중..."):
                    df_ext, err, stats = extract_options_from_file(
                        up_files[0], filename=getattr(up_files[0], "name", None), **kw)
                file_results = None

            # 파일 여러 개 — 각각 변환 후 하나로 누적 병합
            else:
                if use_date:
                    st.warning("여러 파일에 같은 기준일을 강제하면 서로 덮어씁니다. "
                               "'기준일 직접 지정'을 끄고 다시 시도하세요.")
                with st.spinner(f"{len(up_files)}개 파일 변환 및 누적 병합 중..."):
                    df_ext, file_results = extract_options_from_files(up_files, **kw)
                fails = [r for r in file_results if r["error"]]
                err = None if df_ext is not None else "모든 파일의 변환이 실패했습니다."
                stats = {
                    "source": "file",
                    "file_count": len(up_files),
                    "failed_files": [f"{r['filename']}: {r['error']}" for r in fails],
                    "quote_date": (latest_data_date(df_ext) if df_ext is not None else None),
                    "total_rows": 0 if df_ext is None else len(df_ext),
                    "priced_rows": sum(r["priced_rows"] for r in file_results),
                    "loaded_dates": sorted(
                        {str(r["quote_date"]) for r in file_results if r["quote_date"]}),
                }
                if stats["quote_date"] is not None:
                    stats["quote_date"] = pd.Timestamp(stats["quote_date"]).date()

            if err:
                st.error(err)
                st.session_state["extract_error_stats"] = stats
                st.session_state["extract_error_msg"] = err
            else:
                with st.spinner("GitHub 마스터에 자동 반영 중..."):
                    store_extraction(df_ext, stats, file_results)
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
                with st.spinner("GitHub 마스터에 자동 반영 중..."):
                    store_extraction(df_ext, stats)
                st.rerun()

    if "recent_extracted_data" in st.session_state:
        if st.button("↩️ 추출본 버리기 (마스터만 사용)", use_container_width=True):
            for k in ("recent_extracted_data", "extract_stats", "file_results",
                      "accumulated_preview", "accumulated_steps"):
                st.session_state.pop(k, None)
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

    if stats.get("file_count"):
        st.info(f"📚 {stats['file_count']}개 파일 누적 병합 — "
                f"수록 날짜 {len(stats.get('loaded_dates', []))}일 "
                f"({', '.join(stats.get('loaded_dates', [])[:6])}"
                f"{' …' if len(stats.get('loaded_dates', [])) > 6 else ''})")
    if stats.get("failed_files"):
        st.warning("변환 실패 파일:\n\n" +
                   "\n\n".join(f"· {x}" for x in stats["failed_files"]))

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

    # ── 다운로드 ────────────────────────────────────────────────────
    st.markdown("##### 📥 다운로드")

    data_date = latest_data_date(df_ext)
    fn_latest = build_filename(data_date, "분석데이터")
    csv_latest = to_csv_bytes(df_ext)

    st.caption(f"파일명 기준일은 오늘이 아니라 **데이터의 최종 일자**입니다 → `{fn_latest}`")

    dl1, dl2 = st.columns(2)
    dl1.download_button(
        f"📄 최근 데이터 ({len(df_ext):,}행)", data=csv_latest,
        file_name=fn_latest, mime="text/csv", use_container_width=True)
    dl2.download_button(
        f"🗂 {DOWNLOAD_FOLDER} 폴더 (zip)",
        data=to_zip_bytes({fn_latest: csv_latest}),
        file_name=build_filename(data_date, "분석데이터", "zip").replace(" 분석데이터", ""),
        mime="application/zip", use_container_width=True,
        help=f"압축을 풀면 '{DOWNLOAD_FOLDER}' 폴더가 생기고 그 안에 CSV가 들어갑니다.")

    st.caption("브라우저 보안상 웹앱이 PC의 저장 폴더를 직접 지정할 수는 없습니다. "
               f"'{DOWNLOAD_FOLDER}' 폴더로 받으시려면 zip 을 받아 푸시거나, "
               "브라우저 설정에서 '다운로드 전에 저장 위치 확인'을 켜두세요.")

    # ── 누적 데이터: GitHub 마스터 자동 반영 ────────────────────────
    st.markdown(f"##### ☁️ 누적 데이터 — GitHub 자동 반영 (`{MASTER_FILE}`)")

    push_err = st.session_state.get("push_error")
    push_res = st.session_state.get("push_result")

    if push_err:
        st.error(f"자동 반영 실패: {push_err}")
        st.caption("secrets 의 GITHUB_TOKEN / GITHUB_REPO 를 확인하세요. "
                   "아래 수동 버튼으로 다시 시도할 수 있습니다.")
    elif push_res:
        b, a = push_res["before"], push_res["after"]
        st.success(
            f"✅ 자동 반영 완료 — {b['rows']:,}행/{b['days']:,}일 → "
            f"**{a['rows']:,}행/{a['days']:,}일** "
            f"(+{push_res['added_rows']:,}행, +{push_res['added_days']}일)")
        if push_res["report"]["conflict_dates"]:
            st.caption("중복 날짜 "
                       f"{', '.join(str(d) for d in push_res['report']['conflict_dates'])} "
                       "는 기존 기록을 유지했습니다. 새 스냅샷으로 덮으려면 아래에서 "
                       "'새 추출본으로 통째 교체'를 고르고 수동 반영하세요.")
        st.caption("GitHub raw 캐시 반영에 최대 5분 걸릴 수 있습니다.")
    elif not st.session_state.get("auto_push", False):
        st.info("자동 반영이 꺼져 있습니다. 아래 버튼으로 직접 반영하세요.")

    policy = st.session_state["merge_policy"]
    pol_txt = "기존 유지(skip)" if policy == "skip" else "새 추출본으로 교체(replace)"
    if st.button(f"🔁 지금 반영 (정책: {pol_txt})", use_container_width=True):
        with st.spinner("마스터 병합 및 GitHub 반영 중..."):
            try:
                st.session_state["push_result"] = auto_update_master(
                    master_info, df_ext, on_conflict=policy)
                st.session_state.pop("push_error", None)
                st.session_state["master_version"] = uuid.uuid4().hex[:8]
                load_master_data.clear()
                st.rerun()
            except Exception as e:
                st.session_state["push_error"] = str(e)
                st.rerun()

    with st.expander("🗄 누적 데이터 백업 다운로드 (선택)"):
        st.caption("평소에는 필요 없습니다. GitHub 마스터가 원본이고 자동으로 갱신됩니다. "
                   "외부 분석용 스냅샷이 필요할 때만 쓰세요.")
        if st.button("누적본 CSV 만들기", use_container_width=True):
            with st.spinner("병합본 생성 중..."):
                acc_df, _ = merge_many(master_info, [df_ext], on_conflict=policy)
            st.session_state["accumulated_preview"] = acc_df

        acc = st.session_state.get("accumulated_preview")
        if acc is not None and not acc.empty:
            acc_date = latest_data_date(acc)
            st.download_button(
                "📚 누적본 CSV 다운로드", data=to_csv_bytes(acc),
                file_name=build_filename(acc_date, "누적데이터"),
                mime="text/csv", use_container_width=True)

    # ── 로컬 폴더 직접 저장 (로컬 실행 시에만 유효) ────────────────
    with st.expander(f"💾 '{DOWNLOAD_FOLDER}' 폴더에 직접 저장 (로컬 실행 전용)"):
        st.caption("Streamlit Cloud 에서는 서버 컨테이너에 저장되므로 PC 에는 남지 않습니다. "
                   "PC 에서 `streamlit run app.py` 로 돌릴 때만 의미가 있습니다.")
        base_dir = st.text_input("저장 기준 폴더 (비우면 앱 실행 폴더)",
                                 value="", placeholder="예: ~/Documents",
                                 key="local_base_dir")
        if st.button("💾 지금 저장", use_container_width=True):
            try:
                saved = [save_to_local_folder(csv_latest, fn_latest,
                                              base_dir=base_dir or None)]
                if acc is not None and not acc.empty:
                    saved.append(save_to_local_folder(
                        to_csv_bytes(acc), build_filename(latest_data_date(acc), "누적데이터"),
                        base_dir=base_dir or None))
                st.success("저장 완료:\n\n" + "\n\n".join(f"`{p}`" for p in saved))
            except Exception as e:
                st.error(f"저장 실패: {e}")

    # ── 파일별 변환 결과 (다중 업로드 시) ──────────────────────────
    file_results = st.session_state.get("file_results")
    if file_results:
        with st.expander(f"📋 파일별 변환 결과 ({len(file_results)}개)"):
            st.dataframe(
                pd.DataFrame([{
                    "파일": r["filename"],
                    "기준일": r["quote_date"] or "-",
                    "행수": r["rows"],
                    "IV 산출": r["priced_rows"],
                    "결과": "실패: " + r["error"] if r["error"] else "정상",
                } for r in file_results]),
                use_container_width=True, hide_index=True)

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
    if st.button("🧹 작업 정리 (추출본 비우기)", use_container_width=True):
        for k in ("recent_extracted_data", "extract_stats", "file_results",
                  "accumulated_preview", "accumulated_steps",
                  "push_result", "push_error"):
            st.session_state.pop(k, None)
        st.rerun()

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
