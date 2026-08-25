import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import os
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.unicode.east_asian_width', True)

# =====================================================================
# [웹 설정] 페이지 기본 세팅
# =====================================================================
st.set_page_config(page_title="EWY Quant Analytics V27", page_icon="📈", layout="wide")

# =====================================================================
# [엔진 1] G버젼_하락추세조정 로직 (기존 기본 로직)
# =====================================================================
def apply_logic_g_down(df):
    bottom_flags, near_scores, long_scores, hybrid_scores = [], [], [], []
    for i, r in df.iterrows():
        nc_ratio = r['Near_C_Ratio']
        nc_drop = r['Near_C_Ratio_Drop'] if pd.notna(r['Near_C_Ratio_Drop']) else 0
        n_score = max(0, (nc_ratio * 3.33) + (nc_drop * 10))
        
        lp_ratio = r['Long_P_Ratio']
        lp_growth = r['Long_P_OI_Growth'] if pd.notna(r['Long_P_OI_Growth']) else 0
        l_score = max(0, (lp_ratio * 10) + (min(lp_growth, 200.0) * 2))
        
        h_score = (n_score + l_score) / 2
        near_scores.append(int(n_score)); long_scores.append(int(l_score)); hybrid_scores.append(int(h_score))
        bottom_flags.append(1 if (h_score >= 100 or l_score >= 100) else 0)

    df['Bottom_Flag'] = bottom_flags
    df['Recent_Bottom'] = df['Bottom_Flag'].rolling(window=5, min_periods=1).max()
    df['Top_Warning_Flag'] = (df['Near_P_Ratio'] > 30.0).astype(int)
    df['Recent_Top_Warning'] = df['Top_Warning_Flag'].rolling(window=3, min_periods=1).max()

    phase_list = []
    ceiling_active = False
    prev_close = 0.0

    for i, r in df.iterrows():
        curr_close = r['Close Price']
        trend_up, mid_trend_up = curr_close > r['10MA'], r['10MA'] > r['20MA']
        phase = ""
        if trend_up:
            is_warning = r['Recent_Top_Warning'] > 0
            is_rollup = pd.notna(r['Long_P_Wgt_Rollup']) and r['Long_P_Wgt_Rollup'] > 2.0
            if is_warning and is_rollup: ceiling_active = True; phase = "⛔ 대천장 확정 (전량 익절)"
            elif ceiling_active and curr_close > prev_close: ceiling_active = True; phase = "⛔ 대천장 가짜 랠리 (익절 유지)"
            else:
                ceiling_active = False
                if is_warning: phase = "⚠️ 상승장 고점 경계령 (비중축소)"
                else: phase = "📈 대세 상승 추세 진행 중" if mid_trend_up else ("🚀 하락 멈춤 상승 전환" if r['Recent_Bottom'] > 0 else "➖ 횡보 (관망)")
        else:
            ceiling_active = False
            if hybrid_scores[i] >= 100: phase = "🔥 찐바닥 포착" if not mid_trend_up else "⚡ 일시 급락 눌림목"
            elif near_scores[i] >= 100 and long_scores[i] < 100: phase = "🔪 단기 투매 (칼날 주의)"
            elif long_scores[i] >= 100 and near_scores[i] < 100: phase = "🛡️ 세력 하방경직 구축"
            else: phase = "📉 본격 하락 추세 진행 중"
        prev_close = curr_close
        phase_list.append(phase)

    top_short_list, top_long_list, bot_short_list, bot_long_list = [], [], [], []
    for i, r in df.iterrows():
        trend_up = r['Close Price'] > r['10MA']
        np_ratio = r['Near_P_Ratio']
        rollup = r['Long_P_Wgt_Rollup'] if pd.notna(r['Long_P_Wgt_Rollup']) else 0

        if np_ratio >= 100: s_top = f"{np_ratio:.1f}배 🚨 광기"
        elif np_ratio >= 30: s_top = f"{np_ratio:.1f}배 ⚠️ 고점"
        elif np_ratio >= 15: s_top = f"{np_ratio:.1f}배 🟡 헷징"
        else: s_top = f"{np_ratio:.1f}배 ➖ 안정적"

        if rollup >= 4.0: l_top = f"+${rollup:.2f} 💀 대천장"
        elif rollup >= 2.0: l_top = f"+${rollup:.2f} ⛔ 롤업 확정"
        elif rollup >= 0.5: l_top = f"+${rollup:.2f} 🟡 조짐"
        else: l_top = f"{rollup:+.2f} ➖ 평상시"

        bunker_str = f" (${r['Bunker_Price']:.1f})" if r['Bunker_Price'] > 0 else ""
        if near_scores[i] >= 500: s_bot = f"{near_scores[i]} 🚨 항복 선언"
        elif near_scores[i] >= 300: s_bot = f"{near_scores[i]} 🩸 패닉 셀링"
        elif near_scores[i] >= 100: s_bot = f"{near_scores[i]} 🟡 투매 발생"
        else: s_bot = f"{near_scores[i]} ➖ 소화 중"

        if long_scores[i] >= 500: l_bot = f"{long_scores[i]} 🚨 극단치{bunker_str}"
        elif long_scores[i] >= 300: l_bot = f"{long_scores[i]} 🛡️ 세력개입{bunker_str}"
        elif long_scores[i] >= 100: l_bot = f"{long_scores[i]} 🏗️ 방어벽{bunker_str}"
        else: l_bot = f"{long_scores[i]} ➖ 방어없음"

        if trend_up:
            top_short_list.append(s_top); top_long_list.append(l_top); bot_short_list.append("-"); bot_long_list.append("-")
        else:
            top_short_list.append("-"); top_long_list.append("-"); bot_short_list.append(s_bot); bot_long_list.append(l_bot)

    df['[상승장] 단기(풋발작)'] = top_short_list
    df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매)'] = bot_short_list
    df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df

