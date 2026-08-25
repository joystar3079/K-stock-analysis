import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
from datetime import datetime
from scipy.stats import norm
import os
import warnings
from github import Github
import io

warnings.filterwarnings('ignore')
pd.set_option('display.unicode.east_asian_width', True)

# =====================================================================
# [웹 설정] 페이지 기본 세팅
# =====================================================================
st.set_page_config(page_title="EWY Quant Analytics V27", page_icon="📈", layout="wide")

# =====================================================================
# [수학 엔진] 미국식 이항 모형 (IV) 및 B-S 모형 (Delta)
# =====================================================================
def american_binomial_tree(S, K, T, r, q, sigma, opt_type, N=50):
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K) if opt_type.startswith('C') else max(0.0, K - S)
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    discount = np.exp(-r * dt)
    ST = S * (d ** np.arange(N, -1, -1)) * (u ** np.arange(0, N + 1))
    if opt_type.startswith('C'):
        V = np.maximum(0, ST - K)
    else:
        V = np.maximum(0, K - ST)
    for i in range(N - 1, -1, -1):
        ST = ST[:-1] / d
        V = discount * (p * V[1:] + (1 - p) * V[:-1])
        if opt_type.startswith('C'):
            V = np.maximum(V, ST - K)
        else:
            V = np.maximum(V, K - ST)
    return V[0]

def calculate_iv_american(target_price, S, K, T, r, q, opt_type, tol=1e-3, max_iter=50):
    if target_price <= 0 or T <= 0: return np.nan
    low_vol, high_vol = 1e-4, 5.0
    for _ in range(max_iter):
        mid_vol = (low_vol + high_vol) / 2.0
        price = american_binomial_tree(S, K, T, r, q, mid_vol, opt_type)
        if abs(price - target_price) < tol: return mid_vol
        if price > target_price: high_vol = mid_vol
        else: low_vol = mid_vol
    return mid_vol

def calculate_bs_delta(S, K, T, r, q, sigma, opt_type):
    if pd.isna(sigma) or sigma <= 0 or T <= 0: return np.nan
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if opt_type.startswith('C'): return np.exp(-q * T) * norm.cdf(d1)
    else: return np.exp(-q * T) * (norm.cdf(d1) - 1.0)

