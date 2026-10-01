"""옵션 거래량 마이크로스트럭처 레짐 분석 엔진 (V28.4)"""
from __future__ import annotations
import pandas as pd
import numpy as np

def run_volume_analysis(master_df: pd.DataFrame) -> pd.DataFrame:
    """마스터 데이터를 기반으로 거래량 및 미결제약정 결산 시차를 보정한 레짐 분석 수행"""
    if master_df.empty:
        return pd.DataFrame()

    df = master_df.copy()
    df['Quote Date'] = pd.to_datetime(df['Quote Date']).dt.tz_localize(None)
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date']).dt.tz_localize(None)
    df['DTE'] = (df['Expiration Date'] - df['Quote Date']).dt.days

    def calc_daily_microstructure(g):
        spot = g['EWY Price'].iloc[0]
        total_vol = g['Volume'].sum()
        total_oi = g['Open Interest'].sum()

        c = g[g['Option Type'] == 'C']
        p = g[g['Option Type'] == 'P']
        call_vol = c['Volume'].sum()
        put_vol = p['Volume'].sum()
        call_oi = c['Open Interest'].sum()
        put_oi = p['Open Interest'].sum()

        # 당일 만기(DTE <= 0)로 장 마감 후 자연 소멸되는 OI 별도 집계
        exp_oi_total = g[g['DTE'] <= 0]['Open Interest'].sum()
        exp_oi_put = p[p['DTE'] <= 0]['Open Interest'].sum()
        exp_oi_call = c[c['DTE'] <= 0]['Open Interest'].sum()

        # 초단기(DTE <= 3) 만기 왜곡을 제거한 유효 옵션 기준 IV 산출
        valid_g = g[(g['DTE'] >= 4) & (g['Implied Volatility'] > 0.01) & (g['Implied Volatility'] < 3.0)]
        if valid_g.empty:
            valid_g = g[g['Implied Volatility'] > 0.0]

        near_opts = valid_g[valid_g['DTE'] <= 30]
        far_opts = valid_g[valid_g['DTE'] > 30]

        near_iv = np.average(near_opts['Implied Volatility'], weights=near_opts['Volume'] + 1) if not near_opts.empty else np.nan
        far_iv = np.average(far_opts['Implied Volatility'], weights=far_opts['Volume'] + 1) if not far_opts.empty else np.nan
        backwardation = 1 if (pd.notna(near_iv) and pd.notna(far_iv) and near_iv > far_iv) else 0

        otm_puts = valid_g[(valid_g['Option Type'] == 'P') & (valid_g['Strike'] <= spot * 0.95)]
        atm_opts = valid_g[(valid_g['Strike'] >= spot * 0.95) & (valid_g['Strike'] <= spot * 1.05)]

        otm_put_iv = np.average(otm_puts['Implied Volatility'], weights=otm_puts['Volume'] + 1) if not otm_puts.empty else np.nan
        atm_iv = np.average(atm_opts['Implied Volatility'], weights=atm_opts['Volume'] + 1) if not atm_opts.empty else valid_g['Implied Volatility'].mean()
        put_skew = otm_put_iv - atm_iv if (pd.notna(otm_put_iv) and pd.notna(atm_iv)) else 0

        vol_dte_under_5 = g[g['DTE'] <= 5]['Volume'].sum()
        noise_ratio = vol_dte_under_5 / total_vol if total_vol > 0 else 0

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
            'Backwardation_Flag': backwardation,
            'Put_Skew': put_skew,
            'Noise_Ratio': noise_ratio
        })

    daily = df.groupby('Quote Date').apply(calc_daily_microstructure).reset_index()

    # 전산 오류로 인한 OI 비정상 증발 방어 및 보간
    for idx in range(1, len(daily)):
        prev_active_oi = daily.loc[idx - 1, 'Total_OI'] - daily.loc[idx - 1, 'Exp_OI_Total']
        curr_oi = daily.loc[idx, 'Total_OI']
        if prev_active_oi > 10000 and curr_oi < prev_active_oi * 0.30:
            daily.loc[idx, 'Total_OI'] = prev_active_oi
            daily.loc[idx, 'Put_OI'] = daily.loc[idx - 1, 'Put_OI'] - daily.loc[idx - 1, 'Exp_OI_Put']
            daily.loc[idx, 'Call_OI'] = daily.loc[idx - 1, 'Call_OI'] - daily.loc[idx - 1, 'Exp_OI_Call']

    # [핵심 패치] T일 파일에 기록된 OI 증감은 'T-1일 거래의 결산 결과(Settled OI Change)'임
    prev_active_total_oi = (daily['Total_OI'].shift(1) - daily['Exp_OI_Total'].shift(1)).replace(0, np.nan)
    prev_active_put_oi = (daily['Put_OI'].shift(1) - daily['Exp_OI_Put'].shift(1)).replace(0, np.nan)

    daily['Settled_OI_Diff'] = (daily['Total_OI'] - prev_active_total_oi).fillna(0)
    daily['Settled_OI_Chg_Pct'] = (daily['Settled_OI_Diff'] / prev_active_total_oi).fillna(0)
    daily['Settled_Put_OI_Chg_Pct'] = ((daily['Put_OI'] - prev_active_put_oi) / prev_active_put_oi).fillna(0)

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
    daily['IV_Change'] = daily['Avg_IV'].diff().fillna(0.0)

    # 사후 성과 검증용 수익률
    daily['Ret_T+1'] = (daily['EWY_Price'].shift(-1) / daily['EWY_Price'] - 1) * 100
    daily['Ret_T+3'] = (daily['EWY_Price'].shift(-3) / daily['EWY_Price'] - 1) * 100
    daily['Ret_T+5'] = (daily['EWY_Price'].shift(-5) / daily['EWY_Price'] - 1) * 100

    cond_r4 = (
        ((daily['Noise_Ratio'] >= 0.55) & (daily['Vol_Z'] >= 1.0)) |
        ((daily['Noise_Ratio'].shift(1).fillna(0) >= 0.55) & (daily['Settled_OI_Chg_Pct'].abs() >= 0.10))
    )

    cond_r1 = (
        (daily['DD_10'] <= -6.0) &
        ((daily['Ret_1D'] <= -3.0) | (daily['Pos_20D'] <= 0.20)) &
        (daily['Ret_1D'] <= 1.0) &
        (
            (daily['Put_Skew_Pct'] >= 75.0) |
            (daily['Vol_Z'] >= 0.3) |
            (daily['Put_Vol_Z'] >= 0.3) |
            (daily['IV_Change'] > 0)
        )
    )

    cond_r2_realtime = (
        (daily['Pos_20D'] >= 0.85) &
        (
            ((daily['Put_Skew_Pct'] >= 90.0) & ((daily['Put_Vol_Z'] >= 0.20) | ((daily['Near_High_60D'] >= 0.98) & (daily['Runup_10'] >= 14.0)))) |
            ((daily['Runup_10'] >= 7.5) & (daily['Vol_Z'] >= 0.8) & (daily['IV_Change'] <= -0.015))
        )
    )

    cond_r2_settled_oi = (
        ((daily['Pos_20D'].shift(1).fillna(0.5) >= 0.85) | (daily['Near_High_60D'].shift(1).fillna(1.0) >= 0.97)) &
        (daily['Runup_10'].shift(1).fillna(0) >= 7.5) &
        (daily['Pos_20D'] >= 0.65) &
        ((daily['Settled_Put_OI_Chg_Pct'] <= -0.02) | (daily['Settled_OI_Chg_Pct'] <= -0.02))
    )
    cond_r2 = cond_r2_realtime | cond_r2_settled_oi

    cond_r3 = (
        (daily['Vol_Z'] < 1.0) &
        (daily['Vol_Z'].shift(1).fillna(0) < 1.0) &
        (daily['IV_Change'] <= 0) &
        (daily['IV_Change'].shift(1).fillna(0) <= 0.01) &
        (daily['Settled_OI_Diff'] > daily['Total_OI'].shift(1).rolling(20, min_periods=5).mean().fillna(0) * 0.03)
    )

    conditions = [cond_r4, cond_r1, cond_r2, cond_r3]
    choices = [
        'Regime 4: 캘린더 롤오버 노이즈 (무시)',
        'Regime 1: 투매 클라이막스 (급락장 스큐과열 ➔ 매수기회)',
        'Regime 2: 고점 스큐 다이버전스 & 숏커버링 엑시트',
        'Regime 3: 가두리 방어벽 구축 (IV 하락 + 기관 Overwriting)'
    ]

    daily['Regime'] = np.select(conditions, choices, default='일반 횡보/진공 구간')

    def format_skew_status(r):
        skew = r['Put_Skew_Pct']
        if pd.isna(skew) or not np.isfinite(skew):
            return "   -   (초기구간)"
        dd = r['DD_10']
        pos = r['Pos_20D']
        ret = r['Ret_1D']
        if dd <= -6.0 and pos <= 0.40 and ret <= 1.0 and skew >= 75.0:
            return f"{skew:5.1f}% (🚨급락장 투매과열 ➔ 반등매수)"
        elif pos >= 0.85 and skew >= 90.0:
            return f"{skew:5.1f}% (⚠️고점권 헤지폭발 ➔ 다이버전스)"
        elif skew >= 90.0:
            return f"{skew:5.1f}% (🟡스큐과열 ➔ 단기경계)"
        elif pos >= 0.85 and skew <= 25.0:
            return f"{skew:5.1f}% (🔥고점권 안도과열)"
        else:
            return f"{skew:5.1f}% (➖중립)"

    daily['Put_Skew_진단'] = daily.apply(format_skew_status, axis=1)
    
    return daily