"""EWY Quant Analytics V34 — Streamlit UI (휴대폰·PC 공용)

[데이터 직접 수집 · 깃허브 누적 관리 · 분석 엔진 V4.3.7 통합]
  · ⛁ 데이터 관리: 옵션 데이터를 앱이 야후에서 직접 받아 깃허브 저장소(data/)에 누적 — 매일 아침은 깃허브가 자동 수집
                   (CSV 올리기는 코랩 등에서 만든 파일을 넣을 때만)
  · 🛡️ 옵션 가격(방어벽) 분석 · 📊 옵션 거래량(레짐) 분석: V34 계산 그대로
  · 🧠 분석 엔진 V4.3.7: 프롬프트(데이터북) · 3분할 · 표 뷰어 · 최종 보고서 (결과는 깃허브 reports/ 에 보관)
  · 📋 신호 기록·채점: 엔진이 기록·채점한 EWY_신호기록_채점.csv를 깃허브에서 관리
"""
from __future__ import annotations

import base64
import html
import json
import os
import time
import uuid
import warnings
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import streamlit as st

import market
import quant
import storage
from config import ENGINES, MAX_HISTORY, SYMBOL

warnings.filterwarnings("ignore")
os.environ["TZ"] = "KST-9"          # 한국 시각 (스트림잇 서버는 UTC) — 분석 엔진의 파일 이름·보고서 시각도 PC와 같게
if hasattr(time, "tzset"):
    time.tzset()
st.set_page_config(page_title=f"{SYMBOL} Quant Analytics V34", page_icon="📈", layout="wide")