# =====================================================================
# [추출 엔진] Daily 옵션 데이터 수집 및 연산 로직
# =====================================================================
def extract_daily_options():
    symbol = 'EWY'
    DIVIDEND_YIELD = 0.02
    
    try:
        sofr_data = pdr.DataReader('SOFR', 'fred')
        sofr_rate = round(float(sofr_data['SOFR'].dropna().iloc[-1]), 2)
    except: sofr_rate = 3.62
    
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period="1d")
        etf_price = round(hist['Close'].iloc[-1], 2)
        quote_date = hist.index[-1].date()
    except: return None, "주가 데이터를 불러올 수 없습니다."
    
    try: expirations = ticker.options
    except: return None, "만기일 데이터를 가져올 수 없습니다."
    
    all_options = []
    for exp_date in expirations:
        try:
            opt_chain = ticker.option_chain(exp_date)
            calls, puts = opt_chain.calls.copy(), opt_chain.puts.copy()
            calls['Option Type'], puts['Option Type'] = 'Call', 'Put'
            calls['Expiration Date'], puts['Expiration Date'] = exp_date, exp_date
            all_options.extend([calls, puts])
        except: pass
        
    if not all_options: return None, "옵션 데이터가 없습니다."
    
    df = pd.concat(all_options, ignore_index=True)
    df.rename(columns={'contractSymbol': 'Contract Name', 'strike': 'Strike', 'bid': 'Bid', 'ask': 'Ask', 'lastPrice': 'Last Price', 'volume': 'Volume', 'openInterest': 'Open Interest'}, inplace=True)
    for col in ['Bid', 'Ask', 'Last Price', 'Volume', 'Open Interest']: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Quote Date'] = quote_date
    df['Secured Overnight Financing Rate'] = sofr_rate
    price_col_name = f"{symbol} Price"
    df[price_col_name] = etf_price
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date']).dt.date
    
    bus_days = np.busday_count(pd.to_datetime(df['Quote Date']).values.astype('datetime64[D]'), pd.to_datetime(df['Expiration Date']).values.astype('datetime64[D]'))
    df['T'] = np.maximum(bus_days, 0.5) / 252.0
    r = sofr_rate / 100.0
    
    iv_results, delta_results = [np.nan]*len(df), [np.nan]*len(df)
    
    progress_bar = st.progress(0)
    total_rows = len(df)
    
    for i, row in df.iterrows():
        if i % max(1, total_rows // 100) == 0: progress_bar.progress(min(i / total_rows, 1.0))
        S, K, T_val, opt_type = row[price_col_name], row['Strike'], row['T'], row['Option Type']
        bid, ask, last_price = row['Bid'], row['Ask'], row['Last Price']
        target_price = (bid + ask) / 2.0 if (pd.notnull(bid) and pd.notnull(ask) and bid > 0 and ask > 0) else last_price
        
        if target_price > 0 and pd.notnull(S) and pd.notnull(K) and T_val > 0:
            iv = calculate_iv_american(target_price, S, K, T_val, r, DIVIDEND_YIELD, opt_type)
            iv_results[i] = iv
            delta_results[i] = calculate_bs_delta(S, K, T_val, r, DIVIDEND_YIELD, iv, opt_type)
            
    progress_bar.empty()
    df['Implied Volatility'], df['Delta'] = iv_results, delta_results
    df['Implied Volatility'] = df['Implied Volatility'].apply(lambda x: round(x, 4) if pd.notnull(x) else "")
    df['Delta'] = df['Delta'].apply(lambda x: round(x, 4) if pd.notnull(x) else "")
    
    final_cols = ['Contract Name', 'Quote Date', 'Expiration Date', 'Option Type', 'Strike', 'Bid', 'Ask', 'Last Price', 'Volume', 'Open Interest', 'Secured Overnight Financing Rate', price_col_name, 'Implied Volatility', 'Delta']
    df_final = df[final_cols].copy()
    df_final['Volume'] = df_final['Volume'].astype(int)
    df_final['Open Interest'] = df_final['Open Interest'].astype(int)
    
    return df_final, None

# =====================================================================
# [엔진 1~3] 기존 버젼 로직 통합
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

    df['[상승장] 단기(풋발작)'] = top_short_list; df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매)'] = bot_short_list; df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df

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
        trend_up, mid_trend_up = curr_close > r['10MA'], r['10MA'] > r['20MA']
        phase = ""
        if trend_up:
            is_warning = r['Recent_Top_Warning'] > 0
            is_rollup = pd.notna(r['Long_P_Wgt_Rollup']) and r['Long_P_Wgt_Rollup'] > 2.0
            if is_warning and is_rollup: ceiling_active = True; phase = "⛔ 대천장(Ceiling) 확정 / 세력 방어벽 롤업 (전량 익절)"
            elif ceiling_active and curr_close > prev_close: ceiling_active = True; phase = "⛔ 대천장 유지 / 가짜 랠리 (익절 유지)"
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

    df['[상승장] 단기(풋발작)'] = top_short_list; df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매)'] = bot_short_list; df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df

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
            if is_warning and is_rollup: ceiling_active = True; phase = "⛔ 대천장(Ceiling) 확정 (전량 익절)"
            elif ceiling_active and curr_close > prev_close: ceiling_active = True; phase = "⛔ 대천장 유지 / 가짜 랠리"
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
                if bottom_prob >= 90.0 and "가짜 반등" not in phase and "압박" not in phase: phase = "⏳ 찐바닥 셋업 극대화" if not mid_trend_up else "⏳ 눌림목 셋업 극대화"
                elif bottom_prob >= 80.0 and ("본격 하락" in phase or "조정" in phase): phase = "🟡 바닥 다지기 진행 중" if not mid_trend_up else "🟡 견조한 조정 진행 중"
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

    df['[상승장] 단기(풋발작)'] = top_short_list; df['[상승장] 세력(롤업)'] = top_long_list
    df['[하락장] 단기(콜투매/ATM)'] = bot_short_list; df['[하락장] 세력(벙커)'] = bot_long_list
    df['Phase'] = phase_list
    return df

# =====================================================================
# [웹 엔진 코어] 분석 연산
# =====================================================================
@st.cache_data(ttl=3600)
def load_master_data():
    master_file = 'EWY_Options_V27_App_Master.pkl.gz'
    if os.path.exists(master_file):
        return pd.read_pickle(master_file)
    return pd.DataFrame()