# =====================================================================
# [엔진 2] C버젼 로직
# =====================================================================
def apply_logic_c(df):
    bottom_flags, near_scores, long_scores, hybrid_scores = [], [], [], []
    for i, r in df.iterrows():
        nc_ratio = r['Near_C_Ratio']
        nc_drop = r['Near_C_Ratio_Drop'] if pd.notna(r['Near_C_Ratio_Drop']) else 0
        n_score = max(0, (nc_ratio * 3.33) + (nc_drop * 10))

        lp_ratio = r['Long_P_Ratio']
        lp_growth = r['Long_P_OI_Growth'] if pd.notna(r['Long_P_OI_Growth']) else 0
        l_score = max(0, (lp_ratio * 10) + (min(lp_growth, 200.0) * 2))

        h_score = (n_score + l_score) / 2
        near_scores.append(int(n_score)); long_scores.append(int(l_score)); hybrid_scores.append(int(h_score))
        bottom_flags.append(1 if (h_score >= 100 or l_score >= 100) else 0)

    df['Bottom_Flag'] = bottom_flags
    df['Recent_Bottom'] = df['Bottom_Flag'].rolling(window=5, min_periods=1).max()
    df['Top_Warning_Flag'] = (df['Near_P_Ratio'] > 30.0).astype(int)
    df['Recent_Top_Warning'] = df['Top_Warning_Flag'].rolling(window=3, min_periods=1).max()

    phase_list = []
    ceiling_active = False
    prev_close = 0.0

    for i, r in df.iterrows():
        curr_close = r['Close Price']
        trend_up = curr_close > r['10MA']
        mid_trend_up = r['10MA'] > r['20MA']
        phase = ""
        
        if trend_up:
            is_warning = r['Recent_Top_Warning'] > 0
            is_rollup = pd.notna(r['Long_P_Wgt_Rollup']) and r['Long_P_Wgt_Rollup'] > 2.0
            if is_warning and is_rollup:
                ceiling_active = True; phase = "⛔ 대천장(Ceiling) 확정 / 세력 방어벽 롤업 (전량 익절)"
            elif ceiling_active and curr_close > prev_close:
                ceiling_active = True; phase = "⛔ 대천장 유지 / 가짜 랠리 (익절 유지)"
            else:
                ceiling_active = False
                if is_warning: phase = "⚠️ 상승장 고점 경계령 (근월물 풋 투매 / 비중축소)"
                elif mid_trend_up: phase = "📈 대세 상승 추세 진행 중"
                elif r['Recent_Bottom'] > 0: phase = "🚀 하락 멈춤 / 바닥 확인 상승 전환 (본대 투입)"
                else: phase = "➖ 대세 하락 속 횡보 (가짜 반등 주의)"
        else:
            ceiling_active = False
            n_score, l_score, h_score = near_scores[i], long_scores[i], hybrid_scores[i]
            if h_score >= 100: phase = "🔥 패닉셀 붕괴 / 완전체(Hybrid) 찐바닥 포착" if not mid_trend_up else "⚡ 상승장 속 하이브리드 눌림목"
            elif n_score >= 100 and l_score < 100: phase = "🔪 근월물 단기 투매 (칼날 주의 / 방어벽 없음)"
            elif l_score >= 100 and n_score < 100: phase = "🛡️ 원월물 벙커 매집 (하방경직 구축)"
            else: phase = "📉 단기 조정 진행 중" if mid_trend_up else "📉 본격 하락 추세 진행 중"
            
        prev_close = curr_close
        phase_list.append(phase)

    top_short_list, top_long_list, bot_short_list, bot_long_list = [], [], [], []
    for i, r in df.iterrows():
        trend_up = r['Close Price'] > r['10MA']
        np_ratio = r['Near_P_Ratio']
        rollup = r['Long_P_Wgt_Rollup'] if pd.notna(r['Long_P_Wgt_Rollup']) else 0

        if np_ratio >= 100: s_top = f"{np_ratio:.1f}배 🚨 극단적 풋 투매"
        elif np_ratio >= 30: s_top = f"{np_ratio:.1f}배 ⚠️ 고점 발작"
        elif np_ratio >= 15: s_top = f"{np_ratio:.1f}배 🟡 헷징 증가"
        else: s_top = f"{np_ratio:.1f}배 ➖ 안정적"

        if rollup >= 4.0: l_top = f"+${rollup:.2f} 💀 역사적 대천장"
        elif rollup >= 2.0: l_top = f"+${rollup:.2f} ⛔ 롤업 확정"
        elif rollup >= 0.5: l_top = f"+${rollup:.2f} 🟡 인상 조짐"
        else: l_top = f"{rollup:+.2f} ➖ 평상시"

        n_score, l_score = near_scores[i], long_scores[i]
        bunker_p = r['Bunker_Price']
        bunker_str = f" (벽: ${bunker_p:.1f})" if bunker_p > 0 else ""

        if n_score >= 500: s_bot = f"{n_score}점 🚨 항복 선언 (완전 패닉)"
        elif n_score >= 300: s_bot = f"{n_score}점 🩸 패닉 셀링"
        elif n_score >= 100: s_bot = f"{n_score}점 🟡 투매 발생"
        else: s_bot = f"{n_score}점 ➖ 평상시"

        if l_score >= 500: l_bot = f"{l_score}점 🚨 역사적 극단치{bunker_str}"
        elif l_score >= 300: l_bot = f"{l_score}점 🛡️ 강력 세력개입{bunker_str}"
        elif l_score >= 100: l_bot = f"{l_score}점 🏗️ 일반 방어벽{bunker_str}"
        else: l_bot = f"{l_score}점 ➖ 평상시{bunker_str}"

        if trend_up:
            top_short_list.append(s_top); top_long_list.append(l_top); bot_short_list.append("-"); bot_long_list.append("-")
        else:
            top_short_list.append("-"); top_long_list.append("-"); bot_short_list.append(s_bot); bot_long_list.append(l_bot)

    df['[상승장] 단기(풋발작)'] = top_short_list
    df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매)'] = bot_short_list
    df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df

