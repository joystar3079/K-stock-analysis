"""옵션 거래량 마이크로스트럭처 & 4분면(ΔOI×ΔIV) 무편향 레짐 분석 엔진 (V35.0)"""
from __future__ import annotations
import pandas as pd
import numpy as np


def run_volume_analysis(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    [V35.0 핵심 업그레이드 내역]
    1. Option Type ('Call'/'Put' -> 'C'/'P') 자동 정규화 및 날짜/계약 정렬 무결성 확보
    2. OCC 결산 시차 완벽 보정: T일 파일에 기록된 계약별 ΔOI_t(= OI_t - OI_{t-1})를
       실제 거래가 발생한 T-1일의 ΔIV_{t-1}(= IV_{t-1} - IV_{t-2}) 및 Volume_{t-1}과 1:1 매칭
    3. ATM(Spot ±3.5%) 고정 기간구조 산출로 Deep OTM 노이즈에 의한 가짜 백워데이션(91% 오작동) 제거
    4. 25-Delta(-0.15 ~ -0.35) 기준 스큐 산출로 급락장 근접 행사가 대량거래 시 스큐가 폭락하는 착시 제거
    5. 확증 편향 제거: 급락장(Regime 1)을 [1-A 풋벙커 매집], [1-B 진성 하방공습], [1-C 클라이막스 수급충돌],
       [1-V 바나 랠리 점화]로 분리하고 Put_Skew_진단 컬럼에 4분면 수급 요약 표시
    """
    if master_df.empty:
        return pd.DataFrame()

    df = master_df.copy()
    df.columns = [c.strip() for c in df.columns]

    # [패치 1] Option Type 표준화 ('Call'/'Put', 'C'/'P' 모두 'C', 'P'로 통일) 및 날짜 정렬
    df['Option Type'] = df['Option Type'].astype(str).str.strip().str.upper().str[0]
    df['Quote Date'] = pd.to_datetime(df['Quote Date']).dt.tz_localize(None).dt.normalize()
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date']).dt.tz_localize(None).dt.normalize()

    # 중복 계약 제거 및 계약별 시계열 정렬
    df = df.drop_duplicates(subset=['Contract Name', 'Quote Date'], keep='last').copy()
    df = df.sort_values(['Contract Name', 'Quote Date']).reset_index(drop=True)
    df['DTE'] = (df['Expiration Date'] - df['Quote Date']).dt.days

    num_cols = ['Strike', 'Bid', 'Ask', 'Last Price', 'Volume', 'Open Interest',
                'EWY Price', 'Implied Volatility', 'Delta']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # [패치 2] 계약별 시계열 변화량 산출 및 OCC 결산 시차(T일 dOI <-> T-1일 dIV) 정밀 정렬
    grp = df.groupby('Contract Name')
    df['Prev_OI'] = grp['Open Interest'].shift(1)
    df['Next_OI'] = grp['Open Interest'].shift(-1)
    df['Prev_IV'] = grp['Implied Volatility'].shift(1)

    # dIV_Today: T일 당일 장중 거래가 만든 IV 변화 (IV_t - IV_{t-1})
    df['dIV_Today'] = np.where(
        (df['Prev_IV'] > 0.05) & (df['Implied Volatility'] > 0.05),
        df['Implied Volatility'] - df['Prev_IV'],
        0.0
    )
    # dOI_Settled_On_T: T일 아침 파일에 찍힌 OI 변화 (= T-1일 거래의 결과)
    df['dOI_Settled_On_T'] = (df['Open Interest'] - df['Prev_OI']).fillna(0.0)
    # dIV_Of_Trade_Day: T일 아침 OI 변화를 만든 실제 거래일(T-1일)의 IV 변화
    df['dIV_Of_Trade_Day'] = grp['dIV_Today'].shift(1).fillna(df['dIV_Today'])

    def calc_daily_microstructure(g):
        spot = g['EWY Price'].iloc[0]
        total_vol = g['Volume'].sum()
        total_oi = g['Open Interest'].sum()

        c = g[g['Option Type'] == 'C']
        p = g[g['Option Type'] == 'P']
        call_vol, put_vol = c['Volume'].sum(), p['Volume'].sum()
        call_oi, put_oi = c['Open Interest'].sum(), p['Open Interest'].sum()

        exp_oi_total = g[g['DTE'] <= 0]['Open Interest'].sum()
        exp_oi_put = p[p['DTE'] <= 0]['Open Interest'].sum()
        exp_oi_call = c[c['DTE'] <= 0]['Open Interest'].sum()

        # [패치 3] 유효 옵션 필터링 (DTE >= 2 허용하여 만기 주간 본월물 증발 방지 + 호가 노이즈 제거)
        valid_g = g[
            (g['DTE'] >= 2) &
            (g['Implied Volatility'] > 0.05) &
            (g['Implied Volatility'] < 3.0) &
            ((g['Bid'] > 0.05) | (g['Volume'] >= 1) | (g['Open Interest'] >= 10))
        ].copy()
        if valid_g.empty:
            valid_g = g[(g['DTE'] >= 2) & (g['Implied Volatility'] > 0.01)].copy()

        valid_g['Liq_Weight'] = valid_g['Open Interest'] + (valid_g['Volume'] * 5.0) + 1.0

        # 등가격(ATM: Spot ±3.5% 이내) 옵션만으로 근월(DTE 2~21) vs 원월(DTE 35~120) 비교
        atm_pool = valid_g[(valid_g['Strike'] >= spot * 0.965) & (valid_g['Strike'] <= spot * 1.035)]
        if atm_pool.empty:
            atm_pool = valid_g[(valid_g['Strike'] >= spot * 0.94) & (valid_g['Strike'] <= spot * 1.06)]

        near_atm = atm_pool[atm_pool['DTE'] <= 21]
        far_atm = atm_pool[(atm_pool['DTE'] >= 35) & (atm_pool['DTE'] <= 120)]
        if far_atm.empty:
            far_atm = atm_pool[atm_pool['DTE'] > 21]

        near_iv = np.average(near_atm['Implied Volatility'], weights=near_atm['Liq_Weight']) if not near_atm.empty else np.nan
        far_iv = np.average(far_atm['Implied Volatility'], weights=far_atm['Liq_Weight']) if not far_atm.empty else np.nan
        term_spread = (near_iv - far_iv) if (pd.notna(near_iv) and pd.notna(far_iv)) else 0.0
        backwardation = 1 if term_spread > 0.005 else 0

        # [패치 4] 25-Delta 표준 스큐 산출 (DTE 14~90일 주력 구간, 딥 OTM 왜곡 차단)
        skew_pool = valid_g[(valid_g['DTE'] >= 14) & (valid_g['DTE'] <= 90)]
        if skew_pool.empty:
            skew_pool = valid_g

        puts_25d = skew_pool[(skew_pool['Option Type'] == 'P') & (skew_pool['Delta'] <= -0.15) & (skew_pool['Delta'] >= -0.35)]
        if puts_25d.empty:
            puts_25d = skew_pool[(skew_pool['Option Type'] == 'P') & (skew_pool['Strike'] >= spot * 0.88) & (skew_pool['Strike'] <= spot * 0.96)]

        calls_25d = skew_pool[(skew_pool['Option Type'] == 'C') & (skew_pool['Delta'] >= 0.15) & (skew_pool['Delta'] <= 0.35)]
        atm_mid = skew_pool[(skew_pool['Strike'] >= spot * 0.965) & (skew_pool['Strike'] <= spot * 1.035)]

        put25_iv = np.average(puts_25d['Implied Volatility'], weights=puts_25d['Liq_Weight']) if not puts_25d.empty else np.nan
        call25_iv = np.average(calls_25d['Implied Volatility'], weights=calls_25d['Liq_Weight']) if not calls_25d.empty else np.nan
        atm_iv = np.average(atm_mid['Implied Volatility'], weights=atm_mid['Liq_Weight']) if not atm_mid.empty else near_iv

        put_skew = (put25_iv - atm_iv) if (pd.notna(put25_iv) and pd.notna(atm_iv)) else 0.0
        put_call_skew = (put25_iv - call25_iv) if (pd.notna(put25_iv) and pd.notna(call25_iv)) else put_skew

        # [패치 5] 시차 보정된 ΔOI_Settled_On_T × ΔIV_Of_Trade_Day 4분면 수급 집계 (생존 만기 DTE >= 2)
        surv_p = p[p['DTE'] >= 2]
        surv_c = c[c['DTE'] >= 2]

        # Put 4분면 (시차 보정 기준)
        p_q1_long = surv_p[(surv_p['dOI_Settled_On_T'] > 0) & (surv_p['dIV_Of_Trade_Day'] > 0.001)]['dOI_Settled_On_T'].sum()
        p_q2_bunker = surv_p[(surv_p['dOI_Settled_On_T'] > 0) & (surv_p['dIV_Of_Trade_Day'] <= 0.001)]['dOI_Settled_On_T'].sum()
        p_q3_monetize = surv_p[(surv_p['dOI_Settled_On_T'] < 0) & (surv_p['dIV_Of_Trade_Day'] < -0.001)]['dOI_Settled_On_T'].abs().sum()

        # Call 4분면 (시차 보정 기준)
        c_q1_long = surv_c[(surv_c['dOI_Settled_On_T'] > 0) & (surv_c['dIV_Of_Trade_Day'] > 0.001)]['dOI_Settled_On_T'].sum()
        c_q2_over = surv_c[(surv_c['dOI_Settled_On_T'] > 0) & (surv_c['dIV_Of_Trade_Day'] <= 0.001)]['dOI_Settled_On_T'].sum()

        # 당일 실시간 거래량 기반 방향성 추정 (T일 장중 대량 거래의 IV 방향)
        rt_put_buy_vol = surv_p[surv_p['dIV_Today'] > 0.002]['Volume'].sum()
        rt_put_sell_vol = surv_p[surv_p['dIV_Today'] <= 0.002]['Volume'].sum()
        rt_call_buy_vol = surv_c[surv_c['dIV_Today'] > 0.002]['Volume'].sum()

        vol_dte_under_5 = g[g['DTE'] <= 5]['Volume'].sum()
        noise_ratio = vol_dte_under_5 / total_vol if total_vol > 0 else 0.0

        return pd.Series({
            'EWY_Price': spot,
            'Total_Vol': total_vol,
            'Call_Vol': call_vol,
            'Put_Vol': put_vol,
            'Total_OI': total_oi,
            'Call_OI': call_oi,
            'Put_OI': put_oi,
            'Exp_OI_Total': exp_oi_total,
            'Exp_OI_Put': exp_oi_put,
            'Exp_OI_Call': exp_oi_call,
            'Avg_IV': atm_iv,
            'Near_IV': near_iv,
            'Far_IV': far_iv,
            'Term_Spread': term_spread,
            'Backwardation_Flag': backwardation,
            'Put_Skew': put_skew,
            'Put_Call_Skew': put_call_skew,
            'P_Q1_Long': p_q1_long,
            'P_Q2_Bunker': p_q2_bunker,
            'P_Q3_Monetize': p_q3_monetize,
            'C_Q1_Long': c_q1_long,
            'C_Q2_Over': c_q2_over,
            'RT_Put_Buy_Vol': rt_put_buy_vol,
            'RT_Put_Sell_Vol': rt_put_sell_vol,
            'RT_Call_Buy_Vol': rt_call_buy_vol,
            'Noise_Ratio': noise_ratio
        })

    daily = df.groupby('Quote Date', group_keys=False).apply(calc_daily_microstructure).reset_index()
    daily = daily.sort_values('Quote Date').reset_index(drop=True)

    # 전산 오류로 인한 OI 비정상 증발 방어
    for idx in range(1, len(daily)):
        prev_active_oi = daily.loc[idx - 1, 'Total_OI'] - daily.loc[idx - 1, 'Exp_OI_Total']
        curr_oi = daily.loc[idx, 'Total_OI']
        if prev_active_oi > 10000 and curr_oi < prev_active_oi * 0.30:
            daily.loc[idx, 'Total_OI'] = prev_active_oi
            daily.loc[idx, 'Put_OI'] = daily.loc[idx - 1, 'Put_OI'] - daily.loc[idx - 1, 'Exp_OI_Put']
            daily.loc[idx, 'Call_OI'] = daily.loc[idx - 1, 'Call_OI'] - daily.loc[idx - 1, 'Exp_OI_Call']

    prev_active_total_oi = (daily['Total_OI'].shift(1) - daily['Exp_OI_Total'].shift(1)).replace(0, np.nan)
    prev_active_put_oi = (daily['Put_OI'].shift(1) - daily['Exp_OI_Put'].shift(1)).replace(0, np.nan)

    daily['Settled_OI_Diff'] = (daily['Total_OI'] - prev_active_total_oi).fillna(0)
    daily['Settled_OI_Chg_Pct'] = (daily['Settled_OI_Diff'] / prev_active_total_oi).fillna(0)
    daily['Settled_Put_OI_Chg_Pct'] = ((daily['Put_OI'] - prev_active_put_oi) / prev_active_put_oi).fillna(0)

    # 3일 누적 4분면 수급 합산
    for col in ['P_Q1_Long', 'P_Q2_Bunker', 'P_Q3_Monetize', 'C_Q1_Long', 'C_Q2_Over']:
        daily[col + '_3D'] = daily[col].rolling(3, min_periods=1).sum()

    WIN = 20
    def pure_past_zscore(series, window=WIN):
        past_mean = series.shift(1).rolling(window, min_periods=3).mean()
        past_std = series.shift(1).rolling(window, min_periods=3).std().replace(0, np.nan)
        return (series - past_mean) / past_std

    daily['Ret_1D'] = (daily['EWY_Price'].pct_change() * 100).fillna(0.0)
    roll_min_20 = daily['EWY_Price'].rolling(WIN, min_periods=1).min()
    roll_max_20 = daily['EWY_Price'].rolling(WIN, min_periods=1).max()
    denom_20 = (roll_max_20 - roll_min_20).replace(0, np.nan)
    daily['Pos_20D'] = ((daily['EWY_Price'] - roll_min_20) / denom_20).fillna(0.50)

    roll_max_60 = daily['EWY_Price'].rolling(60, min_periods=1).max()
    daily['Near_High_60D'] = (daily['EWY_Price'] / roll_max_60.replace(0, np.nan)).fillna(1.0)

    daily['Roll_Max_10'] = daily['EWY_Price'].rolling(10, min_periods=1).max()
    daily['DD_10'] = ((daily['EWY_Price'] / daily['Roll_Max_10'].replace(0, np.nan) - 1) * 100).fillna(0.0)
    daily['Roll_Min_10'] = daily['EWY_Price'].rolling(10, min_periods=1).min()
    daily['Runup_10'] = ((daily['EWY_Price'] / daily['Roll_Min_10'].replace(0, np.nan) - 1) * 100).fillna(0.0)

    daily['Vol_Z'] = pure_past_zscore(daily['Total_Vol'], WIN).fillna(0.0)
    daily['Put_Vol_Z'] = pure_past_zscore(daily['Put_Vol'], WIN).fillna(0.0)
    daily['Put_Skew_Pct'] = (daily['Put_Skew'].rolling(window=60, min_periods=5).rank(pct=True) * 100).fillna(50.0)
    daily['Put_Call_Skew_Pct'] = (daily['Put_Call_Skew'].rolling(window=60, min_periods=5).rank(pct=True) * 100).fillna(50.0)
    daily['IV_Change'] = daily['Avg_IV'].diff().fillna(0.0)

    # 사후 성과 검증용 수익률
    daily['Ret_T+1'] = (daily['EWY_Price'].shift(-1) / daily['EWY_Price'] - 1) * 100
    daily['Ret_T+3'] = (daily['EWY_Price'].shift(-3) / daily['EWY_Price'] - 1) * 100
    daily['Ret_T+5'] = (daily['EWY_Price'].shift(-5) / daily['EWY_Price'] - 1) * 100

    # [패치 6] 확증 편향을 제거한 다중 전략 레짐 판별식
    cond_r4 = (
        ((daily['Noise_Ratio'] >= 0.55) & (daily['Vol_Z'] >= 1.0)) |
        ((daily['Noise_Ratio'].shift(1).fillna(0) >= 0.55) & (daily['Settled_OI_Chg_Pct'].abs() >= 0.10))
    )

    is_dip_zone = (daily['DD_10'] <= -6.0) & ((daily['Ret_1D'] <= -2.5) | (daily['Pos_20D'] <= 0.20))

    # Regime 1-V: 바나(Vanna) 랠리 점화 (조정권에서 IV가 수축 전환하거나 풋 수익화 청산이 터지며 반등 시작)
    cond_r1_vanna = (
        (daily['DD_10'] <= -4.5) &
        (daily['IV_Change'] <= -0.005) &
        ((daily['P_Q3_Monetize_3D'] >= 3000) | (daily['Backwardation_Flag'].shift(1) == 1) | (daily['RT_Put_Sell_Vol'] > daily['RT_Put_Buy_Vol'] * 1.3))
    )

    # Regime 1-A: 저점 풋벙커 매집 & 콜선취매 우위 (하락장 속에서 Q2 풋매도 벙커 또는 Q1 콜선취매가 하방 롱풋을 압도)
    cond_r1_accum = (
        is_dip_zone &
        ((daily['P_Q2_Bunker_3D'] + daily['C_Q1_Long_3D'] * 0.8) >= daily['P_Q1_Long_3D']) &
        ((daily['P_Q2_Bunker_3D'] >= 5000) | (daily['C_Q1_Long_3D'] >= 5000) | (daily['RT_Put_Sell_Vol'] >= daily['RT_Put_Buy_Vol']))
    )

    # Regime 1-C: 투매 클라이막스 양방향 수급 격돌 (백워데이션 점화 + 하방 Q1 롱풋과 상방 Q1 콜선취매가 동시에 폭발)
    cond_r1_climax = (
        is_dip_zone &
        (~cond_r1_accum) &
        (daily['Backwardation_Flag'] == 1) &
        (daily['P_Q1_Long_3D'] >= 8000) &
        ((daily['C_Q1_Long_3D'] >= 8000) | (daily['RT_Put_Sell_Vol'] >= 15000))
    )

    # Regime 1-B: 진성 하방공습 & 풋 롤다운 경보 (방어벽 없이 Q1 진성 롱풋만 일방적으로 폭증 ➔ 네거티브 감마 폭락 주의)
    cond_r1_bear = is_dip_zone & (~cond_r1_accum) & (~cond_r1_climax)

    # Regime 2: 고점 스큐 다이버전스 & 커버드콜 엑시트
    cond_r2 = (
        (daily['Pos_20D'] >= 0.85) &
        (
            ((daily['Put_Skew_Pct'] >= 85.0) & ((daily['Put_Vol_Z'] >= 0.20) | (daily['P_Q1_Long_3D'] >= 5000))) |
            ((daily['Runup_10'] >= 7.5) & (daily['C_Q2_Over_3D'] > daily['C_Q1_Long_3D'] * 1.2)) |
            ((daily['Runup_10'].shift(1).fillna(0) >= 7.5) & (daily['Settled_OI_Chg_Pct'] <= -0.02))
        )
    )

    # Regime 3: 가두리 방어벽 구축 (콘탱고 + IV 안정 + Q2 풋/콜 매도 Overwriting 우위)
    cond_r3 = (
        (daily['Backwardation_Flag'] == 0) &
        (daily['IV_Change'] <= 0.005) &
        ((daily['P_Q2_Bunker_3D'] + daily['C_Q2_Over_3D']) > (daily['P_Q1_Long_3D'] + daily['C_Q1_Long_3D']) * 1.15)
    )

    conditions = [cond_r4, cond_r1_vanna, cond_r1_accum, cond_r1_climax, cond_r1_bear, cond_r2, cond_r3]
    choices = [
        'Regime 4: 만기 롤오버 노이즈 (무시)',
        'Regime 1-V: 바나(Vanna) 랠리 점화 (IV수축+풋수익화 ➔ 급반등)',
        'Regime 1-A: 저점 풋벙커 매집 우위 (Q2풋매도+Q1콜선취매 ➔ 분할매수)',
        'Regime 1-C: 투매 클라이막스 양방향 격돌 (백워데이션+롱풋vs콜매집 충돌)',
        'Regime 1-B: 진성 하방공습 & 롤다운 경보 (Q1롱풋 독주 ➔ 감마트랩 주의)',
        'Regime 2: 고점 헤지폭발 & 커버드콜 캡 (단기 엑시트 경보)',
        'Regime 3: 가두리 핀닝 & Overwriting (Q2 양매도 프리미엄 수취)'
    ]

    daily['Regime'] = np.select(conditions, choices, default='일반 횡보 / 방향성 탐색 구간')

    def format_skew_status(r):
        skew = r['Put_Skew_Pct']
        pc_skew = r['Put_Call_Skew_Pct']
        p_q1 = int(r['P_Q1_Long_3D'])
        p_q2 = int(r['P_Q2_Bunker_3D'])
        c_q1 = int(r['C_Q1_Long_3D'])
        if pd.isna(skew) or not np.isfinite(skew):
            return "   -   (초기구간)"
        if r['DD_10'] <= -6.0:
            if c_q1 >= 10000 and pc_skew <= 35.0:
                return f"{skew:4.0f}% (🔥콜선취매 역스큐 | 3일 C롱+{c_q1:,} vs P롱+{p_q1:,})"
            elif p_q2 >= p_q1:
                return f"{skew:4.0f}% (🛡️풋벙커 방어우위 | 3일 P벙커+{p_q2:,} vs P롱+{p_q1:,})"
            else:
                return f"{skew:4.0f}% (🚨하방 롱풋우위 | 3일 P롱+{p_q1:,} vs P벙커+{p_q2:,})"
        elif r['Pos_20D'] >= 0.85 and skew >= 85.0:
            return f"{skew:4.0f}% (⚠️고점권 헤지폭발 | 3일 P롱+{p_q1:,})"
        elif skew >= 85.0:
            return f"{skew:4.0f}% (🟡스큐과열 경계 | 3일 P롱+{p_q1:,})"
        elif r['Pos_20D'] >= 0.85 and skew <= 25.0:
            return f"{skew:4.0f}% (🔥고점권 안도과열)"
        else:
            return f"{skew:4.0f}% (➖중립 | P벙커+{p_q2:,}/P롱+{p_q1:,})"

    daily['Put_Skew_진단'] = daily.apply(format_skew_status, axis=1)
    return daily