def run_quant_engine_web(version, mode, target_date=None, target_start=None, target_end=None):
    master_df = load_master_data()
    
    # 💡 [핵심 해결] 오늘 방금 추출한 데이터가 메모리에 있다면 마스터 데이터에 즉시 병합!
    if 'recent_extracted_data' in st.session_state:
        new_df = st.session_state['recent_extracted_data'].copy()
        new_df['Quote Date'] = pd.to_datetime(new_df['Quote Date'])
        new_df['Expiration Date'] = pd.to_datetime(new_df['Expiration Date'])
        new_df['Option Type'] = new_df['Option Type'].apply(lambda x: 'C' if str(x).upper().startswith('C') else 'P')
        new_df.rename(columns={'EWY Price': 'EWY Price'}, inplace=True)
        master_df = pd.concat([master_df, new_df], ignore_index=True)
        master_df = master_df.drop_duplicates(subset=['Quote Date', 'Expiration Date', 'Option Type', 'Strike'], keep='last').sort_values('Quote Date').reset_index(drop=True)

    if master_df.empty:
        st.error("❌ 처리할 데이터가 없습니다.")
        return pd.DataFrame()

    try:
        end_date = (datetime.today() + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        px = yf.download("EWY", start="2024-01-01", end=end_date, progress=False, auto_adjust=False).reset_index()
        if isinstance(px.columns, pd.MultiIndex): px.columns = [c[0] for c in px.columns]
        px.rename(columns={'Date': 'Date', 'Close': 'Close Price'}, inplace=True)
        px['Date'] = pd.to_datetime(px['Date']).dt.tz_localize(None).dt.normalize()
        px = px.sort_values('Date').dropna(subset=['Close Price']).reset_index(drop=True)
    except Exception as e: px = pd.DataFrame()

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

        out.append({'Date': dt, 'Near_C_Ratio': near_c_ratio, 'Long_P_Ratio': long_p_ratio, 'Long_P_OI': long_p_oi, 'Bunker_Price': bunker_price, 'Near_P_Ratio': near_p_ratio, 'Long_P_Wgt': long_p_wgt, 'Total_P_OI': p['Open Interest'].sum(), 'ATM_Put_Dominance': atm_put_dom})

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

    if version == "G버젼_하락추세조정": df = apply_logic_g_down(df)
    elif version == "C버젼": df = apply_logic_c(df)
    elif version == "G버젼_상승특화": df = apply_logic_g_up(df)

    if mode == "구간 조회" and target_start and target_end: out_df = df[(df['Date'] >= pd.to_datetime(target_start)) & (df['Date'] <= pd.to_datetime(target_end))].copy()
    elif mode == "타임머신 (특정일)" and target_date: out_df = df[df['Date'] <= pd.to_datetime(target_date)].tail(10).copy()
    else: out_df = df.tail(10).copy()

    if out_df.empty: return pd.DataFrame()

    bot_short_col = '[하락장] 단기(콜투매/ATM)' if '[하락장] 단기(콜투매/ATM)' in out_df.columns else '[하락장] 단기(콜투매)'
    cols_to_print = ['Date', 'Close Price', '[상승장] 단기(풋발작)', '[상승장] 세력(롤업)', bot_short_col, '[하락장] 세력(벙커)', 'Phase']
    out_df = out_df[cols_to_print]
    out_df['Date'] = out_df['Date'].dt.strftime('%m/%d')
    out_df['Close Price'] = out_df['Close Price'].round(2)
    out_df.rename(columns={'Close Price': 'EWY($)', 'Phase': '현재 시장 국면 진단'}, inplace=True)
    return out_df

# =====================================================================
# [웹 UI] Streamlit 메인 화면 구성
# =====================================================================
st.title("📈 EWY Quant Analytics V27")
st.markdown("**3-in-1 다중 전략 엔진 탑재 (Streamlit Web Version)**")

with st.sidebar:
    st.header("📥 데이터 관리")
    if st.button("Daily 옵션데이터 추출 (실시간)", use_container_width=True):
        st.session_state['run_extraction'] = True
        
    st.divider()
    
    st.header("⚙️ 퀀트 엔진 버젼 선택")
    engine_version = st.radio("버전", ("G버젼_하락추세조정", "C버젼", "G버젼_상승특화"))
    
    st.divider()
    
    st.header("▶ 분석 모드")
    mode_selection = st.selectbox("조회 방식을 선택하세요", ("최근 시그널 분석", "타임머신 (특정일)", "구간 조회"))
    
    target_date = target_start = target_end = None
    if mode_selection == "타임머신 (특정일)": target_date = st.date_input("기준일 선택", datetime.today())
    elif mode_selection == "구간 조회":
        col1, col2 = st.columns(2)
        with col1: target_start = st.date_input("시작일", datetime(2026, 6, 1))
        with col2: target_end = st.date_input("종료일", datetime(2026, 6, 30))
            
    run_button = st.button("🚀 분석 엔진 가동", type="primary", use_container_width=True)

# --- 액션 1: 데이터 추출 실행 ---
if st.session_state.get('run_extraction', False):
    with st.spinner("야후 파이낸스에서 실시간 데이터를 수집하고 수학적 모델(IV/Delta)을 연산 중입니다... (약 1분 소요)"):
        df_ext, err = extract_daily_options()
        if err: st.error(err)
        else:
            st.session_state['recent_extracted_data'] = df_ext
            st.success("✅ 실시간 데이터 추출 및 연산 완료! (이제 아래의 다운로드 버튼을 눌러 저장하거나, 분석 엔진을 가동하세요)")
            
            csv = df_ext.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            quote_date_str = df_ext['Quote Date'].iloc[0].replace('-', '')
            file_name = f"EWY Option 분석데이터_{quote_date_str}.csv"
            
            st.download_button(label="📥 CSV 파일 다운로드 (PC/드라이브 백업용)", data=csv, file_name=file_name, mime='text/csv')
            st.dataframe(df_ext.head(5), use_container_width=True, hide_index=True)
    st.session_state['run_extraction'] = False

# --- 액션 2: 퀀트 엔진 가동 ---
if run_button:
    with st.spinner(f"[{engine_version}] 퀀트 엔진 연산 중..."):
        result_df = run_quant_engine_web(engine_version, mode_selection, target_date, target_start, target_end)
        
        if not result_df.empty:
            st.success(f"✅ 연산이 완료되었습니다! ({mode_selection})")
            if 'recent_extracted_data' in st.session_state:
                st.info("💡 방금 추출한 최신 실시간 데이터가 결합되어 진단되었습니다.")
            st.dataframe(result_df, use_container_width=True, hide_index=True, height=400)