# =====================================================================
# [엔진 3] G버젼_상승특화 로직 
# =====================================================================
def apply_logic_g_up(df):
    df['Near_C_Pct'] = df['Near_C_Ratio'].rolling(window=60, min_periods=1).rank(pct=True) * 100
    df['Near_P_Pct'] = df['Near_P_Ratio'].rolling(window=60, min_periods=1).rank(pct=True) * 100

    capped_growth = df['Long_P_OI_Growth'].fillna(0).clip(upper=200.0)
    df['Raw_Bunker_Score'] = (df['Long_P_Ratio'] * 10) + (capped_growth * 2)
    df['Bunker_Pct'] = df['Raw_Bunker_Score'].rolling(window=252, min_periods=1).rank(pct=True) * 100
    df['Recent_5D_Near_C_Pct'] = df['Near_C_Pct'].rolling(window=5, min_periods=1).max()
    df['Recent_5D_Bunker_Pct'] = df['Bunker_Pct'].rolling(window=5, min_periods=1).max()
    
    df['Top_Warning_Flag'] = (df['Near_P_Pct'] >= 95.0).astype(int)
    df['Recent_Top_Warning'] = df['Top_Warning_Flag'].rolling(window=3, min_periods=1).max()

    phase_list = []
    ceiling_active = False
    prev_close = 0.0

    for i, r in df.iterrows():
        curr_close = r['Close Price']
        trend_up, mid_trend_up = curr_close > r['10MA'], r['10MA'] > r['20MA']
        n_pct = r['Near_C_Pct'] if pd.notna(r['Near_C_Pct']) else 0
        l_pct = r['Bunker_Pct'] if pd.notna(r['Bunker_Pct']) else 0
        atm_dom = r['ATM_Put_Dominance'] if pd.notna(r['ATM_Put_Dominance']) else 50.0

        phase = ""
        if trend_up:
            is_warning = r['Recent_Top_Warning'] > 0
            is_rollup = pd.notna(r['Long_P_Wgt_Rollup']) and r['Long_P_Wgt_Rollup'] > 2.0
            if is_warning and is_rollup:
                ceiling_active = True; phase = "⛔ 대천장(Ceiling) 확정 (전량 익절)"
            elif ceiling_active and curr_close > prev_close:
                ceiling_active = True; phase = "⛔ 대천장 유지 / 가짜 랠리"
            else:
                ceiling_active = False
                if is_warning: phase = "⚠️ 상승장 속 고점 경계령 (비중축소)"
                else: phase = "📈 대세 상승 추세 진행 중" if mid_trend_up else "🚀 하락 멈춤 / 단기 상승 전환"
        else:
            ceiling_active = False
            recent_n = r['Recent_5D_Near_C_Pct'] if pd.notna(r['Recent_5D_Near_C_Pct']) else 0
            recent_l = r['Recent_5D_Bunker_Pct'] if pd.notna(r['Recent_5D_Bunker_Pct']) else 0

            n_prob = min(100.0, (recent_n / 95.0) * 100.0)
            l_prob = min(100.0, (recent_l / 95.0) * 100.0)
            disparity = (curr_close / r['20MA']) * 100.0 if r['20MA'] > 0 else 100.0
            p_prob = max(0.0, min(100.0, (98.0 - disparity) / 8.0 * 100.0))
            atm_prob = max(0.0, min(100.0, (100.0 - atm_dom) / 40.0 * 100.0))
            
            bottom_prob = (n_prob + l_prob + p_prob + atm_prob) / 4.0
            prob_str = f" 🔋[에너지: {bottom_prob:.1f}% | 낙폭: {p_prob:.0f}점]"

            if l_pct < 95:
                if n_pct >= 95: phase = "🔪 단기 투매 발생 (방어벽 부재)" if mid_trend_up else "🔪 개미 패닉셀 발생"
                else: phase = "📉 단기 조정 진행 중" if mid_trend_up else "📉 본격 하락 추세 진행 중"
            else:
                if n_pct < 95: phase = "🛡️ 강력 세력 방어벽 셋업" if mid_trend_up else "🛡️ 강력 세력 벙커 구축 중"
                else:
                    if atm_dom >= 60.0: phase = "⚠️ 가짜 반등 주의 (기관 ATM 숏 지속)" if not mid_trend_up else "⚠️ 섣부른 눌림목 주의"
                    else: phase = "🔥 퍼펙트 찐바닥 포착" if not mid_trend_up else "🔥 퍼펙트 눌림목 포착"

            if "퍼펙트" not in phase:
                if bottom_prob >= 90.0 and "가짜 반등" not in phase and "압박" not in phase:
                    phase = "⏳ 찐바닥 셋업 극대화" if not mid_trend_up else "⏳ 눌림목 셋업 극대화"
                elif bottom_prob >= 80.0 and ("본격 하락" in phase or "조정" in phase):
                    phase = "🟡 바닥 다지기 진행 중" if not mid_trend_up else "🟡 견조한 조정 진행 중"
            
            phase = phase + prob_str

        prev_close = curr_close
        phase_list.append(phase)

    top_short_list, top_long_list, bot_short_list, bot_long_list = [], [], [], []
    for i, r in df.iterrows():
        trend_up = r['Close Price'] > r['10MA']
        np_pct = r['Near_P_Pct']
        np_raw = r['Near_P_Ratio']
        rollup = r['Long_P_Wgt_Rollup'] if pd.notna(r['Long_P_Wgt_Rollup']) else 0

        if np_pct >= 99: s_top = f"[{np_pct:.0f}점] 🚨 풋 투매 ({np_raw:.1f}배)"
        elif np_pct >= 95: s_top = f"[{np_pct:.0f}점] ⚠️ 고점 발작 ({np_raw:.1f}배)"
        elif np_pct >= 90: s_top = f"[{np_pct:.0f}점] 🟡 헷징 증가 ({np_raw:.1f}배)"
        else: s_top = f"[{np_pct:.0f}점] ➖ 안정적"

        if rollup >= 4.0: l_top = f"+${rollup:.2f} 💀 거대 세력 탈출"
        elif rollup >= 2.0: l_top = f"+${rollup:.2f} ⛔ 롤업 확정"
        elif rollup >= 0.5: l_top = f"+${rollup:.2f} 🟡 인상 조짐"
        else: l_top = f"{rollup:+.2f} ➖ 평상시"

        n_raw = r['Near_C_Ratio']
        l_pct = r['Bunker_Pct'] if pd.notna(r['Bunker_Pct']) else 0
        l_raw = r['Long_P_Ratio']
        atm_dom = r['ATM_Put_Dominance']
        
        if atm_dom > 85.0: atm_level = "(MAX 🚨)"
        elif atm_dom >= 70.0: atm_level = "(위험 ⚠️)"
        elif atm_dom >= 55.0: atm_level = "(경계 🟡)"
        else: atm_level = "(해제 🟢)"
        atm_str = f" [하방: {atm_dom:.0f}% {atm_level}]"

        bunker_p = r['Bunker_Price']
        bunker_str = f" (벽: ${bunker_p:.1f} / {l_raw:.1f}배)" if bunker_p > 0 else f" (규모: {l_raw:.1f}배)"
        n_pct = r['Near_C_Pct'] if pd.notna(r['Near_C_Pct']) else 0

        if n_pct >= 99: s_bot = f"[강도: {n_raw:.1f}배] 🚨 항복 선언{atm_str}"
        elif n_pct >= 95: s_bot = f"[강도: {n_raw:.1f}배] 🩸 패닉 셀링{atm_str}"
        elif n_pct >= 90: s_bot = f"[강도: {n_raw:.1f}배] 🟡 투매 발생{atm_str}"
        else: s_bot = f"[강도: {n_raw:.1f}배] ➖ 평상시{atm_str}"

        if l_pct >= 99: l_bot = f"[강도: {l_raw:.1f}배] 🚨 역사적 벙커{bunker_str}"
        elif l_pct >= 95: l_bot = f"[강도: {l_raw:.1f}배] 🛡️ 강력 방어벽{bunker_str}"
        elif l_pct >= 90: l_bot = f"[강도: {l_raw:.1f}배] 🏗️ 일반 방어벽{bunker_str}"
        else: l_bot = f"[강도: {l_raw:.1f}배] ➖ 평상시{bunker_str}"

        if trend_up:
            top_short_list.append(s_top); top_long_list.append(l_top); bot_short_list.append("-"); bot_long_list.append("-")
        else:
            top_short_list.append("-"); top_long_list.append("-"); bot_short_list.append(s_bot); bot_long_list.append(l_bot)

    df['[상승장] 단기(풋발작)'] = top_short_list
    df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매/ATM)'] = bot_short_list
    df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df


