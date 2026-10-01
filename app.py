"""EWY Quant Analytics V34 — Streamlit UI.

[V34 파일 업로드 전용 경량화 & 다중 분석 모듈 탑재] 
  · 야후 API 의존성 완전 제거 (마스터 파일 내장 주가 자체 추출)
  · 사이드바 메뉴 분기: [옵션 가격(방어벽) 분석] vs [옵션 거래량(레짐) 분석]
  · [신규] 옵션 거래량(레짐) 분석 결과 새창 열기 시 지표 설명자료(HTML) 자동 첨부
"""
from __future__ import annotations

import json
import uuid
import warnings
from datetime import datetime
import base64

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

# 신규 퀀트 모델 모듈 임포트
from volume_analysis import run_volume_analysis

warnings.filterwarnings("ignore")
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V34", page_icon="📈", layout="wide")

# =====================================================================
# [웹 UI 전용 CSS]
# =====================================================================
st.markdown("""
<style>
div[data-testid="column"] button[kind="secondary"] {
    width: 100% !important; height: 32px !important; min-height: 32px !important;
    padding: 0px !important; border-radius: 6px !important;
    border: 1px solid rgba(128, 128, 128, 0.4) !important;
    background-color: transparent !important; color: var(--text-color) !important;
}
div[data-testid="column"] button[kind="secondary"] p {
    font-size: 13px !important; margin: 0px !important; font-weight: 500 !important;
}
div[data-testid="column"] button[kind="secondary"]:hover {
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

if "quick_links" not in st.session_state:
    st.session_state["quick_links"] = load_quick_links()

def toggle_edit():
    st.session_state["edit_links_mode"] = not st.session_state["edit_links_mode"]

def remove_history_item(item_id: str) -> None:
    st.session_state["analysis_history"] = [r for r in st.session_state["analysis_history"] if r["id"] != item_id]

# 💡 신규 기능: 거래량 레짐 분석 결과에 첨부될 설명자료 HTML 정의
VOLUME_EXPLANATION_HTML = """
<div style="margin-top: 50px; padding: 25px; border: 1px solid #dcdde1; border-radius: 10px; background-color: #f5f6fa; text-align: left; line-height: 1.6;">
    <h2 style="color: #2f3640; border-bottom: 2px solid #7f8fa6; padding-bottom: 10px;">📊 지표 설명자료 (V28.4 마이크로스트럭처 엔진)</h2>
    
    <h3 style="color: #273c75; margin-top: 25px;">1. 산출 원리 (2단계 연산 구조)</h3>
    <p>코드 내부에서는 다음 두 단계를 거쳐 <strong>Put_Skew_Pct</strong>를 산출합니다.</p>
    
    <h4 style="color: #40739e;">① 원천 하방 스큐 (Put_Skew) 계산:</h4>
    <div style="background-color: #dcdde1; padding: 15px; border-radius: 6px; font-family: 'Courier New', Courier, monospace; font-size: 15px; font-weight: bold; text-align: center; margin: 15px 0;">
        Put_Skew_t = IV_{OTM Put, t} - IV_{ATM, t}
    </div>
    <ul style="color: #2f3640;">
        <li style="margin-bottom: 8px;"><strong>IV_{OTM Put} (외가격 풋옵션 IV):</strong> 현재 주가보다 5% 이상 낮은 행사가(Strike &le; Spot &times; 0.95)에 위치한 풋옵션들의 거래량 가중평균 내재변동성입니다. (급락에 베팅하거나 방어하려는 <i>'폭락 보험료'</i>)</li>
        <li><strong>IV_{ATM} (등가격 옵션 IV):</strong> 현재 주가 &plusmn; 5% 이내(0.95 &le; Strike/Spot &le; 1.05) 옵션들의 가중평균 내재변동성입니다. (시장의 <i>기본 변동성</i>)</li>
    </ul>
    <p style="background-color: #e84118; color: white; padding: 10px; border-radius: 4px; font-weight: bold;">
        💡 즉, Put_Skew가 클수록 시장 참여자들이 평상시 변동성 대비 하방 폭락 가능성에 훨씬 비싼 프리미엄(웃돈)을 지불하며 풋옵션을 사들이고 있음을 의미합니다.
    </p>
    
    <h4 style="color: #40739e; margin-top:30px;">② 60영업일 롤링 백분위 (Put_Skew_Pct) 변환:</h4>
    <p>시장의 기본 변동성 레벨은 시기마다 달라지므로 절대값만으로는 과열 여부를 판단하기 어렵습니다. 따라서 직전 <strong>60영업일(약 3개월)</strong> 동안의 Put_Skew 값들을 줄 세운 뒤, 오늘의 수치가 차지하는 순위를 백분율(0% ~ 100%)로 환산합니다.</p>
    <p style="background-color: #44bd32; color: white; padding: 10px; border-radius: 4px;">
        📌 <strong>예시:</strong> Put_Skew_Pct = 95.0%라면, 최근 60영업일 중 오늘보다 풋옵션 웃돈이 더 비쌌던 날이 단 3일(상위 5%)뿐일 정도로 <strong>하방 헤지 수요가 극에 달했다는 뜻</strong>입니다.
    </p>

    <h3 style="color: #273c75; margin-top: 50px;">2. 구간별 수치 해석 및 실전 매매 활용법</h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <tr style="background-color: #353b48; color: white;">
            <th style="border: 1px solid #7f8fa6; padding: 12px; width: 18%;">Put_Skew_Pct 구간</th>
            <th style="border: 1px solid #7f8fa6; padding: 12px; width: 35%;">시장 미시구조 상태</th>
            <th style="border: 1px solid #7f8fa6; padding: 12px; width: 47%;">주가 위치별 실전 해석 및 전략</th>
        </tr>
        <tr style="background-color: white;">
            <td style="border: 1px solid #dcdde1; padding: 12px; text-align: center;"><strong>90% ~ 100%</strong><br><span style="font-size: 0.85em; color: #c0392b; font-weight: bold;">(극단적 왜곡 / 패닉)</span></td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">딜러들의 숏 베가(Short Vega) 한계 도달.<br>대중과 기관이 가격 불문하고 OTM 풋옵션을 시장가로 쓸어 담는 보험료 폭등 상태</td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li style="margin-bottom: 6px;"><strong>급락장 바닥권 (Regime 1):</strong> 대중의 투매가 끝자락에 도달한 '진성 반등 저점' 시그널 (역발상 매수 타점)</li>
                    <li><strong>상승장 고점권:</strong> 스마트 머니가 폭락 직전 풋옵션을 선취매(Tail-risk Hedging)하는 '고점 발작 경보'</li>
                </ul>
            </td>
        </tr>
        <tr style="background-color: #f5f6fa;">
            <td style="border: 1px solid #dcdde1; padding: 12px; text-align: center;"><strong>75% ~ 89%</strong><br><span style="font-size: 0.85em; color: #e1b12c; font-weight: bold;">(하방 경계심 고조)</span></td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">OTM 풋옵션 수요가 뚜렷하게 증가하며 스큐가 가팔라지는 구간</td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>조정 구간 (DD_10 &le; -6%):</strong> 기간구조 역전(Backwardation)과 결합될 경우 Regime 1(투매 클라이막스) 진입 조건 충족</li>
                </ul>
            </td>
        </tr>
        <tr style="background-color: white;">
            <td style="border: 1px solid #dcdde1; padding: 12px; text-align: center;"><strong>25% ~ 74%</strong><br><span style="font-size: 0.85em; color: #718093; font-weight: bold;">(중립 / 평상시)</span></td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">콜옵션과 풋옵션의 수급 균형이 유지되는 일반적인 시장 상태</td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li>스큐 단독으로는 특이 시그널 없음 (거래량 및 미결제약정 증감으로 방향성 판별)</li>
                </ul>
            </td>
        </tr>
        <tr style="background-color: #f5f6fa;">
            <td style="border: 1px solid #dcdde1; padding: 12px; text-align: center;"><strong>0% ~ 24%</strong><br><span style="font-size: 0.85em; color: #4cd137; font-weight: bold;">(극단적 안도 / 과열)</span></td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">하방 보험 수요가 완전히 소멸하거나, 반대로 상방 콜옵션 수요가 몰려 분모(IV_ATM)가 커진 상태</td>
            <td style="border: 1px solid #dcdde1; padding: 12px;">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>고점 부근:</strong> 시장 참여자들이 하락 공포를 완전히 잊은 FOMO(상승 취함) 구간으로, 이때 기관의 OI 청산이 동반되면 Regime 2(고점 엑시트) 위험 급증</li>
                </ul>
            </td>
        </tr>
    </table>
</div>
"""

def generate_new_window_link(df, title, is_volume_analysis=False):
    html_content = df.to_html(index=False, justify='center')
    
    # 거래량 분석일 경우 결과표 아래에 지표 설명자료 HTML을 결합
    extra_html = VOLUME_EXPLANATION_HTML if is_volume_analysis else ""
    
    html_template = f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>{title}</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; padding: 30px; color: #333; background-color: #ffffff; max-width: 1200px; margin: auto; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ddd; padding: 12px; }}
        th {{ background-color: #2c3e50; color: white; font-weight: bold; font-size: 15px; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #f1f2f6; }}
    </style></head><body>
    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">{title}</h2>
    {html_content}
    {extra_html}
    </body></html>
    """
    b64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8').replace('\n', '')
    btn_html = f"""<a href="javascript:void(0);" onclick="var w=window.open('','_blank'); w.document.write(decodeURIComponent(escape(atob('{b64}')))); w.document.close();" class="custom-new-window-btn">↗️ 새창 열기</a>"""
    return btn_html

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
    if master_df.empty: return pd.DataFrame(), meta

    cfg = ENGINES[version]

    # 마스터 파일 내장 주가 자체 추출 (외부 API 독립)
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
    if opt_df.empty: return pd.DataFrame(), meta

    df = attach_price(opt_df, px, master_df)
    df = assign_phases(df, cfg)
    df = add_display_columns(df, cfg)
    meta["latest_date"] = df["Date"].max()
    meta["n_dates"] = len(df)
    return df, meta

def store_extraction(df_ext, stats, file_results=None) -> None:
    for k in ("extract_error_stats", "extract_error_msg", "accumulated_steps", "push_result", "push_error"):
        st.session_state.pop(k, None)
    st.session_state["recent_extracted_data"] = df_ext
    st.session_state["extract_stats"] = stats
    st.session_state["file_results"] = file_results

    if not st.session_state.get("auto_push", False): return
    try:
        current = load_master_data(st.session_state["master_version"])
        st.session_state["push_result"] = auto_update_master(current, df_ext, on_conflict="skip")
        st.session_state["master_version"] = uuid.uuid4().hex[:8]
        load_master_data.clear()
    except Exception as e:
        st.session_state["push_error"] = str(e)

def run_quant_engine(version: str, mode: str, target_date=None, target_start=None, target_end=None) -> tuple[pd.DataFrame, dict]:
    df, meta = build_full_frame(version)
    if df.empty: return pd.DataFrame(), meta
    if mode == "구간 조회" and target_start and target_end:
        sel = df[(df["Date"] >= pd.to_datetime(target_start)) & (df["Date"] <= pd.to_datetime(target_end))].copy()
    elif mode == "타임머신 (특정일)" and target_date:
        sel = df[df["Date"] <= pd.to_datetime(target_date)].tail(10).copy()
    else:
        sel = df.tail(10).copy()
    if sel.empty: return pd.DataFrame(), meta
    meta["anchor_date"] = sel["Date"].max()
    sel = sel[DISPLAY_COLS].copy()
    sel["Date"] = sel["Date"].dt.strftime("%m/%d")
    sel["Close Price"] = sel["Close Price"].round(2)
    return sel.rename(columns={"Close Price": f"{SYMBOL}($)", "Phase": "현재 시장 국면 진단"}), meta

# =====================================================================
# [상단 UI]
# =====================================================================
col_header, col_links = st.columns([0.65, 0.35])
with col_header:
    st.title(f"📈 {SYMBOL} Quant Analytics V34")
    st.markdown("**쌍방향 퀀트 엔진 & 거래량 마이크로스트럭처 분석 시스템**")

with col_links:
    h1, h2 = st.columns([0.85, 0.15])
    with h1: st.write("🔗 **Quick Links**")
    with h2: st.button("⚙️", on_click=toggle_edit, key="link_edit_btn", help="링크 편집")

    link_cols = st.columns(3)
    for i, link in enumerate(st.session_state["quick_links"][:3]):
        with link_cols[i]:
            st.markdown(
                f"<a href='{link['url']}' target='_blank' style='text-decoration:none;'>"
                f"<button style='width:100%;background-color:#FF4B4B;color:white;border:none;border-radius:4px;font-size:11px;padding:6px 2px;cursor:pointer;font-weight:bold;'>{link['name']}</button></a>",
                unsafe_allow_html=True)
    if st.session_state.get("show_link_success", False):
        st.success("✅ 링크 영구 저장 완료!")
        st.session_state["show_link_success"] = False
    if st.session_state["edit_links_mode"]:
        st.markdown("<br>", unsafe_allow_html=True)
        for i in range(3):
            c1, c2 = st.columns([0.4, 0.6])
            c1.text_input(f"이름 {i+1}", value=st.session_state["quick_links"][i]["name"], key=f"edit_name_{i}")
            c2.text_input(f"URL {i+1}", value=st.session_state["quick_links"][i]["url"], key=f"edit_url_{i}")
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
# [사이드바] 메인 메뉴 및 동적 모듈 제어
# =====================================================================
with st.sidebar:
    st.markdown("### 📌 메인 메뉴")
    main_menu = st.radio(
        "메뉴 선택",
        ["⛁ 데이터 관리", "🛡️ 옵션 가격(방어벽) 분석", "📊 옵션 거래량(레짐) 분석"],
        label_visibility="collapsed"
    )
    st.divider()

    run_button = False
    
    # ── [메뉴 1] 데이터 관리 ──────────────────────────────────────────
    if main_menu == "⛁ 데이터 관리":
        st.markdown("#### ⛁ 데이터 병합 및 관리")
        st.checkbox(f"변환 즉시 GitHub 마스터 자동 반영", value=True, key="auto_push")
        
        up_files = st.file_uploader("📁 옵션 분석데이터 (CSV/Excel) 업로드", type=["csv", "xlsx", "xls"], accept_multiple_files=True, label_visibility="collapsed")
        st.caption("로컬/코랩 환경에서 생성한 완성형 CSV 파일을 드래그 앤 드롭 하세요.")
        
        if up_files:
            st.caption(f"선택된 파일 {len(up_files)}개 — 마스터에 누적 병합됩니다.")

        if st.button("📄 업로드 파일 변환", type="primary", use_container_width=True, disabled=not up_files):
            with st.spinner(f"{len(up_files)}개 파일 파싱 및 병합 중..."):
                df_ext, file_results = extract_options_from_files(up_files)
                
            fails = [r for r in file_results if r["error"]]
            err = None if df_ext is not None else "모든 파일의 파싱이 실패했습니다."
            stats = {
                "source": "file",
                "file_count": len(up_files),
                "failed_files": [f"{r['filename']}: {r['error']}" for r in fails],
                "quote_date": (latest_data_date(df_ext) if df_ext is not None else None),
                "total_rows": 0 if df_ext is None else len(df_ext),
                "priced_rows": sum(r["priced_rows"] for r in file_results),
                "loaded_dates": sorted({str(r["quote_date"]) for r in file_results if r["quote_date"]}),
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

        if "recent_extracted_data" in st.session_state:
            if st.button("↩ 추출본 버리기 (마스터만 사용)", use_container_width=True):
                for k in ("recent_extracted_data", "extract_stats", "file_results", "push_result", "push_error"):
                    st.session_state.pop(k, None)
                st.rerun()
                
        st.caption(f"data_io: {IO_VERSION}")

    # ── [메뉴 2] 옵션 가격(방어벽) 분석 ────────────────────────────────
    elif main_menu == "🛡️ 옵션 가격(방어벽) 분석":
        st.markdown("#### 🛡️ 가격 기반 방어벽 분석")
        engine_version = st.radio("버전", list(ENGINES.keys()), label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### ◱ 분석 모드")
        mode_selection = st.selectbox("조회 방식", ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회"), label_visibility="collapsed")
        target_date = target_start = target_end = None
        if mode_selection == "타임머신 (특정일)":
            target_date = st.date_input("기준일 선택", datetime.today())
        elif mode_selection == "구간 조회":
            c1, c2 = st.columns(2)
            with c1: target_start = st.date_input("시작일", datetime(2026, 6, 1))
            with c2: target_end = st.date_input("종료일", datetime(2026, 6, 30))
            
        run_button = st.button("🚀 가격 방어벽 엔진 가동", type="primary", use_container_width=True)

    # ── [메뉴 3] 옵션 거래량(레짐) 분석 ────────────────────────────────
    elif main_menu == "📊 옵션 거래량(레짐) 분석":
        st.markdown("#### 📊 거래량 기반 레짐 분석")
        mode_selection = st.selectbox("조회 방식", ("최근 시그널 분석 (15일)", "구간 조회"), label_visibility="collapsed")
        target_date = target_start = target_end = None
        if mode_selection == "구간 조회":
            c1, c2 = st.columns(2)
            with c1: target_start = st.date_input("시작일", datetime(2026, 6, 1))
            with c2: target_end = st.date_input("종료일", datetime(2026, 6, 30))
            
        run_button = st.button("🚀 거래량 레짐 엔진 가동", type="primary", use_container_width=True)


# =====================================================================
# [결과 화면 1] 추출 완료 + 마스터 현황 (데이터 관리 메뉴일 때만 표시)
# =====================================================================
if main_menu == "⛁ 데이터 관리":
    if st.session_state.get("extract_error_stats") is not None:
        with st.expander("🩺 수집 실패 진단", expanded=True):
            st.error(st.session_state.get("extract_error_msg", "수집에 실패했습니다."))
            st.json(st.session_state["extract_error_stats"])

    if "recent_extracted_data" in st.session_state:
        df_ext = st.session_state["recent_extracted_data"]
        stats = st.session_state.get("extract_stats", {})
        st.success(f"✅ 업로드 완료 — 전체 {stats.get('total_rows', len(df_ext)):,}행 적용 완료")

        if stats.get("failed_files"):
            st.warning("변환 실패 파일:\n\n" + "\n\n".join(f"· {x}" for x in stats["failed_files"]))

        master_info = load_master_data(st.session_state["master_version"])
        rep = merge_report(master_info, df_ext)

        if rep["conflict_dates"]:
            st.warning(f"⚠️ 업로드된 날짜 **{', '.join(str(d) for d in rep['conflict_dates'])}** 가 이미 마스터에 존재합니다.")
            policy_label = st.radio("중복 날짜 처리", ("기존 기록 유지 (권장)", "새 추출본으로 통째 교체"), horizontal=True, key="policy_radio")
            st.session_state["merge_policy"] = "skip" if policy_label.startswith("기존") else "replace"
        else:
            st.session_state["merge_policy"] = "skip"
            if rep["new_dates"]:
                st.info(f"🆕 마스터에 없는 새 날짜 추가 대기 중: {', '.join(str(d) for d in rep['new_dates'])}")

        if not master_info.empty:
            start_dt = master_info["Quote Date"].min().strftime("%Y-%m-%d")
            end_dt = master_info["Quote Date"].max().strftime("%Y-%m-%d")
            st.info(f"📅 **클라우드 누적 현황:** {start_dt} ~ {end_dt} ({len(master_info):,}행)")

        st.markdown("##### 📥 다운로드 및 병합")
        data_date = latest_data_date(df_ext)
        fn_latest = build_filename(data_date, "분석데이터")
        csv_latest = to_csv_bytes(df_ext)

        dl1, dl2 = st.columns(2)
        dl1.download_button(f"📄 방금 올린 데이터 ({len(df_ext):,}행)", data=csv_latest, file_name=fn_latest, mime="text/csv", use_container_width=True)
        dl2.download_button(f"🗂 {DOWNLOAD_FOLDER} 폴더 (zip)", data=to_zip_bytes({fn_latest: csv_latest}), file_name=build_filename(data_date, "분석데이터", "zip").replace(" 분석데이터", ""), mime="application/zip", use_container_width=True)

        push_err = st.session_state.get("push_error")
        push_res = st.session_state.get("push_result")

        if push_err:
            st.error(f"자동 반영 실패: {push_err}")
        elif push_res:
            b, a = push_res["before"], push_res["after"]
            st.success(f"✅ 자동 반영 완료 — {b['rows']:,}행/{b['days']:,}일 → **{a['rows']:,}행/{a['days']:,}일** (+{push_res['added_rows']:,}행, +{push_res['added_days']}일)")
        
        policy = st.session_state["merge_policy"]
        pol_txt = "기존 유지(skip)" if policy == "skip" else "새 파일로 덮어쓰기(replace)"
        if st.button(f"🔁 지금 마스터에 반영 (정책: {pol_txt})", use_container_width=True):
            with st.spinner("마스터 병합 및 GitHub 반영 중..."):
                try:
                    st.session_state["push_result"] = auto_update_master(master_info, df_ext, on_conflict=policy)
                    st.session_state.pop("push_error", None)
                    st.session_state["master_version"] = uuid.uuid4().hex[:8]
                    load_master_data.clear()
                    st.rerun()
                except Exception as e:
                    st.session_state["push_error"] = str(e)
                    st.rerun()


# =====================================================================
# [결과 화면 2] 분석 모듈별 실행 로직
# =====================================================================
if run_button:
    
    if main_menu == "🛡️️ 옵션 가격(방어벽) 분석":
        with st.spinner(f"[{engine_version}] 가격 모델 연산 중..."):
            result_df, meta = run_quant_engine(engine_version, mode_selection, target_date, target_start, target_end)
        
        if result_df.empty:
            if meta.get("price_error"): st.error("❌ 기초자산 시세(EWY Price) 정보를 찾지 못했습니다. 마스터 파일 데이터를 확인하세요.")
            else: st.error("❌ 조회 결과가 없습니다. 마스터 데이터를 확인하세요.")
        else:
            anchor = meta.get("anchor_date")
            anchor_str = pd.to_datetime(anchor).strftime("%Y-%m-%d") if anchor is not None else "-"
            st.success(f"✅ 가격 모델 완료 ({mode_selection}) · **기준일 {anchor_str}** · 누적 {meta.get('n_dates', 0)}일")
            
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            detail = mode_selection
            if mode_selection == "타임머신 (특정일)": detail += f" ({target_date})"
            elif mode_selection == "구간 조회": detail += f" ({target_start} ~ {target_end})"

            st.session_state["analysis_history"].insert(0, {
                "id": uuid.uuid4().hex[:8],
                "title": f"📌 [{stamp}] 가격(방어벽) 엔진 - {engine_version} | {detail}",
                "data": result_df,
                "type": "price" # 식별자 추가
            })
            st.session_state["analysis_history"] = st.session_state["analysis_history"][:MAX_HISTORY]

    elif main_menu == "📊 옵션 거래량(레짐) 분석":
        with st.spinner("거래량 마이크로스트럭처 레짐 연산 중..."):
            master_df, meta = get_ready_master()
            if master_df.empty:
                st.error("❌ 마스터 데이터가 비어있습니다. [⛁ 데이터 관리] 탭에서 파일을 업로드해주세요.")
            else:
                vol_df = run_volume_analysis(master_df)
                
                if vol_df.empty:
                    st.error("❌ 거래량 모델 연산 실패 (데이터 부족)")
                else:
                    if mode_selection == "구간 조회" and target_start and target_end:
                        sel = vol_df[(vol_df["Quote Date"] >= pd.to_datetime(target_start)) & (vol_df["Quote Date"] <= pd.to_datetime(target_end))].copy()
                    else:
                        sel = vol_df.tail(15).copy()

                    if sel.empty:
                        st.warning("⚠️ 선택하신 기간에 데이터가 없습니다.")
                    else:
                        cols_to_show = ['Quote Date', 'EWY_Price', 'DD_10', 'Pos_20D', 'Backwardation_Flag', 'Put_Skew_진단', 'Regime']
                        out_df = sel[cols_to_show].copy()
                        
                        anchor = out_df["Quote Date"].max()
                        anchor_str = pd.to_datetime(anchor).strftime("%Y-%m-%d")
                        
                        out_df['Quote Date'] = out_df['Quote Date'].dt.strftime('%m-%d')
                        out_df['EWY_Price'] = out_df['EWY_Price'].round(2)
                        
                        out_df['DD_10'] = out_df['DD_10'].replace([np.inf, -np.inf], np.nan).fillna(0.0).round(1).astype(str) + '%'
                        out_df['Pos_20D'] = (out_df['Pos_20D'].replace([np.inf, -np.inf], np.nan).fillna(0.5) * 100).round(0).astype(int).astype(str) + '%'
                        
                        out_df = out_df.rename(columns={'Quote Date': 'Date', 'EWY_Price': f'{SYMBOL}($)', 'Backwardation_Flag': 'Backward(역조)'})

                        st.success(f"✅ 거래량 레짐 모델 완료 ({mode_selection}) · **기준일 {anchor_str}**")

                        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        detail = mode_selection
                        if mode_selection == "구간 조회": detail += f" ({target_start} ~ {target_end})"

                        st.session_state["analysis_history"].insert(0, {
                            "id": uuid.uuid4().hex[:8],
                            "title": f"📊 [{stamp}] 거래량(레짐) 엔진 - V28.4 | {detail}",
                            "data": out_df,
                            "type": "volume" # 식별자 추가
                        })
                        st.session_state["analysis_history"] = st.session_state["analysis_history"][:MAX_HISTORY]


# =====================================================================
# [결과 화면 3] 히스토리 (메뉴 상관없이 항상 하단에 노출)
# =====================================================================
if st.session_state["analysis_history"]:
    st.divider()
    st.header(f"🗂️ 분석 결과 비교 히스토리 (최근 {MAX_HISTORY}건)")
    for record in st.session_state["analysis_history"]:
        with st.container():
            st.markdown(f"**{record['title']}**")
            _, btn_col1, btn_col2 = st.columns([8, 1, 1])
            with btn_col1:
                # 레짐 분석 결과일 경우에만 설명자료 HTML 첨부 옵션 활성화
                is_vol = record.get("type") == "volume"
                st.markdown(generate_new_window_link(record['data'], record['title'], is_volume_analysis=is_vol), unsafe_allow_html=True)
            with btn_col2:
                st.button("❌ 삭제", key=f"del_{record['id']}", on_click=remove_history_item, args=(record["id"],), use_container_width=True)
            st.dataframe(record["data"], use_container_width=True, hide_index=True)
            st.write("")