# =====================================================================
# [웹 UI 전용 CSS] - 다크모드 고대비 가독성 테이블 (원본 그대로) + 휴대폰 여백
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
    width: 100%; max-height: 500px; overflow-x: auto; overflow-y: auto;
    border: 1px solid #2E3A4E; border-radius: 8px;
    background-color: #0F151E;
    margin-top: 6px; margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.quant-table {
    width: 100%; border-collapse: collapse; font-size: 13.5px;
    text-align: center; white-space: nowrap; color: #F1F5F9;
}
.quant-table thead th {
    position: sticky; top: 0; z-index: 2;
    background: linear-gradient(180deg, #243044 0%, #1B2536 100%) !important;
    color: #FFFFFF !important; font-weight: 700; font-size: 13.5px;
    padding: 11px 14px; letter-spacing: 0.2px;
    border-bottom: 2px solid #3B4C66;
    border-right: 1px solid #2E3A4E;
}
.quant-table tbody tr:nth-child(odd) { background-color: #0F151E; }
.quant-table tbody tr:nth-child(even) { background-color: #151D2A; }
.quant-table tbody td {
    padding: 10px 14px; color: #F1F5F9 !important; font-weight: 500;
    border-bottom: 1px solid #232E3F;
    border-right: 1px solid #1E2736;
}
.quant-table tbody td:first-child,
.quant-table tbody td:nth-child(2) { color: #FFFFFF !important; font-weight: 600; }
.quant-table tbody tr:hover { background-color: #212E42 !important; }
@media (max-width: 640px) {
    .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 2.6rem !important; }
    .quant-table { font-size: 12.5px; }
    .quant-table thead th, .quant-table tbody td { padding: 8px 9px; }
    h1 { font-size: 1.6rem !important; }
}
</style>
""", unsafe_allow_html=True)


# =====================================================================
# [저장소] 깃허브(스트림잇 secrets) 또는 이 폴더
# =====================================================================
@st.cache_resource(show_spinner=False)
def get_store():
    secrets = {}
    try:
        for k in ("GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_BRANCH"):
            if k in st.secrets:
                secrets[k] = str(st.secrets[k])
    except Exception:
        pass
    return storage.open_store(secrets)


try:
    STORE = get_store()
except Exception as e:
    st.error(f"❌ 깃허브 저장소에 연결하지 못했습니다: {type(e).__name__}: {e}\n\n"
             "스트림잇 Settings → Secrets의 GITHUB_TOKEN · GITHUB_REPO를 확인하세요.")
    st.stop()


def _tup(e):
    return None if e is None else (e.name, e.path, e.sha, e.size)


def _ent(t):
    return None if t is None else storage.Entry(*t)


@st.cache_data(ttl=60, show_spinner=False)
def get_sources(_store, bust):
    base, daily, legacy = storage.master_sources(_store)
    return _tup(base), [_tup(e) for e in daily], _tup(legacy)


@st.cache_resource(max_entries=2, show_spinner=False)
def get_master(_store, key, base_t, daily_t, legacy_t):
    m, stats = storage.load_master(_store, _ent(base_t), [_ent(t) for t in daily_t], _ent(legacy_t))
    dates = sorted(m["Quote Date"].dt.strftime("%Y-%m-%d").unique().tolist())
    return m, stats, dates


@st.cache_resource(max_entries=2, show_spinner=False)
def get_price_base(key, _m):
    return quant.price_base(_m)


@st.cache_resource(max_entries=2, show_spinner=False)
def get_volume(key, _m):
    return quant.volume_frame(_m)


@st.cache_resource(max_entries=1, show_spinner=False)
def get_master_download(key, _m, name):
    """마스터 전체를 CSV 한 개가 든 zip으로 (윈도우·휴대폰에서 바로 풀림)"""
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr(name, storage.csv_bytes(storage.to_csv_frame(_m)))
    return buf.getvalue()


@st.cache_data(ttl=60, show_spinner=False)
def get_signal_bytes(_store, bust, path=None):
    return storage.read_signal(_store, path)


@st.cache_data(ttl=60, show_spinner=False)
def get_signal_files(_store, bust):
    return storage.signal_files(_store)


@st.cache_data(ttl=120, show_spinner=False)
def get_report_items(_store, bust):
    """보관함의 프롬프트·최종 보고서 전부 (새것 먼저) — 저장소 트리를 한 번에 읽음"""
    return storage.report_items(_store)


@st.cache_data(max_entries=6, show_spinner=False)
def get_report_bytes(_store, path, sha):
    return _store.read(path, sha=sha)


@st.cache_data(ttl=300, show_spinner=False)
def get_engines(_store, bust):
    import engine_service
    return engine_service.list_engines(_store)


def bump(*what):
    """저장한 뒤 다시 읽게 함"""
    st.session_state["bust"] = st.session_state.get("bust", 0) + 1
    if "data" in what:
        get_sources.clear()
    if "signal" in what:
        get_signal_bytes.clear()
        get_signal_files.clear()
    if "reports" in what:
        get_report_items.clear()
    if "engines" in what:
        get_engines.clear()


def load_data():
    """(마스터, 요약, 날짜 목록, 데이터 키) — 저장소가 비었으면 (None, None, [], None)"""
    base_t, daily_t, legacy_t = get_sources(STORE, st.session_state.get("bust", 0))
    if base_t is None and not daily_t and legacy_t is None:
        return None, None, [], None
    key = storage.sources_key(_ent(base_t), [_ent(t) for t in daily_t], _ent(legacy_t))
    m, stats, dates = get_master(STORE, key, base_t, tuple(daily_t), legacy_t)
    return m, stats, dates, key


# =====================================================================
# [퀵링크] 저장소의 quick_links.json
# =====================================================================
DEFAULT_LINKS = [
    {"name": "Google Finance", "url": "https://www.google.com/finance"},
    {"name": "CME FedWatch", "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"},
    {"name": "TradingView", "url": "https://kr.tradingview.com/"},
]


def load_quick_links():
    try:
        raw = STORE.read("quick_links.json")
        links = json.loads(raw.decode("utf-8")) if raw else None
        if isinstance(links, list) and links:
            return (links + DEFAULT_LINKS)[:3]
    except Exception:
        pass
    return [dict(x) for x in DEFAULT_LINKS]


def save_quick_links(links):
    try:
        STORE.write("quick_links.json", json.dumps(links, ensure_ascii=False, indent=2).encode("utf-8"), "Update quick links")
        return True
    except Exception as e:
        st.error(f"링크 저장 오류: {e}")
        return False


# =====================================================================
# [세션 상태 관리]
# =====================================================================
st.session_state.setdefault("analysis_history", [])
st.session_state.setdefault("edit_links_mode", False)
st.session_state.setdefault("show_vol_explanation", True)
st.session_state.setdefault("bust", 0)
if "quick_links" not in st.session_state:
    st.session_state["quick_links"] = load_quick_links()


def toggle_edit():
    st.session_state["edit_links_mode"] = not st.session_state.get("edit_links_mode", False)


def remove_history_item(item_id: str) -> None:
    st.session_state["analysis_history"] = [r for r in st.session_state["analysis_history"] if r["id"] != item_id]


def hide_vol_explanation():
    st.session_state["show_vol_explanation"] = False


# =====================================================================
# [지표 설명자료 MD] — 스큐 산출 설명은 거래량 엔진 V35.0 코드에 맞춤
# =====================================================================
VOLUME_EXPLANATION_MD = """
#### 1. 산출 원리 (2단계 연산 구조)
코드 내부에서는 다음 두 단계를 거쳐 **Put_Skew_Pct**를 산출합니다.

**① 원천 하방 스큐 (Put_Skew) 계산:**
> **Put_Skew_t = IV_{25Δ Put, t} - IV_{ATM, t}**

* **IV_{25Δ Put} (25-델타 풋옵션 IV):** 만기 14~90일 옵션 가운데 델타 -0.15 ~ -0.35 풋옵션들의 유동성 가중평균 내재변동성입니다(가중치 = 미결제약정 + 거래량×5). 그런 풋이 없으면 현재 주가의 88~96% 행사가 풋으로 대신합니다. (급락에 베팅하거나 방어하려는 *'폭락 보험료'*)
* **IV_{ATM} (등가격 옵션 IV):** 같은 만기 구간에서 현재 주가 ±3.5% 이내 옵션들의 유동성 가중평균 내재변동성입니다. (시장의 *기본 변동성*)

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

---

#### 3. 표의 열
* **DD_10**: 최근 10거래일 최고가 대비 하락률
* **Pos_20D**: 최근 20거래일 최저~최고 범위 안에서 오늘 종가의 위치 (0% = 최저, 100% = 최고)
* **Backward(역조)**: 근월(만기 2~21일) 등가격 IV가 원월(35~120일)보다 0.5%p 넘게 높으면 1.0 (기간구조 역전)
* **Put_Skew_진단**: Put_Skew_Pct와 최근 3일 ΔOI×ΔIV 4분면 수급 (P롱 = 풋 미결제 증가+IV 상승, P벙커 = 풋 미결제 증가+IV 하락·보합, C롱 = 콜 미결제 증가+IV 상승)
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
        cells = "".join(f"<td>{'' if pd.isna(v) else html.escape(str(v))}</td>" for v in row)
        rows_html.append(f"<tr>{cells}</tr>")
    st.markdown(f'<div class="quant-table-wrapper"><table class="quant-table"><thead><tr>{headers}</tr></thead>'
                f'<tbody>{"".join(rows_html)}</tbody></table></div>', unsafe_allow_html=True)


def copy_button(text: str, label: str, key: str) -> None:
    """휴대폰에서도 되는 [복사] 버튼 (클립보드 API, 안 되면 예전 방식)"""
    import streamlit.components.v1 as components
    payload = json.dumps(text, ensure_ascii=False).replace("</", "<\\/")
    components.html(f"""
<div style="font-family:sans-serif">
<button id="b" style="background:#FF4B4B;color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:14px;font-weight:600;cursor:pointer">{html.escape(label)}</button>
<span id="m" style="font-size:13px;margin-left:8px;color:#888"></span></div>
<script>
const t = {payload};
document.getElementById('b').onclick = async () => {{
  let ok = false;
  try {{ await navigator.clipboard.writeText(t); ok = true; }} catch (e) {{}}
  if (!ok) {{
    const ta = document.createElement('textarea'); ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.focus(); ta.select();
    try {{ ok = document.execCommand('copy'); }} catch (e) {{}}
    ta.remove();
  }}
  document.getElementById('m').textContent = ok ? '복사했습니다 (' + t.length.toLocaleString() + '자)' : '복사하지 못했습니다 — 내려받기를 쓰세요';
}};
</script>""", height=52)


def convert_uploads(files):
    """올린 파일 -> (수집기 CSV 형식 DataFrame, 파일별 결과)
    · 수집기·코랩이 만든 CSV(열 이름이 같음)는 그대로 읽음 — 여러 날짜가 든 마스터통합데이터 CSV도 모든 날짜를 넣음
    · 그 밖의 파일(다른 형식 CSV · 엑셀)은 V34의 변환 방식(data_io)으로 하루치씩 변환
    · 같은 날짜가 여러 파일에 있으면 나중에 고른 파일이 그 날짜를 통째로 대신함"""
    from data_io import extract_options_from_files
    frames, results, others = [], [], []
    std_cols = storage.NEEDED + ("Implied Volatility", "Delta")
    for f in files:
        df = None
        if f.name.lower().endswith(".csv"):
            try:
                df = storage._read_csv_bytes(f.getvalue())
            except Exception:
                df = None
        if df is not None and all(c in df.columns for c in std_cols):
            frames.append((f.name, df))
            n = pd.to_datetime(df["Quote Date"].astype(str).str.strip(), errors="coerce", format="mixed").nunique()
            results.append({"filename": f.name, "rows": int(len(df)), "days": int(n), "error": None})
        else:
            others.append(f)
    if others:
        d, r = extract_options_from_files(others)
        results += r
        if d is not None and not d.empty:
            frames.append(("변환한 파일", d))
    if not frames:
        return None, results
    try:
        m, _ = storage.build_master(frames)
    except storage.StoreError as e:
        results.append({"filename": "(합치기)", "error": str(e)})
        return None, results
    return storage.to_csv_frame(m), results


def now_kst():
    """한국 시각 (스트림잇 서버는 UTC)"""
    return datetime.now(timezone(timedelta(hours=9)))


def date_default(dates, back=0):
    if not dates:
        return datetime.today().date()
    d = pd.Timestamp(dates[-1]) - pd.Timedelta(days=back)
    return max(d, pd.Timestamp(dates[0])).date()


# =====================================================================
# [상단 UI]
# =====================================================================
col_header, col_links = st.columns([0.65, 0.35])
with col_header:
    st.title(f"📈 {SYMBOL} Quant Analytics V34")
    st.markdown("**쌍방향 퀀트 엔진 & 거래량 마이크로스트럭처 분석 시스템**")

with col_links:
    h1, h2 = st.columns([0.85, 0.15])
    with h1:
        st.write("🔗 **Quick Links**")
    with h2:
        st.button("⚙️", on_click=toggle_edit, key="link_edit_btn", help="링크 편집")
    link_cols = st.columns(3)
    for i, link in enumerate(st.session_state["quick_links"][:3]):
        with link_cols[i]:
            btn_style = ("width:100%;background-color:#FF4B4B;color:white;border:none;"
                         "border-radius:4px;font-size:11px;padding:6px 2px;cursor:pointer;font-weight:bold;")
            st.markdown(f"<a href='{html.escape(link['url'], quote=True)}' target='_blank' style='text-decoration:none;'>"
                        f"<button style='{btn_style}'>{html.escape(link['name'])}</button></a>", unsafe_allow_html=True)
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
            new = [{"name": st.session_state[f"edit_name_{i}"].strip(), "url": st.session_state[f"edit_url_{i}"].strip()}
                   for i in range(3)]
            if any(not x["url"].lower().startswith(("http://", "https://")) for x in new):
                st.error("주소는 http:// 또는 https:// 로 시작해야 합니다.")
            else:
                with st.spinner("저장소에 링크 설정 저장 중..."):
                    st.session_state["quick_links"] = new
                    save_quick_links(new)
                    st.session_state["edit_links_mode"] = False
                    st.session_state["show_link_success"] = True
                st.rerun()

st.divider()

# =====================================================================
# [데이터] 저장소에서 마스터 읽기
# =====================================================================
try:
    with st.spinner("옵션 데이터를 불러오는 중..."):
        MASTER, STATS, DATES, DKEY = load_data()
except Exception as e:
    MASTER, STATS, DATES, DKEY = None, None, [], None
    st.error(f"❌ 옵션 데이터를 읽지 못했습니다: {type(e).__name__}: {e}")

# =====================================================================
# [사이드바] 메인 메뉴
# =====================================================================
MENU_DATA = "⛁ 데이터 관리"
MENU_PRICE = "🛡️ 옵션 가격(방어벽) 분석"
MENU_VOL = "📊 옵션 거래량(레짐) 분석"
MENU_ENGINE = "🧠 분석 엔진"
MENU_ARCHIVE = "🗂 분석 보고서 보관함"
MENU_SIGNAL = "📋 신호 기록·채점"
MENUS = [MENU_DATA, MENU_PRICE, MENU_VOL, MENU_ENGINE, MENU_ARCHIVE, MENU_SIGNAL]
if st.session_state.get("main_menu") not in MENUS:          # 예전 메뉴 이름이 남아 있으면 처음으로
    st.session_state.pop("main_menu", None)
ENGINES_LIST, SEL_ENGINE = [], None

with st.sidebar:
    st.markdown("### 📌 메인 메뉴")
    main_menu = st.radio("메뉴 선택", MENUS, label_visibility="collapsed", key="main_menu")
    st.divider()
    run_button = collect_button = engine_button = False

    if main_menu == MENU_DATA:
        st.markdown("#### ⛁ 데이터 수집 및 관리")
        collect_button = st.button("📥 지금 수집 (야후에서 직접)", type="primary", use_container_width=True)
        st.checkbox("같은 날짜 파일도 다시 받기", value=False, key="collect_overwrite")
        st.caption("매일 한국시간 화~토 아침 07:30쯤 깃허브가 자동으로 받아 쌓습니다. 이 버튼은 바로 받고 싶을 때 씁니다 (1~3분).")
        st.divider()
        st.markdown("##### 📁 CSV로 넣기 (코랩 등)")
        raw_files = st.file_uploader(
            "📁 옵션 분석데이터 (CSV/Excel) 업로드",
            type=["csv", "xlsx", "xls", "pdf", "txt", "doc", "zip"],
            accept_multiple_files=True, label_visibility="collapsed",
            help="안드로이드 '내 파일' 강제 호출을 위해 pdf, txt가 목록에 열려있습니다. 실제로는 CSV/Excel 데이터만 선택해주세요.")
        st.caption("야후 수집이 막힌 날 코랩에서 만든 CSV를 넣을 때 씁니다.")
        up_files = [f for f in (raw_files or []) if f.name.lower().endswith((".csv", ".xls", ".xlsx"))]
        bad_files = [f.name for f in (raw_files or []) if f not in up_files]
        if bad_files:
            st.error(f"❌ 지원되지 않는 파일 포맷 제외됨: {', '.join(bad_files)}")
        if st.button("📄 업로드 파일 변환", use_container_width=True, disabled=not up_files):
            with st.spinner(f"{len(up_files)}개 파일 읽는 중..."):
                df_ext, file_results = convert_uploads(up_files)
            st.session_state["upload"] = {"df": df_ext, "results": file_results, "names": [f.name for f in up_files]}
            st.rerun()

    elif main_menu == MENU_PRICE:
        st.markdown("#### 🛡️ 가격 기반 방어벽 분석")
        engine_version = st.radio("버전", list(ENGINES.keys()), label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ◱ 분석 모드")
        mode_selection = st.selectbox("조회 방식", quant.PRICE_MODES, label_visibility="collapsed", key="mode_price")
        target_date = target_start = target_end = None
        if mode_selection == "타임머신 (특정일)":
            target_date = st.date_input("기준일 선택", date_default(DATES), key="date_price")
        elif mode_selection == "구간 조회":
            c1, c2 = st.columns(2)
            with c1:
                target_start = st.date_input("시작일", date_default(DATES, 30), key="start_price")
            with c2:
                target_end = st.date_input("종료일", date_default(DATES), key="end_price")
        run_button = st.button("🚀 가격 방어벽 엔진 가동", type="primary", use_container_width=True)

    elif main_menu == MENU_VOL:
        st.markdown("#### 📊 거래량 기반 레짐 분석")
        mode_selection = st.selectbox("조회 방식", quant.VOLUME_MODES, label_visibility="collapsed", key="mode_vol")
        target_date = target_start = target_end = None
        if mode_selection == "구간 조회":
            c1, c2 = st.columns(2)
            with c1:
                target_start = st.date_input("시작일", date_default(DATES, 30), key="start_vol")
            with c2:
                target_end = st.date_input("종료일", date_default(DATES), key="end_vol")
        run_button = st.button("🚀 거래량 레짐 엔진 가동", type="primary", use_container_width=True)

    elif main_menu == MENU_ENGINE:
        import engine_service
        st.markdown("#### 🧠 분석 엔진")
        try:
            ENGINES_LIST = get_engines(STORE, st.session_state.get("bust", 0))
        except Exception as e:
            st.error(f"엔진 목록을 읽지 못했습니다: {type(e).__name__}: {e}")
        eng_by_path = {x["path"]: x for x in ENGINES_LIST}
        if st.session_state.get("eng_pick_next") in eng_by_path:     # 방금 추가한 엔진을 고른 상태로
            st.session_state["eng_pick"] = st.session_state.pop("eng_pick_next")
        if st.session_state.get("eng_pick") not in eng_by_path:
            st.session_state.pop("eng_pick", None)
        if eng_by_path:
            eng_pick = st.selectbox("엔진 버전", list(eng_by_path), key="eng_pick",
                                    format_func=lambda p_: engine_service.engine_label(eng_by_path[p_], ENGINES_LIST))
            SEL_ENGINE = eng_by_path[eng_pick]
            st.caption(engine_service.SIGNAL_TEXT.get(SEL_ENGINE["signal_mode"], ""))
        else:
            st.warning("저장소 engine/ 폴더에 분석 엔진 파일이 없습니다.")
        tier = st.selectbox("분석 창", [t for t, _ in engine_service.TIERS],
                            format_func=lambda t: dict(engine_service.TIERS)[t], key="eng_tier")
        date_mode = st.radio("기준일", ["최신 기준일", "날짜 지정"], horizontal=True, key="eng_date_mode")
        eng_date = None
        if date_mode == "날짜 지정":
            eng_date = st.date_input("기준일 선택", date_default(DATES), key="eng_date")
        fmt = st.radio("보고서 형식", ["3분할 (휴대폰 권장)", "PC (데이터북 1개)"], key="eng_fmt")
        binance = st.checkbox("바이낸스 EWYBUSDT 1시간봉 동시 회귀", value=True, key="eng_binance")
        engine_button = st.button("🚀 분석 실행", type="primary", use_container_width=True,
                                  disabled=MASTER is None or not (SEL_ENGINE and SEL_ENGINE["ok"]))
        st.caption("한 번에 1~3분 걸립니다. 프롬프트와 최종 보고서는 깃허브 reports/ 에 쌓여 🗂 분석 보고서 보관함에서 언제든 봅니다.")

    elif main_menu == MENU_ARCHIVE:
        st.markdown("#### 🗂 분석 보고서 보관함")
        st.caption("최종 보고서를 엔진 버전·Tier별로 골라 봅니다. 오래된 보고서와 프롬프트는 '보고서 정리' 탭에서 골라 지웁니다.")

    elif main_menu == MENU_SIGNAL:
        st.markdown("#### 📋 신호 기록·채점")
        st.caption("분석 엔진을 실행할 때마다 기준일·Tier별 신호를 기록하고, 다음 거래일 결과로 자동 채점합니다.")

    st.caption(f"저장소: {STORE.label()}")


# =====================================================================
# [결과 화면 1] 데이터 관리 — 수집 · 현황 · CSV 넣기
# =====================================================================
def show_collect_result(r):
    status = r.get("status")
    facts = []
    if r.get("quote_date"):
        facts.append(f"기준일 **{r['quote_date']}**")
    if r.get("contracts"):
        facts.append(f"계약 {int(r['contracts']):,}개")
    if r.get("expirations"):
        facts.append(f"만기 {r['expirations']}")
    if r.get("valid_iv") is not None:
        facts.append(f"유효 IV {float(r['valid_iv']):.1%}")
    if r.get("sofr"):
        facts.append(f"SOFR {r['sofr']}%")
    line = " · ".join(facts)
    text = f"{r.get('title', '')}" + (f" — {line}" if line else "") + (f"\n\n{r['message']}" if r.get("message") else "")
    if status == "ok":
        st.success("✅ " + text + "\n\n다음 분석부터 이 데이터가 들어갑니다.")
    elif status in ("skipped", "busy", "cancelled"):
        st.info("ℹ️ " + text)
    elif status == "invalid":
        st.warning("⚠️ " + text)
        if r.get("invalid_bytes"):
            st.download_button("📄 받은 데이터 내려받기 (검증실패)", r["invalid_bytes"], file_name=r.get("name", "검증실패.csv"),
                               mime="text/csv")
    else:
        st.error("❌ " + text)


def pending_days():
    """(장 마감 기준 마지막 거래일, 아직 받지 않은 거래일 목록)"""
    expected = market.last_closed_trading_day()
    if MASTER is None:
        return expected, [expected]
    return expected, market.trading_days_after(STATS["end"], expected)


def data_overview(expected, pending):
    if MASTER is None:
        st.warning("⚠️ 저장소에 옵션 데이터가 없습니다. 위 [📥 지금 받기]를 누르거나 data/master_base.csv.gz를 저장소에 올리세요.")
        return
    s = STATS
    missing = market.missing_trading_days(DATES, 120)
    if not pending:
        st.success(f"✅ 최신 데이터 **{s['end']}** — 미국 장 마감 기준 마지막 거래일({expected})까지 들어 있습니다.")
    else:
        msg = (f"📥 **{pending[-1]}** 데이터를 아직 받지 않았습니다. 위 [📥 지금 받기]를 누르거나, "
               "아침 자동 수집(한국시간 화~토 07:30쯤)을 기다리세요.")
        if len(pending) > 1:
            msg += (f" 그 앞의 {len(pending) - 1}거래일({', '.join(d[5:] for d in pending[:-1])})은 야후가 지난 날짜의 옵션 "
                    "데이터를 주지 않아 받을 수 없습니다.")
        st.info(msg)
    if missing:
        st.warning(f"⚠️ 최근 120일 중 데이터가 없는 거래일 {len(missing)}일: {', '.join(d[5:] for d in missing[-20:])} "
                   "— 이 날은 건너뛰고 계산합니다.")
    c1, c2, c3 = st.columns(3)
    c1.metric("최신 데이터", s["end"])
    c2.metric("누적 거래일", f"{s['days']:,}일")
    c3.metric("누적 행", f"{s['rows']:,}")
    st.info(f"📅 **누적 현황:** {s['start']} ~ {s['end']} ({s['rows']:,}행 · {s['days']:,}거래일)")
    base_t, daily_t, legacy_t = get_sources(STORE, st.session_state.get("bust", 0))
    with st.expander("🗂 저장소 파일 보기"):
        st.markdown(f"- 마스터: `{base_t[1] if base_t else (legacy_t[1] + ' (V34 마스터)' if legacy_t else '없음')}`"
                    + (f" · {base_t[3] / 1048576:.1f}MB" if base_t else ""))
        st.markdown(f"- 날짜별 파일 {len(daily_t)}개 (마스터 이후에 받은 날짜 · {storage.COMPACT_AFTER}개가 넘으면 자동 수집이 마스터에 합침)")
        if daily_t:
            st.dataframe(pd.DataFrame([{"파일": t[0], "크기(KB)": round(t[3] / 1024)} for t in daily_t[::-1]]),
                         hide_index=True, use_container_width=True)
        if s.get("replaced"):
            st.caption(f"날짜별 파일이 마스터의 같은 날짜를 대신한 행: {s['replaced']:,}")
        if s.get("skipped"):
            st.caption("건너뛴 파일: " + ", ".join(x["name"] for x in s["skipped"]))
    st.markdown("##### 📥 내려받기")
    d1, d2 = st.columns(2)
    if daily_t:
        last = daily_t[-1]
        if d1.button(f"📄 최근 수집본 ({last[0][-12:-4]})", use_container_width=True):
            st.session_state["dl_daily"] = (last[0], STORE.read(last[1], sha=last[2]))
        if st.session_state.get("dl_daily"):
            n, data = st.session_state["dl_daily"]
            d1.download_button(f"⬇️ {n}", data, file_name=n, mime="text/csv", use_container_width=True)
    if d2.button("🗂 마스터통합데이터 만들기 (zip)", use_container_width=True):
        st.session_state["dl_master"] = DKEY
    if st.session_state.get("dl_master") == DKEY:
        stem = f"마스터통합데이터_{s['end'].replace('-', '')}"
        with st.spinner("마스터 전체를 CSV로 묶는 중..."):
            data = get_master_download(DKEY, MASTER, stem + ".csv")
        d2.download_button(f"⬇️ {stem}.zip ({len(data) / 1048576:.1f}MB)", data, file_name=stem + ".zip",
                           mime="application/zip", use_container_width=True)
        d2.caption("압축을 풀면 PC 분석 엔진에 그대로 넣을 수 있는 CSV 한 개가 나옵니다.")


def upload_panel():
    up = st.session_state.get("upload")
    if not up:
        return
    df_ext, results = up["df"], up["results"]
    fails = [r for r in results if r.get("error")]
    st.markdown("##### 📁 올린 파일")
    if fails:
        st.warning("변환 실패 파일:\n\n" + "\n\n".join(f"· {r['filename']}: {r['error']}" for r in fails))
    if df_ext is None or df_ext.empty:
        st.error("❌ 모든 파일의 변환이 실패했습니다.")
        if st.button("닫기"):
            st.session_state.pop("upload", None)
            st.rerun()
        return
    up_dates = sorted(df_ext["Quote Date"].astype(str).unique().tolist())
    have = set(DATES)
    dup = [d for d in up_dates if d in have]
    new = [d for d in up_dates if d not in have]
    st.success(f"✅ 변환 완료 — {len(df_ext):,}행 · {len(up_dates)}거래일 ({up_dates[0]} ~ {up_dates[-1]})")
    if new:
        st.info(f"🆕 새 날짜 {len(new)}일: {', '.join(new[:12])}{' …' if len(new) > 12 else ''}")
    policy = "skip"
    if dup:
        st.warning(f"⚠️ 이미 있는 날짜 {len(dup)}일: {', '.join(dup[:12])}{' …' if len(dup) > 12 else ''}")
        label = st.radio("중복 날짜 처리", ("기존 기록 유지 (권장)", "새 파일로 통째 교체"), horizontal=True, key="policy_radio")
        policy = "skip" if label.startswith("기존") else "replace"
    save_dates = new + (dup if policy == "replace" else [])
    many = len(save_dates) > 5
    if many:
        st.caption(f"{len(save_dates)}일이라 날짜별 파일 대신 마스터에 바로 합쳐 저장합니다 (몇십 초 걸림).")
    c1, c2 = st.columns(2)
    if c1.button(f"💾 저장소에 저장 ({len(save_dates)}일)", type="primary", use_container_width=True, disabled=not save_dates):
        saved = False
        with st.spinner("저장소에 저장 중..."):
            try:
                frame = df_ext[df_ext["Quote Date"].isin(save_dates)]
                if not many:
                    for d in save_dates:
                        storage.save_daily(STORE, storage.daily_name(d), storage.csv_bytes(frame[frame["Quote Date"] == d]),
                                           f"CSV 올리기 {d}")
                else:
                    cur = storage.to_csv_frame(MASTER) if MASTER is not None else pd.DataFrame(columns=storage.CSV_COLS)
                    merged, _ = storage.build_master([("current", cur), ("upload", frame)])
                    STORE.write(storage.BASE_PATH, storage.csv_bytes(storage.to_csv_frame(merged), gz=True),
                                f"CSV 올리기: {len(save_dates)}일 마스터에 합침")
                    for t in get_sources(STORE, st.session_state.get("bust", 0))[1]:
                        STORE.delete(t[1], f"마스터에 합침: {t[0]}")
                saved = True
            except Exception as e:
                st.error(f"저장 실패: {type(e).__name__}: {e}")
        if saved:
            st.session_state["upload_msg"] = f"✅ {len(save_dates)}거래일을 저장소에 저장했습니다."
            st.session_state.pop("upload", None)
            bump("data")
            st.rerun()
    if c2.button("↩ 올린 파일 버리기", use_container_width=True):
        st.session_state.pop("upload", None)
        st.rerun()


if main_menu == MENU_DATA:
    EXPECTED, PENDING = pending_days()
    if PENDING and not collect_button and not st.session_state.get("collect_result"):
        if st.button(f"📥 {PENDING[-1]} 데이터 지금 받기", type="primary", use_container_width=True, key="collect_main"):
            collect_button = True
    if collect_button:
        import collect_service
        prog = st.progress(0.0, text="수집 준비 중…")
        with st.status("야후에서 옵션 데이터 받는 중…", expanded=False) as box:
            lines = []

            def _log(m):
                lines.append(m)
                if any(k in m for k in ("[1/5]", "[2/5]", "[3/5]", "[4/5]", "[5/5]", "[저장]", "[중단]", "[건너뜀]", "[오류]")):
                    box.write(m.strip())

            def _prog(stage, frac, text):
                prog.progress(min(1.0, ((stage - 1) + frac) / 6), text=text)

            res = collect_service.run_collect(STORE, overwrite=st.session_state.get("collect_overwrite", False),
                                              progress=_prog, log=_log)
            box.update(label=res.get("title", "끝"), state="complete" if res.get("status") in ("ok", "skipped") else "error")
        res = {k: v for k, v in res.items() if k != "csv_bytes"}
        st.session_state["collect_result"] = res
        if res.get("status") == "ok":
            bump("data")
        st.rerun()
    if st.session_state.get("collect_result"):
        show_collect_result(st.session_state["collect_result"])
        if st.button("✖ 수집 결과 닫기", key="close_collect"):
            st.session_state.pop("collect_result", None)
            st.rerun()
    if st.session_state.get("upload_msg"):
        st.success(st.session_state.pop("upload_msg"))
    upload_panel()
    data_overview(EXPECTED, PENDING)

# =====================================================================
# [결과 화면 2] 가격 · 거래량 분석 (V34)
# =====================================================================
if run_button:
    if MASTER is None:
        st.error("❌ 마스터 데이터가 비어있습니다. [⛁ 데이터 관리]에서 데이터를 수집하세요.")
    elif main_menu == MENU_PRICE:
        with st.spinner(f"[{engine_version}] 가격 모델 연산 중..."):
            try:
                base = get_price_base(DKEY, MASTER)
                result_df, anchor, n_dates, detail = quant.run_price(base, engine_version, mode_selection,
                                                                     target_date, target_start, target_end)
            except quant.QuantError as e:
                st.error(str(e))
                result_df = None
        if result_df is not None:
            st.success(f"✅ 가격 모델 완료 ({mode_selection}) · **기준일 {anchor:%Y-%m-%d}** · 누적 {n_dates}일")
            stamp = now_kst().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["analysis_history"].insert(0, {
                "id": uuid.uuid4().hex[:8], "title": f"📌 [{stamp}] 가격(방어벽) 엔진 - {engine_version} | {detail}",
                "data": result_df, "type": "price"})
            st.session_state["analysis_history"] = st.session_state["analysis_history"][:MAX_HISTORY]
    elif main_menu == MENU_VOL:
        st.session_state["show_vol_explanation"] = True
        with st.spinner("거래량 마이크로스트럭처 레짐 연산 중..."):
            try:
                vol_df = get_volume(DKEY, MASTER)
                out_df, anchor, detail = quant.run_volume(vol_df, mode_selection, target_start, target_end)
            except quant.QuantError as e:
                (st.warning if str(e).startswith("⚠") else st.error)(str(e))
                out_df = None
        if out_df is not None:
            st.success(f"✅ 거래량 레짐 모델 완료 ({mode_selection}) · **기준일 {anchor:%Y-%m-%d}**")
            stamp = now_kst().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["analysis_history"].insert(0, {
                "id": uuid.uuid4().hex[:8], "title": f"📊 [{stamp}] 거래량(레짐) 엔진 - {quant.VOLUME_VERSION} | {detail}",
                "data": out_df, "type": "volume"})
            st.session_state["analysis_history"] = st.session_state["analysis_history"][:MAX_HISTORY]


# =====================================================================
# [결과 화면 3] 분석 엔진 (버전 선택)
# =====================================================================
def show_split(sp, key):
    """3분할 프롬프트 + 표 뷰어"""
    import streamlit.components.v1 as components
    tabs = st.tabs([f"파트 {p['k']}/3" for p in sp["parts"]] + ["표 뷰어"])
    for tab, p in zip(tabs, sp["parts"]):
        with tab:
            text = p["data"].decode("utf-8")
            st.caption(f"{p['name']} · {len(text):,}자 — 복사해서 제미나이·클로드 같은 채팅에 붙여 넣고, "
                       f"답이 '— 파트 {p['k']}/3 끝 —'까지 나오면 다음 파트로")
            copy_button(text, f"📋 파트 {p['k']}/3 복사", f"{key}_c{p['k']}")
            st.download_button(f"⬇️ 파트 {p['k']}/3 내려받기", p["data"], file_name=p["name"], mime="text/plain",
                               key=f"{key}_d{p['k']}")
            with st.expander("내용 보기"):
                st.text(text[:6000] + ("\n…" if len(text) > 6000 else ""))
    with tabs[-1]:
        if sp.get("viewer"):
            st.download_button("⬇️ 표 뷰어(HTML) 내려받기", sp["viewer"]["data"], file_name=sp["viewer"]["name"],
                               mime="text/html", key=f"{key}_v")
            components.html(sp["viewer"]["data"].decode("utf-8"), height=640, scrolling=True)


def show_final_report_form(databook_name, databook_bytes, key):
    import engine_service
    import streamlit.components.v1 as components
    st.markdown("##### 🧾 최종 보고서 만들기")
    st.caption("파트 1~3의 답변을 그대로 붙여 넣으면, 섹션마다 데이터북 표 바로 아래에 해설을 넣은 보고서를 만듭니다.")
    answers = [st.text_area(f"파트 {k}/3 답변", key=f"{key}_ans{k}", height=140,
                            placeholder=f"'— 파트 {k}/3 끝 —'까지 붙여 넣으세요") for k in (1, 2, 3)]
    if st.button("🧾 최종 보고서 만들기", type="primary", key=f"{key}_mk", use_container_width=True):
        try:
            with st.spinner("보고서 만드는 중..."):
                r = engine_service.make_final_report(databook_name, databook_bytes, answers)
                rep = next((f for f in r["files"] if f["key"] == "report"), None)
                saved = None
                if rep:
                    try:
                        saved = storage.save_report(STORE, r["date"].replace("-", ""), rep["name"], rep["data"],
                                                    f"최종 보고서 {r['date']}")
                        bump("reports")
                    except Exception as e:
                        st.warning(f"보고서를 깃허브에 보관하지 못했습니다: {e}")
            st.session_state[f"{key}_report"] = {"r": r, "saved": saved}
        except ValueError as e:
            st.error(str(e))
    out = st.session_state.get(f"{key}_report")
    if out:
        r = out["r"]
        st.success(f"✅ 최종 보고서를 만들었습니다 ({r['date']})" + (f" · 보관: {out['saved']}" if out["saved"] else ""))
        if r.get("checks"):
            st.markdown("\n".join(f"- {c}" for c in r["checks"]))
        cols = st.columns(len(r["files"]))
        for c, f in zip(cols, r["files"]):
            c.download_button(f"⬇️ {f['name']}", f["data"], file_name=f["name"], use_container_width=True,
                              key=f"{key}_f_{f['key']}")
        rep = next((f for f in r["files"] if f["key"] == "report"), None)
        if rep:
            components.html(rep["data"].decode("utf-8"), height=760, scrolling=True)


if main_menu == MENU_ENGINE:
    import engine_service
    if st.session_state.get("eng_add_msg"):
        st.success(st.session_state.pop("eng_add_msg"))
    if SEL_ENGINE:
        with st.expander(f"선택한 엔진: {engine_service.engine_label(SEL_ENGINE, ENGINES_LIST)} · {SEL_ENGINE['name']}"):
            st.caption(SEL_ENGINE.get("title") or "")
            st.caption(engine_service.SIGNAL_TEXT.get(SEL_ENGINE["signal_mode"], ""))
        if not SEL_ENGINE["ok"]:
            st.error(f"❌ 이 엔진 파일은 실행할 수 없습니다: {SEL_ENGINE.get('error')}")
    if engine_button and MASTER is not None and SEL_ENGINE:
        prog = st.progress(0.0, text="분석 엔진 시작…")
        with st.status(f"분석 엔진 {SEL_ENGINE['version']} 실행 중… (1~3분)", expanded=False) as box:
            weights = {1: (0, 10), 2: (10, 5), 3: (15, 78), 4: (93, 7)}

            def _prog(stage, frac, text):
                a, w = weights.get(stage, (0, 0))
                prog.progress(min(0.99, (a + w * frac) / 100), text=text)

            def _log(line):
                if any(k in line for k in ("🚀", "[저장 완료]", "[경고]", "Error", "오류")):
                    box.write(line.strip()[:200])

            res = engine_service.run(STORE, MASTER, engine=SEL_ENGINE, tier=tier, split=fmt.startswith("3분할"),
                                     date="latest" if eng_date is None else pd.Timestamp(eng_date).strftime("%Y-%m-%d"),
                                     binance=binance, on_progress=_prog, on_log=_log)
            box.update(label=res.get("title", "끝"), state="complete" if res.get("status") == "ok" else "error")
        prog.empty()
        st.session_state["engine_result"] = res
        for k in ("eng_now_report", "eng_now_ans1", "eng_now_ans2", "eng_now_ans3"):   # 지난 실행의 보고서·답변은 지움
            st.session_state.pop(k, None)
        if res.get("signal_saved"):
            bump("signal")
        if res.get("saved"):
            bump("reports")
    res = st.session_state.get("engine_result")
    if res:
        if res.get("status") == "ok":
            sig_note = ""
            if res.get("signal_saved"):
                sig_note = " · 신호 기록·채점 갱신" + ("" if res.get("signal_file") == storage.SIGNAL_PATH
                                                  else f" ({res.get('engine_version')} 전용 기록)")
            st.success(f"✅ 엔진 {res.get('engine_version', '')} · {res.get('title')} · {res.get('seconds', 0)}초{sig_note}")
            if res.get("signal_error"):
                st.warning(f"신호 기록을 저장소에 저장하지 못했습니다: {res['signal_error']}")
            if res.get("save_error"):
                st.warning(f"프롬프트를 저장소에 보관하지 못했습니다: {res['save_error']}")
            for i, f in enumerate(res.get("files") or []):
                st.markdown(f"**{f['name']}** · {len(f['data']):,}바이트" + (" · 깃허브 reports/ 에 보관" if res.get("saved") else ""))
                if not res.get("splits"):
                    copy_button(f["data"].decode("utf-8", "replace"), "📋 데이터북 전체 복사", f"eng_copy_{i}")
                st.download_button(f"⬇️ {f['name']} 내려받기", f["data"], file_name=f["name"], mime="text/plain",
                                   key=f"eng_dl_{i}")
            for j, sp in enumerate(res.get("splits") or []):
                show_split(sp, f"eng_sp{j}")
            dbs = [f for f in res.get("files") or [] if f["kind"] == "databook"]
            if dbs:
                show_final_report_form(dbs[0]["name"], dbs[0]["data"], "eng_now")
        else:
            st.error(f"❌ {res.get('title')}\n\n{res.get('message', '')}" + (f"\n\n{res['hint']}" if res.get("hint") else ""))
            if res.get("log_tail"):
                with st.expander("진행 기록 보기"):
                    st.text("\n".join(res["log_tail"][-60:]))
    st.divider()
    st.markdown("##### 📂 보관한 프롬프트 다시 열기 (최종 보고서 만들기)")
    try:
        prompts = [x for x in get_report_items(STORE, st.session_state.get("bust", 0)) if x["kind"] == "prompt"][:120]
    except Exception as e:
        prompts = []
        st.caption(f"보관함을 읽지 못했습니다: {e}")
    if not prompts:
        st.caption("아직 보관한 프롬프트가 없습니다. 분석을 실행하면 여기에 쌓입니다.")
    else:
        labels = {x["path"]: f"{x['date']} · Tier {x['tier']} · {x['ver']} · {x['time']} 실행" for x in prompts}
        if st.session_state.get("arch_pick") not in labels:
            st.session_state.pop("arch_pick", None)
        pick = st.selectbox("프롬프트", list(labels), format_func=lambda p_: labels.get(p_, p_), key="arch_pick")
        if st.button("📂 열기 (3분할 · 최종 보고서)", use_container_width=True):
            it = next(x for x in prompts if x["path"] == pick)
            for k in ("arc_report", "arc_ans1", "arc_ans2", "arc_ans3"):
                st.session_state.pop(k, None)
            try:
                data = STORE.read(it["path"], sha=it["sha"])
                st.session_state["archive"] = {"name": it["name"], "data": data,
                                               "split": engine_service.make_split(it["name"], data)}
            except Exception as e:
                st.error(f"열지 못했습니다: {type(e).__name__}: {e}")
        arc = st.session_state.get("archive")
        if arc:
            st.markdown(f"**{arc['name']}**")
            st.download_button("⬇️ 데이터북 내려받기", arc["data"], file_name=arc["name"], mime="text/plain", key="arc_dl")
            show_split(arc["split"], "arc_sp")
            show_final_report_form(arc["name"], arc["data"], "arc")
    st.divider()
    with st.expander("➕ 분석 엔진 파일 추가 (새 버전)"):
        st.caption("엔진 파일(.py)을 올리면 저장소 engine/ 폴더에 저장되어 위 '엔진 버전' 목록에 바로 나옵니다. "
                   "버전은 파일 첫 줄의 [V4.3.8 · 날짜] 같은 표시로 알아냅니다.")
        up_eng = st.file_uploader("엔진 파일 (.py)", type=None, key="eng_up")
        if up_eng is not None:
            data = up_eng.getvalue()
            if not up_eng.name.lower().endswith(".py"):
                st.error("파이썬(.py) 파일만 올릴 수 있습니다.")
            else:
                inf = engine_service.inspect_bytes(data, up_eng.name)
                if not inf["ok"]:
                    st.error(f"❌ {inf['error']}")
                elif inf["version"] == "V0":
                    st.error("❌ 엔진 첫 줄에서 버전 표시([V4.3.8 · 날짜] 같은)를 찾지 못했습니다.")
                else:
                    same = [x for x in ENGINES_LIST if x["version"] == inf["version"]]
                    st.info(f"**{inf['version']}** · {engine_service.SIGNAL_TEXT.get(inf['signal_mode'], '')}\n\n{inf['title'][:240]}")
                    ok_write = True
                    if same:
                        ok_write = st.checkbox(f"이미 있는 {inf['version']} ({same[0]['name']})을 이 파일로 바꿉니다", key="eng_up_ow")
                    if st.button("💾 엔진 저장", type="primary", disabled=not ok_write, key="eng_up_btn"):
                        saved_path = None
                        try:
                            saved_path, _ = engine_service.add_engine(STORE, up_eng.name, data, overwrite=bool(same))
                        except Exception as e:
                            st.error(f"저장하지 못했습니다: {type(e).__name__}: {e}")
                        if saved_path:
                            st.session_state["eng_add_msg"] = f"✅ {inf['version']} 엔진을 {saved_path}에 저장했습니다. 위 '엔진 버전'에서 고르세요."
                            st.session_state["eng_pick_next"] = saved_path
                            bump("engines")
                            st.rerun()

# =====================================================================
# [결과 화면 4] 분석 보고서 보관함 — 최종 보고서 보기 · 골라서 지우기
# =====================================================================
if main_menu == MENU_ARCHIVE:
    import engine_service
    import streamlit.components.v1 as components
    try:
        items = get_report_items(STORE, st.session_state.get("bust", 0))
    except Exception as e:
        items = []
        st.error(f"❌ 보관함을 읽지 못했습니다: {type(e).__name__}: {e}")
    reports = [x for x in items if x["kind"] == "report"]
    n_prompt = len(items) - len(reports)
    msg = st.session_state.pop("rep_del_msg", None)
    if msg:
        done, fails = msg
        if done:
            st.success(f"✅ {done}개를 지웠습니다.")
        if fails:
            st.warning("지우지 못한 파일:\n\n" + "\n\n".join(f"· {x}" for x in fails[:20]))
    if not items:
        st.info("아직 보관한 보고서가 없습니다. 🧠 분석 엔진에서 분석을 실행하고 [🧾 최종 보고서 만들기]를 누르면 여기에 쌓입니다.")
    else:
        dates = sorted({x["date"] for x in items})
        st.caption(f"최종 보고서 {len(reports):,}개 · 프롬프트 {n_prompt:,}개 · 기준일 {dates[0]} ~ {dates[-1]}")
        tab_view, tab_del = st.tabs(["📖 최종 보고서 보기", "🗑 보고서 정리 (골라서 지우기)"])
        with tab_view:
            if not reports:
                st.info("최종 보고서가 아직 없습니다. 🧠 분석 엔진 결과 아래 [🧾 최종 보고서 만들기]로 만들면 여기에 보관됩니다.")
            else:
                f1, f2 = st.columns(2)
                vers = ["전체"] + sorted({x["ver"] for x in reports}, key=engine_service.version_key, reverse=True)
                tiers_ = ["전체"] + sorted({x["tier"] for x in reports})
                vpick = f1.selectbox("엔진", vers, key="arc_ver_f")
                tpick = f2.selectbox("Tier", tiers_, key="arc_tier_f", format_func=lambda t: t if t == "전체" else f"Tier {t}")
                shown = [x for x in reports if vpick in ("전체", x["ver"]) and tpick in ("전체", x["tier"])]
                if not shown:
                    st.info("조건에 맞는 최종 보고서가 없습니다.")
                else:
                    lab = {x["path"]: f"{x['date']} · Tier {x['tier']} · {x['ver']} · {x['time']} 실행" for x in shown}
                    if st.session_state.get("arc_pick_rep") not in lab:
                        st.session_state.pop("arc_pick_rep", None)
                    pick = st.selectbox(f"보고서 ({len(shown):,}개 · 새것 먼저)", list(lab), format_func=lambda p_: lab[p_],
                                        key="arc_pick_rep")
                    it = next(x for x in shown if x["path"] == pick)
                    try:
                        data = get_report_bytes(STORE, it["path"], it["sha"])
                    except Exception as e:
                        data = None
                        st.error(f"보고서를 읽지 못했습니다: {type(e).__name__}: {e}")
                    if data:
                        st.download_button("⬇️ 이 보고서 내려받기 (HTML)", data, file_name=it["name"], mime="text/html",
                                           use_container_width=True, key="arc_rep_dl")
                        components.html(data.decode("utf-8", "replace"), height=900, scrolling=True)
        with tab_del:
            st.caption("지울 것을 표의 '선택' 칸에서 고르세요. 오래된 것을 한꺼번에 고르려면 날짜를 정하고 [그 전 것 모두 고르기]를 누르세요. "
                       "지운 파일은 깃허브 기록(History)에 남아 되살릴 수 있습니다.")
            ver_n = st.session_state.setdefault("rep_del_ver", 0)
            preset = st.session_state.get("rep_preset")
            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            cut_default = (pd.Timestamp(dates[-1]) - pd.Timedelta(days=30)).date()
            cut = c1.date_input("이 기준일보다 오래된 것", value=cut_default, key="rep_cut")
            if c2.button("그 전 것 모두 고르기", use_container_width=True, key="rep_cut_btn"):
                st.session_state["rep_preset"] = str(cut)
                st.session_state["rep_del_ver"] = ver_n + 1
                st.rerun()
            if c3.button("고른 것 모두 풀기", use_container_width=True, key="rep_clear_btn"):
                st.session_state["rep_preset"] = None
                st.session_state["rep_del_ver"] = ver_n + 1
                st.rerun()
            table = pd.DataFrame([{"선택": bool(preset and x["date"] < preset), "기준일": x["date"],
                                   "종류": "최종 보고서" if x["kind"] == "report" else "프롬프트", "Tier": x["tier"],
                                   "엔진": x["ver"], "실행 시각": x["time"], "크기(KB)": max(1, round(x["size"] / 1024))}
                                  for x in items], index=[x["path"] for x in items])
            edited = st.data_editor(table, key=f"rep_editor_{ver_n}", hide_index=True, use_container_width=True,
                                    disabled=[c for c in table.columns if c != "선택"])
            sel = [p_ for p_, v in zip(edited.index, edited["선택"]) if bool(v)]
            by_path = {x["path"]: x for x in items}
            n_rep = sum(1 for p_ in sel if by_path[p_]["kind"] == "report")
            st.markdown(f"**{len(sel)}개 선택** (최종 보고서 {n_rep} · 프롬프트 {len(sel) - n_rep})")
            confirm = st.checkbox("선택한 것을 저장소에서 지웁니다", key=f"rep_del_ok_{ver_n}", disabled=not sel)
            if st.button(f"🗑 선택한 {len(sel)}개 지우기", type="primary", disabled=not (sel and confirm),
                         key=f"rep_del_btn_{ver_n}"):
                prog = st.progress(0.0, text="지우는 중…")
                done, fails = 0, []
                for i, p_ in enumerate(sel, 1):
                    x = by_path[p_]
                    try:
                        STORE.delete(p_, f"분석 보고서 삭제: {x['name']}", sha=x["sha"])
                        done += 1
                    except Exception as e:
                        fails.append(f"{x['name']}: {type(e).__name__}: {e}"[:200])
                    prog.progress(i / len(sel), text=f"지우는 중… {i}/{len(sel)}")
                st.session_state["rep_del_msg"] = (done, fails)
                st.session_state["rep_preset"] = None
                st.session_state["rep_del_ver"] = ver_n + 1
                bump("reports")
                st.rerun()

# =====================================================================
# [결과 화면 5] 신호 기록·채점
# =====================================================================
if main_menu == MENU_SIGNAL:
    try:
        sig_files = get_signal_files(STORE, st.session_state.get("bust", 0))
    except Exception:
        sig_files = [(storage.SIGNAL_PATH, "기본 (V4.3.7 이후 엔진)")]
    sig_path = sig_files[0][0]
    if len(sig_files) > 1:                       # 예전 엔진(V4.3.6 등) 전용 기록이 있으면 골라 봄
        sig_lab = dict(sig_files)
        if st.session_state.get("sig_file") not in sig_lab:
            st.session_state.pop("sig_file", None)
        sig_path = st.selectbox("기록 파일", list(sig_lab), format_func=lambda p_: sig_lab[p_], key="sig_file")
    sig_name = sig_path.rsplit("/", 1)[-1]
    try:
        sig = get_signal_bytes(STORE, st.session_state.get("bust", 0), sig_path)
    except Exception as e:
        sig = None
        st.error(f"❌ 신호 기록을 읽지 못했습니다: {e}")
    if not sig:
        st.info(f"아직 신호 기록 파일이 없습니다. 분석 엔진을 실행하면 {sig_path}가 만들어집니다.")
    else:
        sdf = storage._read_csv_bytes(sig)
        last = str(sdf["기준일"].dropna().astype(str).max()) if "기준일" in sdf.columns else "-"
        scored = int(sdf["채점시각"].notna().sum()) if "채점시각" in sdf.columns else 0
        st.success(f"✅ 신호 기록 {len(sdf):,}건 (채점 끝 {scored:,}건) · 마지막 기준일 {last}")
        f1, f2, f3 = st.columns(3)
        tiers = ["전체"] + (sorted(sdf["Tier"].dropna().astype(str).unique().tolist()) if "Tier" in sdf.columns else [])
        tier_pick = f1.selectbox("Tier", tiers, key="sig_tier")
        n_rows = f2.selectbox("보기", ["최근 30건", "최근 100건", "전체"], key="sig_rows")
        all_cols = f3.checkbox("모든 열 보기", value=False, key="sig_all")
        view = sdf if tier_pick == "전체" else sdf[sdf["Tier"].astype(str) == tier_pick]
        if not all_cols:
            key_cols = ("기준일", "Tier", "기록구분", "EWY종가", "레짐1순위", "국면1순위", "D선", "A선", "기습1차타깃",
                        "다음미국기준일", "다음미국종가", "D선위치_미국종가", "KOSPI_전일대비%", "채점시각")
            view = view[[c for c in key_cols if c in view.columns]]
        if n_rows != "전체":
            view = view.tail(30 if n_rows == "최근 30건" else 100)
        st.dataframe(view.iloc[::-1], hide_index=True, use_container_width=True)
        st.download_button(f"⬇️ {sig_name} 내려받기", sig, file_name=sig_name, mime="text/csv")
    with st.expander(f"📤 신호 기록 파일 바꾸기 — {sig_name} (PC에서 쓰던 파일을 넣을 때)"):
        up = st.file_uploader("EWY_신호기록_채점.csv", type=["csv"], key="sig_up")
        if up is not None:
            data = up.getvalue()
            try:
                udf = storage._read_csv_bytes(data)
                ok = "기준일" in udf.columns and "Tier" in udf.columns
            except Exception:
                ok, udf = False, None
            if not ok:
                st.error("신호 기록 파일이 아닙니다 (기준일 · Tier 열이 없음).")
            else:
                st.caption(f"{len(udf):,}건 · 마지막 기준일 {udf['기준일'].astype(str).max()}")
                if st.checkbox("지금 저장소의 신호 기록을 이 파일로 바꿉니다 (예전 기록은 깃허브 기록에 남음)", key="sig_confirm"):
                    if st.button("💾 바꾸기", type="primary"):
                        storage.save_signal(STORE, data, f"신호 기록 파일 바꾸기 (올림): {sig_name}", path=sig_path)
                        bump("signal")
                        st.success("바꿨습니다.")
                        st.rerun()

# =====================================================================
# [결과 화면 6] 히스토리 (가격 · 거래량)
# =====================================================================
if st.session_state["analysis_history"] and main_menu in (MENU_PRICE, MENU_VOL):
    st.divider()
    has_vol = any(r.get("type") == "volume" for r in st.session_state["analysis_history"])
    if has_vol and st.session_state.get("show_vol_explanation", True):
        with st.container():
            st.markdown(f"**📊 지표 설명자료 ({quant.VOLUME_VERSION} 마이크로스트럭처 엔진)**")
            _, btn_col1, btn_col2 = st.columns([8, 1, 1])
            with btn_col2:
                st.button("❌ 삭제", key="del_vol_exp", on_click=hide_vol_explanation, use_container_width=True)
            st.markdown(VOLUME_EXPLANATION_MD)
        st.divider()
    st.header(f"🗂️ 분석 결과 비교 히스토리 (최근 {MAX_HISTORY}건)")
    for record in st.session_state["analysis_history"]:
        with st.container():
            st.markdown(f"**{record['title']}**")
            _, btn_col1, btn_col2 = st.columns([8, 1, 1])
            with btn_col1:
                st.markdown(generate_new_window_link(record["data"], record["title"]), unsafe_allow_html=True)
            with btn_col2:
                st.button("❌ 삭제", key=f"del_{record['id']}", on_click=remove_history_item, args=(record["id"],),
                          use_container_width=True)
            render_safe_table(record["data"])
            st.write("")