# =====================================================================
# [웹 엔진 코어] 데이터 연산
# =====================================================================
@st.cache_data(ttl=3600)
def load_master_data():
    # 서버 환경(웹) 구동을 고려하여 앱과 동일한 폴더에 위치한 마스터 데이터 파일을 읽습니다.
    master_file = 'EWY_Options_V27_App_Master.pkl.gz'
    if os.path.exists(master_file):
        return pd.read_pickle(master_file)
    return pd.DataFrame()

def run_quant_engine_web(version, mode, target_date=None, target_start=None, target_end=None):
    master_df = load_master_data()

    if master_df.empty:
        st.error("❌ 마스터 데이터 파일(EWY_Options_V27_App_Master.pkl.gz)을 찾을 수 없습니다. (소스코드와 같은 위치에 업로드해주세요.)")
        return pd.DataFrame()

    # 야후 파이낸스 실시간 EWY 데이터 다운로드
    try:
        end_date = (datetime.today() + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        px = yf.download("EWY", start="2024-01-01", end=end_date, progress=False, auto_adjust=False).reset_index()
        if isinstance(px.columns, pd.MultiIndex): px.columns = [c[0] for c in px.columns]
        px.rename(columns={'Date': 'Date', 'Close': 'Close Price'}, inplace=True)
        px['Date'] = pd.to_datetime(px['Date']).dt.tz_localize(None).dt.normalize()
        px = px.sort_values('Date').dropna(subset=['Close Price']).reset_index(drop=True)
    except Exception as e:
        st.warning(f"yfinance 가격 데이터를 가져오는데 실패했습니다: {e}")
        px = pd.DataFrame()

    # 옵션 지표 데이터 계산 코어 파이프라인
    op_f = master_df.copy()
    op_f['DTE'] = (op_f['Expiration Date'] - op_f['Quote Date']).dt.days
    op_f = op_f[op_f['DTE'] >= 10]

    out = []
    for dt, g in op_f.groupby('Quote Date'):
        spot = g['EWY Price'].iloc[0] if g['EWY Price'].iloc[0] > 0 else (px[px['Date'] == dt]['Close Price'].iloc[0] if not px[px['Date'] == dt].empty else 1)
        atm_lower, atm_upper = spot * 0.95, spot * 1.05
        c, p = g[g['Option Type'] == 'C'], g[g['Option Type'] == 'P']
        near_c, near_p, long_p = c[c['DTE'] <= 30], p[p['DTE'] <= 30], p[p['DTE'] >= 91]

        n_c_atm = near_c[(near_c['Strike'] >= atm_lower) & (near_c['Strike'] <= atm_upper)]['Open Interest'].sum()
        n_c_otm = near_c[near_c['Strike'] > atm_upper]['Open Interest'].sum()
        near_c_ratio = n_c_otm / n_c_atm if n_c_atm > 0 else 0

        l_p_atm = long_p[(long_p['Strike'] >= atm_lower) & (long_p['Strike'] <= atm_upper)]['Open Interest'].sum()
        l_p_otm = long_p[long_p['Strike'] < atm_lower]['Open Interest'].sum()
        long_p_ratio = l_p_otm / l_p_atm if l_p_atm > 0 else 0
        long_p_oi = long_p['Open Interest'].sum()

        otm_puts = long_p[long_p['Strike'] < spot]
        bunker_price = (otm_puts.nlargest(10, 'Open Interest')['Strike'] * otm_puts.nlargest(10, 'Open Interest')['Open Interest']).sum() / otm_puts.nlargest(10, 'Open Interest')['Open Interest'].sum() if not otm_puts.empty and otm_puts.nlargest(10, 'Open Interest')['Open Interest'].sum() > 0 else 0

        n_p_atm = near_p[(near_p['Strike'] >= atm_lower) & (near_p['Strike'] <= atm_upper)]['Open Interest'].sum()
        n_p_otm = near_p[near_p['Strike'] < atm_lower]['Open Interest'].sum()
        near_p_ratio = n_p_otm / n_p_atm if n_p_atm > 0 else 0
        long_p_wgt = (long_p['Strike'] * long_p['Open Interest']).sum() / long_p['Open Interest'].sum() if long_p['Open Interest'].sum() > 0 else spot
        
        atm_put_dom = (n_p_atm / (n_p_atm + n_c_atm)) * 100 if (n_p_atm + n_c_atm) > 0 else 50.0

        out.append({
            'Date': dt, 'Near_C_Ratio': near_c_ratio, 'Long_P_Ratio': long_p_ratio, 'Long_P_OI': long_p_oi,
            'Bunker_Price': bunker_price, 'Near_P_Ratio': near_p_ratio, 'Long_P_Wgt': long_p_wgt, 
            'Total_P_OI': p['Open Interest'].sum(), 'ATM_Put_Dominance': atm_put_dom
        })

    opt_df = pd.DataFrame(out).sort_values('Date')
    opt_df['Total_P_OI_Lag'] = opt_df['Total_P_OI'].shift(1)
    
    opt_df['Near_C_Ratio_Drop'] = opt_df['Near_C_Ratio'].shift(1) - opt_df['Near_C_Ratio']
    opt_df['Long_P_OI_Growth'] = (opt_df['Long_P_OI'] / opt_df['Long_P_OI'].shift(1).replace(0, np.nan) - 1) * 100
    opt_df['Long_P_Wgt_Rollup'] = opt_df['Long_P_Wgt'] - opt_df['Long_P_Wgt'].shift(1)

    df = pd.merge(px, opt_df, on='Date', how='right').sort_values('Date').reset_index(drop=True)
    if 'EWY Price' in master_df.columns:
        for i, row in df.iterrows():
            if pd.isna(row['Close Price']) or row['Close Price'] == 0:
                match_px = master_df[master_df['Quote Date'] == row['Date']]['EWY Price']
                if not match_px.empty and match_px.iloc[0] > 0: df.at[i, 'Close Price'] = match_px.iloc[0]

    df['Close Price'] = df['Close Price'].ffill()
    df['10MA'] = df['Close Price'].rolling(window=10, min_periods=1).mean()
    df['20MA'] = df['Close Price'].rolling(window=20, min_periods=1).mean()

    # 선택된 핵심 로직 호출
    if version == "G버젼_하락추세조정":
        df = apply_logic_g_down(df)
    elif version == "C버젼":
        df = apply_logic_c(df)
    elif version == "G버젼_상승특화":
        df = apply_logic_g_up(df)

    # 모드에 따른 출력 필터링
    if mode == "구간 조회" and target_start and target_end:
        out_df = df[(df['Date'] >= pd.to_datetime(target_start)) & (df['Date'] <= pd.to_datetime(target_end))].copy()
    elif mode == "타임머신 (특정일)" and target_date:
        df_filtered = df[df['Date'] <= pd.to_datetime(target_date)]
        out_df = df_filtered.tail(10).copy()
    else:
        out_df = df.tail(10).copy()

    if out_df.empty:
        return pd.DataFrame()

    bot_short_col = '[하락장] 단기(콜투매/ATM)' if '[하락장] 단기(콜투매/ATM)' in out_df.columns else '[하락장] 단기(콜투매)'
    cols_to_print = ['Date', 'Close Price', '[상승장] 단기(풋발작)', '[상승장] 세력(롤업)', bot_short_col, '[하락장] 세력(벙커)', 'Phase']
    out_df = out_df[cols_to_print]
    out_df['Date'] = out_df['Date'].dt.strftime('%m/%d')
    out_df['Close Price'] = out_df['Close Price'].round(2)
    out_df.rename(columns={'Close Price': 'EWY($)', 'Phase': '현재 시장 국면 진단'}, inplace=True)
    
    return out_df

# =====================================================================
# [웹 UI] Streamlit 화면 구성
# =====================================================================
st.title("📈 EWY Quant Analytics V27")
st.markdown("**3-in-1 다중 전략 엔진 탑재 (Streamlit Web Version)**")

with st.sidebar:
    st.header("⚙️ 퀀트 엔진 버젼 선택")
    engine_version = st.radio(
        "버전",
        ("G버젼_하락추세조정", "C버젼", "G버젼_상승특화")
    )
    
    st.divider()
    
    st.header("▶ 분석 모드")
    mode_selection = st.selectbox(
        "조회 방식을 선택하세요",
        ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회")
    )
    
    target_date = None
    target_start = None
    target_end = None
    
    if mode_selection == "타임머신 (특정일)":
        target_date = st.date_input("기준일 선택", datetime.today())
    elif mode_selection == "구간 조회":
        col1, col2 = st.columns(2)
        with col1:
            target_start = st.date_input("시작일", datetime(2026, 6, 1))
        with col2:
            target_end = st.date_input("종료일", datetime(2026, 6, 30))
            
    run_button = st.button("🚀 분석 엔진 가동", type="primary", use_container_width=True)

if run_button:
    with st.spinner(f"[{engine_version}] 퀀트 엔진 연산 중..."):
        result_df = run_quant_engine_web(
            version=engine_version, 
            mode=mode_selection, 
            target_date=target_date, 
            target_start=target_start, 
            target_end=target_end
        )
        
        if not result_df.empty:
            st.success(f"✅ 연산이 완료되었습니다! ({mode_selection})")
            
            # Streamlit의 dataframe 출력 (테이블 크기 및 데이터 표시 방식 최적화)
            st.dataframe(
                result_df, 
                use_container_width=True, 
                hide_index=True,
                height=400
            )