# [V4.3.7 · 2026-11-24] 배당 반영 IV 보정: 수집기 IV(연 2% 연속 배당 가정)를 EWY 실제 배당 일정(12월 1회 · DIVIDEND_EVENTS)으로 다시 풀어 스큐·버터플라이·패리티 베이시스·감마 플립·델타의 12월 배당 착시와 배당락일 IV 급변 착시 제거
# [V4.3.7 · 2026-11-24] 표시 교정: (3-3) 원인② 미점화일 기폭 풋·직하단 문구와 헤지 부호, 징후② 이름·등급 문구, (1-5) 3D 판정, '압도' 배율 기준, 눌림목 요약(실측 방어율), 포인트 4(순증일), 환율 회귀 R² 50% 미만이면 내재 환율 미표시, 핵심 카드가 읽는 감마 플립 문장 복원
# [V4.3.7 · 2026-11-24] (2-3)·(2-4) 현재가 = 중간호가(체결가 지연 차단) · (2-4) 보유측(매수/매도) 판정에서 '오늘 주가 x1.15'·'오늘 델타' 기준 삭제(매집 시점 정보만)
# [V4.3.7 · 2026-11-24] [데이터 품질 점검] 블록 · 병행(검증 중) 원인①② 기록 · 신호 기록 폴더 지정(PC 프로그램 EWY_SIGNAL_LOG_DIR / SIGNAL_LOG_DIR) · 흩어진 기록 파일 합치기 · 기록의 D선을 새 정의로 1회 재계산 · 프롬프트에 면책 문구 금지
# [V4.3.6 · 2026-11-24] 감마 플립(파이프라인 3) D 산식: 당일 만기 계약 제외(DTE≥1) · IV 해 실패 표시값(0.0001/5.0)은 같은 만기 외가격 스마일로 보간 · 수집기와 같은 기준(영업일/252 · SOFR · 배당 2%) · 탐색 구간(현가 0.85~1.25배)에 부호 전환이 없으면 '구간 내 플립 없음'(V4.3.5는 최소 |GEX| 지점을 선으로 출력) · 바나·참도 같은 기준으로 통일하고 가정 시나리오 계산값으로 표기 · '추세 전환 경계선'·'마지노선' 방향 해석 문구 삭제
# [V4.3.6 · 2026-11-24] 신호 기록·자동 채점 신설: 보고서를 만들 때 기준일·Tier별 신호(원인①·②·국면·레짐·D선·V4.3.5 방식 A선)를 OUTPUT_DIR의 'EWY_신호기록_채점.csv'에 저장하고, 다음 한국 정규장 KOSPI·삼성전자(야후 일봉)·EWY 24시간(바이낸스 EWYBUSDT 5분봉)·다음 미국 종가로 자동 채점 -> [섹션 6] (6-5)
# [V4.3.5 · 2026-11-22] 바이낸스 EWYBUSDT 시세가 기준일 15:30(KST) 이전에 없는 날(상장 당일 2026-06-23) 실행 오류(NoneType 서식) 수정 · pandas 3.1 dayofweek 경고 제거(day_of_week)
# [V4.3.4 · 2026-11-18] OI×IV 분면: 체결일 귀속 유효IV(소급 재분류 차단)·포지티브 감마 방석 표시 / 섹션 3-1: 환율 환산 대신 환율고정 KOSPI·항등식 점검 / 섹션 3-2: 1단계 0.5σ·Max Pain 자석 실측·방어율 실측
# [V4.3.3 · 2026-11-18] 미결산 레이더: 야후 미체결 이월(Stale) 거래량 제거·회전율 분모 보정·④-B 권리행사 구분 / 섹션 3-3: 원인① 본대 실재 검증·조건부 시나리오 표기와 실측 도달률
# [V4.3.2 · 2026-11-18] (2-4) 손익 판정 교정: 만기 손익분기(행사가-매집단가) 대신 현재 옵션가 기준 평가손익(MTM)으로 판정, 3선(풋 매도측) 손익·딜러 헤지 부호 반대로 계산
# [PC 프로그램용 · 2026-11-15] 분석 결과를 기준일 폴더(예: 20261112)에 나눠 저장 — 메인 실행부의 date_dir 참고
# ==============================================================================
# [V4.4] V4.2.9 + V4.3 통합: 레짐 점수는 V4.3 방식(2024 비학습 기간 상승/하락 판별 개선분 채택), 국면 모델은 확정 라벨(경계=실제 종가 고점·저점)로 재학습,
#        최종 판정 승격은 검증 통과 경보(분배 경보·기본 징후 2개 이상)와 국면·급락 위험도로 한정 (고점래치·3중 체크·원인①②는 참고 표시)
# ==============================================================================
# [V4.2.9] 사용자 지정 20개 국면 구간(2025-03-17~2026-11-05) 라벨 학습: 국면 판정(상승/하락/횡보) · 급락 위험도 · 신호 신뢰도표 신설,
#          과장 문구(75%+ 확률·100% 포착·Short Squeeze 임박) 검증 수치로 교체
# ==============================================================================
# [Google Colab V4.2] 지속 하락장(Distribution Crash) 100% 포착 4대 업그레이드 & 바이낸스(EWYBUSDT) 1시간봉 동시 회귀 엔진
#  - [V4.2 핵심 업그레이드 1 — Put 4분면 Vol-Crush 대칭 보정 및 고점 콜라(Collar) 헤지 복원]:
#    고점 부근에서 시장 전체 ATM IV가 급락(Vol-Crush)할 때 신규 매수된 헤지용 풋옵션까지 Put Q2(바닥 방어 풋 매도)로 오분류되던 현상을
#    대칭적 ATM IV 차감 보정(0.85 * ΔATM_IV)으로 해결하여 진성 하방 헤지 풋(Put Q1)을 정밀 복원합니다.
#  - [V4.2 핵심 업그레이드 2 — 레짐 D 고점 콘탱고 함정 차단 및 레짐 B(고점 분배) 전환 필터]:
#    진성 상방 콜(Call Q1)이 고갈되고 커버드콜(Q2)+롱콜청산(Q3)이 폭증한 고점 분배 국면에서 근월 콘탱고(-8%p)가 레짐 D(가두리 핀닝) 점수를
#    부풀리는 착시를 차단하고 레짐 B(진성 매도 & 하방 가속)로 가산점을 전환합니다.
#  - [V4.2 핵심 업그레이드 3 — 고점 도지(Doji) 비절벽형(Soft-Threshold) 커트라인 및 3영업일 연속성 래치(Rolling Latch)]:
#    고점 직후 약보합 도지(-0.22%)나 간발의 수치 차이(Call Q3 4,832계약 vs 5,000계약, 콜점유율 43.8% vs 40.0%)로 경보가 하루 만에 해제되지 않도록
#    비절벽형 조건과 고점 3영업일 연속성 래치(Rolling Latch)를 탑재했습니다.
#  - [V4.2 핵심 업그레이드 4 — 크로스-티어 중기 연료 고갈 경보 및 6단계 심층 감마 진공(Deep Vacuum Floor) 타깃 신설]:
#    3D·7D·20D 전 시계열에서 Call Q1 비중이 고갈될 때 기계적 눌림목 분할매수 권고를 자동 중단하고,
#    1차 방어선 붕괴 시 다단계 감마 도미노(Roll-Down)가 직행하는 6단계 심층 콘크리트 요새 타깃을 산출합니다.
#  - [V4.1 핵심 업그레이드 1 — 바이낸스(EWYBUSDT) ↔ 야후(KOSPI·삼성전자·환율) 주간장 1시간봉(1h) 동시 상관·회귀]:
#    한국 주간증시 개장 구간(09:00~15:30 KST)의 1시간 단위 야후파이낸스 시세(^KS11, 005930.KS, KRW=X)와
#    동일 시각(KST 정각) 바이낸스 API EWYBUSDT(24시간 대체거래소 연동 시세) 1시간봉을 1:1 매칭하여
#    시차(Time-Lag)가 0초인 순수 주간장 상관계수(r), 탄력성(Beta), 회귀기울기(Slope)를 정밀 도출합니다!
#  - [V4.1 핵심 업그레이드 2 — 15:30 KST 한국장 마감 시각 EWYBUSDT 자동 추출 + 수동 오버라이드 겸용]:
#    바이낸스 5분봉/1시간봉 API를 통해 기준일 15:30 KST 정각의 EWYBUSDT 가격을 자동으로 추출하여 영점(0.00%)으로 고정하며,
#    코랩 미국 IP 차단(HTTP 451) 우회용 다중 엔드포인트(data-api.binance.vision / Spot / Futures) 및 수동 입력 폴백을 완벽 지원합니다.
#  - [V4.1 핵심 업그레이드 3 — 장 마감 후(아침 8시) Bid=0 호가 초기화 에러 방어 및 4대 가짜 IV 필터 완비]:
#    미국장 마감 후 Bid/Ask가 0으로 비어 있을 때 발생하던 ZeroDivisionError 및 피벗 결측 에러를 원천 차단했습니다.
# ==============================================================================
import os
import re
import glob
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats

# 1. 구글 드라이브 마운트
try:
    from google.colab import drive
    drive.mount('/content/drive')
except ImportError:
    print("[알림] 로컬 또는 비-코랩 환경에서 실행 중입니다.")

# ==============================================================================
# #@title ⚙️ [설정 및 실행 모드] (그냥 실행하면 하단 콘솔에서 Step 1: Tier -> Step 2: 기준일 -> Step 3: ATS 동기화 창이 뜹니다)
# ==============================================================================
OUTPUT_DIR = "/content/drive/MyDrive/00. 주가모니터링/02. 옵션데이터분석/04. 주식시항분석"
INPUT_DIR  = os.path.join(OUTPUT_DIR, "입력데이터")

if not os.path.exists(INPUT_DIR):
    alt_output = "/content/drive/MyDrive/00. 주가모니터링/02. 옵션데이터분석/04. 주식시황분석"
    alt_input  = os.path.join(alt_output, "입력데이터")
    if os.path.exists(alt_input):
        OUTPUT_DIR, INPUT_DIR = alt_output, alt_input

TIER_SELECTION_MODE = "Tier 5: 전 계층 통합 마스터창 (All-in-One)" #@param ["대화형 메뉴로 실행 시점에 Tier 직접 선택 (Interactive Tier Prompt)", "Tier 1: 초단기 전술창 (T+0 ~ 1D)", "Tier 2: 단기 롤오버창 (3D vs 7D)", "Tier 3: 월간 감마창 (20D ~ 22D)", "Tier 4: 구조적 레짐창 (60D ~ 200D)", "Tier 5: 전 계층 통합 마스터창 (All-in-One)"]
VIEW_VERSION_MODE   = "모바일버젼: 표 재출력 금지 & 순수 해설 텍스트 HTML 보고서 (Mobile Version)" #@param ["대화형 메뉴로 실행 시점에 버전 직접 선택 (Interactive Version Prompt)", "PC버젼: 정량 표 전체 포함 표준 보고서 (PC Version)", "모바일버젼: 표 재출력 금지 & 순수 해설 텍스트 HTML 보고서 (Mobile Version)"]
DATE_SELECTION_MODE = "아래 지정한 과거 기준일로 바로 실행 (Preset Date)" #@param ["대화형 메뉴로 실행 시점에 기준일 직접 선택 (Interactive Date Prompt)", "최신 기준일 자동 실행 (Latest Date)", "아래 지정한 과거 기준일로 바로 실행 (Preset Date)"]
PRESET_TARGET_DATE  = "2026-10-16" #@param {type:"string"}

# #@markdown ---
# #@markdown ### ⚡ [V4.1 핵심] 바이낸스 API (`EWYBUSDT`) 1시간봉 주간장(09:00~15:30 KST) 동시 회귀 & 영점 자동 동기화 설정
# #@markdown - `USE_BINANCE_KRX_HOURLY_SYNC = True`이면 한국 주간장 개장 구간(09:00~15:30 KST)의 **야후 1시간봉(KOSPI·삼성전자·환율)**과 **바이낸스 API `EWYBUSDT` 1시간봉**을 동시간대 매칭하여 상관·회귀식을 도출하고, 15:30 KST 종가 시점의 `EWYBUSDT` 가격을 자동으로 영점(Origin)에 세팅합니다.
USE_BINANCE_KRX_HOURLY_SYNC = True #@param {type:"boolean"}
BINANCE_EWY_SYMBOL          = "EWYBUSDT" #@param {type:"string"}
USE_FULL_CUMULATIVE_HISTORY = True #@param {type:"boolean"}
# #@markdown ### 📒 [V4.3.6] 신호 기록·자동 채점 (보고서를 만들 때 신호를 OUTPUT_DIR의 CSV에 저장하고 다음 한국 정규장 결과로 채점)
USE_SIGNAL_LOG      = True #@param {type:"boolean"}
SIGNAL_LOG_FILENAME = "EWY_신호기록_채점.csv" #@param {type:"string"}
# #@markdown - [V4.3.7] `SIGNAL_LOG_DIR`: 신호 기록 파일이 있는 폴더(비우면 OUTPUT_DIR). PC 프로그램에서 폴더를 고르면 그 폴더가 우선합니다.
SIGNAL_LOG_DIR      = "" #@param {type:"string"}
# #@markdown - [V4.3.7] `USE_DIVIDEND_IV_FIX`: 수집기 IV(연 2% 연속 배당 가정)를 EWY 실제 배당 일정(12월 1회)으로 다시 계산
USE_DIVIDEND_IV_FIX = True #@param {type:"boolean"}

# [미래참조오류(Look-Ahead Bias) 방어 및 야후파이낸스 시점 동기화 설정]
STRICT_NO_LOOKAHEAD_YF = True   # True(권장): 선택된 기준일(anchor_date) 이후의 미래 시세 100% 차단
ANCHOR_TO_YF_SPOT      = True   # True: 동시간대(15:30 KST) EWYB/ATS 가격과 한국장 종가를 1:1 영점(0.00%)으로 고정 후 회귀 탄력성 적용

# 네트워크 오프라인 시 비상용 폴백(Fallback) 값
FALLBACK_KOSPI_PT    = 5950.0
FALLBACK_SAMSUNG_KRW = 232000
FALLBACK_USDKRW      = 1385.0

# ==============================================================================
# 2. 월가 4대 퀀트 분석 계층(Tier 1 ~ Tier 4 & 통합 마스터) 파라미터 및 강점·약점·활용목적 정의
# ==============================================================================
TIER_CONFIGS = {
    "1": {
        "code": "TIER_1",
        "name": "Tier 1 [초단기 전술창 | T+0 ~ 1D Intraday & 0DTE~2DTE Tactical]",
        "short_tag": "Tier1_초단기전술창",
        "horizon_str": "당일 장중(T+0 미결산) ~ 1영업일(1D) [보조 비교창: 3영업일(3D)]",
        "traj_days": 3,
        "win_short": 1,
        "win_long": 3,
        "vol_ts_days": 5,
        "cluster_dte": 10,
        "corr_days": 20,
        "halflife": 5,
        "strengths": (
            "익일(T+1) 미국 옵션청산소(OCC) 미결제약정(OI) 결산 이전에 발생하는 당일(T+0) 장중 기습 거래량(Volume), "
            "거래 회전율(Volume/OI), 실시간 내재변동성(ΔIV_1D) 역주행 급변 및 0DTE~2DTE 초단기 행사가 쪼개기(Strike-Splitting) 매복 물량을 하루 먼저 포착하는 데 탁월합니다."
        ),
        "weaknesses": (
            "관측 창이 1~3일로 짧아 장중 데이트레이더의 단기 노이즈(Chasing/Hedging)나 일회성 블록딜에 민감하게 흔들릴 수 있으며, "
            "4일 이전에 구축된 중장기 기관의 코어 풋 벙커나 거시적 추세(Big Picture)가 시야에서 누락되는 단면 착시 위험이 있습니다."
        ),
        "purpose": (
            "당일 데이트레이딩, 미국 본장 개장 직후 및 장 마감 시간외(ATS) 급변 대응, 한국 증시 시초가 갭(Gap) 방향성 판별, "
            "주간 옵션 만기일(OpEx) 전후 1~2일 단기 감마 스퀴즈(Gamma Squeeze) 및 핀닝(Pinning) 타점 포착에 활용합니다."
        ),
        "focus_guide": (
            "당일(T) 미결산 기습 거래량 레이더([섹션 2-④])와 초단기 만기 클러스터([섹션 2-⑤]), 그리고 1일(1D) vs 3일(3D) 수급 변화 속도에 최우선 가중치를 두고 분석하십시오."
        )
    },
    "2": {
        "code": "TIER_2",
        "name": "Tier 2 [단기 롤오버창 | 3D vs 7D Weekly Roll-Over Cycle]",
        "short_tag": "Tier2_단기롤오버창",
        "horizon_str": "3영업일(3D) vs 7영업일(7D, 1주 만기 + 직전 수·목 롤오버 2일 완전 주기)",
        "traj_days": 7,
        "win_short": 3,
        "win_long": 7,
        "vol_ts_days": 10,
        "cluster_dte": 21,
        "corr_days": 40,
        "halflife": 10,
        "strengths": (
            "주간 옵션 만기(금요일) 이틀 전(수·목요일)부터 시작되는 기관의 사전 롤오버(Pre-OpEx Roll)와 OCC T+1 결산 시차를 완벽히 포괄하는 "
            "7영업일(T-6 ~ T) 시계열 창을 사용하여, 3일 이동창(3D)에서 4~7일 전 코어 포지션이 누락되는 '이월 탈락 착시'와 '기점 효과(Base Effect) 왜곡'을 제거합니다."
        ),
        "weaknesses": (
            "주간 만기 단위의 롤오버 흐름에는 최적이나, 한 달 이상 장기 누적된 정기 월간 만기(Monthly OpEx)의 구조적 감마 중심축 이동이나 "
            "분기 단위의 거시적 변동성 레짐 전환을 판별하기에는 시계열 길이가 다소 짧다는 한계가 있습니다."
        ),
        "purpose": (
            "1~2주 호흡의 단기 스윙 트레이딩, 주간 만기 통과 후 차주 바나(Vanna) 랠리 본발동 여부 판별, "
            "최근 7일간의 수급 모멘텀 강화(Accumulation) vs 고갈(Exhaustion) 다이버전스 진단에 활용합니다."
        ),
        "focus_guide": (
            "최근 7영업일 레짐·수급 궤적표([섹션 1-2])와 3일(3D) vs 7일(7D) 누적 OI 생애주기 비교([섹션 2-②, ③])를 중심으로 수급 모멘텀의 지속성과 다이버전스를 심층 분석하십시오."
        )
    },
    "3": {
        "code": "TIER_3",
        "name": "Tier 3 [월간 감마창 | 7D vs 20D~22D Monthly OpEx Gamma Map]",
        "short_tag": "Tier3_월간감마창",
        "horizon_str": "7영업일(7D) vs 20영업일(20D, 1개월 정기 월간 만기 사이클)",
        "traj_days": 10,
        "win_short": 7,
        "win_long": 20,
        "vol_ts_days": 20,
        "cluster_dte": 45,
        "corr_days": 60,
        "halflife": 15,
        "strengths": (
            "매월 세 번째 금요일 도래하는 정기 월간 옵션 만기(Monthly OpEx, 20~22거래일 주기)를 기준으로 한 달간 축적된 거대 기관의 "
            "콘크리트 풋 벙커(Put Wall)와 상단 커버드콜 저항벽(Call Wall), 마켓 메이커(MM)의 월간 감마(Gamma)·바나(Vanna) 중심축 이동을 일일 노이즈 없이 규명합니다."
        ),
        "weaknesses": (
            "7일~20일 누적 데이터를 사용하므로 중기 추세 신뢰도는 높지만, 당일이나 전일에 갑자기 터진 초단기 기습 공습(0DTE~2DTE Ambush)이나 "
            "급격한 장중 변곡점에서는 신호가 1~2일 후행(Lagging)하여 단기 고점/저점 타점이 둔감해질 수 있습니다."
        ),
        "purpose": (
            "2주~1개월 호흡의 포지션 트레이딩, 정기 월간 만기 전후의 중기 변곡점 포착, "
            "현물(EWY·KOSPI·삼성전자)의 핵심 분할 매수 지지선(1·2차 풋 요새) 및 분할 익절 목표가(1·2차 Call Wall) 설정에 활용합니다."
        ),
        "focus_guide": (
            "최근 20거래일 변동성 곡면 추이([섹션 2-①])와 7일(7D) vs 20일(20D) 누적 포지션 변화([섹션 2-②, ③]), 그리고 월간 Call/Put Wall의 중심축 이동을 최우선으로 분석하십시오."
        )
    },
    "4": {
        "code": "TIER_4",
        "name": "Tier 4 [구조적 레짐창 | 20D vs 60D~200D Macro Regime & LEAPS]",
        "short_tag": "Tier4_구조적레짐창",
        "horizon_str": "20영업일(20D) vs 60영업일(60D) 및 연간 누적 백분위수(Expanding %ile)",
        "traj_days": 15,
        "win_short": 20,
        "win_long": 60,
        "vol_ts_days": 30,
        "cluster_dte": 365,
        "corr_days": 120,
        "halflife": 30,
        "strengths": (
            "분기(60거래일)~연간(200거래일) 누적 백분위수(Expanding %ile)와 장기 옵션(LEAPS)·합성 선물(Synthetic Long/Short) 포지션을 해부하여 "
            "현재의 변동성·스큐·꼬리위험이 역사적 극단치(예: 85~95%ile)에 도달했는지 판독하고, EWY-KOSPI-삼성전자-환율 간의 구조적 회귀 탄력성(Beta)을 정밀 도출합니다."
        ),
        "weaknesses": (
            "호흡이 매우 긴(20일~60일) 거시적 레짐 판독 모델이므로, 이번 주 만기일(OpEx)의 단기 핀닝 가격이나 당일 장중의 전술적 매매 타이밍을 "
            "정밀하게 짚어내는 데에는 부적합하며 단기 급등락 시 시차(Lag)가 발생합니다."
        ),
        "purpose": (
            "분기~반기 단위의 중장기 자산배분 및 코어 현물(삼성전자·지수) 비중 조절, "
            "패닉 투매 클라이막스 진바닥(Capitulation Bottom) 및 장기 대세 고점(Distribution Top) 판별에 활용합니다."
        ),
        "focus_guide": (
            "누적 백분위수(%ile) 기준 변동성 레짐의 역사적 위치([섹션 2-①]), 20일(20D) vs 60일(60D) 장기 원월물·LEAPS 수급([섹션 2-②]), 그리고 이종자산 회귀 탄력성([섹션 3])을 중심으로 분석하십시오."
        )
    },
    "5": {
        "code": "TIER_ALL",
        "name": "Tier 1~4 통합 마스터창 [All-in-One Multi-Tier | T+0 ~ 7D ~ 60D]",
        "short_tag": "Tier통합_마스터창",
        "horizon_str": "당일(T+0) 미결산 + 단기(3D vs 7D) 롤오버 + 월간 감마 + 구조적(60D) 회귀 통합",
        "traj_days": 7,
        "win_short": 3,
        "win_long": 7,
        "vol_ts_days": 10,
        "cluster_dte": 15,
        "corr_days": 60,
        "halflife": 15,
        "strengths": (
            "Tier 1(당일 미결산 기습 레이더), Tier 2(3일 vs 7일 롤오버 추세 궤적), Tier 3(전체 잔존 만기 감마 지형도), "
            "Tier 4(누적 백분위수 및 60일 시계열 상관·회귀 환산)의 4대 계층을 단일 데이터북에 입체적으로 결합하여 단기 타이밍과 중장기 방향성을 동시에 교차 검증합니다."
        ),
        "weaknesses": (
            "단기(T+0/3D) 전술 신호와 중장기(7D/60D) 구조적 신호가 한 보고서에 동시에 제시되므로, 단기 조정 속 중장기 매집 국면처럼 "
            "시계열 간 방향이 충돌할 때 투자자가 본인의 투자 호흡(단타 vs 스윙 vs 장투)을 명확히 구분하여 읽어야 합니다."
        ),
        "purpose": (
            "전방위 실전 트레이딩 및 리스크 관리용 마스터 보고서 작성, 단기(1D/3D) 전술과 중기(7D/60D) 전략 간의 정합성 및 다이버전스 교차 검증에 활용합니다."
        ),
        "focus_guide": (
            "Tier 1(당일 미결산 레이더) -> Tier 2(7영업일 수급 궤적 및 3D vs 7D 비교) -> Tier 3(감마 지형도) -> Tier 4(60일 회귀 환산 좌표)를 유기적으로 연결하여 입체적으로 분석하십시오."
        )
    }
}

# ==============================================================================
# 3. [V4.1 핵심] 쉬운 언어 해설 · 표 독해 가이드 · 3단계 요약이 내장된 동적 프롬프트 생성 함수 (PC / MOBILE 모드 분기)
# ==============================================================================
def build_tier_embedded_prompt(t_cfg, view_version="PC"):
    ws = t_cfg['win_short']
    wl = t_cfg['win_long']
    td = t_cfg['traj_days']

    if view_version == "MOBILE":
        output_rule_block = f"""6. [📱 모바일 버젼 전용 출력 조건 — 표(Table) 재출력 전면 금지 & 모바일 텍스트 전용 HTML 파일 생성]:
   - 모든 정량 표(Table)는 이미 엔진이 별도의 뷰어로 사전 생성해 두었으므로, 하단 목차에 '표' 또는 'HTML 요약표'라는 표현이 있더라도 마크다운 표나 HTML 표(<table> 태그)를 절대 다시 그리지 마십시오. (데이터북의 파이프(|) 표를 파싱해 출력하는 작업도 절대 금지합니다.)
   - 대화창 본문에는 첫 줄에 "[기준일] 1순위 레짐(확률) | 국면(확률) · 급락 위험도 | EWY 종가" 1줄만 적고, 텍스트가 길어 모바일 대화창에서 바로 보기가 어려우므로 본문 해설을 채팅창에 바로 생성하지 마십시오.
   - 대신 곧바로 이어서 [섹션 0]부터 [섹션 5]까지의 '📖 핵심 독해 가이드'와 '💡 투자자 눈높이 쉬운 해설 및 실전 판단'만 순수 텍스트 구조(제목·글머리 기호·문단, <table> 태그 완전 배제)로 끝까지 빠짐없이 작성하여 모바일 가독성에 최적화된 단일 HTML 파일(.html)로 생성해 내려받을 수 있게 제공하십시오.
   - 단일 실행 타임아웃을 막기 위해 필요시 2~3단계 분할 이어쓰기(섹션 0~1 -> 섹션 2 -> 섹션 3~5)로 같은 HTML 파일에 이어 붙여 완성하십시오.
   - 모바일 HTML 규칙: 1) <table> 태그 및 마크다운 표 전면 금지 2) 본문 태그에 인라인 style·class 속성 금지 3) <style>은 10줄 이내(모바일 화면 여백·줄간격·글자크기 가독성 최적화) 4) 섹션 0~5는 각각 <details open><summary>로 감싸기 5) 내용을 축약하거나 '이하 생략'·'…'으로 끝내지 말 것
7. [완결성 및 분량 최적화 체크리스트 (모바일 버젼)]:
   - 인위적인 글자 수 늘리기를 금지합니다. 표를 그리지 않는 대신 데이터북의 각 표([섹션 1-1], [섹션 1-2] {td}영업일 궤적, [섹션 1-4]·[섹션 1-5] 징후 진단, [섹션 2-①] 변동성 곡면, [섹션 2-②] (2-1)~(2-4), [섹션 2-③] 감마 지형, [섹션 2-④, ⑤] 미결산·클러스터, [섹션 3-1]~[섹션 3-3] 조견표, [섹션 4] 한계점, [섹션 5] 신호 신뢰도 및 6단계 계측치)에 담긴 핵심 수치를 해설 문장 속에 정확히 인용하여, 표 없이 텍스트만 읽어도 모든 수급 인과관계와 실전 타점이 완벽히 이해되도록 섹션 0~5를 밀도 있게 작성하십시오.
8. [제출 전 자동 검산]:
   - 완성된 모바일 HTML 파일에 달러 기호($)와 <table> 태그가 각각 0개인지 확인하고, 본문에 인용된 레짐 4개 확률, 국면 확률, 급락 위험도, Call·Put 4분면 {ws}일 합계, 감마 플립 가격, 실질 BEP, 단기 Max Pain, 1시그마 주간 레인지가 원문과 일치하는지 검증한 뒤 제출하십시오."""
    else:
        output_rule_block = f"""6. [출력 형식 및 타임아웃 방지 필수 규칙 (파이썬 표 자동 변환 & 분할 이어쓰기)]:
   - 대화창 본문에는 "[기준일] 1순위 레짐(확률) | 국면(확률) · 급락 위험도 | EWY 종가" 1줄만 쓰고 요약을 덧붙이지 마십시오.
   - 보고서 전문(섹션 0~5)은 단일 HTML 파일(.html)로 만들어 내려받을 수 있게 제공하십시오.
   - [핵심: 무한 로딩 및 토큰 초과 방지] 코드 실행 도구(Python)를 쓸 수 있는 환경에서는 AI가 데이터북의 표 숫자를 일일이 다시 타이핑하지 말고, 파이썬 코드로 첨부된 .txt 파일을 직접 읽어(open) 파이프(|) 구분자 표를 HTML <table>로 자동 변환(이때 '$'는 '달러'로, '²'는 '제곱'으로, 'σ'는 '시그마'로, 'Δ'는 '델타'로, 'Γ'는 '감마'로 자동 치환)하여 삽입하십시오.
   - 단일 실행 타임아웃을 막기 위해 반드시 2~3번의 파이썬 실행으로 나누어(1차: 표 파싱 함수 및 섹션 0~1 저장 -> 2차: 섹션 2 이어쓰기 -> 3차: 섹션 3~5 이어쓰기 및 검산) 같은 HTML 파일에 이어 붙여 완성하십시오.
   - HTML 규칙: 1) 본문 태그(table, tr, td 등)에 style·class 속성 금지 2) <style>은 10줄 이내(모바일에서 표 가로 스크롤) 3) 섹션 0~5는 각각 <details open><summary>로 감싸기 4) 표의 행을 줄이거나 '이하 생략'·'…'으로 끝내지 말 것
7. [완결성 및 분량 최적화 체크리스트]:
   - 인위적인 글자 수 늘리기(예: 3만 자 강제)를 금지합니다. 불필요한 미사여구와 중복 서술을 배제하고 핵심 수급 인과관계와 실전 타점 위주로 밀도 있게 작성하되, 섹션 2를 가장 상세히 분석하십시오.
   - 다음 데이터북 표는 행을 빠짐없이 HTML 표로 포함하십시오: [섹션 1-1] 레짐 4개·국면 판정·급락 위험도, [섹션 1-2] 궤적표 전체, [섹션 1-4]·[섹션 1-5] 징후 진단표, [섹션 2-①] 변동성 곡면 추이표, [섹션 2-②] (2-1)~(2-4) 표, [섹션 2-③] 감마 지형표, [섹션 2-④, ⑤] 미결산 및 클러스터 표, [섹션 3-1]~[섹션 3-3] 조견표, [섹션 4] 한계점 요약표, [섹션 5] 신호 신뢰도표와 6단계 계측 요약표.
8. [제출 전 자동 검산]:
   - 마지막 파이썬 실행 단계에서 완성된 HTML 파일에 달러 기호($)가 0개인지 확인하고, 레짐 4개 확률, 국면 확률, 급락 위험도, Call·Put 4분면 {ws}일 합계, 감마 플립 가격, 실질 BEP, 단기 Max Pain, 1시그마 주간 레인지가 원문과 일치하는지 검증한 뒤 제출하십시오."""

    ver_title_tag = "📱 모바일버젼 (표 제외 · 순수 텍스트 해설 HTML)" if view_version == "MOBILE" else "💻 PC버젼 (정량 표 전체 포함 표준 HTML)"

    return f"""[시스템 명령: 아래 프롬프트 지침({ver_title_tag})과 정량 데이터북을 읽고 즉시 심층 분석 보고서를 작성하십시오.]

당신은 글로벌 매크로 헤지펀드의 수석 파생상품(Options) 퀀트 스트래티지스트이자, 복잡한 파생상품 미시구조 데이터를 개인 및 기관 투자자가 직관적으로 이해할 수 있는 쉬운 언어로 번역해 주는 최고의 투자 전략가입니다.
첨부된 텍스트 파일(.txt)은 구글 코랩(Python)을 통해 EWY 옵션 체인 마스터 데이터와 야후파이낸스·바이낸스(KOSPI·삼성전자·원/달러 환율·EWYBUSDT) 1시간봉 시계열을 미래참조오류(Look-Ahead Bias) 없이 분석 기준일 시점으로 절단하고, 장중 틱(Tick) 부재를 극복하는 '월가 4대 퀀트 수학적 우회 모델(Mathematical Proxy Pipeline)'을 탑재해 추출한 [EWY 옵션 미시구조 4대 전략 정밀 판독 데이터북 — {t_cfg['name']} | 출력모드: {ver_title_tag}]입니다.

[절대 준수 원칙: 100% 데이터 앵커링 + 쉬운 언어 번역 + 기호 깨짐 방지 + 월가 4단계 파이프라인 통합]
1. 할루시네이션 엄금: 임의로 수치를 추정하지 말고 반드시 데이터북 내부의 계량 수치, 계약명(만기일·행사가), {td}영업일 추이, 확률(%)을 그대로 인용하십시오. 데이터북에 없는 수치를 직접 계산해 쓸 때는 수치 뒤에 '(계산)'을 붙이십시오.
2. 단일 기준일 매몰 금지 ({ws}일 vs {wl}일 및 최근 {td}영업일 추세 대조): 조회 기준일(T) 하루 수치만 보지 말고 최근 {td}영업일 흐름 속에서 ① 상승 연료(Call Q1) 강화 vs 고갈 여부, ② 단기 창({ws}D)에서 빠진 장기 창({wl}D) 코어 포지션의 최신OI 생존 여부, ③ 주가와 변동성(IV·Skew·Butterfly) 간의 선행 다이버전스를 대조하십시오.
3. 기호 깨짐 및 렌더링 오류 100% 방지 규칙 (필수):
   - 보고서 본문과 표에서 달러 기호($)나 LaTeX 수식 기호를 절대 사용하지 마십시오. (달러 기호와 %가 한 문장에 쓰이면 수식 렌더러 충돌로 글자가 깨집니다.)
   - 모든 가격과 지표는 반드시 '137.01달러', '+3.04%', '+20.64%p', '5,127pt', '189,700원', '델타', '감마', '1시그마', 'R제곱', '->' 형태의 순수 한글·숫자 텍스트로만 표기하십시오.
4. 전문 용어 및 '월가 4단계 실전 파이프라인'의 쉬운 일상 언어(Easy-Quant) 동시 번역 의무:
   - [파이프라인 1단계: 변동성 곡면 역산 & RND 확률지도] ☞ "옵션 가격에 숨은 공포·탐욕을 분해해 현물 차트엔 안 보이는 '미래 주가 확률 지도'와 '블랙스완 꼬리 폭락/급등 확률(Cornish-Fisher 2시그마 꼬리 확률)'을 그리는 내비게이션 (근월-원월 백워데이션 = '단기 응급실 경보등', 25D Skew = '하방 공포 온도계', 25D Butterfly = '양방향 급등락 감마 폭발 지진계')"
   - [파이프라인 2단계: 비대칭 수급 팩터 & 풋-콜 패리티 시초가 베이시스] ☞ "큰손이 현물보다 레버리지가 큰 옵션에 먼저 몰래 베팅한 흔적을 잡는 '선도 세력 방아쇠 탐지기' (Call Q1 = '진짜 로켓 상승 연료', Call Q2 = '머리 위 콘크리트 천장 뚜껑', Put Q2 = '바닥 현금 방석', Put Q1 = '하락 시한폭탄', 풋-콜 패리티 합성선물 베이시스 = '옵션 시장이 미리 반영한 내일 아침 한국 증시 시초가 차익거래 매수/매도 압력')"
   - [파이프라인 3단계: 딜러 헤지 시뮬레이션 (GEX · 감마 플립 · 바나 · 참 · 합성공매도)] ☞ "뉴스와 무관하게 마켓메이커(딜러)가 포지션 중립을 맞추려고 기계적으로 쏟아내야 하는 강제 매수·매도 주식 수 계산기 (감마 플립선 = '딜러 순감마의 부호가 바뀌는 계산상 가격. 방향(추세) 신호가 아니라 변동 폭 구간의 경계이며, 2026년 24시간 시세 측정에서는 선 아래에서 한국장 변동 폭이 커지는 경향이 있었음. "구간 내 플립 없음"이면 딜러 감마가 현가 0.85~1.25배 전 구간에서 한쪽으로 쏠린 상태', 바나·참 = '변동성 안정화[IV 하락]와 시간 경과를 가정했을 때 딜러가 되사야 하는 주식 수의 시나리오 계산값(실제 매수 보장 아님)', 합성 공매도 본대[Deep ITM Put] = '딜러에게 1계약당 80~100주의 상시 대리 공매도를 강제하는 장외 공매도 대못', 매집원가 BEP = '공매도 세력의 실제 누적 원금 마지노선')"
   - [파이프라인 4단계: 다년도 정규화 레짐 전이 사령탑] ☞ "연도별 거래량 스케일 차이를 상대 비중(% of Total OI)과 252일 롤링 백분위수로 정규화하고, 1~3단계 신호를 종합해 오늘 '저점 분할 매수(레짐 A)'할지, '추격 금지/현금 확보(눌림목 경보)'할지, '하방 헤지(레짐 B/분배 폭락)'할지 최종 결정하는 컨트롤 타워"
5. 로딩 최적화형 '통합 독해 가이드 & 투자자 해석' 작성 규칙:
   - 섹션 1~3의 각 항목에서 [📖 표 핵심 독해 가이드]와 [💡 투자자 눈높이 쉬운 해설 & 실전 판단]을 명확히 구분하여 서술하십시오. (단, 하위 표가 여러 개인 섹션 2-②와 섹션 2-④·⑤는 섹션별 통합 독해 가이드 1세트로 묶어서 해설하십시오.)
   - [💡 실전 판단]은 '조건 -> 행동 -> 무효화 조건(손절·재평가 가격)' 순서로 단정적으로 쓰고, 각 판단 뒤에 근거 수치를 괄호로 붙이십시오.
   - [데이터 품질 점검] 데이터북의 '[데이터 품질 점검]' 블록에 적힌 항목(배당 반영 IV 보정, 체결가 지연, 레이더 IV 기준, 환율 회귀 설명력, 병행 기록 등)은 엔진이 이미 처리한 한계입니다. 이를 다시 '오류'로 지적하거나 숫자를 임의로 고치지 말고, 블록에 없는 새 이상만 해당 위치에 '[데이터 이상 의심] ...' 한 줄로 적으십시오. '병행 기록(검증 중)' 신호는 판단 근거로 쓰지 마십시오.
   - 보고서 어디에도 '투자 판단과 책임은 투자자 본인에게 있다' 같은 면책 문구나 투자 주의 문구를 넣지 마십시오.
{output_rule_block}

---

[보고서 필수 작성 목차 및 분석 지침]

## 0. [분석 모델 개요] 선택된 월가 퀀트 계층({t_cfg['name']}) 및 월가 4단계 파이프라인 작동 원리 브리핑
- 첨부 파일 상단 프로필을 바탕으로 ① 분석 시계 및 파라미터, ② 핵심 강점·약점, ③ 야후 옵션 체인과 바이낸스·KRX 1시간봉 시계열만으로 장중 틱(Tick) 부재를 어떻게 수학적 우회 모델(고정괴리율 롤링 보간, 4분면 OI×IV 부호 추론, 풋-콜 패리티 합성선물, 바나·참 편미분)로 극복했는지 투자자 눈높이에서 브리핑하십시오.

## 1. 월가 4대 전략 레짐 판독 및 최근 {td}영업일 수급 모멘텀 궤적 해부 (파이프라인 4단계 사령탑)
- ① 기준일(T) 4대 전략 레짐 확률 요약표 ([섹션 1-1]) + 독해 가이드 및 해설
- ② 최근 {td}영업일 레짐 및 4분면(Q1~Q4) 수급 추세 궤적표 ([섹션 1-2]) + 상승 연료(Call Q1) 증감, 바닥 방석(Put Q2) vs Put 청산(Q3+4), 단기({ws}D) vs 장기({wl}D) 이월 착시 해설
- ③ 현재 정면충돌 행사가 및 단기 Max Pain 이동 역학
- ④ 상승장 속 단기 눌림목(Pullback) & 고점 분배 4대 사전 징후 진단표 ([섹션 1-4] 및 [섹션 1-5])
- ⑤ [국면 판정 · 급락 위험도] ([섹션 1-1] 하단): 국면 확률(상승/하락/횡보)은 '지금 어떤 국면에 있는가'를 나타내는 상태 지표(전환 후 수 영업일 지연)이며 미래 수익률 예측치가 아닙니다. 급락 위험도는 과거 빈도(10영업일 안에 -5% 이상 하락)로만 해석하고 시점 신호로 쓰지 마십시오. 레짐 확률과 국면 판정이 엇갈리면 '국면 = 가격 추세 상태', '레짐 = 옵션 수급 해석'으로 구분해 서술하십시오.

## 2. 세부 미시구조 데이터 정밀 해부 (파이프라인 1단계 곡면 역산 · 2단계 비대칭 수급 · 3단계 합성공매도 및 감마 지형)
- ① [파이프라인 1단계] 변동성 곡면(Term Structure · 25D Skew · Butterfly) 추세 및 선행 다이버전스 해부 ([섹션 2-①])
- ② [파이프라인 2·3단계] OI × IV 4분면 수급 진위 및 '합성 공매도 본대(Deep ITM Put) · 매집당시주가 · 매집단가 대비 평가손익' 정밀 해부 ([섹션 2-②의 (2-1)~(2-4)]):
  * Call 상위 계약(2-1), Put 증가 계약(2-2), Put 감소/청산 계약(2-3), 그리고 [합성 공매도 본대 및 내가격(ITM) 풋 지형·보유측 평가손익 현황표(2-4)]를 분석하십시오.
  * 특히 (2-4)를 바탕으로 1) 1선 태생합성공매도와 2선 공격롱풋->ITM 진화 물량의 규모 및 딜러 대리 공매도 구속 주식 수, 2) 매집단가 대비 현재 옵션가 기준 보유측 평가손익(1·2선은 풋 매수측, 3선은 풋 매도측으로 부호를 구분하며, '만기BEP'는 시간가치가 0이 되는 만기일에만 성립하는 참고치이므로 만기 전 손익 판정에 쓰지 말 것), 3) 최근 청산으로 나온 딜러 환매수(현물 매수)와 매수헤지 해소(현물 매도) 물량을 명쾌하게 해설하십시오.
- ③ [파이프라인 3단계] 딜러 감마(Gamma) 지형도의 중심축 이동과 네거티브 감마 트랩 분석 ([섹션 2-③])
- ④ [파이프라인 2단계] 당일(T) 미결산 기습 거래량 레이더 및 단기 만기 행사가 쪼개기 클러스터 해부 ([섹션 2-④, ⑤])

## 3. 실전 종합 판정 · 월가 표준 5~6단계 눌림목 조견표 · 기습 풋(원인 ①·②) 완전판 하락폭 공식 및 양방향 플레이북
- [섹션 3-1] 핵심 가격 트리거 환산표, [섹션 3-2] 월가 표준 5~6단계 눌림목 분할매수 조견표, [섹션 3-3] 기습 풋 원인 ①·② 완전판 하락폭 공식 조견표를 정리하고, 1) 상방 바나 랠리 및 분할 매수 플레이북, 2) 하방 벙커 붕괴 시 손절·헤지 데드라인, 3) 만기일 체크리스트를 제시하십시오. [섹션 3-1]의 KOSPI·삼성전자 환산치에는 회귀 구간의 평균 환율 동조가 들어 있으므로 원거리 목표가는 '환율고정 KOSPI'와 함께 범위로 인용하고, 감마 트랩(Q1 롱풋)과 감마 방석(Q2 풋매도)을 구분하십시오. [섹션 3-2]의 Max Pain은 자석 효과가 실측되지 않았으므로 회귀 목표로 서술하지 마십시오. [섹션 3-3]의 하락폭 타깃은 원인 ①·②가 작동한다고 가정한 조건부 시나리오이므로 예측치처럼 단정하지 말고, 표 아래 실측 도달률과 원인 ①·②의 신뢰도를 함께 인용하십시오.

## 4. [비판적 검증] AI 추론의 5대 구조적 한계점 및 반대 시나리오(Devil's Advocate) 스트레스 테스트
- [섹션 4]의 4대 가짜 IV 필터링 통계, 부호 역전 계약, 초외가격 수량 왜곡 비중, 단기 vs 장기 다이버전스, 한국 시장 독자 변동분(1 - R제곱), 상·하방 반증 트리거를 정리하십시오.
- [섹션 5]의 '신호 신뢰도표'에서 반영이 '참고'이거나 판정이 '정보력 없음'·'기간 의존'인 신호(고점래치, 사각지대 3중 체크, 원인①·②, 레짐 1순위, 평가손실 다수 판정 등)는 결론의 단독 근거로 쓰지 말고 그 한계를 명시하십시오.
- [섹션 6] '이력 요약 블록'(일별 지표 21거래일 · 계약/행사가 OI 패널 · 채점 요약)은 해석 보조 자료입니다. ① 3D·7D·20D 합계의 이월 착시를 일별 값으로 확인하고, ② 핵심 포지션이 언제 쌓였는지(형성 시점)와 콜벽·풋벽의 이동을 패널로 확인하며, ③ '당일 이상치 점검' 줄로 당일 수급이 평소 범위인지 판정하고, ④ (6-4) 채점으로 1시그마 범위의 신뢰도를 밝히고, ⑤ (6-5) 신호 기록·채점으로 원인①·②·국면·D선 조합의 실제 적중 기록('실시간' 기록 우선, '사후·재현'은 참고)을 밝히십시오. 이 블록의 표는 보고서에 그대로 옮기지 말고 [섹션 1]·[섹션 2]·[섹션 4] 해설의 근거 수치로만 인용하며, 블록의 추세만으로 방향을 단정하지 마십시오.

## 5. [투자자용 30초 실전 판독 요약 & 최종 정리] 핵심 3단계 요약 · '실전 3중 체크법' · '합성 공매도 5대 포인트' · [신설] '월가 4대 파이프라인 최종 실행 사령탑'
- 첨부 파일 [섹션 5]의 자동 계측 데이터를 활용하여 아래 1~6단계를 빠짐없이 명쾌하게 정리하십시오:
  * [우선 원칙] 최종 결론은 [섹션 5]의 '최종 판정(국면·급락 위험도)' 줄과 '신호 신뢰도표'를 우선 근거로 삼고, 눌림목 체크 결론(최종 통합 판정)은 보조로만 제시하십시오.
  * 1단계 ([섹션 1-2] {td}영업일 궤적표 확인 — 10초)
  * 2단계 ([섹션 1-4] 단기 눌림목 4대 징후 & [섹션 3-2] 5단계 눌림목 타점 확인 — 10초)
  * 3단계 ([섹션 2-④, ⑤] 당일 미결산 레이더 & [섹션 3-3] 기습 풋 공식 타깃 확인 — 10초)
  * 4단계 (눌림목 미탐지 사각지대 25% 보완 '실전 3중 체크법' 원리 해설 및 당일 체크 결과 요약표)
  * 5단계 ('합성 공매도 본대(Deep ITM Put)'의 지배력 및 숏커버 전환을 추적하는 5대 핵심 독해 포인트 실시간 진단)
  * ★ 6단계 ([필수 신설] '월가 4대 퀀트 파이프라인[곡면역산 RND -> 비대칭수급·합성선물 -> 딜러 감마플립·바나참 -> 레짐전이]' 전일 대비 1일 변화 통합 계측 요약표 및 투자자 활용 매뉴얼):
    첨부 파일 [섹션 5]의 6단계 계측치(전일 T-1 대비 당일 T 변화량 포함)를 바탕으로, ① RND 주간 확률 레인지 및 좌·우 꼬리 확률의 전일 대비 변화 활용법, ② 풋-콜 패리티 내재 합성선물 베이시스의 전일 대비 추이와 한국장 시초가 갭 판독법, ③ 감마 플립선의 1일 이동폭('구간 내 플립 없음' 여부 포함 · 방향 신호가 아닌 변동 폭 구간 경계로 해석)과 바나·참 시나리오 계산값의 증감 활용법, ④ 다년도 상대OI 정규화 수급 및 최종 매매 실행 명령을 선언하십시오."""

# ==============================================================================
# 4. 입력 폴더 내 모든 CSV 병합 로드 및 전처리 함수
# ==============================================================================
def load_and_merge_csv_files(input_folder):
    if not os.path.exists(input_folder):
        os.makedirs(input_folder, exist_ok=True)
        raise FileNotFoundError(
            f"[오류] 입력 데이터 폴더가 없어 새로 생성했습니다: {input_folder}\n"
            f"해당 폴더 안에 EWY 옵션 CSV 파일들을 넣은 후 다시 실행해 주세요."
        )

    csv_files = sorted(list(set(
        glob.glob(os.path.join(input_folder, "*.csv")) +
        glob.glob(os.path.join(input_folder, "*.CSV"))
    )))

    if not csv_files:
        raise FileNotFoundError(f"[오류] '{input_folder}' 폴더 안에 CSV 파일이 없습니다.")

    print(f"[데이터 로드] 총 {len(csv_files)}개의 CSV 파일을 병합합니다...")
    df_list, loaded_names = [], []

    for fpath in csv_files:
        fname = os.path.basename(fpath)
        try:
            temp_df = pd.read_csv(fpath, encoding='utf-8-sig')
        except UnicodeDecodeError:
            temp_df = pd.read_csv(fpath, encoding='cp949')
        df_list.append(temp_df)
        loaded_names.append(fname)
        print(f"  - 로드 완료: {fname} ({len(temp_df):,} 행)")

    merged_df = pd.concat(df_list, ignore_index=True)
    raw_count = len(merged_df)

    merged_df.columns = [c.strip() for c in merged_df.columns]
    merged_df['Quote Date'] = pd.to_datetime(merged_df['Quote Date'].astype(str).str.strip()).dt.strftime('%Y-%m-%d')
    merged_df['Expiration Date'] = pd.to_datetime(merged_df['Expiration Date'].astype(str).str.strip()).dt.strftime('%Y-%m-%d')
    opt_first = merged_df['Option Type'].astype(str).str.strip().str.upper().str[0]
    merged_df['Option Type'] = np.where(opt_first == 'C', 'Call', 'Put')

    merged_df = merged_df.drop_duplicates(subset=['Contract Name', 'Quote Date'], keep='last').copy()
    dedup_count = len(merged_df)

    num_cols = ['Strike', 'Bid', 'Ask', 'Last Price', 'Volume', 'Open Interest',
                'Secured Overnight Financing Rate', 'EWY Price', 'Implied Volatility', 'Delta']
    for col in num_cols:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0.0)

    merged_df['Quote_dt'] = pd.to_datetime(merged_df['Quote Date'])
    merged_df['Exp_dt'] = pd.to_datetime(merged_df['Expiration Date'])
    merged_df['DTE'] = (merged_df['Exp_dt'] - merged_df['Quote_dt']).dt.days

    merged_df = merged_df.sort_values(['Quote Date', 'Expiration Date', 'Option Type', 'Strike']).reset_index(drop=True)
    print(f"[병합 완료] {raw_count:,}행 -> 중복 제거 후 {dedup_count:,}행 (보유 기간: {merged_df['Quote Date'].min()} ~ {merged_df['Quote Date'].max()}, 총 {merged_df['Quote Date'].nunique()}거래일)\n")
    if USE_DIVIDEND_IV_FIX:   # ★ [V4.3.7] 배당 반영 IV 보정 (실패하면 수집기 IV 그대로)
        try:
            merged_df = apply_dividend_iv_fix_v437(merged_df)
        except Exception as _dv_e:
            print(f"[V4.3.7 배당 반영 IV 보정 실패 — 수집기 IV 그대로 사용] {_dv_e}")
    return merged_df, loaded_names

# ==============================================================================
# 5. Step 1: 월가 4대 계층(Tier 1 ~ Tier 4) 최우선 선택 대화형 메뉴
# ==============================================================================
def select_analysis_tiers_interactively():
    if not TIER_SELECTION_MODE.startswith("대화형"):
        for k, v in TIER_CONFIGS.items():
            if TIER_SELECTION_MODE.startswith(f"Tier {k}"):
                print(f"👉 [폼 설정 Tier 선택] {v['name']} 모델로 분석을 시작합니다.\n")
                return [k]
        return ["5"]

    print("=" * 118)
    print(" 🏛️ [Step 1: 월가 퀀트 분석 모델 계층(Tier 1 ~ Tier 4) 선택 메뉴] (실행 시 최우선 선택)")
    print("-" * 118)
    print("  [1] Tier 1 : 초단기 전술창 (T+0 ~ 1D)    | 강점: 미결산 기습 거래량·실시간 ΔIV 포착 / 약점: 단기 노이즈 민감 (단타/시초가)")
    print("  [2] Tier 2 : 단기 롤오버창 (3D vs 7D)    | 강점: 수·목 롤오버 포함 7일 궤적·이월착시 제거 / 약점: 월간 구조 파악 한계 (1~2주 스윙)")
    print("  [3] Tier 3 : 월간 감마창   (7D vs 20D)   | 강점: 월간 만기(Monthly OpEx) 풋요새·콜벽 규명 / 약점: 초단기 변곡점 1~2일 후행 (포지션)")
    print("  [4] Tier 4 : 구조적 레짐창 (20D vs 60D+) | 강점: 연간 %ile 극단치·LEAPS·구조적 Beta 도출 / 약점: 단기 타이밍 부적합 (중장기 배분)")
    print("  [5] 통합 마스터창 (Tier 1~4 All-in-One)  | 강점: 4대 계층 핵심 테이블 통합 교차검증 / 약점: 단기·중기 신호 충돌 시 호흡 구분 필요 [기본값]")
    print("-" * 118)
    print("  💡 팁: 단일 번호('1'~'5', 그냥 Enter=5) 또는 복수 비교('1, 2' 또는 'ALL' 입력 시 전체 Tier 각각 파일 생성) 가능")
    print("=" * 118)

    try:
        raw_t = input(" ▶ 원하는 분석 Tier 번호(1/2/3/4/5, 복수는 콤마 구분, ALL=1~4 전체)를 입력하세요 [기본값=5 통합]: ").strip()
    except EOFError:
        raw_t = "5"

    if not raw_t:
        selected = ["5"]
    elif raw_t.upper() == "ALL":
        selected = ["1", "2", "3", "4"]
    else:
        parts = [p.strip() for p in raw_t.split(",") if p.strip() in TIER_CONFIGS]
        selected = parts if parts else ["5"]

    sel_names = [TIER_CONFIGS[k]['short_tag'] for k in selected]
    print(f"\n ✅ [분석 Tier 선택 완료] 선택된 모델: {', '.join(sel_names)}\n")
    return selected

# ==============================================================================
# 5-B. Step 1-2: 출력 버전(PC버젼 vs 모바일버젼) 선택 대화형 메뉴
# ==============================================================================
def select_view_version_interactively():
    if VIEW_VERSION_MODE.startswith("PC버젼"):
        print("👉 [폼 설정 버전 선택] 💻 PC버젼 (정량 표 포함 기존 표준 모드)으로 분석을 시작합니다.\n")
        return "PC"
    elif VIEW_VERSION_MODE.startswith("모바일버젼"):
        print("👉 [폼 설정 버전 선택] 📱 모바일버젼 (표 재출력 금지 & 순수 해설 텍스트 HTML 생성 모드)으로 분석을 시작합니다.\n")
        return "MOBILE"

    print("=" * 118)
    print(" 📱 [Step 1-2: 보고서 출력 버전(PC버젼 vs 모바일버젼) 선택 메뉴]")
    print("-" * 118)
    print("  [1] 💻 PC버젼 (기존과 동일) : 데이터북의 모든 정량 표(Table)를 HTML <table>로 변환·포함한 전체 보고서 생성 [기본값]")
    print("  [2] 📱 모바일버젼 (가독성 최적화) : 마크다운/HTML 표 재출력 전면 금지 + 대화창 첫 줄 요약 출력 후,")
    print("                                  [섹션 0~5] 핵심 독해 가이드 & 투자자 눈높이 해설만 담은 텍스트 전용 HTML 파일 생성")
    print("=" * 118)

    try:
        raw_v = input(" ▶ 원하는 출력 버전 번호(1=PC버젼 / 2=모바일버젼)를 입력하세요 [기본값=1 PC버젼]: ").strip()
    except EOFError:
        raw_v = "1"

    if raw_v in ["2", "모바일", "모바일버젼", "M", "m", "MOBILE", "mobile"]:
        print("\n ✅ [출력 버전 선택 완료] 📱 모바일버젼(표 제외 · 순수 텍스트 해설 HTML 파일 모드)이 선택되었습니다.\n")
        return "MOBILE"
    else:
        print("\n ✅ [출력 버전 선택 완료] 💻 PC버젼(기존 표준 모드)이 선택되었습니다.\n")
        return "PC"

# ==============================================================================
# 6. Step 2: 대화형 기준일 선택 메뉴 (최신 기준일 vs 과거 원하는 일자/구간)
# ==============================================================================
def parse_flexible_date_str(raw_str, all_avail_dates):
    s = str(raw_str).strip()
    if not s or s.upper() == "LATEST":
        return [None]

    default_year = all_avail_dates[-1][:4]
    parts = [p.strip() for p in s.split(",") if p.strip()]
    parsed = []

    for p in parts:
        digits = p.replace("-", "").replace("/", "").replace(".", "")
        if len(digits) == 8 and digits.isdigit():
            dt_str = f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}"
        elif len(digits) == 4 and digits.isdigit():
            dt_str = f"{default_year}-{digits[:2]}-{digits[2:4]}"
        elif len(p) <= 5 and any(sep in p for sep in ["-", "/", "."]):
            norm_p = p.replace("/", "-").replace(".", "-")
            dt_str = pd.to_datetime(f"{default_year}-{norm_p}").strftime('%Y-%m-%d')
        else:
            dt_str = pd.to_datetime(p).strftime('%Y-%m-%d')
        parsed.append(dt_str)
    return parsed


def select_analysis_dates_interactively(df):
    all_avail_dates = sorted(df['Quote Date'].unique())
    first_dt = all_avail_dates[0]
    latest_dt = all_avail_dates[-1]

    if DATE_SELECTION_MODE.startswith("최신 기준일"):
        print(f"👉 [자동 선택] 최신 기준일({latest_dt}) 모드로 분석을 시작합니다.\n")
        return [None]
    elif DATE_SELECTION_MODE.startswith("아래 지정한 과거"):
        parsed_preset = parse_flexible_date_str(PRESET_TARGET_DATE, all_avail_dates)
        print(f"👉 [폼 지정 날짜 선택] 지정하신 과거 기준일({parsed_preset})로 분석을 시작합니다.\n")
        return parsed_preset

    recent_15 = all_avail_dates[-15:] if len(all_avail_dates) >= 15 else all_avail_dates
    spot_map = df[df['Quote Date'].isin(recent_15)].groupby('Quote Date')['EWY Price'].first()

    print("=" * 118)
    print(f" 📅 [Step 2: 분석 기준일 선택 메뉴] (보유 데이터 기간: {first_dt} ~ {latest_dt} / 총 {len(all_avail_dates)}거래일)")
    print("-" * 118)
    print(" • 최근 거래일 및 EWY 종가 목록 (과거 날짜 선택 시 참고하세요):")
    row_items = [f"{d}(${spot_map[d]:.2f})" for d in recent_15]
    for i in range(0, len(row_items), 5):
        print("   " + " | ".join(row_items[i:i+5]))
    print("-" * 118)
    print(f"  [1] 최신 기준일로 분석 ({latest_dt})       👉 '1' 입력 또는 그냥 [Enter] 키")
    print(f"  [2] 과거 원하는 일자로 분석 (단일/복수)    👉 '2' 입력 (또는 바로 '2026-10-21' / '20261021' 입력 가능)")
    print(f"  [3] 과거 특정 기간(시작~종료) 일괄 분석    👉 '3' 입력 (또는 바로 '20261019~20261022' 입력 가능)")
    print("=" * 118)

    try:
        user_choice = input(" ▶ 원하는 메뉴 번호(1/2/3) 또는 날짜를 입력하세요 [기본값=1 최신일]: ").strip()
    except EOFError:
        user_choice = "1"

    if user_choice == "" or user_choice == "1" or user_choice.upper() == "LATEST":
        print(f"\n ✅ [최신 기준일 선택] {latest_dt} 기준으로 분석을 진행합니다.\n")
        return [None]
    elif user_choice == "2":
        raw_dt = input(f" ▶ 분석할 과거 날짜를 입력하세요 (예: 2026-10-21 또는 20261021 / 복수는 콤마 구분): ").strip()
        target_dates = parse_flexible_date_str(raw_dt, all_avail_dates)
        print(f"\n ✅ [과거 특정일 선택] {target_dates} 기준으로 미래참조 차단 분석을 진행합니다.\n")
        return target_dates
    elif user_choice == "3":
        raw_rng = input(" ▶ 분석할 과거 시작일~종료일을 입력하세요 (예: 2026-10-19 ~ 2026-10-22): ").strip()
        sep = "~" if "~" in raw_rng else ("," if "," in raw_rng else " ")
        parts = [p.strip() for p in raw_rng.split(sep) if p.strip()]
        if len(parts) >= 2:
            s_dt = parse_flexible_date_str(parts[0], all_avail_dates)[0]
            e_dt = parse_flexible_date_str(parts[-1], all_avail_dates)[0]
            if s_dt > e_dt:
                s_dt, e_dt = e_dt, s_dt
            rng_dates = [d for d in all_avail_dates if s_dt <= d <= e_dt]
            if not rng_dates:
                rng_dates = [e_dt]
            print(f"\n ✅ [과거 구간 선택] {s_dt} ~ {e_dt} 구간 내 총 {len(rng_dates)}개 거래일({rng_dates}) 분석을 진행합니다.\n")
            return rng_dates
        else:
            return parse_flexible_date_str(raw_rng, all_avail_dates)
    else:
        if "~" in user_choice:
            parts = [p.strip() for p in user_choice.split("~") if p.strip()]
            s_dt = parse_flexible_date_str(parts[0], all_avail_dates)[0]
            e_dt = parse_flexible_date_str(parts[-1], all_avail_dates)[0]
            if s_dt > e_dt:
                s_dt, e_dt = e_dt, s_dt
            rng_dates = [d for d in all_avail_dates if s_dt <= d <= e_dt]
            print(f"\n ✅ [과거 구간 직입력] {s_dt} ~ {e_dt} (총 {len(rng_dates)}거래일) 분석을 진행합니다.\n")
            return rng_dates if rng_dates else [e_dt]
        else:
            target_dates = parse_flexible_date_str(user_choice, all_avail_dates)
            print(f"\n ✅ [과거 특정일 직입력] {target_dates} 기준으로 미래참조 차단 분석을 진행합니다.\n")
            return target_dates

# ==============================================================================
# 7. 과거 기준일(Point-in-Time) 절단 및 미래참조오류 원천 차단 함수
# ==============================================================================
def apply_point_in_time_cutoff(df, target_date_str=None):
    if USE_DIVIDEND_IV_FIX and 'Q_eff' not in df.columns:   # ★ [V4.3.7] 다른 경로로 읽은 자료도 한 번만 보정
        try:
            df = apply_dividend_iv_fix_v437(df)
        except Exception as _dv_e:
            print(f"[V4.3.7 배당 반영 IV 보정 실패 — 수집기 IV 그대로 사용] {_dv_e}")
    all_avail_dates = sorted(df['Quote Date'].unique())
    latest_avail_date = all_avail_dates[-1]

    if target_date_str is not None and str(target_date_str).strip() != "" and str(target_date_str).strip().upper() != "LATEST":
        req_date = pd.to_datetime(str(target_date_str).strip()).strftime('%Y-%m-%d')
        valid_dates = [d for d in all_avail_dates if d <= req_date]
        if not valid_dates:
            raise ValueError(
                f"[오류] 지정하신 과거 기준일({req_date}) 이전에 해당하는 옵션 데이터가 없습니다. "
                f"(마스터 데이터 최초 거래일: {all_avail_dates[0]})"
            )
        anchor_date = valid_dates[-1]
        if anchor_date != req_date:
            print(f"  [안내] 입력하신 {req_date}은 휴장일/데이터 미존재일이므로 직전 거래일인 [{anchor_date}]로 자동 매칭합니다.")
        is_historical_mode = (anchor_date < latest_avail_date) or (req_date <= latest_avail_date)
    else:
        req_date = f"LATEST ({latest_avail_date})"
        anchor_date = latest_avail_date
        is_historical_mode = False

    df_pit = df[df['Quote Date'] <= anchor_date].copy().reset_index(drop=True)
    future_dates_blocked = [d for d in all_avail_dates if d > anchor_date]
    blocked_rows = len(df) - len(df_pit)

    pit_meta = {
        'requested_date': req_date,
        'anchor_date': anchor_date,
        'is_historical_mode': is_historical_mode,
        'kept_rows': len(df_pit),
        'kept_days': df_pit['Quote Date'].nunique(),
        'blocked_rows': blocked_rows,
        'blocked_days_count': len(future_dates_blocked),
        'blocked_first_date': future_dates_blocked[0] if future_dates_blocked else None,
        'blocked_last_date': future_dates_blocked[-1] if future_dates_blocked else None,
    }

    print("=" * 118)
    print(f" 🛡️ [Point-in-Time 시점 고정 및 미래참조 차단 엔진 가동]")
    print(f"  • 요청 기준일 : {req_date}  -->  확정 분석 기준일(Anchor Date): {anchor_date}")
    print(f"  • 사용 데이터 : {df_pit['Quote Date'].min()} ~ {anchor_date} ({pit_meta['kept_days']}거래일 / {pit_meta['kept_rows']:,}행)")
    if blocked_rows > 0:
        print(f"  • 미래차단완료: {anchor_date} 이후 미래 데이터 {pit_meta['blocked_days_count']}거래일({pit_meta['blocked_first_date']} ~ {pit_meta['blocked_last_date']}, 총 {blocked_rows:,}행) 완벽 차단됨")
    else:
        print(f"  • 미래차단완료: 마스터 데이터의 최신 거래일({anchor_date}) 기준 분석 (이후 미래 옵션 데이터 없음)")
    print("=" * 118)
    return df_pit, pit_meta


# ==============================================================================
# 8. [V4.1 핵심] 바이낸스 API(EWYBUSDT) 1시간봉 ↔ 야후 KRX 주간장(09~15시) 동시 상관·회귀 & 영점 동기화 엔진
# ==============================================================================
def _parse_float_or_default(val_str, default_val):
    if val_str is None:
        return float(default_val), False
    s = str(val_str).strip().replace(",", "").replace("$", "").replace("원", "").replace("pt", "").strip()
    if not s:
        return float(default_val), False
    try:
        return float(s), True
    except Exception:
        return float(default_val), False


def fetch_binance_klines_kst(symbol="EWYBUSDT", interval="1h", start_kst_str="2026-08-01", end_kst_str="2026-10-28"):
    """
    바이낸스 공개 API(US-IP 호환 Vision 엔드포인트 -> Spot API -> 글로벌 프록시 자동 순회)에서
    지정된 구간의 Klines 시계열을 조회하여 한국시간(KST, Asia/Seoul) 인덱스를 가진 Close Series로 반환합니다.
    """
    sym_candidates = [symbol.strip().upper()]
    if sym_candidates[0] == "EWYBUSDT":
        sym_candidates.append("EWYUSDT")
    elif sym_candidates[0] == "EWYUSDT":
        sym_candidates.append("EWYBUSDT")

    # 1순위: US-IP 허용 Vision 서버 / 2순위: 기본 Spot 서버 / 3순위: 코랩 미국 IP 차단 우회 프록시
    endpoint_templates = [
        ("DIRECT", "https://data-api.binance.vision/api/v3/klines"),
        ("DIRECT", "https://api-gcp.binance.com/api/v3/klines"),
        ("DIRECT", "https://api.binance.com/api/v3/klines"),
        ("PROXY_CODETABS", "https://api.binance.com/api/v3/klines"),
        ("PROXY_ALLORIGINS", "https://api.binance.com/api/v3/klines"),
    ]

    # KST(UTC+9) -> UTC timestamp(ms) 변환
    start_dt_utc = pd.to_datetime(start_kst_str) - timedelta(hours=9)
    end_dt_utc   = pd.to_datetime(end_kst_str) + timedelta(hours=15)  # 익일 00:00 KST = 당일 15:00 UTC
    start_ms = int(start_dt_utc.timestamp() * 1000)
    end_ms   = int(end_dt_utc.timestamp() * 1000)

    for sym in sym_candidates:
        for mode, base_url in endpoint_templates:
            all_rows = []
            curr_start = start_ms
            success_ep = False
            for _ in range(8):  # 최대 8,000캔들(1h 기준 약 330일 누적 전체 시계열) 페이지네이션
                params = urllib.parse.urlencode({
                    "symbol": sym,
                    "interval": interval,
                    "startTime": curr_start,
                    "endTime": end_ms,
                    "limit": 1000
                })
                target_url = f"{base_url}?{params}"
                if mode == "PROXY_CODETABS":
                    url = f"https://api.codetabs.com/v1/proxy?quest={urllib.parse.quote(target_url, safe='')}"
                elif mode == "PROXY_ALLORIGINS":
                    url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(target_url, safe='')}"
                else:
                    url = target_url

                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0:
                        all_rows.extend(data)
                        success_ep = True
                        last_open_ms = int(data[-1][0])
                        if len(data) < 1000 or last_open_ms >= end_ms:
                            break
                        curr_start = last_open_ms + 1
                    else:
                        break
                except Exception:
                    break

            if success_ep and len(all_rows) > 0:
                df_k = pd.DataFrame(all_rows)
                # col 0: open_time(ms), col 4: close_price
                open_ms = pd.to_numeric(df_k[0], errors="coerce")
                close_p = pd.to_numeric(df_k[4], errors="coerce")
                # UTC -> KST (+9h)
                kst_idx = pd.to_datetime(open_ms, unit="ms") + pd.Timedelta(hours=9)
                s_out = pd.Series(close_p.values, index=kst_idx, name="EWY_BINANCE").dropna()
                s_out = s_out[~s_out.index.duplicated(keep="last")].sort_index()
                ep_label = base_url.split('//')[1].split('/')[0] if mode == "DIRECT" else mode
                return s_out, f"{sym} ({ep_label})"

    return pd.Series(dtype=float), "바이낸스 미연결(일봉 폴백)"


def fetch_yf_and_build_relationship_model(df_pit,
                                          pit_meta,
                                          lookback_days=60,
                                          halflife=15,
                                          anchor_to_yf_spot=ANCHOR_TO_YF_SPOT,
                                          strict_no_lookahead_yf=STRICT_NO_LOOKAHEAD_YF,
                                          sync_override_cache=None):
    anchor_date = pit_meta['anchor_date']
    anchor_dt   = pd.to_datetime(anchor_date).tz_localize(None).normalize()

    ewy_daily = df_pit.groupby('Quote Date')['EWY Price'].first().sort_index()
    ewy_daily.index = pd.to_datetime(ewy_daily.index).tz_localize(None).normalize()
    ewy_daily = ewy_daily[ewy_daily.index <= anchor_dt]
    latest_ewy_spot = float(ewy_daily.iloc[-1])

    start_dt = (ewy_daily.index.min() - timedelta(days=15)).strftime('%Y-%m-%d')
    yf_fetch_end_dt = (anchor_dt + timedelta(days=4)).strftime('%Y-%m-%d')

    yf_success = False
    yf_daily_dict = {}
    yf_hourly_dict = {}
    yf_anchor_quotes = {}

    allow_live_1m = (not pit_meta['is_historical_mode']) and (not strict_no_lookahead_yf)
    print(f"[야후파이낸스 & 바이낸스 시점동기화 조회] 기준일({anchor_date}) 이하 KOSPI(^KS11), 삼성전자(005930.KS), 원/달러(KRW=X) 및 {BINANCE_EWY_SYMBOL} 수집 중...")

    try:
        try:
            import yfinance as yf
        except ImportError:
            print("  - yfinance 패키지 자동 설치 중...")
            os.system("pip install -q yfinance")
            import yfinance as yf

        ticker_map = {
            'KOSPI': '^KS11',
            'SAMSUNG': '005930.KS',
            'USDKRW': 'KRW=X'
        }
        # 1h 데이터 조회 시작일: 통계적 설명력(R²) 극대화를 위해 마스터 데이터 최초일(과거 누적 전체 구간, 최대 365일)부터 최신 기준일까지 전체 수집
        hourly_start_dt = max(
            pd.to_datetime(start_dt),
            anchor_dt - timedelta(days=365 if USE_FULL_CUMULATIVE_HISTORY else min(max(lookback_days * 2, 90), 360))
        ).strftime('%Y-%m-%d')

        for key, tkr in ticker_map.items():
            tk_obj = yf.Ticker(tkr)
            # (A) 일봉(1d) 조회
            hist_d = tk_obj.history(start=start_dt, end=yf_fetch_end_dt, interval="1d", auto_adjust=False)
            if hist_d is not None and not hist_d.empty and 'Close' in hist_d.columns:
                s_d = hist_d['Close'].dropna().copy()
                if s_d.index.tz is not None:
                    try:
                        s_d.index = s_d.index.tz_convert('Asia/Seoul').tz_localize(None).normalize()
                    except Exception:
                        s_d.index = pd.to_datetime(s_d.index).tz_localize(None).normalize()
                else:
                    s_d.index = pd.to_datetime(s_d.index).tz_localize(None).normalize()
                s_d = s_d[~s_d.index.duplicated(keep='last')].sort_index()

                s_d_pit = s_d[s_d.index <= anchor_dt].copy()

                # 야후 일봉 T-1 지연 방어용 5분봉 브릿지
                if (s_d_pit.empty or s_d_pit.index[-1] < anchor_dt) and (not pit_meta['is_historical_mode']):
                    try:
                        hist_5m = tk_obj.history(period="5d", interval="5m", auto_adjust=False)
                        if hist_5m is not None and not hist_5m.empty and 'Close' in hist_5m.columns:
                            s_5m = hist_5m['Close'].dropna().copy()
                            if s_5m.index.tz is not None:
                                s_5m.index = s_5m.index.tz_convert('Asia/Seoul').tz_localize(None)
                            else:
                                s_5m.index = pd.to_datetime(s_5m.index).tz_localize(None)
                            s_5m_day = s_5m[s_5m.index.normalize() == anchor_dt]
                            if not s_5m_day.empty:
                                s_d_pit.loc[anchor_dt] = float(s_5m_day.iloc[-1])
                                s_d_pit = s_d_pit.sort_index()
                    except Exception:
                        pass

                if s_d_pit.empty:
                    continue
                yf_daily_dict[key] = s_d_pit

                spot_val = float(s_d_pit.iloc[-1])
                spot_time_str = f"{s_d_pit.index[-1].strftime('%Y-%m-%d')} KRX종가 (야후조회)"

                if allow_live_1m:
                    try:
                        hist_m = tk_obj.history(period="5d", interval="1m", auto_adjust=False)
                        if hist_m is not None and not hist_m.empty and 'Close' in hist_m.columns:
                            s_m = hist_m['Close'].dropna()
                            if not s_m.empty:
                                spot_val = float(s_m.iloc[-1])
                                spot_time_str = pd.to_datetime(s_m.index[-1]).strftime('%Y-%m-%d %H:%M 실시간')
                    except Exception:
                        pass

                yf_anchor_quotes[key] = (spot_val, spot_time_str)
                print(f"  - {key:<7} ({tkr:<9}) 일봉 조회 완료: 기준값 = {spot_val:,.2f} ({spot_time_str} / 누적 {len(s_d_pit)}일)")

            # (B) [V4.1 신규] 한국 주간장 개장 구간(09:00~15:00 KST) 1시간봉(1h) 조회
            if USE_BINANCE_KRX_HOURLY_SYNC:
                try:
                    hist_1h = tk_obj.history(start=hourly_start_dt, end=yf_fetch_end_dt, interval="1h", auto_adjust=False)
                    if hist_1h is not None and not hist_1h.empty and 'Close' in hist_1h.columns:
                        s_1h = hist_1h['Close'].dropna().copy()
                        if s_1h.index.tz is not None:
                            s_1h.index = s_1h.index.tz_convert('Asia/Seoul').tz_localize(None)
                        else:
                            s_1h.index = pd.to_datetime(s_1h.index).tz_localize(None)
                        s_1h.index = s_1h.index.floor('h')
                        s_1h = s_1h[~s_1h.index.duplicated(keep='last')].sort_index()
                        # 미래참조 원천 차단: anchor_dt 15:30 KST 이하 & 한국 주간장 개장 시간(09:00 ~ 15:00 KST, 평일)만 추출
                        cutoff_1h_dt = anchor_dt + pd.Timedelta(hours=15, minutes=30)
                        s_1h_pit = s_1h[
                            (s_1h.index <= cutoff_1h_dt) &
                            (s_1h.index.day_of_week < 5) &
                            (s_1h.index.hour >= 9) &
                            (s_1h.index.hour <= 15)
                        ].copy()
                        if len(s_1h_pit) >= 10:
                            yf_hourly_dict[key] = s_1h_pit
                except Exception:
                    pass

        if len(yf_daily_dict) == 3 and all(len(v) >= 5 for v in yf_daily_dict.values()):
            yf_success = True
    except Exception as e:
        print(f"  - [경고] 야후파이낸스 접속 제한 또는 오류 발생 ({e}) -> 폴백(Fallback) 기준값을 사용합니다.")

    # (C) [V4.1 핵심] 바이낸스 API EWYBUSDT 1시간봉(1h) 및 15:30 KST 마감 정각(5m) 시세 조회
    binance_1h_series = pd.Series(dtype=float)
    binance_1530_spot = None
    binance_source_str = "미사용"
    if USE_BINANCE_KRX_HOURLY_SYNC:
        b_start_str = max(
            ewy_daily.index.min() - timedelta(days=7),
            anchor_dt - timedelta(days=365 if USE_FULL_CUMULATIVE_HISTORY else min(max(lookback_days * 2, 90), 180))
        ).strftime('%Y-%m-%d')
        b_end_str = anchor_dt.strftime('%Y-%m-%d')
        binance_1h_series, binance_source_str = fetch_binance_klines_kst(
            symbol=BINANCE_EWY_SYMBOL,
            interval="1h",
            start_kst_str=b_start_str,
            end_kst_str=b_end_str
        )
        if not binance_1h_series.empty:
            cutoff_1h_dt = anchor_dt + pd.Timedelta(hours=15, minutes=30)
            binance_1h_series.index = binance_1h_series.index.floor('h')
            binance_1h_series = binance_1h_series[
                (binance_1h_series.index <= cutoff_1h_dt) &
                (binance_1h_series.index.day_of_week < 5) &
                (binance_1h_series.index.hour >= 9) &
                (binance_1h_series.index.hour <= 15)
            ]
            # 기준일(anchor_dt) 15:30 KST 정각 EWYBUSDT 가격을 5분봉으로 정밀 추출 (15:25 오픈 캔들의 종가 = 15:30 정각 가격)
            b_5m_series, _ = fetch_binance_klines_kst(
                symbol=BINANCE_EWY_SYMBOL,
                interval="5m",
                start_kst_str=(anchor_dt - timedelta(days=3)).strftime('%Y-%m-%d'),
                end_kst_str=b_end_str
            )
            if not b_5m_series.empty:
                target_1530 = anchor_dt + pd.Timedelta(hours=15, minutes=30)
                sub_5m = b_5m_series[b_5m_series.index < target_1530]
                if not sub_5m.empty:
                    binance_1530_spot = float(sub_5m.iloc[-1])
            if binance_1530_spot is None and not binance_1h_series.empty:
                binance_1530_spot = float(binance_1h_series.iloc[-1])
            if binance_1530_spot is not None:
                print(f"  - ⚡ [바이낸스 {binance_source_str} 연동 완료] 한국 주간장(09~15시 KST) 1시간봉 {len(binance_1h_series)}개 수집 | "
                      f"기준일 15:30 KST 동시간대 EWYBUSDT = ${binance_1530_spot:.2f}")
            else:   # ★ [V4.3.5] 상장 당일(2026-06-23)처럼 응답은 있으나 기준일 15:30 이전 시세가 0개인 경우 -> None 서식 오류 대신 일봉 폴백 안내
                print(f"  - [알림] 바이낸스 {BINANCE_EWY_SYMBOL} 시세가 기준일({anchor_date}) 15:30 KST 이전에는 없습니다 (상장 전 구간) "
                      f"-> 일봉 회귀 및 EWY 종가 영점으로 자동 전환합니다.")
        else:
            print(f"  - [알림] 바이낸스 {BINANCE_EWY_SYMBOL} API 응답 없음 (네트워크/지역제한 또는 상장 전 구간) -> 일봉 회귀 및 수동/기본 ATS 동기화로 자동 전환합니다.")

    # 일봉 병합 테이블 구성 (기본 및 폴백용)
    merged_daily = pd.DataFrame({'EWY': ewy_daily})
    if yf_success:
        full_idx = pd.date_range(
            start=min(ewy_daily.index.min(), min(s.index.min() for s in yf_daily_dict.values())),
            end=anchor_dt,
            freq='D'
        )
        aligned_yf = pd.DataFrame(index=full_idx)
        for key, s in yf_daily_dict.items():
            aligned_yf[key] = s
        aligned_yf = aligned_yf.ffill(limit=5)
        for key in ['KOSPI', 'SAMSUNG', 'USDKRW']:
            merged_daily[key] = aligned_yf[key].reindex(merged_daily.index)
        merged_daily = merged_daily.dropna(subset=['EWY', 'KOSPI', 'SAMSUNG', 'USDKRW'])

        queried_kospi_pt    = round(yf_anchor_quotes['KOSPI'][0], 2)
        queried_samsung_krw = int(round(yf_anchor_quotes['SAMSUNG'][0], -2))
        queried_usdkrw      = round(yf_anchor_quotes['USDKRW'][0], 2)
        queried_time_info   = yf_anchor_quotes['KOSPI'][1]
    else:
        ewy_v = merged_daily['EWY'].values.astype(float)
        merged_daily['KOSPI']   = FALLBACK_KOSPI_PT * (ewy_v / ewy_v[-1]) ** 0.86
        merged_daily['SAMSUNG'] = FALLBACK_SAMSUNG_KRW * (ewy_v / ewy_v[-1]) ** 1.15
        merged_daily['USDKRW']  = FALLBACK_USDKRW * (ewy_v / ewy_v[-1]) ** (-0.18)
        queried_kospi_pt    = FALLBACK_KOSPI_PT
        queried_samsung_krw = int(FALLBACK_SAMSUNG_KRW)
        queried_usdkrw      = FALLBACK_USDKRW
        queried_time_info   = f"폴백(Fallback) 기준값 ({anchor_date})"

    # ★ [V4.1 핵심] 한국 주간장(09:00~15:00 KST) 1시간봉(1h) 동시간대 병합 테이블 구성
    hourly_sync_active = False
    merged_hourly = pd.DataFrame()
    if USE_BINANCE_KRX_HOURLY_SYNC and (not binance_1h_series.empty) and len(yf_hourly_dict) >= 2:
        h_idx = binance_1h_series.index
        df_h = pd.DataFrame({'EWY': binance_1h_series}, index=h_idx)
        for key in ['KOSPI', 'SAMSUNG', 'USDKRW']:
            if key in yf_hourly_dict:
                df_h[key] = yf_hourly_dict[key].reindex(h_idx)
            elif key in yf_daily_dict:
                # 1h가 일부 누락된 자산(예: 환율)은 일봉 값을 시간봉 인덱스에 매핑
                d_map = yf_daily_dict[key].reindex(pd.to_datetime(h_idx.strftime('%Y-%m-%d'))).values
                df_h[key] = d_map
        # 주간장 시간대 내 결측치 보간(전후 2시간 이내)
        df_h['USDKRW'] = df_h['USDKRW'].ffill(limit=6).bfill(limit=2)
        df_h = df_h.dropna(subset=['EWY', 'KOSPI', 'SAMSUNG', 'USDKRW'])
        if len(df_h) >= 15:
            # 통계적 설명력(R²) 극대화를 위해 과거 누적 기간부터 기준일까지의 전체 주간장 1시간봉 시계열 사용 (지수가중 회귀 결합)
            merged_hourly = df_h.copy() if USE_FULL_CUMULATIVE_HISTORY else df_h.tail(lookback_days * 6).copy()
            hourly_sync_active = True
            print(f"  - 🎯 [주간장 1시간봉(1h) 누적 동시간대 매칭 완료] 총 {len(merged_hourly)}개 주간장 1h 캔들 "
                  f"({merged_hourly.index[0].strftime('%Y-%m-%d %H:%M')} ~ {merged_hourly.index[-1].strftime('%Y-%m-%d %H:%M')} KST) 기반으로 시차 0초 회귀식을 자동 산출합니다!")

    # ==========================================================================
    # ★ [V4.1 완전 자동 영점 동기화] 수동 3단계 입력창 없이 한국 주간장 마감(15:30 KST) EWYBUSDT 대용시세와 KRX 종가를 1:1 자동 직결
    # ==========================================================================
    default_ats_spot = float(binance_1530_spot) if (binance_1530_spot is not None and binance_1530_spot > 10.0) else latest_ewy_spot
    default_has_ats  = (binance_1530_spot is not None and binance_1530_spot > 10.0)

    sync_cfg = {
        'sync_ewy_ats': float(default_ats_spot),
        'has_ats_input': bool(default_has_ats),
        'sync_kospi': float(queried_kospi_pt),
        'sync_samsung': int(queried_samsung_krw),
        'sync_usdkrw': float(queried_usdkrw),
        'is_post_us_override': False
    }
    if sync_override_cache is not None:
        sync_override_cache[anchor_date] = sync_cfg

    queried_kospi_pt    = round(sync_cfg['sync_kospi'], 2)
    queried_samsung_krw = int(sync_cfg['sync_samsung'])
    queried_usdkrw      = round(sync_cfg['sync_usdkrw'], 2)
    ewy_anchor_ref      = float(sync_cfg['sync_ewy_ats'])

    if sync_cfg['has_ats_input']:
        src_tag = f"바이낸스 {BINANCE_EWY_SYMBOL}" if (binance_1530_spot is not None and abs(ewy_anchor_ref - binance_1530_spot) < 1e-4) else "EWY ATS"
        if sync_cfg['is_post_us_override']:
            queried_time_info = f"주간장 실시간 Spot Override 직결 ({src_tag} ${ewy_anchor_ref:.2f} ↔ KOSPI {queried_kospi_pt:,.1f}pt 동시동기화)"
        else:
            queried_time_info = f"{anchor_date} 15:30 KST 동시간대 직결 ({src_tag} ${ewy_anchor_ref:.2f} ↔ KOSPI {queried_kospi_pt:,.1f}pt 영점동기화)"

    # ★ 주간장 1시간봉(1h) 매칭 성공 시 1h 데이터셋으로 회귀식 도출, 아닐 경우 일봉(1d) 데이터셋 사용
    if hourly_sync_active:
        win = merged_hourly.copy()
        eff_halflife = max(halflife * 6, 6)  # 1일 약 6개 1h 캔들 기준 반감기 환산
        ret_lag = 6                          # 6시간(1거래일 주간장) 수익률 상관·베타
        freq_unit_str = f"주간장 1시간봉 {len(win)}개 (바이낸스 {BINANCE_EWY_SYMBOL} 1h ↔ 야후 KRX 1h 동시매칭, 반감기 {halflife}일[{eff_halflife}시간])"
        w_start_str = win.index[0].strftime('%Y-%m-%d %H:%M')
        w_end_str   = win.index[-1].strftime('%Y-%m-%d %H:%M')
    else:
        win = merged_daily.tail(min(len(merged_daily), lookback_days)).copy()
        eff_halflife = max(halflife, 1)
        ret_lag = 3
        freq_unit_str = f"일봉 {len(win)}거래일 (반감기 {halflife}일)"
        w_start_str = win.index[0].strftime('%Y-%m-%d')
        w_end_str   = win.index[-1].strftime('%Y-%m-%d')

    def fit_ts_relationship(col_name, current_queried_val):
        x = win['EWY'].values.astype(float)
        y = win[col_name].values.astype(float)
        n = len(win)

        if n >= 3 and np.std(x) > 0 and np.std(y) > 0:
            r_pearson, _ = stats.pearsonr(x, y)
            slope_ols, intercept_ols, _, _, _ = stats.linregress(x, y)
        else:
            r_pearson, slope_ols, intercept_ols = 1.0, 0.0, current_queried_val

        ret_x = win['EWY'].pct_change(ret_lag).dropna().values
        ret_y = win[col_name].pct_change(ret_lag).dropna().values
        if len(ret_x) >= 5 and np.std(ret_x) > 0 and np.std(ret_y) > 0:
            r_ret3, _ = stats.pearsonr(ret_x, ret_y)
            beta_ret3 = r_ret3 * (np.std(ret_y, ddof=1) / np.std(ret_x, ddof=1))
        else:
            r_ret3, beta_ret3 = r_pearson, 1.0

        weights = np.exp(-np.log(2.0) * np.arange(n - 1, -1, -1) / max(eff_halflife, 1))
        weights /= weights.sum()

        mx = np.sum(weights * x)
        my = np.sum(weights * y)
        cov_xy = np.sum(weights * (x - mx) * (y - my))
        var_x  = np.sum(weights * (x - mx) ** 2)
        var_y  = np.sum(weights * (y - my) ** 2)

        slope_ew = cov_xy / var_x if var_x > 0 else slope_ols
        intercept_ew = my - slope_ew * mx
        r_ew = cov_xy / np.sqrt(var_x * var_y) if (var_x > 0 and var_y > 0) else r_pearson

        lx = np.log(np.maximum(x, 1e-6))
        ly = np.log(np.maximum(y, 1e-6))
        mlx = np.sum(weights * lx)
        mly = np.sum(weights * ly)
        cov_lxy = np.sum(weights * (lx - mlx) * (ly - mly))
        var_lx  = np.sum(weights * (lx - mlx) ** 2)

        beta_ew = cov_lxy / var_lx if var_lx > 0 else beta_ret3
        log_a_ew = mly - beta_ew * mlx

        return {
            'n_days': int(n),
            'r_pearson': float(r_pearson),
            'r2_pearson': float(r_pearson ** 2),
            'unexplained_pct': float((1.0 - r_pearson ** 2) * 100.0),
            'r_ew': float(r_ew),
            'r2_ew': float(r_ew ** 2),
            'r_ret3': float(r_ret3),
            'slope_ew': float(slope_ew),
            'intercept_ew': float(intercept_ew),
            'beta_ew': float(beta_ew),
            'log_a_ew': float(log_a_ew),
            'beta_ret3': float(beta_ret3),
            'queried_val': float(current_queried_val)
        }

    rel_info = {
        'KOSPI': fit_ts_relationship('KOSPI', queried_kospi_pt),
        'SAMSUNG': fit_ts_relationship('SAMSUNG', queried_samsung_krw),
        'USDKRW': fit_ts_relationship('USDKRW', queried_usdkrw),
        'queried_kospi_pt': queried_kospi_pt,
        'queried_samsung_krw': queried_samsung_krw,
        'queried_usdkrw': queried_usdkrw,
        'queried_time_info': queried_time_info,
        'ewy_anchor_ref': ewy_anchor_ref,
        'has_ats_input': sync_cfg['has_ats_input'],
        'is_post_us_override': sync_cfg['is_post_us_override'],
        'hourly_sync_active': hourly_sync_active,
        'freq_unit_str': freq_unit_str,
        'binance_source_str': binance_source_str,
        'window_start': w_start_str,
        'window_end': w_end_str,
        'n_obs': int(len(win)),
        'halflife': int(halflife),
        'yf_success': yf_success
    }

    def derive_target_from_ts_relationship(ewy_target, asset_key, blend_log_weight=0.60):
        m = rel_info[asset_key]
        reg_ols_target = m['intercept_ew'] + m['slope_ew'] * ewy_target
        reg_log_target = np.exp(m['log_a_ew'] + m['beta_ew'] * np.log(max(ewy_target, 1.0)))
        pure_reg_target = blend_log_weight * reg_log_target + (1.0 - blend_log_weight) * reg_ols_target

        if anchor_to_yf_spot:
            anchored_log = m['queried_val'] * ((max(ewy_target, 1.0) / max(ewy_anchor_ref, 1.0)) ** m['beta_ew'])
            anchored_ols = m['queried_val'] + m['slope_ew'] * (ewy_target - ewy_anchor_ref)
            return float(blend_log_weight * anchored_log + (1.0 - blend_log_weight) * anchored_ols)
        else:
            return float(pure_reg_target)

    print(f"[시계열 관계 & 동시간대 영점 동기화 완료] 분석 구간: {rel_info['window_start']} ~ {rel_info['window_end']} ({freq_unit_str})")
    print(f"  - 영점(Origin) 매칭: EWY 기준원점 ${ewy_anchor_ref:.2f} ↔ KOSPI {queried_kospi_pt:,.1f}pt / 삼성전자 {queried_samsung_krw:,}원 / 환율 {queried_usdkrw:,.1f}원")
    for k in ['KOSPI', 'SAMSUNG', 'USDKRW']:
        mk = rel_info[k]
        print(f"  - {k:<7}: 기준값={mk['queried_val']:,.2f} | 상관계수 r={mk['r_pearson']:+.4f} (R²={mk['r2_pearson']*100:.1f}%, 고유리스크={mk['unexplained_pct']:.1f}%) "
              f"| 탄력성 Beta={mk['beta_ew']:+.3f} | 회귀기울기 Slope={mk['slope_ew']:+.2f}")
    if sync_cfg['has_ats_input'] and not sync_cfg['is_post_us_override']:
        imp_k = derive_target_from_ts_relationship(latest_ewy_spot, 'KOSPI')
        imp_s = int(round(derive_target_from_ts_relationship(latest_ewy_spot, 'SAMSUNG'), -2))
        ov_pct = (latest_ewy_spot / ewy_anchor_ref - 1.0) * 100.0
        print(f"  - 🌅 [아침 8시 프리마켓 진단] 15:30 KST(${ewy_anchor_ref:.2f}) 이후 미국 본장 마감(${latest_ewy_spot:.2f})까지 야간 순변동: {ov_pct:+.2f}%")
        print(f"  - 🎯 [오늘 09:00 KRX 내재 공정 시초가] 내재 KOSPI = {imp_k:,.1f}pt | 내재 삼성전자 = {imp_s:,}원")
    elif sync_cfg['has_ats_input'] and sync_cfg['is_post_us_override']:
        ov_pct = (ewy_anchor_ref / latest_ewy_spot - 1.0) * 100.0
        print(f"  - 🚀 [주간장 실시간 Spot Override 가동] 미국 정규장 종가(${latest_ewy_spot:.2f}) 대비 현재 EWY ATS/EWYB(${ewy_anchor_ref:.2f}) 장외 변동: {ov_pct:+.2f}%")
    print("")
    return rel_info, derive_target_from_ts_relationship

# ==============================================================================
# 9. 보조 함수: Max Pain, 누적 백분위수(Expanding Rank) 및 동적 기준일 인덱싱
# ==============================================================================
def calc_max_pain(sub_df):
    if len(sub_df) == 0:
        return np.nan
    strikes = sorted(sub_df['Strike'].unique())
    calls = sub_df[sub_df['Option Type'] == 'Call'].groupby('Strike')['Open Interest'].sum()
    puts  = sub_df[sub_df['Option Type'] == 'Put'].groupby('Strike')['Open Interest'].sum()

    min_loss = None
    mp_strike = np.nan
    for s in strikes:
        c_loss = sum(max(0.0, s - k) * oi for k, oi in calls.items())
        p_loss = sum(max(0.0, k - s) * oi for k, oi in puts.items())
        tot_loss = c_loss + p_loss
        if min_loss is None or tot_loss < min_loss:
            min_loss = tot_loss
            mp_strike = s
    return float(mp_strike)

def pit_expanding_pct_rank(series, min_periods=5):
    try:
        return series.expanding(min_periods=min_periods).rank(pct=True).fillna(0.5) * 100.0
    except Exception:
        vals = series.values
        out = np.full(len(vals), 50.0)
        for i in range(len(vals)):
            sub = vals[:i + 1]
            valid = sub[np.isfinite(sub)]
            if len(valid) >= min_periods and np.isfinite(vals[i]):
                out[i] = (np.sum(valid <= vals[i]) / len(valid)) * 100.0
        return pd.Series(out, index=series.index)

def get_base_date_for_window(date_list, win_days):
    n = len(date_list)
    if n == 0:
        return None
    if win_days <= 1:
        idx = max(0, n - 2)
    else:
        idx = max(0, n - win_days)
    return date_list[idx]


# ==============================================================================
# 10. [핵심 V4.1] 표 독해 가이드 & 쉬운 해설 & 30초 3단계 요약이 탑재된 리포트 생성 엔진
# ==============================================================================
# ==============================================================================
# ★ [V4.4] 확정 라벨 20개 구간(2025-03-17 ~ 2026-11-05, 경계 = 실제 종가 고점·저점) 학습·검증 블록
#  - 국면 판정(상승 U / 하락 D / 횡보 S): 15일 고점 대비 낙폭·15일 저점 대비 상승폭(20일 실현변동성으로 나눠 정규화),
#    20일 실현변동성, 20일 범위 내 위치, IV 스트레스(근월 IV 백분위·근월 IV 5일 변화·근월-원월 IV 차 평균)의 L1 다항 로지스틱
#  - 라벨 기간 구간 제외 교차검증 균형정확도 55%(2025<->2026 교차 61%) vs 20일선 48%,
#    2024 비학습 기간(종가 8% 되돌림 대리 라벨) 상승/하락 71% vs 20일선 68%. 현재 상태 인식용(미래 수익률 예측용 아님)
#  - 급락 위험도: 풋/콜 OI 비율(만기 남은 계약, 120영업일 백분위)과 근월 25D 스큐 백분위의 평균 -> 상(2/3 이상)/중/하(1/3 미만)
#  - 신호 신뢰도표: 각 신호가 켜진 날의 '10영업일 안에 -5% 이상 하락' 비율을 라벨 기간과 2024 비학습 기간으로 나눠 표기(V4.4 전 거래일 실행 기준)
# ==============================================================================
PHASE_MODEL = {'feats': ['p_dd15n', 'p_ru15n', 'p_rv20', 'p_pos20', 'c_stress'], 'mu': [-0.089252, 0.241832, 0.436339, 0.67114, -0.005591], 'sd': [0.103422, 0.184856, 0.219806, 0.340012, 0.736027], 'coef': {'U': [0.0, 0.518448, 0.0, 0.0, 0.0], 'D': [-0.100424, 0.0, 0.273005, -0.41938, 0.0], 'S': [0.0, 0.0, 0.0, 0.0, -0.141561]}, 'icpt': {'U': 0.068784, 'D': -0.117584, 'S': 0.048801}, 'comp': {'c_stress': {'cols': ['o_ivn_pct', 'o_ivn_d5', 'o_term'], 'mu': [0.684999, 0.003613, 0.050518], 'sd': [0.271872, 0.159097, 0.11537]}}, 'cv': {'loso': 55.0, 'year': 61.3, 'ma20': 48.1, 'reg': 48.3, 'ho_phase': 70.6, 'ho_ma': 68.3, 'lag': 4.0}}
PHASE_REL = {'rows': [('분배 폭락 경보', 'dist', '경보', 2, 50, 28, 43, 28, 7, '유효(위험↑, 두 기간 일치) · 2024 표본 적음'), ('기본 징후 2개 이상', 'pb2', '경보', 23, 36, 26, 45, 28, 11, '유효(위험↑, 두 기간 일치) · 2024 표본 적음'), ('검증 경보(분배 또는 기본 징후 2+)', 'v44', '경보', 24, 37, 25, 41, 28, 17, '유효(위험↑, 두 기간 일치) · 2024 표본 적음'), ('급락 위험도 상', 'rkH', '판정', 30, 47, 20, 39, 22, 95, '유효(위험↑, 두 기간 일치)'), ('급락 위험도 하', 'rkL', '판정', 26, 9, 35, 13, 30, 23, '유효(위험↓, 두 기간 일치)'), ('국면 하락(D) 1순위', 'phD', '상태', 35, 39, 22, 26, 31, 115, '기간 의존(두 기간 방향 반대)'), ('국면 상승(U) 1순위', 'phU', '상태', 45, 20, 35, 52, 24, 42, '기간 의존(두 기간 방향 반대)'), ('국면 횡보(S) 1순위', 'phS', '상태', 20, 27, 29, 20, 33, 83, '약함·불확실'), ('고점래치', 'latch', '참고', 5, 0, 30, 30, 29, 10, '기간 의존(두 기간 방향 반대) · 2024 표본 적음'), ('사각지대 3중 체크 1개 이상', 'bs1', '참고', 49, 23, 33, 35, 27, 43, '기간 의존(두 기간 방향 반대)'), ('원인① 점화', 'c1', '참고', 3, 57, 27, 50, 29, 2, '유효(위험↑, 두 기간 일치) · 2024 표본 적음'), ('원인② 점화', 'c2', '참고', 33, 38, 24, 22, 30, 37, '기간 의존(두 기간 방향 반대)'), ('레짐 B 1순위', 'regB', '참고', 37, 35, 24, 30, 28, 81, '약함·불확실'), ('레짐 A 1순위', 'regA', '참고', 46, 22, 33, 35, 26, 81, '기간 의존(두 기간 방향 반대)'), ('평가손실 다수(60%+) 판정', 'sq', '참고', 60, 26, 31, 29, 28, 158, '정보력 없음')], 'base_lb': 28, 'base_ho': 29, 'risk': {'상': 44, '중': 25, '하': 10, 'base': 28, 'n': 644}, 'alarm': {'dist': [50, 28, 43, 28], 'pb2': [36, 26, 45, 28], 'v44': [37, 25, 41, 28]}}
AMB_CAL = {'n': 673, 't1_all': 14, 't1_c2': 12, 'n_c2': 174, 't1_all5': 41, 't1_c25': 37, 'n_c1': 16, 't2_c1': 0, 't2_c15': 31}   # ★ [V4.3.3] 섹션 3-3 하락폭 타깃 실측 도달률(%) — 674거래일 실행 기준
PB_CAL = {'n': 673, 's1': 73, 's2': 88, 's4': 88, 'mp_up': 58, 'base_up': 57, 'mp_dn': 43, 'base_dn': 42}   # ★ [V4.3.4] 섹션 3-2 눌림목 단계 실측 방어율(%)·Max Pain 자석 실측 — 674거래일 실행 기준


def phase_price_feats(px):
    px = px.astype(float); lr = np.log(px).diff(); o = pd.DataFrame(index=px.index)
    for n in (1, 5, 10, 20):
        o['p_r%d' % n] = np.log(px / px.shift(n))
    ma20 = px.rolling(20, min_periods=10).mean(); ma5 = px.rolling(5).mean()
    o['p_ma20'] = px / ma20 - 1.0; o['p_ma5_20'] = ma5 / ma20 - 1.0
    o['p_dd15'] = px / px.rolling(15, min_periods=5).max() - 1.0; o['p_ru15'] = px / px.rolling(15, min_periods=5).min() - 1.0
    o['p_rv20'] = lr.rolling(20, min_periods=10).std() * np.sqrt(252.0)
    mx, mn = px.rolling(20, min_periods=10).max(), px.rolling(20, min_periods=10).min()
    o['p_pos20'] = (px - mn) / (mx - mn).replace(0, np.nan)
    o['p_dd15n'] = o['p_dd15'] / o['p_rv20']; o['p_ru15n'] = o['p_ru15'] / o['p_rv20']
    return o


def phase_daily_aggs(df):
    d = df[(df['DTE'] > 0) & (df['Open Interest'] > 0)]
    oi = d['Open Interest'].astype(float).values; isP = (d['Option Type'] == 'Put').values
    g = pd.DataFrame({'q': d['Quote Date'].values, 'a_coi': np.where(~isP, oi, 0.0), 'a_poi': np.where(isP, oi, 0.0)}).groupby('q').sum()
    return g


def phase_base_table(df_pit, ts_metrics):
    M = PHASE_MODEL
    px = df_pit.groupby('Quote Date')['EWY Price'].first()
    B = phase_price_feats(px)
    a = phase_daily_aggs(df_pit).reindex(B.index)
    B['o_pcoi'] = np.log(a['a_poi'] / a['a_coi'])
    t = ts_metrics.reindex(B.index)
    B['o_ivn_pct'] = t['Near_ATM_IV_pct'] / 100.0
    B['o_ivn_d5'] = t['Near_ATM_IV'] - t['Near_ATM_IV'].shift(5)
    B['o_term'] = t['Term_Near_Back']
    B['o_skn_pct'] = t['Near_Skew_25D_pct'] / 100.0
    for k, c in M['comp'].items():
        B[k] = pd.concat([((B[cc] - mu) / sd).clip(-4, 4) for cc, mu, sd in zip(c['cols'], c['mu'], c['sd'])], axis=1).mean(axis=1)
    z = np.column_stack([((B[f] - mu) / sd).clip(-4, 4).values for f, mu, sd in zip(M['feats'], M['mu'], M['sd'])])
    z = np.where(np.isfinite(z), z, 0.0)
    lg = np.column_stack([M['icpt'][c] + z.dot(np.array(M['coef'][c])) for c in ('U', 'D', 'S')])
    lg = lg - lg.max(axis=1, keepdims=True); ex = np.exp(lg); pr = ex / ex.sum(axis=1, keepdims=True) * 100.0
    B['PhU'], B['PhD'], B['PhS'] = pr[:, 0], pr[:, 1], pr[:, 2]
    B['PcoiPct'] = B['o_pcoi'].rolling(120, min_periods=40).apply(lambda v: float(np.mean(v <= v[-1])), raw=True)
    B['Risk'] = (B['PcoiPct'] + B['o_skn_pct']) / 2.0
    return B


# ==============================================================================
# ★ [V4.3.6 신설] 감마 플립 D 산식 · 신호 기록 · 자동 채점
#  - D 산식: ① 당일 만기 계약 제외(DTE≥1: 오늘 종가에 결제된 계약은 다음 세션 헤지 대상이 아님)
#            ② IV 해 실패 표시값(수집기 탐색 범위 경계 0.0001·5.0)과 0 이하 IV는 같은 만기 외가격 스마일로 보간
#            ③ 감마·바나·참을 수집기 IV 계산과 같은 기준(영업일/252 · SOFR · 배당 2%)으로 계산
#            ④ 탐색 구간(현가 0.85~1.25배)에서 순감마 부호가 바뀌지 않으면 '구간 내 플립 없음' (V4.3.5는 최소 |GEX| 지점을 선으로 출력)
#  - 신호 기록: 보고서를 만들 때 기준일·Tier별 신호를 OUTPUT_DIR의 SIGNAL_LOG_FILENAME(CSV)에 저장
#            (다음 한국 정규장 09:00 KST 전에 최신 기준일로 만든 기록만 '실시간', 그 외 '사후')
#  - 자동 채점: 다음 한국 정규장 KOSPI·삼성전자(야후 일봉)와 EWY 24시간 가격(바이낸스 EWYBUSDT 5분봉),
#            다음 미국 종가(옵션 데이터)로 채점해 [섹션 6] (6-5)에 표시
# ==============================================================================
ENGINE_VERSION = "V4.3.7"
FLIP_GRID_LO, FLIP_GRID_HI, FLIP_GRID_N = 0.85, 1.25, 81   # 탐색 구간(현가 배수)·격자 수 (V4.3.5와 동일)
GAMMA_IV_FLOOR = 0.20                                       # IV 하한 (V4.3.5와 동일)
GAMMA_DIV_YIELD = 0.02                                      # [V4.3.7] 배당 반영 값(Q_eff)이 없을 때만 쓰는 대체값(수집기 가정)
GAMMA_RF_FALLBACK = 0.045                                   # SOFR 열이 비었을 때만 사용
IV_MARK_LO, IV_MARK_HI = 0.0011, 4.99                       # 수집기 IV 탐색 범위(1e-4~5.0) 경계 = 해 실패 표시값
SMILE_VALID_LO, SMILE_VALID_HI = 0.05, 3.0                  # 스마일 보간에 쓰는 정상 IV 범위


def _smile_iv_v436(day_df, spot, valid):
    """같은 만기의 외가격(콜: 행사가≥현가 · 풋: 행사가<현가) · Bid>0 · 정상 IV 계약으로 행사가별 스마일을 만들고 선형 보간"""
    out = np.full(len(day_df), np.nan)
    if len(day_df) == 0:
        return out
    iv = day_df['Implied Volatility'].values.astype(float)
    k = day_df['Strike'].values.astype(float)
    typ = day_df['Option Type'].values
    bid = pd.to_numeric(day_df['Bid'], errors='coerce').fillna(0.0).values.astype(float)
    exps = day_df['Expiration Date'].astype(str).values
    for e in pd.unique(exps):
        idx = np.where(exps == e)[0]
        otm = ((typ[idx] == 'Call') & (k[idx] >= spot)) | ((typ[idx] == 'Put') & (k[idx] < spot))
        ok = otm & (bid[idx] > 0) & valid[idx]
        if ok.sum() >= 1:
            v = pd.Series(iv[idx][ok], index=k[idx][ok]).groupby(level=0).median().sort_index()
            out[idx] = np.interp(k[idx], v.index.values, v.values) if len(v) >= 2 else v.values[0]
    return out


def _gamma_v436(S, K, T, sig, r, q):
    sq = sig * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sig ** 2) * T) / sq
    return np.exp(-q * T) * stats.norm.pdf(d1) / (S * sq)


def _flip_scan_v436(S, K, T, sig, oi, w, r, q):
    """순감마(1% 변동당 주수) 곡선이 0을 지나는 가격 중 현가에 가장 가까운 점. 없으면 (nan, True, 구간 부호)"""
    if len(K) == 0:
        return float('nan'), True, ''
    grs = np.linspace(S * FLIP_GRID_LO, S * FLIP_GRID_HI, FLIP_GRID_N)
    gx = np.array([np.sum(oi * 100.0 * _gamma_v436(s, K, T, sig, r, q) * 0.01 * s * w) for s in grs])
    sch = np.where(np.diff(np.sign(gx)) != 0)[0]
    if len(sch) == 0:
        return float('nan'), True, ('+' if np.nanmean(gx) > 0 else '-')
    bi = sch[np.argmin(np.abs(grs[sch] - S))]
    s0, s1, g0, g1 = grs[bi], grs[bi + 1], gx[bi], gx[bi + 1]
    return (float(s0 - g0 * (s1 - s0) / (g1 - g0)) if g1 != g0 else float(s0)), False, ''


def calc_gamma_flip_v436(day_df, spot):
    """[V4.3.6 · V4.3.7 배당 반영] 감마 플립 D 산식 + GEX·바나·참(같은 기준) + V4.3.5 방식(A) 참고값(수집기 원래 IV)"""
    res = {'gflip': float('nan'), 'gflip_none': True, 'gflip_sign': '', 'gex_1pct': 0, 'van_sh': 0, 'chm_sh': 0, 'vc_tot': 0,
           'gflip_a': float('nan'), 'gflip_a_none': True, 'n_marker': 0}
    if day_df is None or len(day_df) == 0 or not np.isfinite(spot) or spot <= 0:
        return res
    d = day_df
    oi = pd.to_numeric(d['Open Interest'], errors='coerce').fillna(0.0).values.astype(float)
    dte = pd.to_numeric(d['DTE'], errors='coerce').values.astype(float)
    K = np.maximum(pd.to_numeric(d['Strike'], errors='coerce').fillna(1.0).values.astype(float), 1.0)
    iv = np.nan_to_num(pd.to_numeric(d['Implied Volatility'], errors='coerce').values.astype(float), nan=0.0)
    iv_a = np.nan_to_num(pd.to_numeric(d['IV_수집기'], errors='coerce').values.astype(float), nan=0.0) if 'IV_수집기' in d.columns else iv
    q_arr = (np.nan_to_num(pd.to_numeric(d['Q_eff'], errors='coerce').values.astype(float), nan=GAMMA_DIV_YIELD)
             if 'Q_eff' in d.columns else np.full(len(d), GAMMA_DIV_YIELD))   # ★ [V4.3.7] 만기별 실제 배당을 연속 배당률로 환산한 값
    isc = (d['Option Type'].values == 'Call')
    w = np.where(isc, 1.0, -1.0)
    qd = np.array(d['Quote Date'].astype(str).str[:10].tolist(), dtype='datetime64[D]')
    ed = np.array(d['Expiration Date'].astype(str).str[:10].tolist(), dtype='datetime64[D]')
    T_bd = np.maximum(np.busday_count(qd, ed).astype(float), 0.5) / 252.0      # 수집기와 같은 영업일 기준 (공휴일 미반영)
    T_cal = np.maximum(dte / 365.0, 1.0 / 365.0)
    r_d = GAMMA_RF_FALLBACK
    if 'Secured Overnight Financing Rate' in d.columns:
        _sf = pd.to_numeric(d['Secured Overnight Financing Rate'], errors='coerce')
        _sf = _sf[_sf > 0]
        if len(_sf) > 0:
            r_d = float(_sf.iloc[0]) / 100.0
    marker = (iv <= IV_MARK_LO) | (iv >= IV_MARK_HI)
    valid = (iv > SMILE_VALID_LO) & (iv < SMILE_VALID_HI) & ~marker
    sm = _smile_iv_v436(d, spot, valid)
    sig_d = np.maximum(np.where(marker | (iv <= 0), np.where(np.isfinite(sm), sm, GAMMA_IV_FLOOR), iv), GAMMA_IV_FLOOR)
    sig_a = np.maximum(iv_a, GAMMA_IV_FLOOR)
    base = (oi > 0) & np.isfinite(dte) & (dte <= 180)
    m_d = base & (dte >= 1)
    m_a = base & (dte >= 0)
    res['n_marker'] = int((marker & base).sum())

    # D 산식 감마 플립
    gf, none, sgn = _flip_scan_v436(spot, K[m_d], T_bd[m_d], sig_d[m_d], oi[m_d], w[m_d], r_d, q_arr[m_d])
    res.update(gflip=gf, gflip_none=none, gflip_sign=sgn)
    # V4.3.5 방식(A) 참고값: 당일 만기 포함 · 달력일/365 · r 4.5% · 배당 0 · 교차 없으면 최소 |GEX| 지점
    if m_a.any():
        Ka, Ta, sa, oa, wa = K[m_a], T_cal[m_a], sig_a[m_a], oi[m_a], w[m_a]
        ga, na, _ = _flip_scan_v436(spot, Ka, Ta, sa, oa, wa, 0.045, 0.0)
        if na:
            grs = np.linspace(spot * FLIP_GRID_LO, spot * FLIP_GRID_HI, FLIP_GRID_N)
            gx = np.array([np.sum(oa * 100.0 * _gamma_v436(s, Ka, Ta, sa, 0.045, 0.0) * 0.01 * s * wa) for s in grs])
            ga = float(grs[np.argmin(np.abs(gx))])
        res.update(gflip_a=ga, gflip_a_none=na)

    # 현가 GEX · 바나 · 참 (D 기준 통일)
    if m_d.any():
        Kd, Td, sd, od, wd, cd = K[m_d], T_bd[m_d], sig_d[m_d], oi[m_d], w[m_d], isc[m_d]
        q = q_arr[m_d]
        sq = sd * np.sqrt(Td)
        d1 = (np.log(spot / Kd) + (r_d - q + 0.5 * sd ** 2) * Td) / sq
        d2 = d1 - sq
        eqt = np.exp(-q * Td)
        pdf = stats.norm.pdf(d1)
        gam = eqt * pdf / (spot * sq)
        van = -eqt * pdf * d2 / sd
        chm = -(eqt * pdf * (2.0 * (r_d - q) * Td - d2 * sq) / (2.0 * Td * sq)) / 252.0
        res['gex_1pct'] = int(round(np.sum(od * 100.0 * gam * (0.01 * spot) * wd)))
        otmp = (~cd) & (Kd <= spot * 1.05) & (Kd >= spot * 0.80)
        res['van_sh'] = int(round(np.sum(od[otmp] * 100.0 * np.abs(van[otmp]) * 0.03)))
        res['chm_sh'] = int(round(np.sum(od[otmp] * 100.0 * np.abs(chm[otmp]))))
        res['vc_tot'] = res['van_sh'] + res['chm_sh']
    return res


# ------------------------------------------------------------------------------
# 신호 기록 · 자동 채점
# ------------------------------------------------------------------------------
SIG_SIGNAL_COLS = ['기준일', 'Tier', '엔진버전', '기록시각', '기록구분', 'EWY종가', '근월ATM_IV', '레짐1순위', '국면1순위', '하락국면', '급락위험상',
                   '원인1', '원인2', '검증경보', '기습1차타깃', '기습2차타깃', 'D선', 'D선없음', 'D선부호', 'A선', 'A선없음', 'GEX_D',
                   '원인1_병행', '원인2_병행', '병행_지배력', 'D선정의', 'D선_이전']
SIG_RESULT_COLS = ['한국장일', 'KOSPI_시가갭%', 'KOSPI_시가종가%', 'KOSPI_전일대비%', 'KOSPI_시가저가%', 'KOSPI_고저폭%',
                   '삼성_시가갭%', '삼성_시가종가%', '삼성_전일대비%',
                   'EWY24_출처', 'EWY24_미국마감가', 'EWY24_한국시가', 'EWY24_한국종가', 'EWY24_한국고가', 'EWY24_한국저가',
                   'D선위치_미국종가', 'D선위치_한국시가', 'D선위치_한국종가', '다음미국기준일', '다음미국종가', '채점시각']
SIG_LOG_COLS = SIG_SIGNAL_COLS + SIG_RESULT_COLS
# 실시간/사후 구분에만 쓰는 KRX 휴장일 (확실한 날짜만 넣음: 빠진 휴장일은 '사후'로 더 엄격하게 분류될 뿐 채점에는 영향 없음 — 채점은 야후 KOSPI 실제 거래일 사용)
KRX_HOLIDAYS_KNOWN = {'2026-01-01', '2026-02-16', '2026-02-17', '2026-02-18', '2026-03-02', '2026-05-01', '2026-05-05', '2026-05-25',
                      '2026-06-03', '2026-07-17', '2026-08-17', '2026-09-24', '2026-09-25', '2026-10-05', '2026-10-09', '2026-12-25',
                      '2026-12-31', '2027-01-01', '2027-03-01', '2027-05-05', '2027-12-31'}
EWYB_LISTING_DATE = '2026-06-23'
_SIG_MKT_CACHE = {}


def _sig_log_path():
    return os.path.join(_sig_dir_v437()[0], SIGNAL_LOG_FILENAME)   # ★ [V4.3.7] PC 프로그램 지정 폴더 > SIGNAL_LOG_DIR > OUTPUT_DIR


def _now_kst():
    return pd.Timestamp.now(tz='Asia/Seoul').tz_localize(None)


def _next_kr_open_kst(quote_date):
    d = pd.Timestamp(quote_date) + pd.Timedelta(days=1)
    while d.dayofweek >= 5 or d.strftime('%Y-%m-%d') in KRX_HOLIDAYS_KNOWN:
        d += pd.Timedelta(days=1)
    return d + pd.Timedelta(hours=9)


def _f(v):
    try:
        x = float(v)
        return x if np.isfinite(x) else np.nan
    except Exception:
        return np.nan


def _num(series):
    return pd.to_numeric(pd.Series(series).replace('', np.nan), errors='coerce').astype(float)


def _b(v):
    return str(v).strip().lower() in ('true', '1', 'y', 'yes')


def _s(v, nd=2):
    return '' if (v is None or not np.isfinite(v)) else f"{v:.{nd}f}"


def _load_sig_log(path):
    """기록 파일 읽기. 엑셀 저장 등으로 인코딩이 바뀌었으면 cp949도 시도하고, 끝내 못 읽으면 (빈 기록, False)를 돌려 원본을 덮어쓰지 않게 함"""
    log, readable = None, True
    if os.path.exists(path):
        for enc in ('utf-8-sig', 'cp949'):
            try:
                log = pd.read_csv(path, dtype=str, keep_default_na=False, encoding=enc)
                break
            except Exception:
                log = None
        readable = log is not None
    if log is None:
        log = pd.DataFrame(columns=SIG_LOG_COLS)
    for c in SIG_LOG_COLS:
        if c not in log.columns:
            log[c] = ''
    log = log[SIG_LOG_COLS].astype(object)
    return log.fillna(''), readable


def _upsert_signal_record(log, rec):
    key = (log['기준일'].astype(str) == rec['기준일']) & (log['Tier'].astype(str) == rec['Tier'])
    if key.any():
        i = log.index[key][0]
        if str(log.at[i, '기록구분']) == '실시간' and rec['기록구분'] != '실시간':
            return log                                   # 실시간 기록은 사후 재실행으로 덮어쓰지 않음
        if str(log.at[i, 'D선정의']) != str(rec.get('D선정의', '')) and str(log.at[i, 'D선_이전']) == '' and str(log.at[i, 'D선없음']) != '':
            log.at[i, 'D선_이전'] = '없음' if _b(log.at[i, 'D선없음']) else str(log.at[i, 'D선'])   # ★ [V4.3.7] 정의가 바뀌기 전 D선 보관
        for c in SIG_SIGNAL_COLS:
            if c == 'D선_이전' and str(rec.get(c, '')) == '':
                continue                                 # ★ [V4.3.7] 보관해 둔 이전 정의 D선은 지우지 않음
            log.at[i, c] = rec.get(c, '')
        return log
    row = {c: rec.get(c, '') for c in SIG_LOG_COLS}
    return pd.concat([log, pd.DataFrame([row], dtype=object)], ignore_index=True)


def _yf_daily_ohlc(ticker, start, end):
    key = ('yf', ticker, start, end)
    if key in _SIG_MKT_CACHE:
        return _SIG_MKT_CACHE[key]
    out = None
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(start=start, end=end, interval='1d', auto_adjust=False)
        if h is not None and len(h) > 0:
            h = h[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric, errors='coerce').dropna()
            h = h[(h['Open'] > 0) & (h['Close'] > 0)]
            idx = h.index
            if getattr(idx, 'tz', None) is not None:
                idx = idx.tz_convert('Asia/Seoul').tz_localize(None)
            h.index = pd.to_datetime(idx).strftime('%Y-%m-%d')
            out = h[~h.index.duplicated(keep='last')].sort_index()
    except Exception:
        out = None
    _SIG_MKT_CACHE[key] = out
    return out


def _binance_5m_ohlc(start_ms, end_ms):
    """바이낸스 EWYBUSDT 5분봉 OHLC (직접 접속 엔드포인트만 사용) -> UTC 인덱스 DataFrame"""
    key = ('bn', start_ms, end_ms)
    if key in _SIG_MKT_CACHE:
        return _SIG_MKT_CACHE[key]
    sym = (BINANCE_EWY_SYMBOL or 'EWYBUSDT').strip().upper()
    out = None
    for base in ("https://data-api.binance.vision/api/v3/klines", "https://api-gcp.binance.com/api/v3/klines", "https://api.binance.com/api/v3/klines"):
        rows, cur, ok = [], int(start_ms), False
        try:
            for _ in range(80):
                url = base + "?" + urllib.parse.urlencode({"symbol": sym, "interval": "5m", "startTime": cur, "endTime": int(end_ms), "limit": 1000})
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                ok = True
                if not data:
                    break
                rows += data
                cur = int(data[-1][0]) + 1
                if len(data) < 1000 or cur > end_ms:
                    break
        except Exception:
            ok = False
        if ok:
            if rows:
                b = pd.DataFrame([r[:5] for r in rows], columns=['t', 'open', 'high', 'low', 'close'])
                b['t'] = pd.to_datetime(b['t'].astype('int64'), unit='ms', utc=True)
                out = b.set_index('t')[['open', 'high', 'low', 'close']].astype(float).sort_index()
                out = out[~out.index.duplicated(keep='last')]
            else:
                out = pd.DataFrame(columns=['open', 'high', 'low', 'close'])
            break
    _SIG_MKT_CACHE[key] = out
    return out


def _side(px, line):
    if not np.isfinite(px) or not np.isfinite(line):
        return ''
    return '아래' if px < line else '위'


def _score_signal_log(log, df_pit, now_kst):
    notes, n_new = [], 0
    if len(log) == 0:
        return log, n_new, notes
    today = now_kst.strftime('%Y-%m-%d')
    # (1) 다음 미국 기준일 · EWY 종가 (옵션 데이터, 네트워크 불필요)
    px = df_pit.groupby('Quote Date')['EWY Price'].first()
    qd = list(px.index)
    for i in log.index:
        if str(log.at[i, '다음미국종가']) == '':
            d = str(log.at[i, '기준일'])
            j = int(np.searchsorted(qd, d, side='right'))
            if j < len(qd):
                log.at[i, '다음미국기준일'] = qd[j]
                log.at[i, '다음미국종가'] = _s(float(px.iloc[j]))
    # (2) KOSPI · 삼성전자 일봉 (야후)
    pend = log[log['KOSPI_시가종가%'].astype(str) == '']
    if len(pend) > 0:
        st = (pd.Timestamp(min(pend['기준일'].astype(str))) - pd.Timedelta(days=12)).strftime('%Y-%m-%d')
        en = (pd.Timestamp(today) + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        kx = _yf_daily_ohlc('^KS11', st, en)
        sx = _yf_daily_ohlc('005930.KS', st, en)
        if kx is None or len(kx) == 0:
            notes.append('야후 KOSPI 일봉 조회 실패 — 다음 실행 때 다시 채점')
        else:
            kd = list(kx.index)
            done_cut = today if (now_kst.hour * 60 + now_kst.minute) >= 16 * 60 + 30 else (pd.Timestamp(today) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            for i in pend.index:
                d = str(log.at[i, '기준일'])
                j = int(np.searchsorted(kd, d, side='right'))
                if j >= len(kd) or j == 0:
                    continue
                kday = kd[j]
                if kday > done_cut:
                    continue
                o, h, l, c = (float(kx.iloc[j][x]) for x in ('Open', 'High', 'Low', 'Close'))
                pc = float(kx.iloc[j - 1]['Close'])
                log.at[i, '한국장일'] = kday
                log.at[i, 'KOSPI_시가갭%'] = _s(np.log(o / pc) * 100)
                log.at[i, 'KOSPI_시가종가%'] = _s(np.log(c / o) * 100)
                log.at[i, 'KOSPI_전일대비%'] = _s(np.log(c / pc) * 100)
                log.at[i, 'KOSPI_시가저가%'] = _s(np.log(l / o) * 100)
                log.at[i, 'KOSPI_고저폭%'] = _s(np.log(h / l) * 100)
                if sx is not None and kday in sx.index:
                    sj = list(sx.index).index(kday)
                    if sj >= 1:
                        so, sc, spc = float(sx.iloc[sj]['Open']), float(sx.iloc[sj]['Close']), float(sx.iloc[sj - 1]['Close'])
                        log.at[i, '삼성_시가갭%'] = _s(np.log(so / spc) * 100)
                        log.at[i, '삼성_시가종가%'] = _s(np.log(sc / so) * 100)
                        log.at[i, '삼성_전일대비%'] = _s(np.log(sc / spc) * 100)
                log.at[i, '채점시각'] = now_kst.strftime('%Y-%m-%d %H:%M')
                n_new += 1
    # (3) EWY 24시간 가격 (바이낸스 EWYBUSDT 5분봉): 미국 마감가 · 한국 정규장 시가/종가/고가/저가
    need = log[(log['한국장일'].astype(str) != '') & (log['EWY24_출처'].astype(str) == '')]
    if len(need) > 0:
        old = need['한국장일'].astype(str) < EWYB_LISTING_DATE
        for i in need.index[old.values]:
            log.at[i, 'EWY24_출처'] = '자료없음'
        need = need[~old.values]
    if len(need) > 0:
        t0 = min(pd.Timestamp(str(d) + ' 15:00').tz_localize('America/New_York') for d in need['기준일'])
        t1 = max(pd.Timestamp(str(k) + ' 15:30').tz_localize('Asia/Seoul') for k in need['한국장일'])
        bars = _binance_5m_ohlc(int(t0.tz_convert('UTC').timestamp() * 1000), int(t1.tz_convert('UTC').timestamp() * 1000))
        if bars is None:
            notes.append('바이낸스 EWYBUSDT 조회 실패 — 다음 실행 때 다시 채점')
        else:
            for i in need.index:
                d, k = str(log.at[i, '기준일']), str(log.at[i, '한국장일'])
                uc = pd.Timestamp(d + ' 16:00').tz_localize('America/New_York').tz_convert('UTC')
                pre = bars[(bars.index < uc) & (bars.index >= uc - pd.Timedelta(minutes=30))]
                ks = bars[(bars.index >= pd.Timestamp(k + ' 09:00').tz_localize('Asia/Seoul').tz_convert('UTC')) &
                          (bars.index < pd.Timestamp(k + ' 15:30').tz_localize('Asia/Seoul').tz_convert('UTC'))]
                if len(pre) == 0 or len(ks) < 60:
                    if (now_kst - pd.Timestamp(k)).days > 5:
                        log.at[i, 'EWY24_출처'] = '자료없음'
                    continue
                log.at[i, 'EWY24_출처'] = 'binance_' + (BINANCE_EWY_SYMBOL or 'EWYBUSDT').upper()
                log.at[i, 'EWY24_미국마감가'] = _s(float(pre['close'].iloc[-1]), 3)
                log.at[i, 'EWY24_한국시가'] = _s(float(ks['open'].iloc[0]), 3)
                log.at[i, 'EWY24_한국종가'] = _s(float(ks['close'].iloc[-1]), 3)
                log.at[i, 'EWY24_한국고가'] = _s(float(ks['high'].max()), 3)
                log.at[i, 'EWY24_한국저가'] = _s(float(ks['low'].min()), 3)
    # (4) D선 위치
    for i in log.index:
        L = _f(log.at[i, 'D선'])
        none = _b(log.at[i, 'D선없음'])
        for col, src in (('D선위치_미국종가', 'EWY종가'), ('D선위치_한국시가', 'EWY24_한국시가'), ('D선위치_한국종가', 'EWY24_한국종가')):
            v = _f(log.at[i, src])
            if np.isfinite(v):
                log.at[i, col] = '없음' if none else _side(v, L)
    return log, n_new, notes


def _sig_stats_lines(g, block):
    """한 기록 묶음(실시간 / 사후·재현)의 신호별 채점 줄"""
    out = []
    g = g[g['KOSPI_시가종가%'].astype(str) != ''].copy()
    if len(g) == 0:
        out.append(f"[{block}] 채점 완료 기록 없음|0|-|-|-|-|-|-|-|-|표본 부족")
        return out
    oc = _num(g['KOSPI_시가종가%'])
    hit = (oc < 0).values
    pos = np.where(g['D선위치_한국시가'].astype(str) != '', g['D선위치_한국시가'].astype(str), g['D선위치_미국종가'].astype(str))
    groups = [('모든 날(기저)', np.ones(len(g), bool)),
              ('원인② 점화', g['원인2'].map(_b).astype(bool).values),
              ('원인① 점화', g['원인1'].map(_b).astype(bool).values),
              ('하락 국면 · D선 아래', g['하락국면'].map(_b).astype(bool).values & (pos == '아래')),
              ('하락 국면 · D선 위', g['하락국면'].map(_b).astype(bool).values & (pos == '위')),
              ('D선 아래 (국면 무관)', pos == '아래'),
              ('구간 내 플립 없음', pos == '없음')]
    _uni = (g['원인2_병행'].astype(str) != '').values           # ★ [V4.3.7] 병행 신호는 병행 값이 기록된 날끼리만 비교
    groups += [('원인② 점화(병행·검증 중)', g['원인2_병행'].map(_b).astype(bool).values & _uni),
               ('원인① 점화(병행·검증 중)', g['원인1_병행'].map(_b).astype(bool).values & _uni)]
    base = hit.mean()

    def pct(x):
        x = np.asarray(x, float)
        x = x[np.isfinite(x)]
        return f"{(x < 0).mean():.0%}" if len(x) else '-'
    for nm, m in groups:
        n = int(m.sum())
        if n == 0:
            out.append(f"[{block}] {nm}|0|-|-|-|-|-|-|-|-|표본 부족")
            continue
        hr = hit[m].mean()
        uni = _uni if '병행' in nm else np.ones(len(g), bool)
        rest = uni & ~m
        if nm.startswith('모든 날'):
            dif_s, p_s, verdict = '-', '-', '-'
        else:
            a, b_ = int(hit[m].sum()), int((~hit[m]).sum())
            c_, d_ = int(hit[rest].sum()), int((~hit[rest]).sum())
            try:
                p = float(stats.fisher_exact([[a, b_], [c_, d_]], alternative='greater')[1]) if (c_ + d_) > 0 else np.nan
            except Exception:
                p = np.nan
            dif = (hr - (hit[uni].mean() if uni.any() else base)) * 100
            dif_s, p_s = f"{dif:+.0f}%p", ('-' if not np.isfinite(p) else f"{p:.3f}")
            verdict = '표본 부족' if n < 20 else ('유효 후보' if (dif >= 10 and np.isfinite(p) and p < 0.05) else '차이 없음')
        gs = g[m]
        ewy = (_num(gs['EWY24_한국종가']) / _num(gs['EWY24_미국마감가'])).map(lambda x: np.log(x) * 100 if np.isfinite(x) and x > 0 else np.nan)
        dip = _num(gs['KOSPI_시가저가%'])
        dip_s = f"{(dip[np.isfinite(dip)] <= -1).mean():.0%}" if np.isfinite(dip).any() else '-'
        out.append(f"[{block}] {nm}|{n}|{hr:.0%}|{dif_s}|{p_s}|{pct(_num(gs['KOSPI_시가갭%']))}|{pct(_num(gs['KOSPI_전일대비%']))}|"
                   f"{pct(_num(gs['삼성_전일대비%']))}|{pct(ewy)}|{dip_s}|{verdict}")
    return out


def _sig_line_metrics(g, line_col, none_col):
    """한국 종가가 선 아래 -> 다음 미국 종가 회복 / 위 -> 이탈 건수"""
    L = _num(g[line_col])
    kc = _num(g['EWY24_한국종가'])
    nx = _num(g['다음미국종가'])
    ok = np.isfinite(L) & np.isfinite(kc) & np.isfinite(nx) & ~g[none_col].map(_b).astype(bool).values
    below = ok & (kc < L)
    above = ok & (kc >= L)
    rec = int((below & (nx >= L)).sum())
    brk = int((above & (nx < L)).sum())
    return rec, int(below.sum()), brk, int(above.sum())


def run_signal_log_and_score(today_rec, df_pit, pit_meta, latest_date):
    path = _sig_log_path()
    now_kst = _now_kst()
    # 최신 데이터 기준일로 만들고(미래 기준일 차단 0일) 다음 한국 정규장 09:00 KST 전에 만든 기록만 '실시간'
    is_latest = int(pit_meta.get('blocked_days_count', 0) or 0) == 0
    label = '실시간' if (is_latest and now_kst < _next_kr_open_kst(latest_date)) else '사후'
    rec = dict(today_rec)
    rec['기록시각'] = now_kst.strftime('%Y-%m-%d %H:%M')
    rec['기록구분'] = label
    log, readable = _load_sig_log(path)
    log, _mg_notes, _mg_files = _merge_stray_logs_v437(log, path)     # ★ [V4.3.7] 다른 폴더(엔진 출력 폴더·기준일 폴더)에 흩어진 기록 합치기
    log = _upsert_signal_record(log, rec)
    log, _n_mig = _migrate_dline_v437(log, df_pit)                     # ★ [V4.3.7] 예전 정의 D선은 새 정의로 1회 재계산
    log, n_new, notes = _score_signal_log(log, df_pit, now_kst)
    notes = list(_mg_notes) + list(notes)
    if _n_mig:
        notes.append(f"D선 {_n_mig}건을 새 정의({DLINE_DEF} · 배당 반영)로 다시 계산(이전 값은 'D선_이전' 열)")
    save_path = path
    if not readable:   # 기존 기록 파일을 읽지 못하면 덮어쓰지 않고 새 이름으로 저장
        save_path = path.replace('.csv', f"_읽기실패대체_{now_kst.strftime('%Y%m%d%H%M')}.csv")
        notes.append(f"기존 기록 파일을 읽지 못해 원본은 그대로 두고 {os.path.basename(save_path)}에 저장(UTF-8 CSV로 다시 저장 필요)")
    try:
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        log.sort_values(['기준일', 'Tier']).to_csv(save_path, index=False, encoding='utf-8-sig')
    except Exception as e:
        notes.append(f"기록 파일 저장 실패({e})")

    # 화면 표시는 보고서 기준일 시점까지 확정된 결과만 사용 (기준일 뒤의 결과는 숨김 = 미래참조 차단)
    cut = str(latest_date)
    tier = rec['Tier']
    g = log[log['Tier'].astype(str) == tier].copy()
    g = g[g['기준일'].astype(str) < cut]
    g.loc[g['한국장일'].astype(str) > cut, SIG_RESULT_COLS] = ''
    g.loc[g['다음미국기준일'].astype(str) > cut, ['다음미국기준일', '다음미국종가']] = ''
    live = g[g['기록구분'].astype(str) == '실시간']
    late = g[g['기록구분'].astype(str) != '실시간']
    n_scored = int((g['KOSPI_시가종가%'].astype(str) != '').sum())
    cnt = g['기록구분'].astype(str).value_counts()

    L = []
    L.append(f"### (6-5) 신호 기록·채점 [V4.3.6 신설 · V4.3.7 보강] (보고서를 만들 때 신호를 저장하고, 다음 한국 정규장 결과로 자동 채점)")
    L.append(f" - 기록 파일: {path} ({_sig_dir_v437()[1]}) | 이 Tier({tier}) 기록 {len(g)}건 (실시간 {int(cnt.get('실시간', 0))} · 사후 {int(cnt.get('사후', 0))} · "
             f"사후재현 {int(cnt.get('사후재현', 0))}) | 채점 완료 {n_scored}건 | 이번 실행 '{label}' 기록 · 신규 채점 {n_new}건"
             + (f" | {' / '.join(notes)}" if notes else ''))
    _d_s = '구간 내 플립 없음' if _b(rec.get('D선없음')) else f"{_f(rec.get('D선')):.2f}달러"
    _a_s = ('없음(대체점 ' + f"{_f(rec.get('A선')):.2f})") if _b(rec.get('A선없음')) else f"{_f(rec.get('A선')):.2f}달러"
    _pos = '-' if _b(rec.get('D선없음')) else _side(_f(rec.get('EWY종가')), _f(rec.get('D선')))
    L.append(f" - 오늘 기록: 원인① {'ON' if _b(rec.get('원인1')) else 'OFF'} · 원인② {'ON' if _b(rec.get('원인2')) else 'OFF'} · 국면 {rec.get('국면1순위', '-')} 1순위 · "
             f"D선 {_d_s} (V4.3.5 방식 A선 {_a_s})" + ('' if _pos == '-' else f" · EWY 종가는 D선 {_pos}")
             + (f" | 병행(검증 중) 원인① {'ON' if _b(rec.get('원인1_병행')) else 'OFF'} · 원인② {'ON' if _b(rec.get('원인2_병행')) else 'OFF'}"
                if str(rec.get('원인2_병행', '')) != '' else ''))
    L.append(" - [판정 규칙(사전 고정)] 주 지표 = 다음 한국 정규장 KOSPI 시가→종가 하락 여부. 신호일 20건 이상 · 기저 대비 +10%p 이상 · 우연 확률 p<0.05(피셔 단측)를 모두 넘을 때만 '유효 후보'. "
             "D선 위치는 EWY 24시간 가격의 한국장 시가 기준(없으면 미국 종가 기준). "
             "'병행(검증 중)' 행은 V4.3.7부터 쌓이는 비교용 기록으로, 같은 규칙을 통과해도 판정 기준을 바꾸기 전까지는 판단에 쓰지 않습니다.")
    L.append("구분|n|KOSPI 시가→종가↓|기저 대비|p|KOSPI 시가갭↓|KOSPI 전일대비↓|삼성 전일대비↓|EWY 미국마감→한국종가↓|KOSPI 장중-1%↓|판정")
    L.append("-" * 40)
    L.extend(_sig_stats_lines(live, '실시간'))
    L.extend(_sig_stats_lines(late, '사후·재현'))
    for blk, gg in (('실시간', live), ('사후·재현', late)):
        rd, nd, bd, na = _sig_line_metrics(gg, 'D선', 'D선없음')
        ra, nra, ba, naa = _sig_line_metrics(gg, 'A선', 'A선없음')
        if nd + na + nra + naa > 0:
            L.append(f" - [{blk} · 선의 미국 종가 교차] 한국 종가가 D선 아래 -> 다음 미국 종가 회복 {rd}/{nd} · 위 -> 이탈 {bd}/{na} "
                     f"(V4.3.5 방식 A선: 회복 {ra}/{nra} · 이탈 {ba}/{naa})")
        posg = np.where(gg['D선위치_한국시가'].astype(str) != '', gg['D선위치_한국시가'].astype(str), gg['D선위치_미국종가'].astype(str))
        rg = _num(gg['KOSPI_고저폭%']).values
        mb, ma = np.isfinite(rg) & (posg == '아래'), np.isfinite(rg) & (posg == '위')
        if mb.sum() >= 3 and ma.sum() >= 3:
            L.append(f" - [{blk} · D선 변동 폭] KOSPI 장중 고저폭 평균: D선 아래 시작 {rg[mb].mean():.2f}%(n={int(mb.sum())}) vs 위 시작 {rg[ma].mean():.2f}%(n={int(ma.sum())})"
                     f" -> {rg[mb].mean() / max(rg[ma].mean(), 1e-9):.2f}배")
    L.append(" - [해석 주의] '실시간'만 진짜 사후 검증입니다(다음 한국 정규장 09:00 전에 만든 최신 기준일 보고서). '사후·재현'은 지난 날짜를 다시 돌린 결과라 "
             "국면 모델 등이 같은 기간을 학습한 영향이 섞여 실제보다 좋게 나올 수 있습니다. KOSPI 시가 갭은 대부분 보고서가 나오기 전에 끝난 미국장 움직임으로 정해지므로 "
             "주 지표는 시가→종가입니다. 감마 플립선은 방향 신호가 아니라 변동 폭 구간의 경계로 읽으십시오.")
    return L


# ==============================================================================


# ==============================================================================
# ★ [V4.3.7 신설] 배당 반영 IV 보정 · 데이터 품질 점검 · 병행(검증 중) 원인 ①·② · 신호 기록 폴더 지정
# ==============================================================================
DLINE_DEF = "V4.3.7"                 # 신호 기록의 D선 정의 (이 값과 다른 기록은 한 번만 새 정의로 다시 계산하고 이전 값은 'D선_이전'에 보관)
COLLECTOR_DIV_YIELD = 0.02           # 수집기 IV·델타 계산의 가정: 블랙-숄즈 · 영업일/252 · SOFR · 연 2% 연속 배당
# EWY는 1년에 한 번 12월에 분배금을 지급합니다. (배당락일, 1주당 달러)
# 2026-12-15는 예상치(2.67~2.95달러의 중간값) — 확정 공시가 나오면 금액을 고치십시오.
DIVIDEND_EVENTS = [('2023-12-20', 0.921734), ('2024-12-17', 1.298136), ('2025-12-16', 2.037071), ('2026-12-15', 2.80)]
DIV_PROJ_YIELD = 0.022               # 표에 없는 해의 12월 분배금 추정 = 기준일 주가 x 2.2% (배당락일 = 12월 셋째 금요일 주의 화요일)
_DIV_FIX_INFO = {}


def _proj_exdate(year):
    d0 = pd.Timestamp(year=int(year), month=12, day=1)
    fri1 = d0 + pd.Timedelta(days=(4 - d0.dayofweek) % 7)
    return (fri1 + pd.Timedelta(days=14) - pd.Timedelta(days=3)).strftime('%Y-%m-%d')


def _div_schedule(quote_date, spot, until_date):
    """quote_date 다음 날 ~ until_date 사이 배당락 목록 [(배당락일, 금액, 추정여부)]"""
    q, u = str(quote_date)[:10], str(until_date)[:10]
    out = [(d, float(a), False) for d, a in DIVIDEND_EVENTS if q < d <= u]
    y = max(int(d[:4]) for d, _ in DIVIDEND_EVENTS) + 1
    while True:
        ex = _proj_exdate(y)
        if ex > u:
            break
        if ex > q:
            out.append((ex, DIV_PROJ_YIELD * float(spot), True))
        y += 1
    return out


def _pv_divs(quote_date, expiry, spot, r):
    s = 0.0
    for ex, amt, _est in _div_schedule(quote_date, spot, expiry):
        t_ex = max(float(np.busday_count(str(quote_date)[:10], ex)), 0.0) / 252.0
        s += amt * np.exp(-r * t_ex)
    return s


def _bs_px(S, K, T, r, q, sig, is_call):
    from scipy.special import ndtr
    sq = sig * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sig * sig) * T) / sq
    d2 = d1 - sq
    eq, er = np.exp(-q * T), np.exp(-r * T)
    return np.where(is_call, S * eq * ndtr(d1) - K * er * ndtr(d2), K * er * ndtr(-d2) - S * eq * ndtr(-d1))


def apply_dividend_iv_fix_v437(df):
    """[V4.3.7] 수집기 IV(연 2% 연속 배당 가정)를 EWY 실제 배당 일정(12월 1회)에 맞춰 다시 풂.
    같은 옵션 가격을 두고 선도가만 실제 배당 기준으로 바꿔 IV·델타를 다시 계산합니다. 원래 값은 'IV_수집기'·'Delta_수집기'에 보관하고,
    만기별 실제 배당을 연속 배당률로 바꾼 값은 'Q_eff'(감마 플립·바나·참 계산용)에 둡니다."""
    global _DIV_FIX_INFO
    if df is None or len(df) == 0:
        return df
    d = df
    S = pd.to_numeric(d['EWY Price'], errors='coerce').fillna(0.0).values.astype(float)
    K = pd.to_numeric(d['Strike'], errors='coerce').fillna(0.0).values.astype(float)
    iv = pd.to_numeric(d['Implied Volatility'], errors='coerce').fillna(0.0).values.astype(float)
    dl = pd.to_numeric(d['Delta'], errors='coerce').fillna(0.0).values.astype(float) if 'Delta' in d.columns else np.zeros(len(d))
    r = pd.to_numeric(d['Secured Overnight Financing Rate'], errors='coerce').fillna(0.0).values.astype(float) / 100.0 \
        if 'Secured Overnight Financing Rate' in d.columns else np.zeros(len(d))
    r = np.where(r > 0, r, GAMMA_RF_FALLBACK)
    qd_s = np.array(d['Quote Date'].astype(str).str[:10].tolist(), dtype=object)
    ed_s = np.array(d['Expiration Date'].astype(str).str[:10].tolist(), dtype=object)
    T = np.maximum(np.busday_count(np.array(qd_s.tolist(), dtype='datetime64[D]'), np.array(ed_s.tolist(), dtype='datetime64[D]')).astype(float), 0.5) / 252.0
    key = pd.DataFrame({'q': qd_s, 'e': ed_s, 'S': S, 'r': r})
    first = key.groupby(['q', 'e'], sort=False).first()
    pv_map = {k_: _pv_divs(k_[0], k_[1], row['S'], row['r']) for k_, row in first.iterrows()}
    pv = np.array([pv_map[(a, b)] for a, b in zip(qd_s, ed_s)], dtype=float)
    ratio = np.clip(1.0 - pv / np.maximum(S, 1e-6), 0.5, 1.0)
    q_t = -np.log(ratio) / T
    d['Q_eff'] = q_t
    d['IV_수집기'] = iv
    d['Delta_수집기'] = dl
    is_call = (d['Option Type'].astype(str).values == 'Call')
    cand = (iv > IV_MARK_LO) & (iv < IV_MARK_HI) & (S > 0) & (K > 0) & (np.abs(q_t - COLLECTOR_DIV_YIELD) * T > 1e-7)
    idx = np.where(cand)[0]
    new_iv, new_dl = iv.copy(), dl.copy()
    n_fix = n_keep = 0
    if len(idx) > 0:
        from scipy.special import ndtr
        Sx, Kx, Tx, rx, sx, cx, qt = S[idx], K[idx], T[idx], r[idx], iv[idx], is_call[idx], q_t[idx]
        qc = np.full(len(idx), COLLECTOR_DIV_YIELD)
        px = _bs_px(Sx, Kx, Tx, rx, qc, sx, cx)
        d1c = (np.log(Sx / Kx) + (rx - qc + 0.5 * sx * sx) * Tx) / (sx * np.sqrt(Tx))
        vega_c = Sx * np.exp(-qc * Tx) * np.exp(-0.5 * d1c * d1c) / np.sqrt(2.0 * np.pi) * np.sqrt(Tx)
        lo, hi = np.full(len(idx), 1e-4), np.full(len(idx), 5.0)
        plo, phi = _bs_px(Sx, Kx, Tx, rx, qt, lo, cx), _bs_px(Sx, Kx, Tx, rx, qt, hi, cx)
        tol = 1e-6 * np.maximum(px, 1e-3)
        solv = (px > plo + tol) & (px < phi - tol) & (vega_c > 1e-3)
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            up = _bs_px(Sx, Kx, Tx, rx, qt, mid, cx) > px
            hi = np.where(up, mid, hi)
            lo = np.where(up, lo, mid)
        sol = np.where(solv, 0.5 * (lo + hi), sx)
        d1n = (np.log(Sx / Kx) + (rx - qt + 0.5 * sol * sol) * Tx) / (sol * np.sqrt(Tx))
        dn = np.where(cx, np.exp(-qt * Tx) * ndtr(d1n), -np.exp(-qt * Tx) * ndtr(-d1n))
        new_iv[idx] = sol
        new_dl[idx] = np.where(solv, dn, dl[idx])
        n_fix, n_keep = int(solv.sum()), int((~solv).sum())
    d['Implied Volatility'] = new_iv
    if 'Delta' in d.columns:
        d['Delta'] = new_dl
    big = np.abs(new_iv - iv) >= 0.02
    _DIV_FIX_INFO = {'rows': int(len(d)), 'fixed': n_fix, 'kept': n_keep, 'big': int(big.sum()),
                     'div_rows': int((pv > 0).sum())}
    print(f"[V4.3.7 배당 반영 IV 보정] {len(d):,}행 중 {n_fix:,}행 재계산 (2%p 이상 바뀐 행 {int(big.sum()):,} · 배당락을 넘는 만기 행 {int((pv > 0).sum()):,} · 해 없음 {n_keep:,}행은 원래 값 유지)")
    return d


def _mark_price_v437(bid, ask, last, intrinsic):
    """현재가: 매수·매도 호가가 모두 있으면 중간호가, 없으면 마지막 체결가 (둘 다 내재가치 아래로는 내리지 않음). (가격, 체결가사용여부)"""
    bid, ask, last, intrinsic = (np.asarray(x, dtype=float) for x in (bid, ask, last, intrinsic))
    okq = (bid > 0) & (ask > 0) & (ask >= bid)
    px = np.where(okq, 0.5 * (bid + ask), last)
    return np.maximum(px, intrinsic), ~okq


def _sig_dir_v437():
    """신호 기록 폴더: 환경변수 EWY_SIGNAL_LOG_DIR(PC 프로그램이 넘김) > SIGNAL_LOG_DIR 설정 > OUTPUT_DIR (기준일 폴더면 그 위 폴더)"""
    env = str(os.environ.get('EWY_SIGNAL_LOG_DIR', '') or '').strip().strip('"')
    if env:
        return env, 'PC 프로그램에서 고른 폴더'
    cfg = str(globals().get('SIGNAL_LOG_DIR', '') or '').strip().strip('"')
    if cfg:
        return cfg, '엔진 설정 SIGNAL_LOG_DIR'
    base = str(OUTPUT_DIR)
    if re.fullmatch(r'\d{8}', os.path.basename(os.path.normpath(base)) or ''):
        return os.path.dirname(os.path.normpath(base)), '엔진 출력 폴더(기준일 폴더의 위)'
    return base, '엔진 출력 폴더'


def _stray_log_paths_v437(main_path):
    """다른 폴더에 흩어진 기록 파일 후보: 엔진 출력 폴더와 그 아래 기준일 폴더(예: 20261123)"""
    roots = []
    base = os.path.normpath(str(OUTPUT_DIR))
    roots.append(base)
    if re.fullmatch(r'\d{8}', os.path.basename(base) or ''):
        roots.append(os.path.dirname(base))
    found = []
    for rt in roots:
        cands = [os.path.join(rt, SIGNAL_LOG_FILENAME)]
        try:
            for nm in os.listdir(rt):
                if re.fullmatch(r'\d{8}', nm):
                    cands.append(os.path.join(rt, nm, SIGNAL_LOG_FILENAME))
        except OSError:
            pass
        for c in cands:
            try:
                if os.path.isfile(c) and os.path.normcase(os.path.abspath(c)) != os.path.normcase(os.path.abspath(main_path)) and c not in found:
                    found.append(c)
            except OSError:
                continue
    return found


def _merge_stray_logs_v437(log, main_path):
    """흩어진 기록 파일을 본 기록에 합침: 없는 기준일·Tier는 추가, 같은 키는 '실시간' 기록과 빈 채점 칸만 보충"""
    notes, merged_files, n_add, n_fill = [], [], 0, 0
    for sp in _stray_log_paths_v437(main_path):
        sl, ok = _load_sig_log(sp)
        if not ok or len(sl) == 0:
            continue
        for _, row in sl.iterrows():
            k = (str(row['기준일']), str(row['Tier']))
            if not k[0] or not k[1]:
                continue
            m = (log['기준일'].astype(str) == k[0]) & (log['Tier'].astype(str) == k[1])
            if not m.any():
                log = pd.concat([log, pd.DataFrame([{c: row.get(c, '') for c in SIG_LOG_COLS}], dtype=object)], ignore_index=True)
                n_add += 1
                continue
            i = log.index[m][0]
            if str(row['기록구분']) == '실시간' and str(log.at[i, '기록구분']) != '실시간':
                for c in SIG_SIGNAL_COLS:
                    log.at[i, c] = row.get(c, '')
                n_fill += 1
            for c in SIG_RESULT_COLS:
                if str(log.at[i, c]) == '' and str(row.get(c, '')) != '':
                    log.at[i, c] = row.get(c, '')
        merged_files.append(sp)
    if n_add + n_fill > 0:
        notes.append(f"다른 폴더의 기록 파일 {len(merged_files)}개를 합침(추가 {n_add}건 · 실시간 보충 {n_fill}건)")
    return log.fillna(''), notes, merged_files


def _migrate_dline_v437(log, df_pit):
    """D선 정의가 바뀐 기록(V4.3.6 이전 · 사후재현 시드)은 같은 기준일 옵션 자료로 D선을 한 번만 다시 계산.
    df_pit는 보고서 본문과 같은 OI 결측 복원을 마친 자료이고, 기준일 당일 자료만 쓰므로 미래참조가 없습니다."""
    n = 0
    if len(log) == 0:
        return log, 0
    need = [i for i in log.index if str(log.at[i, 'D선정의']) != DLINE_DEF]
    if not need:
        return log, 0
    want = {str(log.at[i, '기준일']) for i in need}
    sub = df_pit[df_pit['Quote Date'].isin(want)]
    days = {k_: g_ for k_, g_ in sub.groupby('Quote Date')}
    for i in need:
        d = str(log.at[i, '기준일'])
        day = days.get(d)
        if day is None or len(day) == 0:
            continue
        spot = float(pd.to_numeric(day['EWY Price'], errors='coerce').dropna().iloc[0])
        gf = calc_gamma_flip_v436(day, spot)
        if str(log.at[i, 'D선_이전']) == '':
            log.at[i, 'D선_이전'] = '없음' if _b(log.at[i, 'D선없음']) else str(log.at[i, 'D선'])
        log.at[i, 'D선'] = '' if gf['gflip_none'] else f"{float(gf['gflip']):.2f}"
        log.at[i, 'D선없음'] = str(bool(gf['gflip_none']))
        log.at[i, 'D선부호'] = str(gf.get('gflip_sign', ''))
        log.at[i, 'D선정의'] = DLINE_DEF
        n += 1
    return log, n


def _parity_div_check_v437(day_df, spot, latest_date):
    """패리티로 역산한 배당(달러): 배당락을 넘는 만기의 (현가 - K·e^-rT - (C-P)) 중앙값 - 넘지 않는 만기의 같은 값(자금조달·조기행사 잡음 상쇄)"""
    try:
        d = day_df[(day_df['DTE'] >= 1) & (day_df['Bid'] > 0) & (day_df['Ask'] > 0)].copy()
        if len(d) == 0:
            return None
        d['Mid'] = 0.5 * (d['Bid'] + d['Ask'])
        r = GAMMA_RF_FALLBACK
        _sf = pd.to_numeric(d.get('Secured Overnight Financing Rate', pd.Series(dtype=float)), errors='coerce')
        _sf = _sf[_sf > 0]
        if len(_sf) > 0:
            r = float(_sf.iloc[0]) / 100.0
        sch = _div_schedule(latest_date, spot, (pd.Timestamp(latest_date) + pd.Timedelta(days=400)).strftime('%Y-%m-%d'))
        if not sch:
            return None
        ex1 = sch[0][0]
        pre, post = [], []
        for e, g in d.groupby('Expiration Date'):
            if str(e) > (pd.Timestamp(ex1) + pd.Timedelta(days=45)).strftime('%Y-%m-%d'):
                continue                       # 배당락 직후 45일 안 만기만 (먼 만기는 조기행사 프리미엄·자금조달 잡음이 커짐)
            pv_ = g.pivot_table(index='Strike', columns='Option Type', values='Mid', aggfunc='first').dropna()
            if 'Call' not in pv_.columns or 'Put' not in pv_.columns:
                continue
            k = pv_.index.values.astype(float)
            mm = np.abs(k - spot) / spot <= 0.03
            if mm.sum() < 2:
                continue
            T = max(float(np.busday_count(str(latest_date)[:10], str(e)[:10])), 0.5) / 252.0
            val = float(np.median(spot - k[mm] * np.exp(-r * T) - (pv_['Call'].values[mm] - pv_['Put'].values[mm])))
            (post if str(e) >= ex1 else pre).append(val)
        if not post:
            return None
        est = float(np.median(post) - (np.median(pre) if pre else 0.0))
        return {'ex': ex1, 'amt': float(sch[0][1]), 'est_flag': bool(sch[0][2]), 'implied': est, 'n_post': len(post), 'n_pre': len(pre)}
    except Exception:
        return None


def shadow_ambush_v437(amb_df, p_tbl, ts_metrics, d_curr, d_prev, latest_spot, daily_chg_pct, s_vol, s_oi, is_reg_b_top,
                       latest_date, put_bunker_1st, near_ng_chg, mode='shadow'):
    """[V4.3.7] 병행(검증 중) 원인 ①·②. mode='orig'는 본 판정과 같은 계산(일치 점검용), mode='shadow'는
    ① 레이더 IV 변화를 [섹션 2] 분면 표와 같은 '같은 만기대 ATM IV 변화를 뺀 잔차'로 통일하고 ② 같은 수량의 스프레드 다리(캘린더·수직)와
    ③ 심층 내가격(|델타| 0.85 이상) 계약을 뺀 결과. 판정에는 쓰지 않고 신호 기록에만 남깁니다."""
    a = amb_df.copy()
    n_spread = n_deep = 0
    if mode == 'shadow':
        dte = pd.to_numeric(a['DTE_Latest'], errors='coerce').fillna(0.0).values.astype(float)
        atm = np.zeros(len(a))
        for col, lo_, hi_ in (('Near_ATM_IV', -1.0, 45.0), ('Mid_ATM_IV', 45.0, 120.0), ('Back_ATM_IV', 120.0, 1e9)):
            try:
                va = float(ts_metrics.loc[d_curr, col]) - float(ts_metrics.loc[d_prev, col])
            except Exception:
                va = np.nan
            atm = np.where((dte > lo_) & (dte <= hi_), va if np.isfinite(va) else 0.0, atm)
        raw = a['Raw_IV_Chg_1D'].values.astype(float)
        ivl, ivp = a['IV_Latest'].values.astype(float), a['IV_Prev1'].values.astype(float)
        has_iv = (ivl > 0.01) & (ivp > 0.01)
        isput = (a['Option Type'].values == 'Put')
        if 'IV_Roll_Prev1' in a.columns:
            rp = a['IV_Roll_Prev1'].values.astype(float)
            roll = np.where((rp > 0.01) & (ivl > 0.01), ivl - rp, raw)
        else:
            roll = raw
        base_p = np.where((daily_chg_pct > 0) & (a['Strike'].values.astype(float) < latest_spot), np.minimum(raw, roll), raw)
        ivs = np.where(isput, base_p - 0.85 * atm, raw - 0.80 * atm)
        ivs = np.where(has_iv, ivs, 0.0)
        ivs = np.where(~a['Is_Valid_Quote'].values & (ivs > 0), 0.0, ivs)
        a['IV_S'] = ivs
        # 같은 수량 스프레드 다리: 같은 종류에서 (같은 행사가·다른 만기) 또는 (같은 만기·다른 행사가) 짝의 당일 거래량이 2% 이내
        vol = a['Vol_Latest'].values.astype(float)
        vmin = max(10, int(round(150 * s_vol)))
        leg = np.zeros(len(a), dtype=bool)
        big = np.where(vol >= vmin)[0]
        typ, ks, ex_ = a['Option Type'].values, a['Strike'].values.astype(float), a['Expiration Date'].astype(str).values
        for ii in range(len(big)):
            for jj in range(ii + 1, len(big)):
                p_, q_ = big[ii], big[jj]
                if typ[p_] != typ[q_]:
                    continue
                if not ((ks[p_] == ks[q_] and ex_[p_] != ex_[q_]) or (ex_[p_] == ex_[q_] and ks[p_] != ks[q_])):
                    continue
                if abs(vol[p_] - vol[q_]) <= max(2.0, 0.02 * max(vol[p_], vol[q_])):
                    leg[p_] = leg[q_] = True
        deep = np.abs(a['BS_Delta'].values.astype(float)) >= 0.85
        excl = leg | deep
        n_spread, n_deep = int(leg.sum()), int((deep & ~leg & (vol >= vmin)).sum())
    else:
        a['IV_S'] = a['IV_Chg_1D'].values.astype(float)
        excl = np.zeros(len(a), dtype=bool)
    a['Excl_S'] = excl
    ivs = a['IV_S'].values
    vq = a['Is_Valid_Quote'].values.astype(bool)
    isput = (a['Option Type'].values == 'Put')
    bear_put = isput & (ivs >= 0.005) & vq
    cap_call = (~isput) & (ivs <= -0.005)
    _amb_min_vol = max(10, int(round(150 * s_vol)))
    _amb_high_vol = max(30, int(round(500 * s_vol)))
    sel = vq & (a['Vol_Latest'].values >= _amb_min_vol) & ((a['Vol_OI_Ratio'].values >= 0.25) | (a['Vol_Latest'].values >= _amb_high_vol)) & ~excl
    top_idx = a[sel].sort_values(by='Vol_Latest', ascending=False).head(12).index
    tpos = a.index.get_indexer(top_idx)
    ratio = (int(bear_put[tpos].sum()) + int(cap_call[tpos].sum())) / max(len(tpos), 1) * 100.0
    near = a[vq & isput & (a['DTE_Latest'].values >= 1) & (a['DTE_Latest'].values <= 90) &
             (a['Strike'].values >= latest_spot * 0.85) & (a['Strike'].values <= latest_spot * 1.03) &
             (a['Vol_Latest'].values >= max(15, int(round(300 * s_vol)))) & ~excl].copy()
    c2, ap_strike, ap_sh, ap_desc = False, float('nan'), 0, '-'
    if len(near) > 0:
        near['Score_S'] = near['Hedge_Shares_Abs'] * (1.0 + np.maximum(0.0, near['IV_S'] * 12.0)) * np.where(near['IV_S'] > 0, 1.5, 0.5)
        tp = near.sort_values(by='Score_S', ascending=False).iloc[0]
        ap_strike, ap_sh = float(tp['Strike']), int(round(tp['Hedge_Shares_Abs']))
        ap_div, ap_vol = float(tp['IV_S']) * 100.0, int(tp['Vol_Latest'])
        c2 = (ap_div >= 0.5) and (ap_vol >= max(25, int(round(500 * s_vol))))
        ap_desc = f"{tp['Expiration Date']} {ap_strike:.1f}P(IV {ap_div:+.2f}%p · {ap_vol:,}계약)"
    upper = min(ap_strike - 0.5, latest_spot * 0.99) if c2 else latest_spot * 0.99
    sub = p_tbl[p_tbl['Quadrant'].str.startswith('Q1') & (p_tbl.index.get_level_values('Strike') <= upper) &
                (p_tbl.index.get_level_values('Strike') >= latest_spot * 0.90)].sort_values(by='OI_Chg_Short', ascending=False)
    if len(sub) > 0:
        cas_chg = int(sub['OI_Chg_Short'].iloc[0])
    else:
        cc = p_tbl[(p_tbl.index.get_level_values('Strike') == float(put_bunker_1st)) & (p_tbl.index.get_level_values('Expiration Date') > latest_date)]
        if len(cc) > 0:
            ck = cc['OI_Latest'].idxmax()
            cas_chg = int(cc.loc[ck, 'OI_Chg_Short']) if str(cc.loc[ck, 'Quadrant']).startswith('Q1') else 0
        else:
            cas_chg = int(near_ng_chg)
    army = int(round(max(cas_chg, 0) * 100.0 * 0.35))
    army_ok = bool(c2 and (army >= max(ap_sh, 1)))
    c1 = bool(c2 and army_ok and ((ratio >= 70.0) or is_reg_b_top))
    return {'c1': c1, 'c2': bool(c2), 'ratio': float(ratio), 'ap': ap_desc, 'n_spread': n_spread, 'n_deep': n_deep}


def build_dq_block_v437(dq):
    """[데이터 품질 점검] 블록: 엔진이 이미 아는 데이터 한계를 한곳에 모아 AI가 같은 내용을 '오류'로 다시 지적하지 않게 함"""
    L = ["### [데이터 품질 점검 — 엔진 자동 점검 (V4.3.7)]",
         " 📌 아래 항목은 엔진이 이미 알고 처리한 데이터 한계입니다. 보고서 작성 시 이 항목을 다시 '오류'로 지적하지 말고, 여기에 없는 새 이상만 해당 위치에 '[데이터 이상 의심]' 한 줄로 적으십시오."]
    dv = dq.get('div') or {}
    if dv:
        L.append(f" - 배당(EWY 연 1회 12월 분배): 다음 배당락 {dv.get('ex', '-')} · 1주당 {dv.get('amt', float('nan')):.2f}달러({'추정' if dv.get('est') else '설정값'}, 현가의 {dv.get('amt_pct', float('nan')):.2f}%)"
                 f" · 이 배당락을 넘는 만기 {dv.get('n_exp', 0)}개(첫 만기 {dv.get('first_exp', '-')})"
                 + (f" · 패리티 역산 약 {dv['implied']:.2f}달러(만기 {dv.get('n_post', 0)}개)" if np.isfinite(dv.get('implied', np.nan)) else '')
                 + ". 수집기 IV는 '연 2% 연속 배당'으로 계산돼 이 만기들의 풋 IV가 부풀고 콜 IV가 눌리므로, 엔진이 실제 배당 일정으로 IV·델타·선도가를 다시 계산해 모든 표에 썼습니다"
                 + (f"(전체 {dq.get('fix', {}).get('fixed', 0):,}행 재계산)." if dq.get('fix') else "."))
        if dv.get('warn'):
            L.append(f"   · 설정 배당과 패리티 역산값 차이가 큽니다({dv['warn']}). 배당 공시를 확인해 DIVIDEND_EVENTS를 고치십시오.")
    if dq.get('exday'):
        L.append(f" - 오늘은 배당락일: EWY 등락률 {dq['exday']['chg']:+.2f}% 중 {-dq['exday']['div_pct']:+.2f}%p는 배당락분 -> 배당 제외 등락률 {dq['exday']['chg'] + dq['exday']['div_pct']:+.2f}%(계산).")
    if dq.get('stale'):
        st = dq['stale']
        L.append(f" - 체결가 지연: [섹션 2-②] (2-3)·(2-4)의 현재가는 중간호가 기준입니다. 마지막 체결가가 중간호가와 15% 넘게 다른 계약 {st['n']}개"
                 + (f"(예: {st['ex']})" if st.get('ex') else '') + " — 체결이 없던 날 예전 체결가가 남은 것이므로 체결가로 손익을 읽지 마십시오.")
    rd = dq.get('radar') or {}
    if rd and abs(rd.get('atm', 0.0)) >= 5.0 and not rd.get('adj'):
        L.append(f" - 레이더 ④ IV 기준: 근월 ATM IV가 하루 {rd['atm']:+.1f}%p 움직였는데 레이더 ④는 명목 IV 변화로 분류합니다(보정 조건 '주가 상승 & 콜 점유율 53% 이상' 미충족, 콜 점유율 {rd.get('cshare', 0):.1f}%). "
                 f"{'콜의 커버드콜·풋의 매도 분류' if rd['atm'] < 0 else '콜의 매집·풋의 기습 매수 분류'}가 실제보다 많을 수 있습니다. [섹션 2] 분면 표는 ATM 변화를 뺀 잔차 기준입니다.")
    if dq.get('fx_r2') is not None and dq['fx_r2'] < 0.5:
        L.append(f" - 환율 회귀 설명력 R² {dq['fx_r2'] * 100:.0f}%(50% 미만): 내재 환율은 표시하지 않고 15:30 환율을 그대로 둡니다.")
    sh = dq.get('shadow') or {}
    if sh:
        L.append(f" - 병행 기록(검증 중, 판정에 쓰지 않음): 레이더 IV 기준을 분면 표와 같게 통일하고 같은 수량 스프레드 다리 {sh.get('n_spread', 0)}개 · 심층 내가격 {sh.get('n_deep', 0)}개를 뺀 계산 -> "
                 f"원인① {'ON' if sh.get('c1') else 'OFF'} · 원인② {'ON' if sh.get('c2') else 'OFF'} (하방·상단캡 지배력 {sh.get('ratio', 0):.0f}%, 근접 풋 {sh.get('ap', '-')})"
                 + ("" if sh.get('orig_ok', True) else " · [점검] 본 판정 재현 불일치 — 병행 값은 참고만"))
    L.append("")
    return L


# ★ [이력 블록 신설] [섹션 6] 이력 요약 블록: 일별 지표 21거래일 · 계약/행사가 OI 패널 · 채점 요약
#  - 근거: 마스터 CSV 워크포워드 시뮬레이션(7·15·21일 창 비교, 2026-04-15~2026-11-09 144거래일)
#    · 근월·등가 근처 OI 중 창 안에서 새로 쌓인 비중: 7일 35% / 15일 58% / 21일 69%
#    · 현재 추세 구간 시작점(8% 전환점)이 창 안: 24% / 54% / 68% · 이상치 경보 정밀도: 28% / 47% / 56%
#  - 구성: (6-1) 일별 지표 HIST_DAYS행  (6-2)·(6-3) OI 패널은 같은 범위를 '이전 주말 3회 + 최근 5일' 열로 압축
#          (6-4) 60일 채점 · 30일 고점/저점 · 21일 전 대비 변화는 한 줄 값
#  - 아래 상수만 바꾸면 길이를 조절할 수 있습니다.
# ==============================================================================
HIST_DAYS          = 21   # (6-1) 일별 지표 행 수(거래일)
HIST_PANEL_RECENT  = 5    # (6-2)(6-3) 패널에서 매일 보여 줄 최근 거래일 수
HIST_PANEL_WEEKS   = 3    # 그 이전 구간에서 보여 줄 주말(그 주의 마지막 거래일) 스냅샷 수
HIST_TOP_CONTRACTS = 30   # (6-2) 계약 수
HIST_TOP_STRIKES   = 24   # (6-3) 행사가 수
HIST_SCORE_DAYS    = 60   # (6-4) 예측 채점 합계 기간


def build_history_block(df_pit, all_dates, latest_date, ts_metrics, hist_traj_df, ph_tbl, w_short, snap_fn=None, extra_lines=None):
    L = []
    n_all = len(all_dates)
    hist_dates = list(all_dates[-HIST_DAYS:])
    base_dates = list(all_dates[-(HIST_DAYS + 1):])            # 1일 증감 계산용으로 하루 더
    px = df_pit.groupby('Quote Date')['EWY Price'].first()
    spot = float(px.loc[latest_date])

    sub = df_pit[df_pit['Quote Date'].isin(base_dates)]
    oi = sub.pivot_table(index='Contract Name', columns='Quote Date', values='Open Interest', aggfunc='last').reindex(columns=base_dates)
    oi = oi.ffill(axis=1, limit=3)                             # 수집 누락일(행 수 급감)은 직전값 유지
    meta = sub.groupby('Contract Name').agg(exp=('Expiration Date', 'first'), typ=('Option Type', 'first'), k=('Strike', 'first')).reindex(oi.index)
    exp_a = meta['exp'].values.astype(str)
    put_a = (meta['typ'] == 'Put').values
    k_a = meta['k'].values.astype(float)
    vol_d = sub.groupby('Quote Date')['Volume'].sum()

    def _fmt_i(v, sign=False):
        if v is None or not np.isfinite(v):
            return '-'
        return f"{int(round(v)):+d}" if sign else f"{int(round(v)):d}"

    # ---------- (6-1) 일별 지표 ----------
    traj = hist_traj_df.set_index('Date') if (hist_traj_df is not None and len(hist_traj_df) > 0) else pd.DataFrame()
    day = {}
    for d in hist_dates:
        cur = oi[d].values.astype(float)
        alive = (exp_a > d) & np.isfinite(cur)                 # 당일 만기 계약 제외
        r = {'tot': float(cur[alive].sum()), 'coi': float(cur[alive & ~put_a].sum()), 'poi': float(cur[alive & put_a].sum()),
             'c1': np.nan, 'p1': np.nan, 'vol': float(vol_d.get(d, np.nan)), 'gflip': np.nan, 'gflip_none': False}
        i = base_dates.index(d)
        if i >= 1:
            prev = np.nan_to_num(oi[base_dates[i - 1]].values.astype(float))
            chg = cur - prev
            r['c1'] = float(chg[alive & ~put_a].sum())
            r['p1'] = float(chg[alive & put_a].sum())
        ts_ok = d in ts_metrics.index
        r['ivn'] = float(ts_metrics.loc[d, 'Near_ATM_IV']) * 100.0 if ts_ok else np.nan
        r['skm'] = float(ts_metrics.loc[d, 'Mid_Skew_25D']) * 100.0 if ts_ok else np.nan
        if snap_fn is not None and ts_ok:
            try:
                _dd = df_pit[(df_pit['Quote Date'] == d) & (df_pit['Expiration Date'] >= d)]
                _sn = snap_fn(_dd, float(px.loc[d]), ts_metrics.loc[d])
                r['gflip_none'] = bool(_sn.get('gflip_none', False))
                r['gflip'] = float('nan') if r['gflip_none'] else float(_sn['gflip'])
            except Exception:
                pass
        day[d] = r

    L.append(f"## [섹션 6] 이력 요약 블록 (일별 지표 {len(hist_dates)}거래일 · 계약/행사가 OI 패널 · 채점 요약)")
    L.append(" 📌 [사용 지침] 이 블록은 [섹션 1~5] 해석의 보조 자료입니다. ① 3D·7D·20D 합계에 숨은 이월 착시를 일별 값으로 확인, ② 현재 포지션이 언제 쌓였는지(형성 시점) 확인, "
             "③ 당일 값이 평소와 다른지는 아래 [당일 이상치 점검] 줄로 확인, ④ 예측치 신뢰도는 (6-4) 채점, ⑤ 신호별 실제 적중 기록은 (6-5) 신호 기록·채점으로 확인하는 용도입니다. 이 블록의 추세만으로 방향을 단정하지 마십시오.")
    L.append(f"### (6-1) 일별 지표 (최근 {len(hist_dates)}거래일, 4분면은 {w_short}D 합계 · OI 1일 증감은 만기 남은 계약 기준 순증감)")
    L.append(f"일자|EWY종가(등락%)|레짐A/B/C/D(%)|국면(1순위)|급락위험|Call_Q1({w_short}D)|Call_Q2({w_short}D)|Put_Q1({w_short}D)|Put_Q2({w_short}D)|Put청산|콜OI_1일|풋OI_1일|전체OI|거래량|근월IV(%)|중기스큐(%p)|감마플립|단기MP")
    L.append("-" * 40)
    for d in hist_dates:
        r = day[d]
        sp = float(px.loc[d])
        if d in traj.index:
            tr = traj.loc[d]
            sp_s = f"{sp:.2f}({float(tr['Chg']):+.2f})"
            reg_s = f"{tr['PA']:.1f}/{tr['PB']:.1f}/{tr['PC']:.1f}/{tr['PD']:.1f}"
            ph = [(n_, float(tr.get(k_, np.nan))) for n_, k_ in (('상승', 'PhU'), ('하락', 'PhD'), ('횡보', 'PhS'))]
            ph = [x for x in ph if np.isfinite(x[1])]
            ph_s = (max(ph, key=lambda x: x[1])[0] + f"{max(ph, key=lambda x: x[1])[1]:.0f}%") if ph else '-'
            q_s = f"{int(tr['CQ1']):+d}|{int(tr['CQ2']):+d}|{int(tr['PQ1']):+d}|{int(tr['PQ2']):+d}|{-int(tr['PQ34']):+d}"
            mp_s = f"{float(tr['NearMP']):.1f}"
        else:
            sp_s, reg_s, ph_s, q_s, mp_s = f"{sp:.2f}", '-', '-', '-|-|-|-|-', '-'
        rk = float(ph_tbl.loc[d, 'Risk']) if (ph_tbl is not None and d in ph_tbl.index) else np.nan
        rk_s = ('상' if rk >= 2.0 / 3.0 else ('하' if rk < 1.0 / 3.0 else '중')) if np.isfinite(rk) else '-'
        gf_s = '없음' if r.get('gflip_none') else (f"{r['gflip']:.2f}" if np.isfinite(r['gflip']) else '-')
        iv_s = f"{r['ivn']:.2f}" if np.isfinite(r['ivn']) else '-'
        sk_s = f"{r['skm']:+.2f}" if np.isfinite(r['skm']) else '-'
        L.append(f"{d}|{sp_s}|{reg_s}|{ph_s}|{rk_s}|{q_s}|{_fmt_i(r['c1'], True)}|{_fmt_i(r['p1'], True)}|{_fmt_i(r['tot'])}|{_fmt_i(r['vol'])}|{iv_s}|{sk_s}|{gf_s}|{mp_s}")

    # 당일 이상치 점검: 블록 안의 직전 거래일들 평균·표준편차 대비 당일 값
    def _z_line(name, key, unit=''):
        s = pd.Series([day[d][key] for d in hist_dates], index=hist_dates).dropna()
        if len(s) < 11 or s.index[-1] != latest_date:
            return None
        base = s.iloc[:-1]
        mu, sd = float(base.mean()), float(base.std(ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            return None
        z = (float(s.iloc[-1]) - mu) / sd
        tag = '이상(2시그마 밖)' if abs(z) >= 2.0 else '평소 범위'
        return f"{name} {s.iloc[-1]:+,.0f}{unit} (직전 {len(base)}일 평균 {mu:+,.0f} · 표준편차 {sd:,.0f} -> {z:+.1f}시그마 · {tag})"
    for d in hist_dates:
        day[d]['iv1'] = np.nan
    for a_, b_ in zip(hist_dates[:-1], hist_dates[1:]):
        day[b_]['iv1'] = (day[b_]['ivn'] - day[a_]['ivn']) * 100.0   # 근월IV 1일 변화(bp)
    zl = [x for x in (_z_line('콜OI_1일', 'c1', '계약'), _z_line('풋OI_1일', 'p1', '계약'), _z_line('거래량', 'vol', '계약'), _z_line('근월IV 1일변화', 'iv1', 'bp')) if x]
    if zl:
        L.append(" [당일 이상치 점검] " + " / ".join(zl))
    L.append("")

    # ---------- (6-2)(6-3) OI 패널: 이전 주말 스냅샷 + 최근 5거래일 ----------
    recent = hist_dates[-HIST_PANEL_RECENT:]
    older = hist_dates[:-HIST_PANEL_RECENT]
    pos = {d: i for i, d in enumerate(all_dates)}
    _wk = lambda s: tuple(pd.Timestamp(s).isocalendar())[:2]
    week_ends = [d for d in older if pos[d] + 1 < n_all and _wk(all_dates[pos[d] + 1]) != _wk(d)]
    cols = week_ends[-HIST_PANEL_WEEKS:] + recent
    col_hdr = "|".join(c[5:] for c in cols)

    cur = oi[latest_date].values.astype(float)
    alive_t = (exp_a > latest_date) & np.isfinite(cur)
    near = alive_t & (np.abs(k_a / spot - 1.0) <= 0.25)
    first = np.nan_to_num(oi[hist_dates[0]].values.astype(float))
    idx_near = np.where(near)[0]
    by_oi = idx_near[np.argsort(-cur[idx_near])][:HIST_TOP_CONTRACTS // 2]
    by_chg = [i for i in idx_near[np.argsort(-np.abs(cur[idx_near] - first[idx_near]))] if i not in set(by_oi)][:HIST_TOP_CONTRACTS - len(by_oi)]
    L.append(f"### (6-2) 계약 OI 패널 (현가 ±25% 이내 · 최신 OI 상위 {len(by_oi)}개 + {len(hist_dates)}일 증감 상위 {len(by_chg)}개 · 열 = 이전 주말 {len(cols) - len(recent)}회 + 최근 {len(recent)}거래일)")
    L.append(f"계약(만기YYMMDD·C/P·행사가)|{col_hdr}|{len(hist_dates)}일증감")
    L.append("-" * 40)
    for i in list(by_oi) + list(by_chg):
        lab = f"{exp_a[i][2:4]}{exp_a[i][5:7]}{exp_a[i][8:10]}{'P' if put_a[i] else 'C'}{k_a[i]:g}"
        vals = [oi[c].values[i] for c in cols]
        L.append(f"{lab}|" + "|".join('-' if not np.isfinite(v) else f"{int(v):d}" for v in vals) + f"|{int(cur[i] - first[i]):+d}")
    L.append("")

    ks_near = alive_t & (np.abs(k_a / spot - 1.0) <= 0.22)
    tot_by_k = pd.Series(cur[ks_near]).groupby(k_a[ks_near]).sum().sort_values(ascending=False)
    top_k = sorted(tot_by_k.index[:HIST_TOP_STRIKES], reverse=True)
    L.append(f"### (6-3) 행사가 OI 패널 (현가 ±22% 이내 OI 상위 {len(top_k)}개 행사가 · 각 일자에 만기 남은 계약 합계 · 열은 (6-2)와 동일)")
    L.append(f"행사가|구분|{col_hdr}")
    L.append("-" * 40)
    grid = {}
    for c in cols:
        v = oi[c].values.astype(float)
        ok = (exp_a > c) & np.isfinite(v)
        g = pd.DataFrame({'k': k_a[ok], 'p': put_a[ok], 'v': v[ok]}).groupby(['k', 'p'])['v'].sum()
        grid[c] = g
    for K in top_k:
        for is_p, nm in ((False, 'Call'), (True, 'Put')):
            L.append(f"{K:g}|{nm}|" + "|".join(f"{int(grid[c].get((K, is_p), 0.0)):d}" for c in cols))
    L.append("")

    # ---------- (6-4) 한 줄 요약값 ----------
    L.append("### (6-4) 한 줄 요약값 (채점 · 고점/저점 · 21일 전 대비)")
    sc_dates = list(all_dates[-(HIST_SCORE_DAYS + 1):])
    ret = px.reindex(sc_dates).astype(float).pct_change()
    iv_prev = ts_metrics['Near_ATM_IV'].reindex(sc_dates).astype(float).shift(1)
    z = (ret / (iv_prev / np.sqrt(252.0))).dropna()
    if len(z) >= 10:
        def _cnt(zz):
            return int((zz < -1.0).sum()), int((zz.abs() > 1.0).sum()), len(zz)
        d60, t60, n60 = _cnt(z)
        d21, t21, n21 = _cnt(z.iloc[-min(HIST_DAYS, len(z)):])
        L.append(f" - [예측 채점] 전일 근월IV 기준 1일 1시그마 범위 이탈: 최근 {n60}거래일 하단 {d60}회({d60 / n60 * 100:.1f}%) · 양방향 {t60}회({t60 / n60 * 100:.1f}%) | "
                 f"최근 {n21}거래일 하단 {d21}회 · 양방향 {t21}회 (정규분포 기대: 하단 15.9% · 양방향 31.7%)")
    w30 = px.reindex(list(all_dates[-30:])).astype(float)
    hi_d, lo_d = w30.idxmax(), w30.idxmin()
    L.append(f" - [30거래일 종가 고점/저점] 고점 {hi_d} {w30.max():.2f} (현재가 대비 {(spot / w30.max() - 1.0) * 100.0:+.2f}%, {n_all - 1 - pos[hi_d]}거래일 전) | "
             f"저점 {lo_d} {w30.min():.2f} (현재가 대비 {(spot / w30.min() - 1.0) * 100.0:+.2f}%, {n_all - 1 - pos[lo_d]}거래일 전)")
    d0 = hist_dates[0]
    a, b = day[d0], day[latest_date]
    parts = []
    if np.isfinite(a['ivn']) and np.isfinite(b['ivn']):
        parts.append(f"근월IV {a['ivn']:.2f}% -> {b['ivn']:.2f}% ({b['ivn'] - a['ivn']:+.2f}%p)")
    if np.isfinite(a['skm']) and np.isfinite(b['skm']):
        parts.append(f"중기 25D 스큐 {a['skm']:+.2f}%p -> {b['skm']:+.2f}%p ({b['skm'] - a['skm']:+.2f}%p)")
    if a['coi'] > 0 and b['coi'] > 0:
        parts.append(f"풋/콜 OI 비율 {a['poi'] / a['coi']:.2f} -> {b['poi'] / b['coi']:.2f}")
    parts.append(f"전체 OI {a['tot']:,.0f} -> {b['tot']:,.0f} ({b['tot'] - a['tot']:+,.0f})")
    L.append(f" - [{len(hist_dates)}거래일 전({d0}) 대비 변화] " + " | ".join(parts))
    L.append(" - [해석 주의] 시뮬레이션에서 급락 빈도와 약하게 연결된 것은 근월IV·스큐의 한 달 단위 변화뿐이었고(1주 단위 변화는 판별력 없음), 그 연결도 약합니다. 단독 근거로 쓰지 마십시오.")
    if extra_lines:
        L.append("")
        L.extend(extra_lines)
    L.append("=" * 124)
    return L


def generate_4regime_quant_report(df_pit, loaded_files, pit_meta, t_cfg, rel_info, derive_target_fn, view_version="PC"):
    _dq = {}   # ★ [V4.3.7] [데이터 품질 점검] 블록 재료
    all_dates = sorted(df_pit['Quote Date'].unique())
    total_days = len(all_dates)
    first_date = all_dates[0]
    latest_date = all_dates[-1]

    w_short = t_cfg['win_short']
    w_long  = t_cfg['win_long']
    traj_days = t_cfg['traj_days']
    vol_ts_days = t_cfg['vol_ts_days']
    cluster_dte = t_cfg['cluster_dte']

    prev1_date = get_base_date_for_window(all_dates, 1)
    short_date = get_base_date_for_window(all_dates, w_short)
    long_date  = get_base_date_for_window(all_dates, w_long)

    lookback_dates = all_dates[-15:] if total_days >= 15 else all_dates
    spot_series = df_pit[df_pit['Quote Date'].isin(lookback_dates)].groupby('Quote Date')['EWY Price'].first()
    peak_date = spot_series.idxmax()
    peak_spot = float(spot_series.max())
    latest_spot = float(spot_series.loc[latest_date])
    prev1_spot = float(df_pit[df_pit['Quote Date'] == prev1_date]['EWY Price'].iloc[0])
    drawdown_pct = (latest_spot / peak_spot - 1.0) * 100.0
    daily_chg_pct = (latest_spot / prev1_spot - 1.0) * 100.0

    CURRENT_KOSPI_PT    = rel_info['queried_kospi_pt']
    CURRENT_SAMSUNG_KRW = rel_info['queried_samsung_krw']
    CURRENT_USDKRW      = rel_info['queried_usdkrw']
    km = rel_info['KOSPI']
    sm = rel_info['SAMSUNG']
    fm = rel_info['USDKRW']

    # --------------------------------------------------------------------------
    # ★ [V4.2.5 핵심 업그레이드] 다년도(2024~2026) 스케일 불변(Auto-Scaling) 동적 계수(s_oi, s_vol) 산출
    #  - 2026년(Total OI >= 60만, 일거래량 >= 4만)에는 s_oi=1.0, s_vol=1.0으로 고정되어 기존 2026년 결과를 100% 보존하고,
    #    유동성이 작았던 2024~2025년에만 시장 규모에 비례해 수량 임계치를 자동 축소합니다.
    # --------------------------------------------------------------------------
    _lb20_dates = all_dates[-20:] if total_days >= 20 else all_dates
    _grp20_stat = df_pit[df_pit['Quote Date'].isin(_lb20_dates)].groupby('Quote Date')
    _med_oi_20d  = float(_grp20_stat['Open Interest'].sum().median()) if len(_lb20_dates) > 0 else 600000.0
    _med_vol_20d = float(_grp20_stat['Volume'].sum().median()) if len(_lb20_dates) > 0 else 40000.0

    s_oi  = float(np.clip(_med_oi_20d / 600000.0, 0.03, 1.00))
    s_vol = float(np.clip(_med_vol_20d / 40000.0, 0.015, 1.00))

    YF_MIN_VOLUME_CUTOFF = max(2, int(round(10 * (s_vol ** 0.5))))  # [규칙 1 동적화] 2026년 10계약 / 2025H2 3계약 / 2024년 2계약
    YF_MAX_SPREAD_RATIO  = 0.50    # [규칙 2] 호가 스프레드 비율: (Ask - Bid) / Ask > 50% 초과(또는 Bid <= $0.05) 시 IV 신뢰도 0% 강등
    YF_PSEUDO_DELTA_COEF = 0.035   # [규칙 3] 괴리율 기반 유사 델타: Max_OTM = min(0.20, max(0.055, 0.035 * sqrt(DTE)))
    USE_ROLLING_STRIKE   = True    # [규칙 4] 고정 비율 행사가 추적(Sticky-Moneyness)

    def calc_pseudo_delta_max_otm(dte_arr):
        dte_clean = np.maximum(np.asarray(dte_arr, dtype=float), 1.0)
        return np.minimum(0.20, np.maximum(0.055, YF_PSEUDO_DELTA_COEF * np.sqrt(dte_clean)))

    def safe_weighted_avg(vals, wgts):
        v = np.asarray(vals, dtype=float)
        w = np.asarray(wgts, dtype=float)
        mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
        if not np.any(mask):
            valid_v = v[np.isfinite(v)]
            return float(np.mean(valid_v)) if len(valid_v) > 0 else np.nan
        return float(np.average(v[mask], weights=w[mask]))

    def get_piv_series(piv_df, col_lv1, col_lv2, default_val=0.0):
        if len(piv_df) == 0 or col_lv1 not in piv_df.columns:
            return pd.Series(default_val, index=piv_df.index, dtype=float)
        sub = piv_df[col_lv1]
        if isinstance(sub, pd.DataFrame) and col_lv2 in sub.columns:
            return pd.to_numeric(sub[col_lv2], errors='coerce').fillna(default_val)
        return pd.Series(default_val, index=piv_df.index, dtype=float)

    def eval_rule2_spread_fail(bid_arr, ask_arr, last_p_arr):
        b = np.asarray(bid_arr, dtype=float)
        a = np.asarray(ask_arr, dtype=float)
        lp = np.asarray(last_p_arr, dtype=float)
        has_quote = (b > 0.0) & (a > 0.0)
        sp_ratio = np.where(has_quote, (a - b) / np.maximum(a, 1e-6), 0.0)
        # 장중 호가가 살아있으면 (Bid <= 0.05 또는 Spread > 50%) 탈락 / 장마감 후 호가(Bid=0) 초기화 시 Last Price <= $0.10 탈락
        return np.where(has_quote, (b <= 0.05) | (sp_ratio > YF_MAX_SPREAD_RATIO), lp <= 0.10)

    def interpolate_rolling_iv_by_moneyness(day_sub_df, target_moneyness_arr, opt_type):
        """
        [규칙 4: 고정 비율 행사가 추적 (Rolling Strike Mapping)]
        특정 일자(day_sub_df)의 유효 옵션 체인(규칙 1·2 통과)에서
        주어진 괴리율(Moneyness = (Strike - Spot) / Spot) 배열에 대응하는 내재변동성(IV)을 선형 보간하여 반환합니다.
        """
        if len(day_sub_df) == 0:
            return np.full(len(target_moneyness_arr), np.nan)
        spot_d = float(day_sub_df['EWY Price'].iloc[0])
        if spot_d <= 0:
            return np.full(len(target_moneyness_arr), np.nan)

        sub = day_sub_df[day_sub_df['Option Type'] == opt_type].copy()
        if len(sub) == 0:
            return np.full(len(target_moneyness_arr), np.nan)

        ask_v  = sub['Ask'].values.astype(float)
        bid_v  = sub['Bid'].values.astype(float)
        last_v = sub['Last Price'].values.astype(float)
        vol_v  = sub['Volume'].values.astype(float)
        iv_v   = sub['Implied Volatility'].values.astype(float)
        r2_fail = eval_rule2_spread_fail(bid_v, ask_v, last_v)

        # 규칙 1 & 규칙 2를 통과한 신뢰구간 호가만 보간 기준점으로 사용 (부족 시 완화 폴백)
        valid_m = (iv_v > 0.05) & (~r2_fail) & (vol_v >= YF_MIN_VOLUME_CUTOFF)
        if np.sum(valid_m) < 2:
            valid_m = (iv_v > 0.05) & (~r2_fail)
        if np.sum(valid_m) < 2:
            valid_m = (iv_v > 0.05)

        sub_valid = sub[valid_m].sort_values('Strike')
        if len(sub_valid) == 0:
            return np.full(len(target_moneyness_arr), np.nan)

        m_grid = (sub_valid['Strike'].values.astype(float) - spot_d) / spot_d
        iv_grid = sub_valid['Implied Volatility'].values.astype(float)
        return np.interp(target_moneyness_arr, m_grid, iv_grid)

    # --------------------------------------------------------------------------
    # [연산 1] 4대 정제 규칙 & 고정비율 행사가 추적(Rolling Strike Mapping) 기반 변동성 곡면 산출
    # --------------------------------------------------------------------------
    df_pit['Spread_Ratio'] = np.where(
        df_pit['Ask'] > 0,
        (df_pit['Ask'] - df_pit['Bid']) / df_pit['Ask'],
        1.0
    )
    df_pit['OTM_Dist_Pct'] = np.where(
        df_pit['Option Type'] == 'Put',
        np.maximum(0.0, (df_pit['EWY Price'] - df_pit['Strike']) / np.maximum(df_pit['EWY Price'], 1e-6)),
        np.maximum(0.0, (df_pit['Strike'] - df_pit['EWY Price']) / np.maximum(df_pit['EWY Price'], 1e-6))
    )
    df_pit['Max_Valid_OTM_Pct'] = calc_pseudo_delta_max_otm(df_pit['DTE'].values)

    df_pit['Rule2_Fail'] = eval_rule2_spread_fail(df_pit['Bid'].values, df_pit['Ask'].values, df_pit['Last Price'].values)

    # [규칙 1 + 규칙 2 + 규칙 3 결합] 표면/곡면 산출용 클린 데이터셋
    liq_df = df_pit[
        (df_pit['Implied Volatility'] > 0.05) &
        (~df_pit['Rule2_Fail']) &
        (df_pit['OTM_Dist_Pct'] <= df_pit['Max_Valid_OTM_Pct']) &
        (df_pit['Volume'] >= YF_MIN_VOLUME_CUTOFF)
    ].copy()

    # 거래량 10계약 이상 계약이 극소수인 과거/원월물 또는 장마감 후 호가 초기화 방어용 안전 폴백
    if liq_df['Quote Date'].nunique() < df_pit['Quote Date'].nunique():
        fallback_df = df_pit[
            (df_pit['Implied Volatility'] > 0.05) &
            ((df_pit['Bid'] > 0.05) | (df_pit['Last Price'] > 0.10)) &
            ((df_pit['Volume'] >= 1) | (df_pit['Open Interest'] >= 10))
        ].copy()
        missing_dates = set(df_pit['Quote Date'].unique()) - set(liq_df['Quote Date'].unique())
        liq_df = pd.concat([liq_df, fallback_df[fallback_df['Quote Date'].isin(missing_dates)]], ignore_index=True)

    Mid_Price = np.where((liq_df['Bid'] > 0) & (liq_df['Ask'] > 0), 0.5 * (liq_df['Bid'] + liq_df['Ask']), liq_df['Last Price'])
    liq_df['Weight'] = (liq_df['Volume'] * np.maximum(Mid_Price, 0.10) * 100.0) + liq_df['Open Interest'] + 1.0

    def calc_daily_surface(day_df):
        spot = day_df['EWY Price'].iloc[0]
        near_sub = day_df[(day_df['DTE'] >= 2) & (day_df['DTE'] <= 21)]
        mid_sub  = day_df[(day_df['DTE'] >= 22) & (day_df['DTE'] <= 50)]
        back_sub = day_df[(day_df['DTE'] >= 60) & (day_df['DTE'] <= 150)]

        def get_atm(sub):
            if len(sub) == 0:
                return np.nan
            atm = sub[np.abs(sub['Strike'] - spot) / spot <= 0.03]
            if len(atm) == 0:
                atm = sub.iloc[(sub['Strike'] - spot).abs().argsort()[:4]]
            return safe_weighted_avg(atm['Implied Volatility'], atm['Weight'])

        def get_rolling_skew_and_bfly(sub, atm_val, target_otm_pct=0.05):
            """
            [규칙 3 & 4: 괴리율 기반 유사 델타 + 고정 비율 행사가 추적(Rolling Strike Mapping)]
            야후 데이터의 불안정한 Delta 대신 현가 대비 고정 비율(-5% Put vs +5% Call, 원월은 ±7%) 위치의
            행사가 IV를 보간·추적하여 스마일 슬라이딩이 제거된 순수 Skew와 Butterfly를 산출합니다.
            """
            if len(sub) == 0 or np.isnan(atm_val):
                return np.nan, np.nan, np.nan, np.nan
            puts = sub[
                (sub['Option Type'] == 'Put') &
                (((spot - sub['Strike']) / spot).between(target_otm_pct - 0.03, target_otm_pct + 0.04))
            ]
            calls = sub[
                (sub['Option Type'] == 'Call') &
                (((sub['Strike'] - spot) / spot).between(target_otm_pct - 0.03, target_otm_pct + 0.04))
            ]
            if len(puts) == 0:
                puts = sub[(sub['Option Type'] == 'Put') & (sub['Delta'] <= -0.18) & (sub['Delta'] >= -0.32)]
            if len(calls) == 0:
                calls = sub[(sub['Option Type'] == 'Call') & (sub['Delta'] >= 0.18) & (sub['Delta'] <= 0.32)]

            p_iv = safe_weighted_avg(puts['Implied Volatility'], puts['Weight']) if len(puts) > 0 else np.nan
            c_iv = safe_weighted_avg(calls['Implied Volatility'], calls['Weight']) if len(calls) > 0 else np.nan
            skew = p_iv - c_iv
            bfly = 0.5 * (p_iv + c_iv) - atm_val
            return p_iv, c_iv, skew, bfly

        n_iv = get_atm(near_sub)
        m_iv = get_atm(mid_sub)
        b_iv = get_atm(back_sub)

        _, _, sk_n, bf_n = get_rolling_skew_and_bfly(near_sub, n_iv, target_otm_pct=0.045)
        _, _, sk_m, bf_m = get_rolling_skew_and_bfly(mid_sub, m_iv, target_otm_pct=0.055)
        _, _, sk_b, bf_b = get_rolling_skew_and_bfly(back_sub, b_iv, target_otm_pct=0.070)

        return pd.Series({
            'Spot': spot,
            'Near_ATM_IV': n_iv,
            'Mid_ATM_IV': m_iv,
            'Back_ATM_IV': b_iv,
            'Term_Near_Back': n_iv - b_iv,
            'Term_Near_Mid': n_iv - m_iv,
            'Near_Skew_25D': sk_n,
            'Mid_Skew_25D': sk_m,
            'Back_Skew_25D': sk_b,
            'Near_Bfly_25D': bf_n,
            'Mid_Bfly_25D': bf_m,
            'Back_Bfly_25D': bf_b
        })

    # --------------------------------------------------------------------------
    # ★ [V4.2.3 업그레이드 A] 3년 마스터 DB vs 현업 시그널 창(2025-01-02~ & 252일 롤링 %ile) 이원화 및 1일 OI=0 결측 자동 복원
    # --------------------------------------------------------------------------
    SIGNAL_START_DATE  = "2025-01-02"
    ROLLING_PCT_WINDOW = 252  # 최근 1년(252거래일) 롤링 백분위수 기준 (2024년 초저변동성 기저효과 왜곡 차단)

    # 1) [1일 OI=0 피드 결측(Glitch) 자동 복원]: 만기 생존 계약이 직전 OI>=50인데 거래량<0.5*직전OI 상태에서 하루 0으로 빠진 경우 직전 OI 유지
    df_pit = df_pit.sort_values(['Contract Name', 'Quote Date']).reset_index(drop=True)
    _prev_pos_oi = df_pit['Open Interest'].replace(0, np.nan).groupby(df_pit['Contract Name']).ffill().fillna(0.0)
    _is_oi_glitch = (df_pit['Open Interest'] == 0) & (_prev_pos_oi >= 50) & (df_pit['Volume'] < _prev_pos_oi * 0.5) & (df_pit['DTE'] > 0)
    df_pit['Open Interest'] = np.where(_is_oi_glitch, _prev_pos_oi, df_pit['Open Interest'])
    df_pit = df_pit.sort_values(['Quote Date', 'Expiration Date', 'Option Type', 'Strike']).reset_index(drop=True)

    # 2) [현업 시그널 창 분리]: 기준일이 2025-06-01 이후면 2025-01-02 이후(또는 최근 300거래일) 정밀 수급 구간만 변동성 곡면 고속 연산
    _sig_start_dt = SIGNAL_START_DATE if latest_date >= "2025-06-01" else all_dates[max(0, total_days - 300)]
    _liq_sig_df = liq_df[liq_df['Quote Date'] >= _sig_start_dt].copy()
    if _liq_sig_df['Quote Date'].nunique() < min(total_days, 30):
        _liq_sig_df = liq_df.copy()

    ts_metrics = _liq_sig_df.groupby('Quote Date', group_keys=False).apply(calc_daily_surface).ffill()
    for col in ['Near_ATM_IV', 'Mid_ATM_IV', 'Term_Near_Back', 'Near_Skew_25D',
                'Mid_Skew_25D', 'Back_Skew_25D', 'Near_Bfly_25D', 'Mid_Bfly_25D']:
        try:
            ts_metrics[col + '_pct'] = ts_metrics[col].rolling(window=ROLLING_PCT_WINDOW, min_periods=5).rank(pct=True).fillna(0.5) * 100.0
        except Exception:
            ts_metrics[col + '_pct'] = pit_expanding_pct_rank(ts_metrics[col], min_periods=5)

    curr_ts = ts_metrics.loc[latest_date]
    prev_ts = ts_metrics.loc[prev1_date]
    # ★ [V4.2.9] 국면 판정·급락 위험도 일자별 표 (가격·변동성 곡면·전체 OI만 사용 -> 모든 일자에 같은 정의)
    _ph_tbl = phase_base_table(df_pit, ts_metrics)

    # --------------------------------------------------------------------------
    # [연산 2] 4대 정제 규칙 & 고정비율 행사가 추적(Rolling Strike) 탑재 OI × IV 4분면 분류
    # --------------------------------------------------------------------------
    d_3d_base  = get_base_date_for_window(all_dates, 3)
    d_7d_base  = get_base_date_for_window(all_dates, 7)
    d_20d_base = get_base_date_for_window(all_dates, 20)
    surv_df = df_pit[(df_pit['Quote Date'] >= min(peak_date, long_date, d_20d_base)) & (df_pit['Expiration Date'] >= latest_date)].copy()
    active_exps = sorted(surv_df[surv_df['Quote Date'] == latest_date]['Expiration Date'].unique())
    future_exps = [e for e in active_exps if e > latest_date]
    nearest_exp = future_exps[0] if len(future_exps) > 0 else (active_exps[0] if len(active_exps) > 0 else latest_date)

    near_exp_puts = surv_df[
        (surv_df['Expiration Date'] == nearest_exp) &
        (surv_df['Option Type'] == 'Put')
    ].groupby('Quote Date')['Open Interest'].sum()
    near_exp_oi_latest = int(near_exp_puts.get(latest_date, 0))
    near_exp_oi_short  = int(near_exp_puts.get(short_date, near_exp_oi_latest))
    near_exp_oi_chg_s  = near_exp_oi_latest - near_exp_oi_short

    def build_quadrant_table_for_dates(sub_surv_df, d_curr, d_p1, d_short, d_long, d_peak, opt_type, iv_attr='trade'):
        # ★ [V4.3.4] iv_attr='trade': 체결일 귀속 유효IV(기본) / 'window': 기존 창 전체 IV 기준(분배 폭락 경보의 검증 정의 유지용)
        piv = sub_surv_df[sub_surv_df['Option Type'] == opt_type].pivot_table(
            index=['Expiration Date', 'Strike'],
            columns='Quote Date',
            values=['Open Interest', 'Volume', 'Implied Volatility', 'Last Price', 'Bid', 'Ask', 'Delta', 'DTE'],
            aggfunc='first'
        )
        # ★ [V4.2.5 보완] 2024~2025년 무거래일 행 누락(NaN) 시 직전 거래일 OI·IV·종가를 유지(Past-Only FFill)하여 가짜 OI 폭증 차단
        if len(piv) == 0:
            empty_cols = ['OI_Peak','OI_Long','OI_Short','OI_Prev1','OI_Latest','Vol_Prev1','Vol_Latest','Vol_ShortWin',
                          'IV_Long','IV_Short','IV_Prev1','IV_Latest','Price_Latest','Bid_Latest','Ask_Latest','Delta_Latest','DTE_Latest',
                          'OI_Chg_1D','OI_Chg_Short','OI_Chg_Long','OI_Chg_Peak','Raw_IV_Chg_1D','IV_Chg_1D','IV_Chg_Short','IV_Chg_Long',
                          'Eff_IV_Chg','Rule1_ZeroVol_Fail','Rule2_Spread_Fail','Rule3_Moneyness_Fail','Is_Clean_Contract','Quadrant','Quad_Long']
            empty_idx = pd.MultiIndex.from_arrays([[], []], names=['Expiration Date', 'Strike'])
            return pd.DataFrame(columns=empty_cols, index=empty_idx)

        for _ff_col in ['Open Interest', 'Implied Volatility', 'Last Price', 'Delta']:
            if _ff_col in piv.columns:
                piv[_ff_col] = piv[_ff_col].ffill(axis=1)

        short_win_dates = [d for d in sorted(sub_surv_df['Quote Date'].unique()) if d_short <= d <= d_curr]

        vol_short_sum = sum(get_piv_series(piv, 'Volume', d, 0.0) for d in short_win_dates)
        spot_curr_d  = float(sub_surv_df[sub_surv_df['Quote Date'] == d_curr]['EWY Price'].iloc[0])
        spot_p1_d    = float(sub_surv_df[sub_surv_df['Quote Date'] == d_p1]['EWY Price'].iloc[0]) if d_p1 in sub_surv_df['Quote Date'].values else spot_curr_d
        spot_short_d = float(sub_surv_df[sub_surv_df['Quote Date'] == d_short]['EWY Price'].iloc[0]) if d_short in sub_surv_df['Quote Date'].values else spot_p1_d
        spot_long_d  = float(sub_surv_df[sub_surv_df['Quote Date'] == d_long]['EWY Price'].iloc[0]) if d_long in sub_surv_df['Quote Date'].values else spot_short_d

        tbl = pd.DataFrame({
            'OI_Peak': get_piv_series(piv, 'Open Interest', d_peak, 0.0),
            'OI_Long': get_piv_series(piv, 'Open Interest', d_long, 0.0),
            'OI_Short': get_piv_series(piv, 'Open Interest', d_short, 0.0),
            'OI_Prev1': get_piv_series(piv, 'Open Interest', d_p1, 0.0),
            'OI_Latest': get_piv_series(piv, 'Open Interest', d_curr, 0.0),
            'Vol_Prev1': get_piv_series(piv, 'Volume', d_p1, 0.0),
            'Vol_Latest': get_piv_series(piv, 'Volume', d_curr, 0.0),
            'Vol_ShortWin': vol_short_sum,
            'IV_Long': get_piv_series(piv, 'Implied Volatility', d_long, 0.0),
            'IV_Short': get_piv_series(piv, 'Implied Volatility', d_short, 0.0),
            'IV_Prev1': get_piv_series(piv, 'Implied Volatility', d_p1, 0.0),
            'IV_Latest': get_piv_series(piv, 'Implied Volatility', d_curr, 0.0),
            'Price_Latest': get_piv_series(piv, 'Last Price', d_curr, 0.0),
            'Bid_Latest': get_piv_series(piv, 'Bid', d_curr, 0.0),
            'Ask_Latest': get_piv_series(piv, 'Ask', d_curr, 0.0),
            'Delta_Latest': get_piv_series(piv, 'Delta', d_curr, 0.0),
            'DTE_Latest': get_piv_series(piv, 'DTE', d_curr, 0.0),
        }).fillna(0.0)

        strk_arr = tbl.index.get_level_values('Strike').values.astype(float)
        tbl['Moneyness_Latest'] = (strk_arr - spot_curr_d) / max(spot_curr_d, 1e-6)
        tbl['OTM_Dist_Pct'] = np.where(
            opt_type == 'Put',
            np.maximum(0.0, (spot_curr_d - strk_arr) / max(spot_curr_d, 1e-6)),
            np.maximum(0.0, (strk_arr - spot_curr_d) / max(spot_curr_d, 1e-6))
        )
        tbl['Max_Valid_OTM_Pct'] = calc_pseudo_delta_max_otm(tbl['DTE_Latest'].values)
        tbl['Spread_Ratio'] = np.where(
            tbl['Ask_Latest'] > 0,
            (tbl['Ask_Latest'] - tbl['Bid_Latest']) / tbl['Ask_Latest'],
            1.0
        )

        # [V4.1 규칙 1·2·3 통합 신뢰도 마스크]
        # - 규칙 1(Zero-Volume): 단기창 거래량 합계(Vol_ShortWin) < 10 이면서 당일 거래량(Vol_Latest) < 10 이면 유령호가
        # - 규칙 2(Bid-Ask Spread): (Ask - Bid)/Ask > 50% 또는 Bid <= $0.05 이면 호가 경직성 착시
        # - 규칙 3(Pseudo-Delta Moneyness): OTM 괴리율이 DTE 연동 한계(DTE 3일 기준 ±6.06%)를 초과하면 스마일 슬라이딩 노이즈
        tbl['Rule1_ZeroVol_Fail']   = (tbl['Vol_Latest'] < YF_MIN_VOLUME_CUTOFF) & (tbl['Vol_ShortWin'] < YF_MIN_VOLUME_CUTOFF)
        tbl['Rule2_Spread_Fail']    = eval_rule2_spread_fail(tbl['Bid_Latest'].values, tbl['Ask_Latest'].values, tbl['Price_Latest'].values)
        tbl['Rule3_Moneyness_Fail'] = tbl['OTM_Dist_Pct'] > tbl['Max_Valid_OTM_Pct']
        tbl['Is_Clean_Contract']    = ~(tbl['Rule1_ZeroVol_Fail'] | tbl['Rule2_Spread_Fail'] | tbl['Rule3_Moneyness_Fail'])

        # [V4.1 규칙 4: 고정 비율 행사가 추적 (Rolling Strike Mapping)]
        # 어제/기준일 주가 대비 오늘과 동일한 괴리율(Moneyness_Latest) 위치에 있던 행사가의 IV를 보간하여 비교
        if USE_ROLLING_STRIKE:
            iv_roll_p1    = np.zeros(len(tbl))
            iv_roll_short = np.zeros(len(tbl))
            iv_roll_long  = np.zeros(len(tbl))
            for exp_val in tbl.index.get_level_values('Expiration Date').unique():
                exp_mask = (tbl.index.get_level_values('Expiration Date') == exp_val)
                m_targets = tbl.loc[exp_mask, 'Moneyness_Latest'].values

                sub_p1    = sub_surv_df[(sub_surv_df['Quote Date'] == d_p1) & (sub_surv_df['Expiration Date'] == exp_val)]
                sub_short = sub_surv_df[(sub_surv_df['Quote Date'] == d_short) & (sub_surv_df['Expiration Date'] == exp_val)]
                sub_long  = sub_surv_df[(sub_surv_df['Quote Date'] == d_long) & (sub_surv_df['Expiration Date'] == exp_val)]

                iv_roll_p1[exp_mask]    = interpolate_rolling_iv_by_moneyness(sub_p1, m_targets, opt_type)
                iv_roll_short[exp_mask] = interpolate_rolling_iv_by_moneyness(sub_short, m_targets, opt_type)
                iv_roll_long[exp_mask]  = interpolate_rolling_iv_by_moneyness(sub_long, m_targets, opt_type)

            tbl['IV_Roll_Prev1'] = np.where(np.isfinite(iv_roll_p1) & (iv_roll_p1 > 0.05), iv_roll_p1, tbl['IV_Prev1'])
            tbl['IV_Roll_Short'] = np.where(np.isfinite(iv_roll_short) & (iv_roll_short > 0.05), iv_roll_short, tbl['IV_Short'])
            tbl['IV_Roll_Long']  = np.where(np.isfinite(iv_roll_long) & (iv_roll_long > 0.05), iv_roll_long, tbl['IV_Long'])
        else:
            tbl['IV_Roll_Prev1'] = tbl['IV_Prev1']
            tbl['IV_Roll_Short'] = tbl['IV_Short']
            tbl['IV_Roll_Long']  = tbl['IV_Long']

        tbl['OI_Chg_1D']    = tbl['OI_Latest'] - tbl['OI_Prev1']
        tbl['OI_Chg_Short'] = tbl['OI_Latest'] - tbl['OI_Short']
        tbl['OI_Chg_Long']  = tbl['OI_Latest'] - tbl['OI_Long']
        tbl['OI_Chg_Peak']  = tbl['OI_Latest'] - tbl['OI_Peak']

        # ★ [V4.2.7 신설 — 규칙 5: 동일 만기 대칭 수량 멀티레그(Vertical Spread / Condor) 거품 차단 필터]
        # 동일 만기 내에서 2개 이상의 행사가가 대규모(|dOI| >= max(150, 2000*s_oi))이면서 수량 편차 8% 이내로 동시에 증감한 경우
        # 방향성 네이키드 수급이 아닌 차익/스프레드 결합 상품이므로 Is_Clean_Contract에서 제외하여 Q1/Q2 뻥튀기를 원천 차단합니다.
        _mleg_cut = max(150.0, 2000.0 * s_oi)
        _is_mleg_short = np.zeros(len(tbl), dtype=bool)
        _exps_arr = tbl.index.get_level_values('Expiration Date').values
        _doi_s_arr = tbl['OI_Chg_Short'].values.astype(float)
        for _ev in np.unique(_exps_arr):
            _idx_e = np.where((_exps_arr == _ev) & (np.abs(_doi_s_arr) >= _mleg_cut))[0]
            if len(_idx_e) >= 2:
                for _i in range(len(_idx_e)):
                    for _j in range(_i + 1, len(_idx_e)):
                        _vi, _vj = _doi_s_arr[_idx_e[_i]], _doi_s_arr[_idx_e[_j]]
                        _wi, _wj = float(tbl['Vol_ShortWin'].values[_idx_e[_i]]), float(tbl['Vol_ShortWin'].values[_idx_e[_j]])
                        # ★ [V4.2.8 ④] OI 수량만 비슷하면 우연 일치(만기일 동시 청산 등)도 멀티레그로 오탐 → 단기창 거래량도 ±10% 이내일 때만 인정
                        if (_vi * _vj > 0) and (abs(_vi - _vj) / max(abs(_vi), abs(_vj), 1.0) <= 0.08) and (abs(_wi - _wj) / max(_wi, _wj, 1.0) <= 0.10):
                            _is_mleg_short[_idx_e[_i]] = True
                            _is_mleg_short[_idx_e[_j]] = True
        tbl['Rule4_MultiLeg_Fail'] = _is_mleg_short
        tbl['Is_Clean_Contract']   = tbl['Is_Clean_Contract'] & (~tbl['Rule4_MultiLeg_Fail'])

        # [V4.1 프랍 퀀트 보정] 주가 상승일에 OTM 풋이 스큐 곡선을 타고 미끄러지며 발생하는 가짜 IV 폭등(Smile Sliding)만 정밀 제거하고,
        # 콜옵션이 주가 반등(IV Crush) 시 Q2(커버드콜)로 억지 둔갑하는 현상을 방지합니다.
        tbl['Raw_IV_Chg_1D']    = tbl['IV_Latest'] - tbl['IV_Prev1']
        tbl['Raw_IV_Chg_Short'] = np.where(tbl['IV_Short'] > 0.05, tbl['IV_Latest'] - tbl['IV_Short'], tbl['Raw_IV_Chg_1D'])
        tbl['Raw_IV_Chg_Long']  = np.where(tbl['IV_Long'] > 0.05, tbl['IV_Latest'] - tbl['IV_Long'], tbl['Raw_IV_Chg_Short'])

        # ★ [V4.2.8 ①] 곡면 중립 잔차 IV: 각 계약 IV 변화에서 '같은 만기대' ATM IV 변화분을 양방향·무조건 차감 (근월≤45일/중기≤120일/원월)
        _dte_q = tbl['DTE_Latest'].values.astype(float)
        def _atm_bucket_chg(_da, _db):
            _out = np.zeros(len(tbl))
            for _col, _lo, _hi in (('Near_ATM_IV', -1.0, 45.0), ('Mid_ATM_IV', 45.0, 120.0), ('Back_ATM_IV', 120.0, 1e9)):
                _a = float(ts_metrics.loc[_da, _col]) if (_da in ts_metrics.index and _col in ts_metrics.columns) else np.nan
                _b = float(ts_metrics.loc[_db, _col]) if (_db in ts_metrics.index and _col in ts_metrics.columns) else np.nan
                _out = np.where((_dte_q > _lo) & (_dte_q <= _hi), (_a - _b) if (np.isfinite(_a) and np.isfinite(_b)) else 0.0, _out)
            return _out
        _atm_1d, _atm_sh = _atm_bucket_chg(d_curr, d_p1), _atm_bucket_chg(d_curr, d_short)
        _atm_lg, _atm_t1 = _atm_bucket_chg(d_curr, d_long), _atm_bucket_chg(d_p1, d_short)

        # ★ [V4.3.4] 체결일 귀속 유효 IV: 창 안의 하루하루 OI 변동(보고일 d)은 직전 거래일(체결일 t)의 IV 변동 IV(t)-IV(t의 전일)에 귀속하고,
        #   OI 변동 크기로 가중 평균한다. (기존: 마지막 하루 OI 비중이 60% 미만이면 창 전체 IV 변동을 써서, 체결 뒤에 생긴 IV 변화로 과거 물량이 소급 재분류됨)
        _all_q_dates = sorted(sub_surv_df['Quote Date'].unique())
        def _trade_day_iv_attr(d_start, k_atm):
            _w = [d for d in _all_q_dates if d_start <= d <= d_curr]
            _num = np.zeros(len(tbl)); _den = np.zeros(len(tbl))
            for _j in range(1, len(_w)):
                _d, _t = _w[_j], _w[_j - 1]
                _it = _all_q_dates.index(_t)
                if _it == 0:
                    continue
                _tp = _all_q_dates[_it - 1]
                _doi = get_piv_series(piv, 'Open Interest', _d, 0.0).values.astype(float) - get_piv_series(piv, 'Open Interest', _t, 0.0).values.astype(float)
                _iv_t  = get_piv_series(piv, 'Implied Volatility', _t, 0.0).values.astype(float)
                _iv_tp = get_piv_series(piv, 'Implied Volatility', _tp, 0.0).values.astype(float)
                _ok  = (_iv_t > 0.05) & (_iv_tp > 0.05) & np.isfinite(_doi)
                _div = (_iv_t - _iv_tp) - k_atm * _atm_bucket_chg(_t, _tp)
                _wgt = np.where(_ok, np.abs(_doi), 0.0)
                _num += _wgt * np.where(_ok, _div, 0.0)
                _den += _wgt
            return np.where(_den > 0, _num / np.maximum(_den, 1e-12), np.nan) if iv_attr == 'trade' else np.full(len(tbl), np.nan)

        if opt_type == 'Put':
            # ★ [V4.2 업그레이드 1] 고점 Vol-Crush 국면에서 시장 ATM IV 하락분(0.85 * ΔATM_IV) 대칭 보정으로 콜라 헤지 풋(Q1) 복원
            day_c_vol_p = float(sub_surv_df[(sub_surv_df['Quote Date'] == d_curr) & (sub_surv_df['Option Type'] == 'Call')]['Volume'].sum())
            day_p_vol_p = float(sub_surv_df[(sub_surv_df['Quote Date'] == d_curr) & (sub_surv_df['Option Type'] == 'Put')]['Volume'].sum())
            call_share_p = day_c_vol_p / max(day_c_vol_p + day_p_vol_p, 1.0)
            atm_s_curr_p  = ts_metrics.loc[d_curr, 'Near_ATM_IV'] if d_curr in ts_metrics.index else 0.0
            atm_s_p1_p    = ts_metrics.loc[d_p1, 'Near_ATM_IV'] if d_p1 in ts_metrics.index else atm_s_curr_p
            atm_s_short_p = ts_metrics.loc[d_short, 'Near_ATM_IV'] if d_short in ts_metrics.index else atm_s_p1_p
            atm_s_long_p  = ts_metrics.loc[d_long, 'Near_ATM_IV'] if d_long in ts_metrics.index else atm_s_short_p
            back_sk_pct_p = ts_metrics.loc[d_curr, 'Back_Skew_25D_pct'] if (d_curr in ts_metrics.index and 'Back_Skew_25D_pct' in ts_metrics.columns) else 50.0
            spot_peak_p   = float(sub_surv_df[sub_surv_df['Quote Date'] == d_peak]['EWY Price'].iloc[0]) if d_peak in sub_surv_df['Quote Date'].values else spot_curr_d
            dd_peak_p     = (spot_curr_d / max(spot_peak_p, 1e-6) - 1.0) * 100.0
            is_top_vc_reg = (dd_peak_p >= -3.5) and ((call_share_p < 0.48) or (back_sk_pct_p >= 85.0))

            roll_diff_1d    = np.where(tbl['IV_Roll_Prev1'] > 0.05, tbl['IV_Latest'] - tbl['IV_Roll_Prev1'], tbl['Raw_IV_Chg_1D'])
            roll_diff_short = np.where(tbl['IV_Roll_Short'] > 0.05, tbl['IV_Latest'] - tbl['IV_Roll_Short'], tbl['Raw_IV_Chg_Short'])
            roll_diff_long  = np.where(tbl['IV_Roll_Long'] > 0.05, tbl['IV_Latest'] - tbl['IV_Roll_Long'], tbl['Raw_IV_Chg_Long'])

            base_p_1d = np.where((spot_curr_d > spot_p1_d) & (strk_arr < spot_curr_d), np.minimum(tbl['Raw_IV_Chg_1D'], roll_diff_1d), tbl['Raw_IV_Chg_1D'])
            base_p_sh = np.where((spot_curr_d > spot_short_d) & (strk_arr < spot_curr_d), np.minimum(tbl['Raw_IV_Chg_Short'], roll_diff_short), tbl['Raw_IV_Chg_Short'])
            base_p_lg = np.where((spot_curr_d > spot_long_d) & (strk_arr < spot_curr_d), np.minimum(tbl['Raw_IV_Chg_Long'], roll_diff_long), tbl['Raw_IV_Chg_Long'])
            base_p_t1 = np.where((tbl['IV_Short'] > 0.05) & (tbl['IV_Prev1'] > 0.05), tbl['IV_Prev1'] - tbl['IV_Short'], base_p_1d)

            # ★ [V4.2.8 ①] 기존: 고점 Vol-Crush 국면에서만 IV '하락분'만 보정 → 변경: 같은 만기대 ATM IV 변화분을 양방향·무조건 차감 (계수 0.85 유지)
            vc_1d = 0.85 * _atm_1d
            vc_sh = 0.85 * _atm_sh
            vc_lg = 0.85 * _atm_lg
            vc_t1 = 0.85 * _atm_t1

            tbl['IV_Chg_1D']          = base_p_1d - vc_1d
            tbl['IV_Chg_Short']       = base_p_sh - vc_sh
            tbl['IV_Chg_Long']        = base_p_lg - vc_lg
            tbl['IV_Chg_TradeDay_T1'] = base_p_t1 - vc_t1
            raw_eff_iv_window = np.where(
                np.abs(tbl['OI_Chg_1D']) >= 0.6 * np.abs(tbl['OI_Chg_Short']),
                tbl['IV_Chg_TradeDay_T1'],
                tbl['IV_Chg_Short']
            )   # 기존 방식(진단용)
            _attr_sh = _trade_day_iv_attr(d_short, 0.85)
            _attr_lg = _trade_day_iv_attr(d_long, 0.85)
            raw_eff_iv = np.where(np.isfinite(_attr_sh), _attr_sh, raw_eff_iv_window)   # ★ [V4.3.4] 체결일 귀속
        else:
            # ★ [V4.1 과최적화 방지 조건부 바나(Spot-Vol Beta) 보정]:
            # 무조건적 바나 보정 대신, 주가 반등(Spot↑) 및 콜 거래량 우위(Call Share >= 53%)가 동시에 확인된 '진성 반등 국면'에서만
            # 만기별 ATM IV 하락분(0.80 * ΔATM_IV)을 차감하고, 현가 근접(-1%~+4.5%) 저항벽에서 당일 거래량(>=100)을 동반한 양전환(Sign-Flip >= +0.5%p)만 승격!
            day_c_vol = float(sub_surv_df[(sub_surv_df['Quote Date'] == d_curr) & (sub_surv_df['Option Type'] == 'Call')]['Volume'].sum())
            day_p_vol = float(sub_surv_df[(sub_surv_df['Quote Date'] == d_curr) & (sub_surv_df['Option Type'] == 'Put')]['Volume'].sum())
            call_share_curr = day_c_vol / max(day_c_vol + day_p_vol, 1.0)
            is_bull_vanna_regime = (spot_curr_d > spot_short_d) and (call_share_curr >= 0.53)

            atm_s_curr  = ts_metrics.loc[d_curr, 'Near_ATM_IV'] if d_curr in ts_metrics.index else 0.0
            atm_s_p1    = ts_metrics.loc[d_p1, 'Near_ATM_IV'] if d_p1 in ts_metrics.index else atm_s_curr
            atm_s_short = ts_metrics.loc[d_short, 'Near_ATM_IV'] if d_short in ts_metrics.index else atm_s_p1

            # ★ [V4.2.8 ①] 기존: 주가 반등+콜점유율 53%↑일 때만 IV '하락분'만 보정 → 변경: 같은 만기대 ATM IV 변화분을 양방향·무조건 차감 (계수 0.80 유지)
            vanna_adj_1d = 0.80 * _atm_1d
            vanna_adj_sh = 0.80 * _atm_sh
            vanna_adj_t1 = 0.80 * _atm_t1

            tbl['IV_Chg_1D']    = tbl['Raw_IV_Chg_1D'] - vanna_adj_1d
            tbl['IV_Chg_Short'] = tbl['Raw_IV_Chg_Short'] - vanna_adj_sh
            tbl['IV_Chg_Long']  = tbl['Raw_IV_Chg_Long'] - 0.80 * _atm_lg
            tbl['IV_Chg_TradeDay_T1'] = np.where(
                (tbl['IV_Short'] > 0.05) & (tbl['IV_Prev1'] > 0.05),
                (tbl['IV_Prev1'] - tbl['IV_Short']) - vanna_adj_t1,
                tbl['IV_Chg_1D']
            )
            base_eff_iv = np.where(
                np.abs(tbl['OI_Chg_1D']) >= 0.6 * np.abs(tbl['OI_Chg_Short']),
                tbl['IV_Chg_TradeDay_T1'],
                tbl['IV_Chg_Short']
            )
            # 조건부 숏감마 핀치(Short-Gamma Pinch) 승격: 현가 -1%~+4.5% 근접 행사가에서 주가 상승 + 콜 우위 + 당일 원시 IV +0.5%p 이상 급등 & 거래량 >= 100계약일 때만 승격
            pinch_promote = (
                is_bull_vanna_regime &
                (strk_arr >= spot_curr_d * 0.99) &
                (strk_arr <= spot_curr_d * 1.045) &
                (tbl['Raw_IV_Chg_1D'].values >= 0.005) &
                (tbl['Vol_Latest'].values >= max(5, int(round(100 * s_vol))))
            )
            raw_eff_iv_window = np.where(pinch_promote, np.maximum(base_eff_iv, tbl['Raw_IV_Chg_1D'].values), base_eff_iv)   # 기존 방식(진단용)
            _attr_sh = _trade_day_iv_attr(d_short, 0.80)
            _attr_lg = _trade_day_iv_attr(d_long, 0.80)
            _base_attr = np.where(np.isfinite(_attr_sh), _attr_sh, base_eff_iv)   # ★ [V4.3.4] 체결일 귀속
            raw_eff_iv = np.where(pinch_promote, np.maximum(_base_attr, tbl['Raw_IV_Chg_1D'].values), _base_attr)

        # [핵심] 규칙 1·2·3에 위배된 유령호가/스프레드과다/초외가격 노이즈 계약은 가짜 IV 급등(>0)을 0.0으로 강등(NaN/무효화)
        tbl['Eff_IV_Chg'] = np.where(~tbl['Is_Clean_Contract'] & (raw_eff_iv > 0), 0.0, raw_eff_iv)
        tbl['Eff_IV_Chg_Window'] = np.where(~tbl['Is_Clean_Contract'] & (raw_eff_iv_window > 0), 0.0, raw_eff_iv_window)   # 진단용: 기존 창 전체 IV 기준
        _old_lg = np.where(np.abs(tbl['OI_Chg_1D']) < 0.6 * np.abs(tbl['OI_Chg_Long']), tbl['IV_Chg_Long'], tbl['IV_Chg_TradeDay_T1'])
        tbl['Eff_IV_Chg_Long'] = np.where(np.isfinite(_attr_lg), _attr_lg, _old_lg)   # ★ [V4.3.4] 장기창도 체결일 귀속 (iv_attr='window'면 _attr_lg가 NaN이라 기존 값)
        tbl['IV_Chg_1D']  = np.where((tbl['Vol_Latest'] < YF_MIN_VOLUME_CUTOFF) | tbl['Rule2_Spread_Fail'] | tbl['Rule3_Moneyness_Fail'],
                                     np.minimum(0.0, tbl['IV_Chg_1D']), tbl['IV_Chg_1D'])

        quads = []
        quads_long = []
        for _, r in tbl.iterrows():
            doi = r['OI_Chg_Short']
            div = r['Eff_IV_Chg']
            doi_l = r['OI_Chg_Long']
            div_l = r['Eff_IV_Chg_Long']
            is_clean = bool(r['Is_Clean_Contract'])

            if opt_type == 'Call':
                if not is_clean:
                    quads.append("노이즈제외 (초외가격/유령호가/멀티레그)")
                elif doi > 0 and div > 0.002:
                    quads.append("Q1: 진성 상방 매수 (Bullish Long Call)")
                elif doi > 0:
                    quads.append("Q2: 상단 캡 커버드콜 (Bearish Call Overwriting)")
                elif doi < 0 and div < -0.002:
                    quads.append("Q3: 상방 포기 롱 청산 (Call Liquidation)")
                else:
                    quads.append("Q4: 콜 매도 환매수/롤오버 (Short Cover/Roll)")

                if not is_clean:
                    quads_long.append("NOISE")
                elif doi_l > 0 and div_l > 0.002:
                    quads_long.append("Q1")
                elif doi_l > 0:
                    quads_long.append("Q2")
                elif doi_l < 0 and div_l < -0.002:
                    quads_long.append("Q3")
                else:
                    quads_long.append("Q4")
            else:
                if not is_clean:
                    quads.append("노이즈제외 (초외가격/유령호가/멀티레그)")
                elif doi > 0 and div > 0.002:
                    quads.append("Q1: 하방 폭락 베팅/롤다운 (Bearish Long Put)")
                elif doi > 0 and float(r.name[1]) > spot_curr_d and spot_curr_d < spot_short_d:
                    # ★ [V4.2.8 ②] 주가 하락 중 내가격 풋의 IV 하락은 머니니스 이동에 따른 자연 하락 → Q2(바닥 방어)로 단정하지 않고 방향 보류
                    quads.append("ITM풋 방향보류 (내가격 심화 자연 IV하락)")
                elif doi > 0:
                    quads.append("Q2: 바닥 방어 풋 매도 (Bullish Put Overwriting)")
                elif doi < 0 and div < -0.002:
                    quads.append("Q3: 풋 수익화 청산 (Put Monetization/Vanna)")
                else:
                    quads.append("Q4: 만기전 청산/숏커버 (Put Close/Short Cover)")

                if not is_clean:
                    quads_long.append("NOISE")
                elif doi_l > 0 and div_l > 0.002:
                    quads_long.append("Q1")
                elif doi_l > 0 and float(r.name[1]) > spot_curr_d and spot_curr_d < spot_long_d:
                    quads_long.append("HOLD")
                elif doi_l > 0:
                    quads_long.append("Q2")
                elif doi_l < 0 and div_l < -0.002:
                    quads_long.append("Q3")
                else:
                    quads_long.append("Q4")

        tbl['Quadrant'] = quads
        tbl['Quad_Long'] = quads_long
        return tbl

    c_tbl = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, short_date, long_date, peak_date, 'Call')
    p_tbl = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, short_date, long_date, peak_date, 'Put')

    # 단기창(w_short) 4분면 합계 (규칙 1·2·3 통과한 Clean Contract만 Q1/Q2 방향성 수급에 합산)
    c_clean = c_tbl['Is_Clean_Contract']
    p_clean = p_tbl['Is_Clean_Contract']

    c_q1_sum = int(c_tbl[c_tbl['Quadrant'].str.startswith('Q1') & c_clean]['OI_Chg_Short'].sum())
    c_q2_sum = int(c_tbl[c_tbl['Quadrant'].str.startswith('Q2') & c_clean]['OI_Chg_Short'].sum())
    c_q3_sum = int(abs(c_tbl[c_tbl['Quadrant'].str.startswith('Q3') & c_clean]['OI_Chg_Short'].sum()))
    c_q4_sum = int(abs(c_tbl[c_tbl['Quadrant'].str.startswith('Q4') & c_clean]['OI_Chg_Short'].sum()))

    p_q1_sum = int(p_tbl[p_tbl['Quadrant'].str.startswith('Q1') & p_clean]['OI_Chg_Short'].sum())
    p_q2_sum = int(p_tbl[p_tbl['Quadrant'].str.startswith('Q2') & p_clean]['OI_Chg_Short'].sum())
    p_q3_sum = int(abs(p_tbl[p_tbl['Quadrant'].str.startswith('Q3') & p_clean]['OI_Chg_Short'].sum()))
    p_q4_sum = int(abs(p_tbl[p_tbl['Quadrant'].str.startswith('Q4') & p_clean]['OI_Chg_Short'].sum()))

    # 장기창(w_long) 4분면 합계
    c_q1_long = int(c_tbl[(c_tbl['Quad_Long'] == 'Q1') & c_clean]['OI_Chg_Long'].sum())
    c_q2_long = int(c_tbl[(c_tbl['Quad_Long'] == 'Q2') & c_clean]['OI_Chg_Long'].sum())
    c_q3_long = int(abs(c_tbl[(c_tbl['Quad_Long'] == 'Q3') & c_clean]['OI_Chg_Long'].sum()))
    c_q4_long = int(abs(c_tbl[(c_tbl['Quad_Long'] == 'Q4') & c_clean]['OI_Chg_Long'].sum()))

    p_q1_long = int(p_tbl[(p_tbl['Quad_Long'] == 'Q1') & p_clean]['OI_Chg_Long'].sum())
    p_q2_long = int(p_tbl[(p_tbl['Quad_Long'] == 'Q2') & p_clean]['OI_Chg_Long'].sum())
    p_q3_long = int(abs(p_tbl[(p_tbl['Quad_Long'] == 'Q3') & p_clean]['OI_Chg_Long'].sum()))
    p_q4_long = int(abs(p_tbl[(p_tbl['Quad_Long'] == 'Q4') & p_clean]['OI_Chg_Long'].sum()))

    # --------------------------------------------------------------------------
    # [연산 2-A] 최근 traj_days 영업일 일자별 레짐 확률 & 4분면 수급 궤적 산출 (4대 정제 규칙 동일 적용)
    # --------------------------------------------------------------------------
    traj_dates = all_dates[-traj_days:] if total_days >= traj_days else all_dates
    _hist_dates = all_dates[-max(traj_days, HIST_DAYS):]   # ★ [이력 블록] 궤적 연산만 HIST_DAYS 거래일까지 확장 (궤적표 출력은 traj_days 그대로)
    traj_rows = []
    for d_idx_pos, d_t in enumerate(all_dates):
        if d_t not in _hist_dates:
            continue
        sub_dates_upto_t = all_dates[:d_idx_pos + 1]
        d_p1 = get_base_date_for_window(sub_dates_upto_t, 1)
        d_sh = get_base_date_for_window(sub_dates_upto_t, w_short)
        d_lg = get_base_date_for_window(sub_dates_upto_t, w_long)

        lb_15 = sub_dates_upto_t[-15:] if len(sub_dates_upto_t) >= 15 else sub_dates_upto_t
        sp_ser = df_pit[df_pit['Quote Date'].isin(lb_15)].groupby('Quote Date')['EWY Price'].first()
        pk_dt = sp_ser.idxmax()
        sp_curr = float(sp_ser.loc[d_t])
        sp_prev = float(df_pit[df_pit['Quote Date'] == d_p1]['EWY Price'].iloc[0])
        sp_chg  = (sp_curr / sp_prev - 1.0) * 100.0 if d_idx_pos >= 1 else 0.0

        sub_s = df_pit[(df_pit['Quote Date'] >= min(pk_dt, d_sh)) & (df_pit['Quote Date'] <= d_t) & (df_pit['Expiration Date'] >= d_t)]
        act_ex = sorted(sub_s[sub_s['Quote Date'] == d_t]['Expiration Date'].unique())
        fut_ex = [e for e in act_ex if e > d_t]
        nr_ex = fut_ex[0] if len(fut_ex) > 0 else (act_ex[0] if len(act_ex) > 0 else d_t)

        mp_nr = calc_max_pain(sub_s[(sub_s['Quote Date'] == d_t) & (sub_s['Expiration Date'] == nr_ex)])

        nr_puts = sub_s[(sub_s['Expiration Date'] == nr_ex) & (sub_s['Option Type'] == 'Put')].groupby('Quote Date')['Open Interest'].sum()
        nr_oi_chg_s = int(nr_puts.get(d_t, 0)) - int(nr_puts.get(d_sh, nr_puts.get(d_t, 0)))

        ct_d = build_quadrant_table_for_dates(sub_s, d_t, d_p1, d_sh, d_lg, pk_dt, 'Call')
        pt_d = build_quadrant_table_for_dates(sub_s, d_t, d_p1, d_sh, d_lg, pk_dt, 'Put')

        cq1 = int(ct_d[ct_d['Quadrant'].str.startswith('Q1') & ct_d['Is_Clean_Contract']]['OI_Chg_Short'].sum())
        cq2 = int(ct_d[ct_d['Quadrant'].str.startswith('Q2') & ct_d['Is_Clean_Contract']]['OI_Chg_Short'].sum())
        pq1 = int(pt_d[pt_d['Quadrant'].str.startswith('Q1') & pt_d['Is_Clean_Contract']]['OI_Chg_Short'].sum())
        pq2 = int(pt_d[pt_d['Quadrant'].str.startswith('Q2') & pt_d['Is_Clean_Contract']]['OI_Chg_Short'].sum())
        pq34 = int(abs(pt_d[pt_d['Quadrant'].str.startswith('Q3') & pt_d['Is_Clean_Contract']]['OI_Chg_Short'].sum()) +
                   abs(pt_d[pt_d['Quadrant'].str.startswith('Q4') & pt_d['Is_Clean_Contract']]['OI_Chg_Short'].sum()))

        ts_c = ts_metrics.loc[d_t]
        ts_p = ts_metrics.loc[d_p1]

        # ★ [V4.1 205거래일 전수 백테스트 검증 5대 프랍 퀀트 알파 팩터 통합]
        # 1) 팩터 1 & 2: 당일/단기창 콜 거래량 점유율(Call_Vol_Share, 평균 IC +0.197) 및 10일 평균 대비 콜 거래량 서지(Call_Vol_Surge, 평균 IC +0.253 전체 1위)
        day_c_vol_d = float(ct_d['Vol_Latest'].sum())
        day_p_vol_d = float(pt_d['Vol_Latest'].sum())
        c_vol_share_1d = day_c_vol_d / max(day_c_vol_d + day_p_vol_d, 1.0)
        lb_10_dates = sub_dates_upto_t[-10:] if len(sub_dates_upto_t) >= 10 else sub_dates_upto_t
        avg_10d_c_vol = float(df_pit[(df_pit['Quote Date'].isin(lb_10_dates)) & (df_pit['Option Type'] == 'Call')].groupby('Quote Date')['Volume'].sum().mean())
        c_vol_surge_ratio = day_c_vol_d / max(avg_10d_c_vol, 1.0)
        dir_vol_surge = c_vol_surge_ratio * (1.0 if c_vol_share_1d >= 0.55 else (-1.0 if c_vol_share_1d <= 0.45 else 0.0))

        # ★ [V4.2.5 스케일 불변] 해당 일자(d_t)의 활성 총 OI 기준 동적 스케일 계수(_s_oi_d) 및 1,000계약 대응 단위(_unit_1k) 산출
        _tot_oi_d = float(ct_d['OI_Latest'].sum() + pt_d['OI_Latest'].sum())
        _s_oi_d   = float(np.clip(_tot_oi_d / 600000.0, 0.03, 1.00))
        _unit_1k  = 1000.0 * _s_oi_d

        # 2) 팩터 3: 수급 결합형 상단 감마 진공지대 가속 지수 (Active_Air_Pocket = 상단 OI 진공도 * 콜 수급 우위, 평균 IC +0.176)
        near_up_calls = ct_d.loc[(ct_d.index.get_level_values('Strike') >= sp_curr) & (ct_d.index.get_level_values('Strike') <= sp_curr * 1.04)]
        if len(near_up_calls) > 0:
            c_oi_by_strk_d = near_up_calls.groupby(level='Strike')['OI_Latest'].sum()
            cw_near_s = float(c_oi_by_strk_d.idxmax())
            cw_near_oi_v = float(c_oi_by_strk_d.max())
            air_Zone = ct_d.loc[(ct_d.index.get_level_values('Strike') > cw_near_s) & (ct_d.index.get_level_values('Strike') <= cw_near_s * 1.04)]
            if len(air_Zone) > 0 and cw_near_oi_v >= max(100.0, 2000.0 * _s_oi_d):
                air_avg_oi_v = float(air_Zone.groupby(level='Strike')['OI_Latest'].sum().mean())
                air_vac_ratio = max(0.0, 1.0 - (air_avg_oi_v / cw_near_oi_v))
            else:
                air_vac_ratio = 0.0
        else:
            air_vac_ratio = 0.0
        active_air_pocket_d = air_vac_ratio * max(0.0, c_vol_share_1d - 0.50) * 2.0

        # 3) 팩터 4: 외가격(OTM) 콜-풋 달러 거래대금 불균형 (OTM_DVol_Imb, T+10~20일 IC +0.228 ~ +0.379)
        c_otm_m = ct_d['Is_Clean_Contract'] & (ct_d.index.get_level_values('Strike') > sp_curr)
        p_otm_m = pt_d['Is_Clean_Contract'] & (pt_d.index.get_level_values('Strike') < sp_curr)
        c_otm_dvol = float((ct_d.loc[c_otm_m, 'Vol_ShortWin'] * np.maximum(ct_d.loc[c_otm_m, 'Price_Latest'], 0.05) * 100.0).sum())
        p_otm_dvol = float((pt_d.loc[p_otm_m, 'Vol_ShortWin'] * np.maximum(pt_d.loc[p_otm_m, 'Price_Latest'], 0.05) * 100.0).sum())
        otm_dvol_imb = (c_otm_dvol - p_otm_dvol) / max(c_otm_dvol + p_otm_dvol, 1.0)

        # 4) 팩터 5: 진성 상방 콜 매집 비중 (CQ1_Share, T+1~3일 IC +0.160) 및 풋 청산 바나 부스터 (PQ34)
        cq1_share_d = cq1 / max(cq1 + cq2, 1.0)

        cq3_d = int(abs(ct_d[ct_d['Quadrant'].str.startswith('Q3')]['OI_Chg_Short'].sum()))

        # ★ [V4.4] 레짐 점수: V4.3 '4대 레짐 상태 분리' 블록 이식 (V4.3은 라벨 구간에 맞춰 조정된 규칙이므로 채택 근거는 2024 비학습 기간 성적)
        sp_3d_d  = float(df_pit[df_pit['Quote Date'] == sub_dates_upto_t[max(0, len(sub_dates_upto_t)-4)]]['EWY Price'].iloc[0])
        sp_10d_d = float(df_pit[df_pit['Quote Date'] == sub_dates_upto_t[max(0, len(sub_dates_upto_t)-11)]]['EWY Price'].iloc[0])
        ret3_d   = (sp_curr / max(sp_3d_d, 1e-6) - 1.0) * 100.0
        ret10_d  = (sp_curr / max(sp_10d_d, 1e-6) - 1.0) * 100.0
        div1_d   = float((ts_c['Near_ATM_IV'] - ts_p['Near_ATM_IV']) * 100.0)
        tnb_d    = float(ts_c['Term_Near_Back'] * 100.0)

        is_crash_day_d  = (sp_chg <= -1.2) or (ret3_d <= -2.5 and sp_chg < 0.0)
        is_vanna_turn_d = (sp_chg >= -0.3) and (ret3_d >= -1.5 or div1_d <= -0.5)

        vol_surge_bull = max(0.0, (c_vol_share_1d - 0.45) * 35.0) + max(0.0, min(18.0, (dir_vol_surge - 1.0) * 10.0))
        vol_surge_bear = max(0.0, (0.48 - c_vol_share_1d) * 35.0) + max(0.0, min(18.0, (-dir_vol_surge - 1.0) * 10.0))
        air_pocket_bonus = min(16.0, active_air_pocket_d * 28.0)
        dvol_bull_bonus  = max(0.0, otm_dvol_imb * 16.0)
        dvol_bear_bonus  = max(0.0, -otm_dvol_imb * 16.0)

        # 1) 레짐 A (저점 매집 & 바나 리버설): 폭락 진행일(is_crash_day)에는 가짜 바나 가산점을 차단하고 반등/IV 진정 확인 시에만 점화
        vanna_term_pts = (min(20.0, tnb_d * 2.0) if (tnb_d > 0 and is_vanna_turn_d and not is_crash_day_d) else 0.0)
        vanna_pq34_pts = (min(14.0, (pq34 / _unit_1k) * 0.8) if (is_vanna_turn_d and not is_crash_day_d) else 0.0)
        bull_flow_pts  = min(26.0, (cq1 / _unit_1k) * 1.6) + min(20.0, (pq2 / _unit_1k) * 1.4) + vol_surge_bull + air_pocket_bonus + dvol_bull_bonus
        sa = 14.0 + bull_flow_pts + vanna_term_pts + vanna_pq34_pts
        if is_crash_day_d:
            sa *= 0.50

        # 2) 레짐 B (진성 매도 & 하방 가속): 롱풋(PQ1)·콜캡(CQ2)·콜청산(CQ3) 및 하락장 패닉/콘탱고 함정 에너지 집중
        bear_panic_pts = (min(22.0, max(0.0, tnb_d * 2.0) + max(0.0, div1_d * 1.8) + abs(min(0.0, sp_chg)) * 2.5) if is_crash_day_d else 0.0)
        if sp_chg <= -1.2 and tnb_d < 0:
            bear_panic_pts += 18.0
        bear_flow_pts  = min(28.0, (pq1 / _unit_1k) * 1.3) + min(18.0, (cq2 / _unit_1k) * 1.2) + min(14.0, (cq3_d / _unit_1k) * 1.0) + vol_surge_bear + dvol_bear_bonus + (10.0 if ts_c['Back_Skew_25D_pct'] >= 80.0 else 0.0)
        sb = 12.0 + bear_flow_pts + bear_panic_pts
        if sp_chg >= 1.0 and ret3_d >= 2.0 and cq1 >= cq2:
            sb *= 0.65

        # 3) 레짐 C (변동성 극대화 & 양방향 감마 폭발)
        sc = 10.0 + (15.0 if ts_c['Near_ATM_IV_pct'] >= 72.0 else 0.0) + (18.0 if (abs(div1_d) >= 4.5 or ts_c['Mid_Bfly_25D_pct'] >= 70.0) else 0.0) + (15.0 if (cq1 > int(round(5000 * _s_oi_d)) and pq1 > int(round(5000 * _s_oi_d))) else 0.0)

        # 4) 레짐 D (변동성 수축 & 가두리 횡보 박스권): 하락 일이 아닐 때만 작동하며 콘탱고 및 주가 진폭 수축 결합
        is_box_regime_d   = (not is_crash_day_d) and (abs(sp_chg) <= 2.2) and (abs(ret10_d) <= 8.5) and (tnb_d <= 0.8)
        contango_box_pts  = (28.0 if (tnb_d <= 0.0 and is_box_regime_d) else (15.0 if is_box_regime_d else 0.0))
        vol_crush_box_pts = (15.0 if (div1_d <= 0.3 and is_box_regime_d) else 0.0)
        cap_floor_pts     = (15.0 if (cq1_share_d <= 0.52 and is_box_regime_d) else 0.0)
        sd = 10.0 + contango_box_pts + vol_crush_box_pts + cap_floor_pts + (12.0 if (not is_crash_day_d and abs(sp_curr - mp_nr) / sp_curr <= 0.025) else 0.0)
        if is_crash_day_d or abs(sp_chg) >= 2.8 or abs(ret10_d) >= 11.0 or div1_d >= 2.5:
            sd *= 0.25

        t_sc = sa + sb + sc + sd
        pa = round(sa / t_sc * 100.0, 1)
        pb = round(sb / t_sc * 100.0, 1)
        pc = round(sc / t_sc * 100.0, 1)
        pd_v = round(100.0 - (pa + pb + pc), 1)
        top_reg = sorted([('레짐A', pa), ('레짐B', pb), ('레짐C', pc), ('레짐D', pd_v)], key=lambda x: x[1], reverse=True)[0]

        traj_rows.append({
            'Date': d_t,
            'Spot': sp_curr,
            'Chg': sp_chg,
            'PA': pa, 'PB': pb, 'PC': pc, 'PD': pd_v,
            'TopReg': f"{top_reg[0]}({top_reg[1]:.1f}%)",
            'CQ1': cq1, 'CQ2': cq2,
            'PQ1': pq1, 'PQ2': pq2, 'PQ34': pq34,
            'NearMP': mp_nr,
            'CallVolShare': c_vol_share_1d * 100.0,
            'CallVolSurge': c_vol_surge_ratio,
            'AirVacPct': air_vac_ratio * 100.0,
            'ActiveAirPocket': active_air_pocket_d,
            'OTMDVolImb': otm_dvol_imb * 100.0,
            'CQ1SharePct': cq1_share_d * 100.0
        })
    traj_df = pd.DataFrame(traj_rows)
    traj_df = traj_df.join(_ph_tbl[['PhU', 'PhD', 'PhS']], on='Date')  # ★ [V4.2.9] 궤적표 국면 확률
    hist_traj_df = traj_df.copy()                                               # ★ [이력 블록] HIST_DAYS 거래일 전체 보관
    traj_df = traj_df[traj_df['Date'].isin(traj_dates)].reset_index(drop=True)  # 이후 기존 로직은 traj_days 행만 사용 (출력 불변)

    # --------------------------------------------------------------------------
    # [연산 2-B] 당일(T) 미결산 기습 거래량 레이더 & Tier별 만기 클러스터 집계 (4대 정제 규칙 적용)
    # --------------------------------------------------------------------------
    piv_amb = surv_df[surv_df['Quote Date'].isin([prev1_date, latest_date])].pivot_table(
        index=['Option Type', 'Expiration Date', 'Strike'],
        columns='Quote Date',
        values=['Volume', 'Open Interest', 'Implied Volatility', 'Last Price', 'Bid', 'Ask', 'Delta', 'DTE'],
        aggfunc='first'
    )
    amb_df = pd.DataFrame({
        'Vol_Prev1': get_piv_series(piv_amb, 'Volume', prev1_date, 0.0),
        'Vol_Latest': get_piv_series(piv_amb, 'Volume', latest_date, 0.0),
        'OI_Prev1': get_piv_series(piv_amb, 'Open Interest', prev1_date, 0.0),
        'OI_Latest': get_piv_series(piv_amb, 'Open Interest', latest_date, 0.0),
        'IV_Prev1': get_piv_series(piv_amb, 'Implied Volatility', prev1_date, 0.0),
        'IV_Latest': get_piv_series(piv_amb, 'Implied Volatility', latest_date, 0.0),
        'Price_Latest': get_piv_series(piv_amb, 'Last Price', latest_date, 0.0),
        'Bid_Latest': get_piv_series(piv_amb, 'Bid', latest_date, 0.0),
        'Ask_Latest': get_piv_series(piv_amb, 'Ask', latest_date, 0.0),
        'Delta_Latest': get_piv_series(piv_amb, 'Delta', latest_date, 0.0),
        'DTE_Latest': get_piv_series(piv_amb, 'DTE', latest_date, 0.0),
    }).reset_index()

    # ★ [V4.3.3] 야후 미체결 스냅샷 이월(Stale) 판정: 체결이 없는 날에도 마지막 체결일의 거래량·종가가 그대로 복사되어 올라오므로,
    #   '거래량>0 이고 거래량·종가가 전 거래일과 모두 같으면' 당일 체결 없음(거래량 0)으로 처리 (전일 거래량도 전전일과 같은 방식으로 판정)
    _amb_key = ['Option Type', 'Expiration Date', 'Strike']
    prev2_date = all_dates[-3] if len(all_dates) >= 3 else None
    _p1_lp = surv_df[surv_df['Quote Date'] == prev1_date].drop_duplicates(_amb_key)[_amb_key + ['Last Price']].rename(columns={'Last Price': 'Price_Prev1'})
    amb_df = amb_df.merge(_p1_lp, on=_amb_key, how='left')
    if prev2_date is not None and prev2_date != prev1_date:
        _p2_vp = surv_df[surv_df['Quote Date'] == prev2_date].drop_duplicates(_amb_key)[_amb_key + ['Volume', 'Last Price']].rename(columns={'Volume': 'Vol_Prev2', 'Last Price': 'Price_Prev2'})
        amb_df = amb_df.merge(_p2_vp, on=_amb_key, how='left')
    else:
        amb_df['Vol_Prev2'] = np.nan
        amb_df['Price_Prev2'] = np.nan
    _pp1 = pd.to_numeric(amb_df['Price_Prev1'], errors='coerce').fillna(-1.0).values
    _pp2 = pd.to_numeric(amb_df['Price_Prev2'], errors='coerce').fillna(-2.0).values
    _vp2 = pd.to_numeric(amb_df['Vol_Prev2'], errors='coerce').fillna(-1.0).values
    amb_df['Stale_Latest'] = (amb_df['Vol_Latest'].values > 0) & (amb_df['Vol_Latest'].values == amb_df['Vol_Prev1'].values) & (amb_df['Price_Latest'].values > 0) & (np.abs(amb_df['Price_Latest'].values - _pp1) < 1e-6)
    amb_df['Stale_Prev1']  = (amb_df['Vol_Prev1'].values > 0) & (amb_df['Vol_Prev1'].values == _vp2) & (_pp1 > 0) & (np.abs(_pp1 - _pp2) < 1e-6)
    amb_df['Vol_Latest_Raw'] = amb_df['Vol_Latest'].values
    amb_df['Vol_Prev1_Raw']  = amb_df['Vol_Prev1'].values
    amb_df.loc[amb_df['Stale_Latest'], 'Vol_Latest'] = 0.0
    amb_df.loc[amb_df['Stale_Prev1'], 'Vol_Prev1'] = 0.0
    n_stale_latest = int(amb_df['Stale_Latest'].sum())
    n_stale_prev1  = int(amb_df['Stale_Prev1'].sum())

    amb_df['OI_Chg_1D'] = amb_df['OI_Latest'] - amb_df['OI_Prev1']
    amb_df['Spread_Ratio'] = np.where(
        amb_df['Ask_Latest'] > 0,
        (amb_df['Ask_Latest'] - amb_df['Bid_Latest']) / amb_df['Ask_Latest'],
        1.0
    )
    amb_df['Moneyness_Latest'] = (amb_df['Strike'] - latest_spot) / max(latest_spot, 1e-6)
    amb_df['OTM_Dist_Pct'] = np.where(
        amb_df['Option Type'] == 'Put',
        np.maximum(0.0, (latest_spot - amb_df['Strike']) / max(latest_spot, 1e-6)),
        np.maximum(0.0, (amb_df['Strike'] - latest_spot) / max(latest_spot, 1e-6))
    )
    amb_df['Max_Valid_OTM_Pct'] = calc_pseudo_delta_max_otm(amb_df['DTE_Latest'].values)

    # [규칙 1·2·3·4 통합] 당일 미결산 데이터의 고정 비율 행사가 보정(Rolling Strike Mapping) 및 유령호가 차단
    amb_df['Raw_IV_Chg_1D'] = np.where(
        (amb_df['IV_Prev1'] > 0.01) & (amb_df['IV_Latest'] > 0.01),
        amb_df['IV_Latest'] - amb_df['IV_Prev1'],
        0.0
    )
    if USE_ROLLING_STRIKE:
        roll_base_iv = np.zeros(len(amb_df))
        for (ot_val, exp_val), grp_idx in amb_df.groupby(['Option Type', 'Expiration Date']).groups.items():
            sub_p1 = surv_df[(surv_df['Quote Date'] == prev1_date) & (surv_df['Expiration Date'] == exp_val)]
            m_targets = amb_df.loc[grp_idx, 'Moneyness_Latest'].values
            roll_base_iv[grp_idx] = interpolate_rolling_iv_by_moneyness(sub_p1, m_targets, ot_val)
        amb_df['IV_Roll_Prev1'] = np.where(np.isfinite(roll_base_iv) & (roll_base_iv > 0.05), roll_base_iv, amb_df['IV_Prev1'])
        put_roll_diff = np.where(
            (amb_df['IV_Roll_Prev1'] > 0.01) & (amb_df['IV_Latest'] > 0.01),
            amb_df['IV_Latest'] - amb_df['IV_Roll_Prev1'],
            amb_df['Raw_IV_Chg_1D']
        )
        # Put은 주가 상승일 스마일 슬라이딩 거품만 제거하고, Call은 고정행사가 원시 IV 변동(조건부 바나 보정 포함)을 보존하여 클러스터 ΔIV 부호 왜곡 방지
        tot_c_vol_latest = float(amb_df.loc[amb_df['Option Type'] == 'Call', 'Vol_Latest'].sum())
        tot_p_vol_latest = float(amb_df.loc[amb_df['Option Type'] == 'Put', 'Vol_Latest'].sum())
        c_share_latest = tot_c_vol_latest / max(tot_c_vol_latest + tot_p_vol_latest, 1.0)
        atm_drop_1d = 0.80 * min(0.0, float(curr_ts['Near_ATM_IV'] - prev_ts['Near_ATM_IV'])) if (daily_chg_pct > 0 and c_share_latest >= 0.53) else 0.0
        _dq['radar'] = {'atm': float(curr_ts['Near_ATM_IV'] - prev_ts['Near_ATM_IV']) * 100.0, 'cshare': c_share_latest * 100.0, 'adj': bool(atm_drop_1d != 0.0)}   # ★ [V4.3.7]

        amb_df['IV_Chg_1D'] = np.where(
            amb_df['Option Type'] == 'Put',
            np.where((daily_chg_pct > 0) & (amb_df['Strike'] < latest_spot), np.minimum(amb_df['Raw_IV_Chg_1D'], put_roll_diff), amb_df['Raw_IV_Chg_1D']),
            amb_df['Raw_IV_Chg_1D'] - atm_drop_1d
        )
    else:
        amb_df['IV_Chg_1D'] = amb_df['Raw_IV_Chg_1D']

    amb_df['Rule2_Spread_Fail'] = eval_rule2_spread_fail(
        amb_df['Bid_Latest'].values, amb_df['Ask_Latest'].values, amb_df['Price_Latest'].values
    )
    amb_df['Is_Valid_Quote'] = (
        (amb_df['Vol_Latest'] >= YF_MIN_VOLUME_CUTOFF) &
        (~amb_df['Rule2_Spread_Fail']) &
        (amb_df['OTM_Dist_Pct'] <= amb_df['Max_Valid_OTM_Pct'])
    )
    # 유령호가/스프레드과다/초외가격 노이즈 구간에서 발생한 가짜 IV 상승은 0.0으로 강등
    amb_df['IV_Chg_1D'] = np.where(~amb_df['Is_Valid_Quote'] & (amb_df['IV_Chg_1D'] > 0), 0.0, amb_df['IV_Chg_1D'])
    amb_df['Vol_OI_Ratio'] = amb_df['Vol_Latest'] / np.maximum(np.maximum(amb_df['OI_Latest'], amb_df['OI_Prev1']), 1.0)   # ★ [V4.3.3] OI가 0으로 소멸(권리행사·청산)한 계약의 분모 1 대입 -> 가짜 회전율 방지

    # ★ [V4.1 핵심 추가] 블랙-숄즈 수리모델 기반 당일 미결산 계약별 실시간 델타(BS_Delta)·감마(BS_Gamma)·딜러 초동 강제 헤지 주식 수 산출
    amb_T_yr = np.maximum(amb_df['DTE_Latest'].values.astype(float) / 365.0, 1.0 / 365.0)
    amb_sig  = np.maximum(amb_df['IV_Latest'].values.astype(float), 0.15)
    amb_strk = np.maximum(amb_df['Strike'].values.astype(float), 1.0)
    amb_d1   = (np.log(latest_spot / amb_strk) + (0.048 + 0.5 * (amb_sig ** 2)) * amb_T_yr) / (amb_sig * np.sqrt(amb_T_yr))
    amb_bs_delta = np.where(amb_df['Option Type'].values == 'Call', stats.norm.cdf(amb_d1), stats.norm.cdf(amb_d1) - 1.0)
    amb_bs_gamma = stats.norm.pdf(amb_d1) / (latest_spot * amb_sig * np.sqrt(amb_T_yr))
    amb_df['BS_Delta'] = amb_bs_delta
    amb_df['BS_Gamma'] = amb_bs_gamma
    # 딜러 초동 헤지 주식 수 = 거래량 * 100 * |BS_Delta| (기습 풋매수/콜매도는 음(-)의 매도 헤지, 기습 콜매수/풋매도는 양(+)의 매수 헤지)
    amb_df['Hedge_Shares_Abs'] = amb_df['Vol_Latest'].values.astype(float) * 100.0 * np.abs(amb_bs_delta)

    amb_signals = []
    for _, r in amb_df.iterrows():
        ot = r['Option Type']
        div = r['IV_Chg_1D']
        valid_q = bool(r['Is_Valid_Quote'])
        if ot == 'Put':
            if div >= 0.005 and valid_q:
                amb_signals.append("🚨 당일 기습 하방공습/풋매집 (Unsettled Long Put)")
            elif div <= -0.005:
                amb_signals.append("🛡️ 당일 기습 풋매도/수익화청산 (Unsettled Put Write/Close)")
            else:
                amb_signals.append("⚡ 당일 대량 풋교체/중립거래 (Unsettled Put Turnover)")
        else:
            if div >= 0.005 and valid_q:
                amb_signals.append("🔥 당일 기습 상방매집/콜숏커버 (Unsettled Long Call)")
            elif div <= -0.005:
                amb_signals.append("🧱 당일 기습 상단캡 커버드콜 (Unsettled Call Overwriting)")
            else:
                amb_signals.append("⚡ 당일 대량 콜교체/중립거래 (Unsettled Call Turnover)")
    amb_df['Intraday_Signal'] = amb_signals

    _amb_min_vol  = max(10, int(round(150 * s_vol)))
    _amb_high_vol = max(30, int(round(500 * s_vol)))
    top_ambush = amb_df[
        amb_df['Is_Valid_Quote'] &
        (amb_df['Vol_Latest'] >= _amb_min_vol) &
        ((amb_df['Vol_OI_Ratio'] >= 0.25) | (amb_df['Vol_Latest'] >= _amb_high_vol))
    ].sort_values(by='Vol_Latest', ascending=False).head(12)

    # [규칙 1·2·3·4가 모두 적용된 클러스터 레이더]
    near_cluster_sub = amb_df[
        amb_df['Is_Valid_Quote'] &
        (amb_df['DTE_Latest'] >= 1) &
        (amb_df['DTE_Latest'] <= cluster_dte) &
        (amb_df['Strike'] >= latest_spot * 0.85) &
        (amb_df['Strike'] <= latest_spot * 1.15)
    ].copy()

    cluster_list = []
    if len(near_cluster_sub) > 0:
        for (exp_d, ot), grp in near_cluster_sub.groupby(['Expiration Date', 'Option Type']):
            mid_p = np.where((grp['Bid_Latest'] > 0) & (grp['Ask_Latest'] > 0),
                             0.5 * (grp['Bid_Latest'] + grp['Ask_Latest']), grp['Price_Latest'])
            w = (grp['Vol_Latest'] * np.maximum(mid_p, 0.10)) + 1.0
            cluster_list.append({
                'Exp': exp_d,
                'Type': ot,
                'Active_Strikes': int((grp['Vol_Latest'] >= max(3, int(round(20 * s_vol)))).sum()),
                'Vol_Prev1': int(grp['Vol_Prev1'].sum()),
                'Vol_Latest': int(grp['Vol_Latest'].sum()),
                'OI_Latest': int(grp['OI_Latest'].sum()),
                'OI_Chg_1D': int(grp['OI_Chg_1D'].sum()),
                'W_IV_Latest': safe_weighted_avg(grp['IV_Latest'], w),
                'W_IV_Chg_1D': safe_weighted_avg(grp['IV_Chg_1D'], w)
            })
    cluster_df = pd.DataFrame(cluster_list)

    # --------------------------------------------------------------------------
    # [연산 3] 행사가별 Call Wall vs Put Wall 지형도 (단기창 증감 & 장기창 증감 동시 산출)
    # --------------------------------------------------------------------------
    latest_surv = surv_df[surv_df['Quote Date'] == latest_date]
    mp_nearest = calc_max_pain(latest_surv[latest_surv['Expiration Date'] == nearest_exp])
    mp_all     = calc_max_pain(latest_surv)

    call_by_strk = surv_df[surv_df['Option Type'] == 'Call'].groupby(['Quote Date', 'Strike'])['Open Interest'].sum().unstack(level=0).ffill(axis=1).fillna(0.0)
    put_by_strk  = surv_df[surv_df['Option Type'] == 'Put'].groupby(['Quote Date', 'Strike'])['Open Interest'].sum().unstack(level=0).ffill(axis=1).fillna(0.0)

    wall_map = pd.DataFrame({
        'Call_OI_Latest': call_by_strk.get(latest_date, 0.0),
        'Call_Chg_Short': call_by_strk.get(latest_date, 0.0) - call_by_strk.get(short_date, 0.0),
        'Call_Chg_Long': call_by_strk.get(latest_date, 0.0) - call_by_strk.get(long_date, 0.0),
        'Put_OI_Latest': put_by_strk.get(latest_date, 0.0),
        'Put_Chg_Short': put_by_strk.get(latest_date, 0.0) - put_by_strk.get(short_date, 0.0),
        'Put_Chg_Long': put_by_strk.get(latest_date, 0.0) - put_by_strk.get(long_date, 0.0),
        'Put_Chg_Peak': put_by_strk.get(latest_date, 0.0) - put_by_strk.get(peak_date, 0.0),
    }).fillna(0.0)
    wall_map['Net_Put_Minus_Call'] = wall_map['Put_OI_Latest'] - wall_map['Call_OI_Latest']

    upper_calls = wall_map.loc[(wall_map.index > latest_spot) & (wall_map.index <= latest_spot * 1.30)].sort_values(by='Call_OI_Latest', ascending=False)
    if len(upper_calls) >= 2:
        # OI 상위 2개 저항벽을 뽑되, 현가에서 가까운 행사가를 1차 목표가, 먼 행사가를 2차 목표가로 거리순 정렬
        _top2_cw = sorted([float(upper_calls.index[0]), float(upper_calls.index[1])])
        call_wall_1st, call_wall_2nd = _top2_cw[0], _top2_cw[1]
        call_wall_1st_oi = int(wall_map.loc[call_wall_1st, 'Call_OI_Latest'])
        call_wall_2nd_oi = int(wall_map.loc[call_wall_2nd, 'Call_OI_Latest'])
    elif len(upper_calls) == 1:
        call_wall_1st = float(upper_calls.index[0])
        call_wall_1st_oi = int(upper_calls['Call_OI_Latest'].iloc[0])
        call_wall_2nd, call_wall_2nd_oi = round(latest_spot * 1.15, 1), 0
    else:
        call_wall_1st, call_wall_1st_oi = round(latest_spot * 1.08, 1), 0
        call_wall_2nd, call_wall_2nd_oi = round(latest_spot * 1.15, 1), 0

    near_puts_below = wall_map.loc[(wall_map.index < latest_spot) & (wall_map.index >= latest_spot * 0.94)].sort_values(by='Put_OI_Latest', ascending=False)
    put_bunker_1st = float(near_puts_below.index[0]) if len(near_puts_below) > 0 else round(latest_spot * 0.97, 1)
    put_bunker_1st_oi = int(near_puts_below['Put_OI_Latest'].iloc[0]) if len(near_puts_below) > 0 else 0

    # 기존 범위(0.85~현가)를 그대로 유지하되, 1차 방어선과 동일한 행사가 중복 선택만 제외
    core_puts_below = wall_map.loc[(wall_map.index <= latest_spot) & (wall_map.index >= latest_spot * 0.85) & (wall_map.index != put_bunker_1st)].sort_values(by='Put_OI_Latest', ascending=False)
    put_bunker_core = float(core_puts_below.index[0]) if len(core_puts_below) > 0 else put_bunker_1st
    put_bunker_core_oi = int(core_puts_below['Put_OI_Latest'].iloc[0]) if len(core_puts_below) > 0 else put_bunker_1st_oi

    q1_puts_below = p_tbl[(p_tbl['Quadrant'].str.startswith('Q1')) & (p_tbl.index.get_level_values('Strike') < latest_spot)].sort_values(by='OI_Chg_Short', ascending=False)
    if len(q1_puts_below) > 0:
        neg_gamma_exp, neg_gamma_strike = q1_puts_below.index[0]
        neg_gamma_chg = int(q1_puts_below['OI_Chg_Short'].iloc[0])
    else:
        neg_gamma_exp, neg_gamma_strike, neg_gamma_chg = nearest_exp, put_bunker_core - 5.0, 0

    q1_puts_near_spot = p_tbl[
        (p_tbl['Quadrant'].str.startswith('Q1')) &
        (p_tbl.index.get_level_values('Strike') < latest_spot) &
        (p_tbl.index.get_level_values('Strike') >= latest_spot * 0.85)
    ].sort_values(by='OI_Chg_Short', ascending=False)
    if len(q1_puts_near_spot) > 0:
        near_ng_exp, near_ng_strike = q1_puts_near_spot.index[0]
        near_ng_chg = int(q1_puts_near_spot['OI_Chg_Short'].iloc[0])
        near_ng_bep = float(near_ng_strike - q1_puts_near_spot['Price_Latest'].iloc[0])
    else:
        near_ng_exp, near_ng_strike, near_ng_chg, near_ng_bep = neg_gamma_exp, put_bunker_core, 0, put_bunker_core - 5.0

    # ★ [V4.3.4] 포지티브 감마 방석: 현가 -15% 이내 Q2(풋 매도) 신규 물량 최대 계약 — 고객 풋 매도 = 딜러 풋 매수(롱감마) -> 하락 시 딜러 저가 매수 헤지
    q2_puts_near_spot = p_tbl[
        (p_tbl['Quadrant'].str.startswith('Q2')) &
        (p_tbl.index.get_level_values('Strike') < latest_spot) &
        (p_tbl.index.get_level_values('Strike') >= latest_spot * 0.85)
    ].sort_values(by='OI_Chg_Short', ascending=False)
    if len(q2_puts_near_spot) > 0:
        pos_gc_exp, pos_gc_strike = q2_puts_near_spot.index[0]
        pos_gc_chg = int(q2_puts_near_spot['OI_Chg_Short'].iloc[0])
        pos_gc_bep = float(pos_gc_strike - q2_puts_near_spot['Price_Latest'].iloc[0])
    else:
        pos_gc_exp, pos_gc_strike, pos_gc_chg, pos_gc_bep = None, None, 0, None

    prob_a = traj_df.iloc[-1]['PA']
    prob_b = traj_df.iloc[-1]['PB']
    prob_c = traj_df.iloc[-1]['PC']
    prob_d = traj_df.iloc[-1]['PD']
    prev_prob_c = traj_df.iloc[-2]['PC'] if len(traj_df) >= 2 else prob_c

    regime_ranking = sorted([
        ("레짐 A [저점 매집 & 바나 리버설 세팅]", prob_a),
        ("레짐 B [진성 매도 & 하방 가속(Roll-Down)]", prob_b),
        ("레짐 C [변동성 극대화 & 양방향 감마 폭발]", prob_c),
        ("레짐 D [변동성 수축 & 가두리 핀닝(Pinning)]", prob_d)
    ], key=lambda x: x[1], reverse=True)

    # --------------------------------------------------------------------------
    # [연산 4] AI 추론 한계점 검증 및 반대 시나리오(Devil's Advocate) 정량 지표 산출
    # --------------------------------------------------------------------------
    _flip_min_oi = max(20, int(round(300 * s_oi)))
    c_sign_flip = c_tbl[(c_tbl['OI_Chg_Short'] > _flip_min_oi) & ((c_tbl['Eff_IV_Chg'] * c_tbl['IV_Chg_1D']) < -0.0001)].sort_values(by='OI_Chg_Short', ascending=False)
    p_sign_flip = p_tbl[(p_tbl['OI_Chg_Short'] > _flip_min_oi) & ((p_tbl['Eff_IV_Chg'] * p_tbl['IV_Chg_1D']) < -0.0001)].sort_values(by='OI_Chg_Short', ascending=False)

    flip_examples = []
    for (ed, st), r in c_sign_flip.head(3).iterrows():
        flip_examples.append(f"Call {ed} ${st:.1f}(+{int(r['OI_Chg_Short']):,}계약: 체결일IV {r['Eff_IV_Chg']*100:+.2f}%p vs 당일IV {r['IV_Chg_1D']*100:+.2f}%p)")
    for (ed, st), r in p_sign_flip.head(3).iterrows():
        flip_examples.append(f"Put {ed} ${st:.1f}(+{int(r['OI_Chg_Short']):,}계약: 체결일IV {r['Eff_IV_Chg']*100:+.2f}%p vs 당일IV {r['IV_Chg_1D']*100:+.2f}%p)")
    flip_summary_str = " / ".join(flip_examples[:4]) if flip_examples else "해당 기준일 주요 상위 계약 중 심각한 IV 부호 역전 없음"

    # ★ [V4.3.4] 체결일 귀속 보정 진단: 기존(창 전체 IV) 방식이었다면 분면이 뒤바뀌었을 계약
    def _qcode(_tb, _col):
        _d = _tb['OI_Chg_Short'].values.astype(float); _e = _tb[_col].values.astype(float)
        return np.where(_d > 0, np.where(_e > 0.002, 1, 2), np.where((_d < 0) & (_e < -0.002), 3, 4))
    def _reclass(_tb):
        if len(_tb) == 0 or 'Eff_IV_Chg_Window' not in _tb.columns:
            return _tb.iloc[0:0]
        _mk = _tb['Is_Clean_Contract'].astype(bool).values & (np.abs(_tb['OI_Chg_Short'].values) > _flip_min_oi) & (_qcode(_tb, 'Eff_IV_Chg') != _qcode(_tb, 'Eff_IV_Chg_Window'))
        return _tb[_mk].sort_values(by='OI_Chg_Short', key=np.abs, ascending=False)
    c_reclass, p_reclass = _reclass(c_tbl), _reclass(p_tbl)
    reclass_examples = []
    for _lbl, _tb in (('Put', p_reclass), ('Call', c_reclass)):
        for (ed, st), r in _tb.head(2).iterrows():
            _qo = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}[int(_qcode(_tb.loc[[(ed, st)]], 'Eff_IV_Chg_Window')[0])]
            reclass_examples.append(f"{_lbl} {ed} ${st:.1f}({int(r['OI_Chg_Short']):+,}계약: 체결일IV {r['Eff_IV_Chg']*100:+.2f}%p -> {str(r['Quadrant'])[:2]} / 창IV {r['Eff_IV_Chg_Window']*100:+.2f}%p였다면 {_qo})")
    reclass_summary_str = " / ".join(reclass_examples[:4]) if reclass_examples else "해당 없음"

    # ★ [V4.2.7 보완] 원시(필터링 전) Q1 풋 / Q2 콜 총합 대비 초외가격(±20% 밖) 거품 비중(0~100%)과 실전 근접 정제 물량(p_q1_sum / c_q2_sum) 정합성 일치
    p_q1_deep_otm = int(p_tbl[(p_tbl['OI_Chg_Short'] > 0) & (p_tbl['Eff_IV_Chg'] > 0.002) & (p_tbl.index.get_level_values('Strike') < latest_spot * 0.80)]['OI_Chg_Short'].sum())
    p_q1_raw_tot  = p_q1_sum + p_q1_deep_otm
    p_q1_deep_pct = (p_q1_deep_otm / max(p_q1_raw_tot, 1)) * 100.0

    c_q2_deep_otm = int(c_tbl[(c_tbl['Quadrant'].str.startswith('Q2')) & (~c_tbl['Rule4_MultiLeg_Fail']) & (c_tbl.index.get_level_values('Strike') > latest_spot * 1.20)]['OI_Chg_Short'].sum())
    c_q2_raw_tot  = c_q2_sum + c_q2_deep_otm
    c_q2_deep_pct = (c_q2_deep_otm / max(c_q2_raw_tot, 1)) * 100.0

    cq1_first, cq1_last = int(traj_df.iloc[0]['CQ1']), int(traj_df.iloc[-1]['CQ1'])
    pq2_first, pq2_last = int(traj_df.iloc[0]['PQ2']), int(traj_df.iloc[-1]['PQ2'])
    cq1_trend_pct = ((cq1_last / max(cq1_first, 1)) - 1.0) * 100.0

    # ==========================================================================
    # 텍스트 리포트 조립
    # ==========================================================================
    lines = []
    sep_bold = "=" * 124
    sep_thin = "-" * 124

    mode_tag = f"타임머신 과거시점 고정 ({latest_date})" if pit_meta['is_historical_mode'] else f"최신 거래일 기준 ({latest_date})"
    block_info = (f"{latest_date} 이후 미래 데이터 {pit_meta['blocked_days_count']}거래일({pit_meta['blocked_rows']:,}행) 원천 차단됨"
                  if pit_meta['blocked_rows'] > 0 else f"{latest_date} 이후 미래 데이터 없음 (시점 무결성 100%)")

    lines.append(build_tier_embedded_prompt(t_cfg, view_version=view_version).strip())
    lines.append("")
    lines.append(sep_bold)
    lines.append(f" [첨부 정량 데이터북 시작] EWY 옵션 미시구조 4대 전략 판독 데이터북 (V4.4 — {t_cfg['name']})")
    lines.append(sep_bold)
    lines.append(" [선택된 분석 Tier 프로필 (보고서 섹션 0 작성용 핵심 메타데이터)]")
    lines.append(f" • 선택된 분석 Tier : {t_cfg['name']}")
    lines.append(f" • Tier 분석 시계   : {t_cfg['horizon_str']} (궤적표: 최근 {traj_days}영업일 / 변동성곡면: 최근 {vol_ts_days}거래일 / 회귀: {rel_info['n_obs']}거래일)")
    lines.append(f" • Tier 핵심 강점   : {t_cfg['strengths']}")
    lines.append(f" • Tier 약점/한계   : {t_cfg['weaknesses']}")
    lines.append(f" • Tier 활용 목적   : {t_cfg['purpose']}")
    lines.append(sep_thin)
    lines.append(f" • 분석 실행 일시   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f" • 분석 기준 시점   : {mode_tag} [선택/입력값: {pit_meta['requested_date']}]")
    lines.append(f" • 미래참조 방어    : {block_info} (Expanding Rank & Past-Only FFill 적용)")
    lines.append(f" • 병합 대상 파일   : 총 {len(loaded_files)}개 CSV ({', '.join(loaded_files[:3])}{' 외' if len(loaded_files)>3 else ''})")
    lines.append(f" • 유효 데이터기간  : {first_date} ~ {latest_date} (총 {total_days}거래일 / 고유 계약-일자 {len(df_pit):,}건)")
    ewy_anchor_ref = float(rel_info.get('ewy_anchor_ref', latest_spot))
    has_ats_input  = bool(rel_info.get('has_ats_input', False))
    is_post_us_ovr = bool(rel_info.get('is_post_us_override', False))
    implied_krx_kospi = derive_target_fn(latest_spot, 'KOSPI')
    implied_krx_sam   = int(round(derive_target_fn(latest_spot, 'SAMSUNG'), -2))
    implied_krx_fx    = derive_target_fn(latest_spot, 'USDKRW')
    _fx_r2 = float(fm.get('r2_pearson', 0.0) or 0.0)   # ★ [V4.3.7] 환율 회귀 R² 50% 미만이면 내재 환율을 쓰지 않음(원거리 환산 규칙과 통일)
    _fx_ok = _fx_r2 >= 0.5
    _fx_s = f"내재 환율 {implied_krx_fx:,.1f}원" if _fx_ok else f"환율 {CURRENT_USDKRW:,.1f}원(15:30 값 유지 · 환율 회귀 R² {_fx_r2 * 100:.0f}%로 낮아 내재 환율 미표시)"
    _fx_s6 = f"환율 {implied_krx_fx:>6.1f}원" if _fx_ok else "환율 미표시(R² 낮음)"
    _dq['fx_r2'] = _fx_r2
    overnight_us_gap_pct = (latest_spot / max(ewy_anchor_ref, 1e-6) - 1.0) * 100.0

    lines.append(f" • EWY 미국본장종가 : ${latest_spot:.2f} (전일비 {daily_chg_pct:+.2f}% / 단기 고점 {peak_date} ${peak_spot:.2f} 대비 {drawdown_pct:+.2f}%)")
    lines.append(f" • 동시간대영점원점 : EWY 기준원점 ${ewy_anchor_ref:.2f} ↔ KOSPI {CURRENT_KOSPI_PT:,.1f}pt / 삼성전자 {CURRENT_SAMSUNG_KRW:,}원 / 원달러 {CURRENT_USDKRW:,.1f}원 ({rel_info['queried_time_info']})")
    if has_ats_input and (not is_post_us_ovr):
        lines.append(f" • 09시내재공정시가 : 밤사이 미국장 순변동({overnight_us_gap_pct:+.2f}%, ${ewy_anchor_ref:.2f}->${latest_spot:.2f}) 반영 -> 내재 KOSPI {implied_krx_kospi:,.1f}pt / 내재 삼성전자 {implied_krx_sam:,}원 / {_fx_s}")
    elif has_ats_input and is_post_us_ovr:
        post_gap_pct = (ewy_anchor_ref / max(latest_spot, 1e-6) - 1.0) * 100.0
        trapped_calls = int(wall_map.loc[(wall_map.index > latest_spot) & (wall_map.index <= ewy_anchor_ref), 'Call_OI_Latest'].sum()) if ewy_anchor_ref > latest_spot else 0
        lines.append(f" • 주간장오버라이드 : 미국종가(${latest_spot:.2f}) 대비 현재 EWY ATS(${ewy_anchor_ref:.2f}, {post_gap_pct:+.2f}%) 장외 돌파 -> 포위된 콜 저항벽 {trapped_calls:,}계약이 딜러 강제 숏커버 연료로 전환!")
    lines.append(sep_bold)
    lines.append("")

    # [섹션 1-1 & 1-2]
    lines.append(f"## [섹션 1] 월가 4대 전략 레짐 판독 및 최근 {traj_days}영업일 수급 모멘텀 궤적 매트릭스 ({t_cfg['short_tag']})")
    lines.append(sep_thin)
    lines.append("### (1-1) 기준일(T) 월가 4대 전략 레짐 정량 검증 요약")
    lines.append(f" • 1순위 지배 전략 : {regime_ranking[0][0]} (확률 {regime_ranking[0][1]:.1f}%)")
    lines.append(f" • 2순위 경계 전략 : {regime_ranking[1][0]} (확률 {regime_ranking[1][1]:.1f}%)")
    lines.append("")
    lines.append(f" [레짐 A] 저점 매집 및 바나 리버설 세팅 (Shakeout & Accumulation)       | 산출 확률: {prob_a:>5.1f}%")
    lines.append(f"   - 핵심 수치 : 근월-원월 백워데이션 {curr_ts['Term_Near_Back']*100:+.2f}%p ({curr_ts['Term_Near_Back_pct']:.1f}%ile) / "
                 f"Q2 바닥방어 풋매도 {w_short}일 +{p_q2_sum:,}계약({w_long}일 +{p_q2_long:,}) / Q1 진성 콜매수 {w_short}일 +{c_q1_sum:,}계약({w_long}일 +{c_q1_long:,}) / "
                 f"{nearest_exp} 만기 풋 {near_exp_oi_chg_s:+,}계약")
    lines.append("")
    lines.append(f" [레짐 B] 진성 매도 및 하방 가속 전략 (Distribution & Bear Attack)      | 산출 확률: {prob_b:>5.1f}%")
    lines.append(f"   - 핵심 수치 : Q1 하방베팅 풋매수 {w_short}일 +{p_q1_sum:,}계약({w_long}일 +{p_q1_long:,}) / "
                 f"Q2 상단억제 커버드콜 매도 {w_short}일 +{c_q2_sum:,}계약({w_long}일 +{c_q2_long:,}) / 원월 25D Put Skew {curr_ts['Back_Skew_25D']*100:+.2f}%p ({curr_ts['Back_Skew_25D_pct']:.1f}%ile)")
    lines.append("")
    lines.append(f" [레짐 C] 변동성 극대화 및 양방향 감마 폭발 전략 (Volatility Breakout)   | 산출 확률: {prob_c:>5.1f}%")
    lines.append(f"   - 핵심 수치 : 근월 ATM IV {curr_ts['Near_ATM_IV']*100:.2f}% ({curr_ts['Near_ATM_IV_pct']:.1f}%ile) / "
                 f"중기 25D Butterfly {curr_ts['Mid_Bfly_25D']*100:+.2f}%p ({curr_ts['Mid_Bfly_25D_pct']:.1f}%ile) / "
                 f"양방향 동시 매수(Q1 Call +{c_q1_sum:,} & Q1 Put +{p_q1_sum:,})")
    lines.append("")
    lines.append(f" [레짐 D] 변동성 수축 및 가두리 핀닝 전략 (Vol-Crush & Pinning)         | 산출 확률: {prob_d:>5.1f}%")
    lines.append(f"   - 핵심 수치 : 최근접 만기({nearest_exp}) Max Pain ${mp_nearest:.1f} (현가 괴리 {(mp_nearest/latest_spot-1)*100:+.2f}%) / "
                 f"전체 잔존 만기 Max Pain ${mp_all:.1f} / 상단 Call매도(Q2 +{c_q2_sum:,}) & 하단 Put매도(Q2 +{p_q2_sum:,})")
    lines.append("")
    # ★ [V4.2.9] 국면 판정 & 급락 위험도 (라벨 학습·검증)
    _ph_t = _ph_tbl.loc[latest_date]
    _ph_p = {'U': float(_ph_t['PhU']), 'D': float(_ph_t['PhD']), 'S': float(_ph_t['PhS'])}
    _ph_top = max(_ph_p, key=_ph_p.get)
    _ph_kr = {'U': '상승', 'D': '하락', 'S': '횡보'}
    _ph_prev = traj_df.iloc[-4] if len(traj_df) >= 4 else traj_df.iloc[0]
    _rk = float(_ph_t['Risk']) if np.isfinite(_ph_t['Risk']) else 0.5
    _rk_lv = '상' if _rk >= 2.0 / 3.0 else ('중' if _rk >= 1.0 / 3.0 else '하')
    _rs = PHASE_REL['risk']; _cv = PHASE_MODEL['cv']
    lines.append(" [V4.4 국면 판정] 확정 라벨 20개 구간(2025-03-17~2026-11-05, 경계 = 실제 종가 고점·저점)으로 학습한 '현재 국면' 인식 지표")
    lines.append(f"   - 국면 확률 : 상승(U) {_ph_p['U']:.1f}% | 하락(D) {_ph_p['D']:.1f}% | 횡보(S) {_ph_p['S']:.1f}% -> 1순위 [{_ph_kr[_ph_top]} 국면] ({_ph_prev['Date']} {_ph_kr[_ph_top]} {float(_ph_prev['Ph' + _ph_top]):.1f}% -> {latest_date} {_ph_p[_ph_top]:.1f}%)")
    lines.append(f"   - 판정 근거 : 15일 고점 대비 {_ph_t['p_dd15']*100:+.1f}% · 15일 저점 대비 {_ph_t['p_ru15']*100:+.1f}% (20일 실현변동성 {_ph_t['p_rv20']*100:.0f}%로 나눈 값 {_ph_t['p_dd15n']:+.2f} / {_ph_t['p_ru15n']:+.2f}) · 20일 범위 내 위치 {_ph_t['p_pos20']*100:.0f}% · IV 스트레스 {_ph_t['c_stress']:+.2f} (0 = 라벨 기간 평균)")
    lines.append(f"   - 검증 : 라벨 기간 구간 제외 교차검증 균형정확도 {_cv['loso']:.0f}% (2025<->2026 교차 {_cv['year']:.0f}%) vs 20일선 {_cv['ma20']:.0f}% · 레짐 1순위 {_cv['reg']:.0f}% | 2024 비학습 기간(종가 8% 되돌림 대리 라벨) 상승/하락 {_cv['ho_phase']:.0f}% vs 20일선 {_cv['ho_ma']:.0f}% | 전환 감지 지연 중앙값 {_cv['lag']:.0f}영업일 | 미래 수익률 예측 근거로 사용 금지")
    lines.append(f" [V4.4 급락 위험도] 풋/콜 OI 비율 120영업일 백분위 {_ph_t['PcoiPct']*100:.0f}% + 근월 25D 스큐 백분위 {_ph_t['o_skn_pct']*100:.0f}% -> 평균 {_rk:.2f} = [{_rk_lv}]")
    lines.append(f"   - 과거 빈도(10영업일 안에 종가 대비 -5% 이상 하락): 상 {_rs['상']}% · 중 {_rs['중']}% · 하 {_rs['하']}% (기저 {_rs['base']}%, 2024-04~2026-11 {_rs['n']}일 · 2024 비학습 기간에서도 상>중>하 유지) | 시점 신호가 아닌 위험 수준 지표")
    lines.append("")
    lines.append(f"### (1-2) [Tier 맞춤형 추세] 최근 {traj_days}영업일 전략 레짐 확률 및 4분면(Q1~Q4, {w_short}D 기준) 수급 모멘텀 궤적표")
    lines.append(f" 📌 [표 핵심 독해 가이드] ① Call_Q1(상승 로켓 연료)이 최근 연속 증가(충전) 중인지 감소(연료 고갈) 중인지 먼저 확인하고, ② Call_Q2(머리 위 천장 뚜껑)와 Put_Q2(바닥 현금 방석)의 크기를 비교하십시오. ③ 주가가 오른 날 레짐C(감마폭발 경보)가 갑자기 1.5~2배로 뛰면 시한폭탄 설치 신호입니다.")
    lines.append(f"{'일자(Date)':<11} | {'EWY종가(등락)':>15} | {'레짐A':>6} | {'레짐B':>6} | {'레짐C':>6} | {'레짐D':>6} | {'1순위지배레짐':<13} | {'국면(1순위)':<8} | {f'Call_Q1({w_short}D)':>11} | {f'Call_Q2({w_short}D)':>11} | {f'Put_Q1({w_short}D)':>11} | {f'Put_Q2({w_short}D)':>11} | {'Put청산(Q3+4)':>12} | {'단기MP':>6}")
    lines.append("-" * 177)
    def _ph_cell(_tr):
        _c = [(n_, float(_tr.get(k_, np.nan))) for n_, k_ in (('상승', 'PhU'), ('하락', 'PhD'), ('횡보', 'PhS'))]
        _c = [x for x in _c if np.isfinite(x[1])]
        return (max(_c, key=lambda x: x[1])[0] + f"{max(_c, key=lambda x: x[1])[1]:.0f}%") if _c else '-'
    for _, tr in traj_df.iterrows():
        sp_str = f"${tr['Spot']:>6.2f}({tr['Chg']:>+5.2f}%)"
        lines.append(
            f"{tr['Date']:<11} | {sp_str:>15} | {tr['PA']:>5.1f}% | {tr['PB']:>5.1f}% | {tr['PC']:>5.1f}% | {tr['PD']:>5.1f}% | "
            f"{tr['TopReg']:<13} | {_ph_cell(tr):<8} | {int(tr['CQ1']):>+11,d} | {int(tr['CQ2']):>+11,d} | {int(tr['PQ1']):>+11,d} | {int(tr['PQ2']):>+11,d} | {-int(tr['PQ34']):>+12,d} | ${tr['NearMP']:>5.1f}"
        )
    lines.append("")
    last_tr = traj_df.iloc[-1]
    prev_tr = traj_df.iloc[-2] if len(traj_df) >= 2 else last_tr
    lines.append("### (1-3) [V4.1 월가 프랍 데스크 5대 핵심 알파 팩터 진단 (205거래일 전수 백테스트 검증 지표)]")
    lines.append(f" • 팩터1 [방향성 콜 거래량 서지 (205일 IC +0.253 1위)] : 10일 평균 대비 당일 콜 거래량 {last_tr['CallVolSurge']:.2f}배 폭발 (콜 거래량 점유율 {last_tr['CallVolShare']:.1f}%)")
    lines.append(f" • 팩터2 [콜 수급 결합 상단 감마 진공지대 (IC +0.176)] : 최근접 저항벽 위 상단 OI 진공도 {last_tr['AirVacPct']:.1f}% | 활성 에어포켓 지수 {last_tr['ActiveAirPocket']:.3f}")
    lines.append(f" • 팩터3 [외가격 OTM 달러 거래대금 불균형 (IC +0.379)] : 최근 {w_short}일 OTM 콜-풋 달러 프리미엄 불균형 {last_tr['OTMDVolImb']:+.1f}% (+면 기관 콜 매집 우위)")
    lines.append(f" • 팩터4 [조건부 바나 보정 진성 Call Q1 비중 (IC +0.160)]: 신규 콜 OI 중 진성 상방 매수(Call Q1) 비중 {last_tr['CQ1SharePct']:.1f}% (+{int(last_tr['CQ1']):,}계약 vs Q2 +{int(last_tr['CQ2']):,}계약)")
    lines.append("")

    # ==========================================================================
    # ★ [V4.2 업그레이드 3 & 4] 비절벽형(Soft-Threshold) 4대 징후 + 고점 3일 래치(Rolling Latch) + 중기 분배 폭락 경보
    # ==========================================================================
    term_nb_curr_pct = float(curr_ts['Term_Near_Back'] * 100.0)
    term_nb_prev_pct = float(prev_ts['Term_Near_Back'] * 100.0)
    term_nb_chg_1d   = term_nb_curr_pct - term_nb_prev_pct
    near_iv_chg_1d   = float((curr_ts['Near_ATM_IV'] - prev_ts['Near_ATM_IV']) * 100.0)
    c_share_chg_1d   = float(last_tr['CallVolShare'] - prev_tr['CallVolShare'])
    mp_over_ext_pct  = float((latest_spot / max(mp_nearest, 1e-6) - 1.0) * 100.0)
    mp_all_over_pct  = float((latest_spot / max(mp_all, 1e-6) - 1.0) * 100.0)

    spot_3d_ago = float(df_pit[df_pit['Quote Date'] == d_3d_base]['EWY Price'].iloc[0]) if d_3d_base in df_pit['Quote Date'].values else prev1_spot
    chg_3d_pct  = (latest_spot / max(spot_3d_ago, 1e-6) - 1.0) * 100.0
    is_high_doji_exhaustion = (drawdown_pct >= -2.5) and (chg_3d_pct >= 1.5) and (last_tr['CallVolShare'] <= 46.0) and (last_tr['CQ1SharePct'] <= 20.0)

    pb_cond1 = (daily_chg_pct >= 1.5) and (term_nb_curr_pct >= 5.0) and ((term_nb_chg_1d >= 1.0) or (near_iv_chg_1d >= 0.8))
    pb_cond2 = ((daily_chg_pct >= 1.0) and ((last_tr['CallVolShare'] < 50.0) or (c_share_chg_1d <= -15.0))) or is_high_doji_exhaustion
    _q3_cut_hi  = max(300, int(round(10000 * s_oi)))
    _q3_cut_mid = max(150, int(round(4500 * s_oi)))
    pb_cond3 = (c_q3_sum >= _q3_cut_hi) or (c_q3_sum >= max(0.5 * c_q1_sum, _q3_cut_mid)) or ((c_q3_sum >= 3.0 * max(c_q1_sum, 1)) and ((c_q2_sum + c_q3_sum) >= _q3_cut_hi))
    pb_cond4 = (mp_over_ext_pct >= 1.5) or (mp_all_over_pct >= 5.0)

    prev2_tr = traj_df.iloc[-3] if len(traj_df) >= 3 else prev_tr
    high_dist_latch_on = (
        (drawdown_pct >= -2.5) and
        (last_tr['CQ1SharePct'] < 30.0) and
        ((prev_tr['CQ1SharePct'] <= 15.0) or (prev2_tr['CQ1SharePct'] <= 15.0)) and
        ((c_q2_sum + c_q3_sum) >= 5.0 * max(c_q1_sum, 1))
    )

    ct_3_7_dyn = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, d_3d_base, d_7d_base, peak_date, 'Call', iv_attr='window')   # ★ [V4.3.4] 분배 폭락 경보 검증 정의(창 전체 IV) 유지
    pt_3_7_dyn = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, d_3d_base, d_7d_base, peak_date, 'Put', iv_attr='window')   # ★ [V4.3.4] 분배 폭락 경보 검증 정의(창 전체 IV) 유지
    cq1_3d_dyn = int(ct_3_7_dyn[ct_3_7_dyn['Quadrant'].str.startswith('Q1') & ct_3_7_dyn['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    cq2_3d_dyn = int(ct_3_7_dyn[ct_3_7_dyn['Quadrant'].str.startswith('Q2') & ct_3_7_dyn['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    cq3_3d_dyn = int(abs(ct_3_7_dyn[ct_3_7_dyn['Quadrant'].str.startswith('Q3')]['OI_Chg_Short'].sum()))
    pq1_3d_dyn = int(pt_3_7_dyn[pt_3_7_dyn['Quadrant'].str.startswith('Q1') & pt_3_7_dyn['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    pq2_3d_dyn = int(pt_3_7_dyn[pt_3_7_dyn['Quadrant'].str.startswith('Q2') & pt_3_7_dyn['Is_Clean_Contract']]['OI_Chg_Short'].sum())

    ct_7_20  = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, d_7d_base, d_20d_base, peak_date, 'Call', iv_attr='window')   # ★ [V4.3.4] 분배 폭락 경보 검증 정의(창 전체 IV) 유지
    pt_7_20  = build_quadrant_table_for_dates(surv_df, latest_date, prev1_date, d_7d_base, d_20d_base, peak_date, 'Put', iv_attr='window')   # ★ [V4.3.4] 분배 폭락 경보 검증 정의(창 전체 IV) 유지
    cq1_7d_dyn  = int(ct_7_20[ct_7_20['Quadrant'].str.startswith('Q1') & ct_7_20['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    cq2_7d_dyn  = int(ct_7_20[ct_7_20['Quadrant'].str.startswith('Q2') & ct_7_20['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    cq3_7d_dyn  = int(abs(ct_7_20[ct_7_20['Quadrant'].str.startswith('Q3')]['OI_Chg_Short'].sum()))
    pq1_7d_dyn  = int(pt_7_20[pt_7_20['Quadrant'].str.startswith('Q1') & pt_7_20['Is_Clean_Contract']]['OI_Chg_Short'].sum())
    pq2_7d_dyn  = int(pt_7_20[pt_7_20['Quadrant'].str.startswith('Q2') & pt_7_20['Is_Clean_Contract']]['OI_Chg_Short'].sum())

    cq1_20d_dyn = int(ct_7_20[(ct_7_20['Quad_Long'] == 'Q1') & ct_7_20['Is_Clean_Contract']]['OI_Chg_Long'].sum())
    cq2_20d_dyn = int(ct_7_20[(ct_7_20['Quad_Long'] == 'Q2') & ct_7_20['Is_Clean_Contract']]['OI_Chg_Long'].sum())
    cq3_20d_dyn = int(abs(ct_7_20[ct_7_20['Quad_Long'] == 'Q3']['OI_Chg_Long'].sum()))
    pq1_20d_dyn = int(pt_7_20[(pt_7_20['Quad_Long'] == 'Q1') & pt_7_20['Is_Clean_Contract']]['OI_Chg_Long'].sum())
    pq2_20d_dyn = int(pt_7_20[(pt_7_20['Quad_Long'] == 'Q2') & pt_7_20['Is_Clean_Contract']]['OI_Chg_Long'].sum())

    sh_3d_pct  = cq1_3d_dyn / max(cq1_3d_dyn + cq2_3d_dyn, 1) * 100.0
    sh_7d_pct  = cq1_7d_dyn / max(cq1_7d_dyn + cq2_7d_dyn, 1) * 100.0
    sh_20d_pct = cq1_20d_dyn / max(cq1_20d_dyn + cq2_20d_dyn, 1) * 100.0

    is_distribution_crash_regime = (
        (sh_3d_pct <= 20.0) and
        (sh_7d_pct <= 15.0) and
        (sh_20d_pct <= 18.0) and
        ((cq2_3d_dyn + cq3_3d_dyn) >= 5.0 * max(cq1_3d_dyn, 1)) and
        ((drawdown_pct >= -5.0) or (mp_over_ext_pct >= 2.0))
    )

    pb_active_cnt = int(pb_cond1) + int(pb_cond2) + int(pb_cond3) + int(pb_cond4)
    # ★ [V4.2.8 ③] 과열 경보 0개 ≠ 상승 추세: 종가가 20일 평균 아래면 '상승 순항' 문구 대신 추세 판정 보류
    _px_hist = df_pit[df_pit['Quote Date'] <= latest_date].groupby('Quote Date')['EWY Price'].first()
    _ma20 = float(_px_hist.tail(20).mean()) if len(_px_hist) >= 5 else float(latest_spot)
    is_downtrend_state = (_ph_top == 'D')   # ★ [V4.2.9] 20일선 단순 비교 -> 라벨 학습 국면 판정(하락 1순위)으로 교체
    is_sideways_state = (_ph_top == 'S')

    if is_distribution_crash_regime:
        pb_alert_grade = (
            f"🚨 [중기 상방 연료 고갈 & 고점 분배 폭락(Distribution Crash) 경보 ({pb_active_cnt}/4 점화 | 고점래치 {'ON' if high_dist_latch_on else 'OFF'})] "
            f"3D({sh_3d_pct:.1f}%)·7D({sh_7d_pct:.1f}%)·20D({sh_20d_pct:.1f}%) 전 시계열에서 상승 연료(Call Q1)가 고갈되고 커버드콜(Q2)·롱콜청산(Q3) 폭격이 진행 중입니다! "
            f"(단순 눌림목 기계적 분할매수 엄금 & 1차 지지선 이탈 시 비중 축소·풋 헤지 전환)"
            f" (검증: 분배 경보가 켜진 날 10영업일 내 -5% 이상 하락 {PHASE_REL['alarm']['dist'][0]}% vs 꺼진 날 {PHASE_REL['alarm']['dist'][1]}%, 2024 {PHASE_REL['alarm']['dist'][2]}% vs {PHASE_REL['alarm']['dist'][3]}% · 드물게 발생)"
        )
    elif pb_active_cnt >= 3:   # ★ [V4.4] 고점래치는 라벨·2024 검증 미달 -> 등급 승격에서 제외(신뢰도표에만 표시)
        pb_alert_grade = f"🚨 [고위험 경보 ({pb_active_cnt}/4 점화 · 고점래치 {'ON' if high_dist_latch_on else 'OFF'}는 참고)] (검증: 기본 징후 2개 이상인 날 10영업일 내 -5% 이상 하락 {PHASE_REL['alarm']['pb2'][0]}% vs 꺼진 날 {PHASE_REL['alarm']['pb2'][1]}%, 2024 {PHASE_REL['alarm']['pb2'][2]}% vs {PHASE_REL['alarm']['pb2'][3]}%) 추격매수 자제 · 5단계 눌림목 타점은 참고용"
    elif pb_active_cnt == 2:
        pb_alert_grade = f"⚡ [주의 경계 ({pb_active_cnt}/4 점화)] 단기 차익실현 및 만기 핀닝 되돌림 가능성 (검증: 기본 징후 2개 이상인 날 10영업일 내 -5% 이상 하락 {PHASE_REL['alarm']['pb2'][0]}% vs 꺼진 날 {PHASE_REL['alarm']['pb2'][1]}%) 고점 추격 자제 및 장중 1~2단계 눌림목 지지 확인"
    else:
        if is_downtrend_state:
            pb_alert_grade = f"⚪ [고점 과열 경보 없음 (징후 {pb_active_cnt}/4 점화 · 경보 기준 2개 이상) · 하락 국면 진행 중 (국면 D {_ph_p['D']:.0f}%)] 과열 경보 부재를 상승 신호로 해석 금지 (종가 ${float(latest_spot):.2f} / 20일 평균 ${_ma20:.2f})"
        elif is_sideways_state:
            pb_alert_grade = f"⚪ [고점 과열 경보 없음 (징후 {pb_active_cnt}/4 점화 · 경보 기준 2개 이상) · 횡보 국면 (국면 S {_ph_p['S']:.0f}%)] 방향성 추세가 약한 구간 -> 박스 상·하단 확인 우선"
        else:
            pb_alert_grade = f"✅ [과열 경보 없음 · 안정 순항 (징후 {pb_active_cnt}/4 점화 · 경보 기준 2개 이상) · 상승 국면 (국면 U {_ph_p['U']:.0f}%)] 단기 옵션 수급 과열/소진 징후 없음"

    lines.append("### (1-4) [V4.2 단기 눌림목(Pullback) & 고점 분배(Distribution Crash) 4대 사전 징후 진단 (3영업일 연속성 래치 탑재)]")
    lines.append(f" • 종합 눌림목/분배 경보 등급 : {pb_alert_grade}")
    lines.append(f"   1) [징후① 주가상승+단기IV/백워데이션 역주행 (Spot↑·Vol↑ 과열)] : {'🚨점화(ON)' if pb_cond1 else '⚪미점화(OFF)'} | 당일 주가 {daily_chg_pct:+.2f}%, 근월IV 변동 {near_iv_chg_1d:+.2f}%p, 근월-원월 {term_nb_curr_pct:+.2f}%p(전일비 {term_nb_chg_1d:+.2f}%p)")
    lines.append(f"   2) [징후② 상승일 콜 거래량 점유율 저하(50% 미만 또는 전일비 -15%p) · 고점 도지 소진 — 고점 위치 조건 없음] : {'🚨점화(ON)' if pb_cond2 else '⚪미점화(OFF)'} | 당일 콜 거래량 점유율 {last_tr['CallVolShare']:.1f}%(전일비 {c_share_chg_1d:+.1f}%p, 3일등락 {chg_3d_pct:+.2f}%, 고점도지소진 {'ON' if is_high_doji_exhaustion else 'OFF'})")
    lines.append(f"   3) [징후③ 근월 롱콜 대량 익절청산(Call Q3) 딜러 델타 언와인딩]  : {'🚨점화(ON)' if pb_cond3 else '⚪미점화(OFF)'} | 최근 {w_short}일 Call Q3(롱콜 청산) -{c_q3_sum:,}계약 (진성매수 Call Q1 +{c_q1_sum:,}계약 대비 {c_q3_sum/max(c_q1_sum,1)*100:.1f}%)")
    lines.append(f"   4) [징후④ 주간 만기({nearest_exp}) 단기 Max Pain 상방 오버슈팅]  : {'🚨점화(ON)' if pb_cond4 else '⚪미점화(OFF)'} | 현재가(${latest_spot:.2f})가 단기 Max Pain(${mp_nearest:.1f}) 대비 {mp_over_ext_pct:+.2f}% 상방 괴리 (전체MP 대비 {mp_all_over_pct:+.2f}%)")
    lines.append(sep_thin)
    lines.append("")

    if t_cfg['code'] == 'TIER_ALL' or is_distribution_crash_regime:
        # ★ [V4.3.7] 3D 판정: 기존 기본값 '순항' -> 콜 Q1·Q2 크기(1.15배 기준)와 국면을 반영
        if is_distribution_crash_regime:
            verdict_3d = "🚨단기 콜연료 고갈 / 분배경보"
        elif pb_active_cnt >= 2:
            verdict_3d = "단기 과열 소화 / 2~3단계 눌림목 지지"
        elif _ph_top == 'D':
            verdict_3d = ("하락 국면 · 단기 반등 콜 매수 우위" if cq1_3d_dyn >= 1.15 * max(cq2_3d_dyn, 1) else
                          ("하락 국면 · 단기 상단 콜 매도 우위" if cq2_3d_dyn >= 1.15 * max(cq1_3d_dyn, 1) else "하락 국면 · 단기 콜 수급 균형"))
        elif cq1_3d_dyn >= 1.15 * max(cq2_3d_dyn, 1):
            verdict_3d = "단기 상방 모멘텀 순항"
        elif cq2_3d_dyn >= 1.15 * max(cq1_3d_dyn, 1):
            verdict_3d = "단기 상단 저항(콜 매도) 우위"
        else:
            verdict_3d = "단기 콜 수급 균형(박빙)"
        verdict_7d  = "🚨주간 상방연료 고갈 / 콜캡 폭격" if sh_7d_pct <= 15.0 else ("주간 롤오버 상방 연료 우위" if cq1_7d_dyn >= cq2_7d_dyn else "주간 상단 저항 소화 중")
        verdict_20d = "🚨월간 상방연료 고갈 / 추세하락 경계" if sh_20d_pct <= 18.0 else ("월간 대세 상승 레짐 A 확고" if cq1_20d_dyn >= cq2_20d_dyn else "월간 박스권 공방")

        lines.append("### (1-5) [V4.2 크로스-티어 멀티-호라이즌 마스터 대시보드 (단기 3D 눌림목 경보 vs 7D/20D 중기 코어 수급 & 고점 분배 판별)]")
        lines.append(" 📌 [표 핵심 독해 가이드] 단기 3일 창의 '눌림목 경보'와 주간(7일)·월간(20일) 창의 '코어 상승 연료(Call Q1)'를 한눈에 대조하여, 단기 조정이 중기 상승 추세를 훼손하는 추세 반전(Distribution Crash)인지 단순 숨고르기(매수 기회)인지 판정하십시오.")
        lines.append(" • [V4.3.4] 이 표는 분배 폭락 경보의 검증 정의(창 전체 IV 기준 순포지션)로 계산되어, 체결일 귀속으로 계산한 [섹션 2] 분면 합계와 다를 수 있습니다.")
        lines.append(f"{'분석 시계 (Horizon)':<22} | {'상승 로켓 연료 (Call Q1)':<25} | {'천장 뚜껑 (Call Q2)':<20} | {'바닥 현금 방석 (Put Q2)':<22} | {'하방 시한폭탄 (Put Q1)':<22} | {'종합 국면 판정'}")
        lines.append("-" * 150)
        lines.append(f"{'단기 전술창 (3D / T+1)':<22} | {f'+{cq1_3d_dyn:,}계약 ({sh_3d_pct:.1f}%)':<25} | {f'+{cq2_3d_dyn:,}계약':<20} | {f'+{pq2_3d_dyn:,}계약':<22} | {f'+{pq1_3d_dyn:,}계약':<22} | {verdict_3d}")
        lines.append(f"{'단기 롤오버창 (7D / Weekly)':<22} | {f'+{cq1_7d_dyn:,}계약 ({sh_7d_pct:.1f}%)':<25} | {f'+{cq2_7d_dyn:,}계약':<20} | {f'+{pq2_7d_dyn:,}계약':<22} | {f'+{pq1_7d_dyn:,}계약':<22} | {verdict_7d}")
        lines.append(f"{'월간 감마창 (20D / Monthly)':<22} | {f'+{cq1_20d_dyn:,}계약 ({sh_20d_pct:.1f}%)':<25} | {f'+{cq2_20d_dyn:,}계약':<20} | {f'+{pq2_20d_dyn:,}계약':<22} | {f'+{pq1_20d_dyn:,}계약':<22} | {verdict_20d}")
        lines.append(sep_thin)
        lines.append("")

    # [섹션 2]
    lines.append(f"## [섹션 2] 4대 핵심 미시구조 정밀 데이터 해부 ({w_short}일[{w_short}D] vs {w_long}일[{w_long}D] 누적 추세 통합)")
    lines.append(sep_thin)
    lines.append(f"### ① 변동성 기간구조(Term Structure), 스큐(25D Skew), 꼬리 위험(25D Butterfly) 시계열 (기준일 직전 {vol_ts_days}거래일, 누적%ile)")
    lines.append(" 📌 [표 핵심 독해 가이드] ① 근월-원월(단기 응급실 경보등): +5%p 이상이면 단기 패닉 과열, 0%p 이하면 평온(콘탱고)입니다. ② 주가가 하락하는데도 근월IV나 중기25D스큐(하방 공포 온도계)가 오르지 않거나 하락하면 '진짜 바닥(매도 소진)' 신호이고, 반대로 주가가 오르는데 근월-원월과 중기Butterfly(급등락 지진계)가 치솟으면 '장 뒤의 기습 폭탄 설치' 신호입니다.")
    lines.append(f"{'일자(Date)':<11} | {'EWY종가':>7} | {'근월IV':>7} | {'중기IV':>7} | {'원월IV':>7} | {'근월-원월(%ile)':>17} | {'중기25D스큐(%ile)':>17} | {'원월25D스큐(%ile)':>17} | {'중기Butterfly(%ile)':>19}")
    lines.append("-" * 135)
    for dt_idx, r in ts_metrics.tail(vol_ts_days).iterrows():
        lines.append(
            f"{dt_idx:<11} | ${r['Spot']:>6.2f} | {r['Near_ATM_IV']*100:>6.2f}% | {r['Mid_ATM_IV']*100:>6.2f}% | {r['Back_ATM_IV']*100:>6.2f}% | "
            f"{r['Term_Near_Back']*100:>+6.2f}%p({r['Term_Near_Back_pct']:>5.1f}%) | "
            f"{r['Mid_Skew_25D']*100:>+6.2f}%p({r['Mid_Skew_25D_pct']:>5.1f}%) | "
            f"{r['Back_Skew_25D']*100:>+6.2f}%p({r['Back_Skew_25D_pct']:>5.1f}%) | "
            f"{r['Mid_Bfly_25D']*100:>+6.2f}%p({r['Mid_Bfly_25D_pct']:>5.1f}%)"
        )
    lines.append("")

    lines.append(f"### ② [핵심] OCC 결산 시차(T-1) 보정 OI × IV 4분면 수급 진위 해부 (단기창[{w_short}D] vs 장기창[{w_long}D] 총량 비교)")
    lines.append(f" 📌 [표 핵심 독해 가이드] 단기({w_short}일) 합계만 보면 4~{w_long}일 전에 들어온 큰손의 코어 물량이 빠져나가 착시가 생깁니다. 반드시 아래의 '{w_long}일OI증감(큰손의 원래 누적 매집량)'과 '{w_short}일/1일OI증감(최근 가속/감속 여부)'을 나란히 비교하고, Put에서는 '실질BEP(세력의 본전 방어선)' 가격을 체크하십시오.")
    lines.append(f"  • Call 4분면 (최근{w_short:>2d}일 합계) : Q1[진성 상방 매수] +{c_q1_sum:,}계약 | Q2[상단 캡 커버드콜 매도] +{c_q2_sum:,}계약 | Q3[상방 포기 청산] -{c_q3_sum:,}계약 | Q4[숏커버/롤오버] -{c_q4_sum:,}계약")
    lines.append(f"  • Call 4분면 (최근{w_long:>2d}일 합계) : Q1[진성 상방 매수] +{c_q1_long:,}계약 | Q2[상단 캡 커버드콜 매도] +{c_q2_long:,}계약 | Q3[상방 포기 청산] -{c_q3_long:,}계약 | Q4[숏커버/롤오버] -{c_q4_long:,}계약")
    lines.append(f"  • Put  4분면 (최근{w_short:>2d}일 합계) : Q1[하방 폭락 베팅/롤다운] +{p_q1_sum:,}계약 | Q2[바닥 방어 풋 매도(Bunker)] +{p_q2_sum:,}계약 | Q3[풋 수익화 청산] -{p_q3_sum:,}계약 | Q4[만기청산/숏커버] -{p_q4_sum:,}계약")
    lines.append(f"  • Put  4분면 (최근{w_long:>2d}일 합계) : Q1[하방 폭락 베팅/롤다운] +{p_q1_long:,}계약 | Q2[바닥 방어 풋 매도(Bunker)] +{p_q2_long:,}계약 | Q3[풋 수익화 청산] -{p_q3_long:,}계약 | Q4[만기청산/숏커버] -{p_q4_long:,}계약")
    # ★ [V4.2.8 ④] 청산(OI 감소)은 정산 데이터라 IV 노이즈와 무관하게 실재 → 방향 판정(Q3/Q4)과 별개로 총량을 따로 표기
    _c_live = c_tbl[c_tbl.index.get_level_values('Expiration Date') > latest_date]
    _p_live = p_tbl[p_tbl.index.get_level_values('Expiration Date') > latest_date]
    _c_close_all = int(_c_live.loc[_c_live['OI_Chg_Short'] < 0, 'OI_Chg_Short'].sum())
    _p_close_all = int(_p_live.loc[_p_live['OI_Chg_Short'] < 0, 'OI_Chg_Short'].sum())
    _c_dir_close = int(_c_live.loc[(_c_live['OI_Chg_Short'] < 0) & _c_live['Quadrant'].str.match(r'Q[34]'), 'OI_Chg_Short'].sum())
    _p_dir_close = int(_p_live.loc[(_p_live['OI_Chg_Short'] < 0) & _p_live['Quadrant'].str.match(r'Q[34]'), 'OI_Chg_Short'].sum())
    lines.append(f"  • 총 청산(방향 무관·당일만기 제외, 최근{w_short:>2d}일) : Call {_c_close_all:+,}계약 (그중 방향 판정 Q3+Q4 {_c_dir_close:+,}) | Put {_p_close_all:+,}계약 (그중 방향 판정 Q3+Q4 {_p_dir_close:+,})")
    lines.append("")

    lines.append(f"#### (2-1) Call 상위 변동 계약 4분면 해부 ({w_long}일전[{long_date}] vs {w_short}일전[{short_date}] vs 최신[{latest_date}])")
    lines.append(f"{'만기일(Exp)':<11} | {'행사가':>6} | {'최신OI':>8} | {f'{w_long}일OI증감':>9} | {f'{w_short}일OI증감':>9} | {'1일OI증감':>9} | {f'{w_short}일거래량':>9} | {'유효IV변동(T-1결산)':>19} | {'당일IV변동(T)':>13} | {'OI×IV 4분면 수급 판정'}")
    lines.append("-" * 158)
    _c_valid_sub = c_tbl[c_tbl['Is_Clean_Contract'] & (c_tbl.index.get_level_values('Expiration Date') > latest_date)]
    if len(_c_valid_sub) < 6:
        _c_valid_sub = c_tbl[c_tbl['Is_Clean_Contract']]
    top_c_movers = _c_valid_sub.reindex((_c_valid_sub['OI_Chg_Short'].abs() + _c_valid_sub['OI_Chg_Long'].abs()*0.5).sort_values(ascending=False).index).head(12)
    for (exp_d, strk), r in top_c_movers.iterrows():
        eff_iv_str = f"{r['Eff_IV_Chg']*100:>+6.2f}%p (IV {r['IV_Prev1']*100:>4.1f}%)"
        rt_iv_str  = f"{r['IV_Chg_1D']*100:>+6.2f}%p({r['IV_Latest']*100:>4.1f}%)"
        lines.append(
            f"{exp_d:<11} | ${strk:>5.1f} | {int(r['OI_Latest']):>8,d} | {int(r['OI_Chg_Long']):>+9,d} | "
            f"{int(r['OI_Chg_Short']):>+9,d} | {int(r['OI_Chg_1D']):>+9,d} | {int(r['Vol_ShortWin']):>9,d} | "
            f"{eff_iv_str:>19} | {rt_iv_str:>13} | {r['Quadrant']}"
        )
    lines.append("")

    lines.append(f"#### (2-2) Put 상위 증가 계약 4분면 해부: [Q1 진성 하방 베팅/롤다운] vs [Q2 현금담보 풋 매도 벙커] ({w_long}일/{w_short}일/1일 연속 추적)")
    lines.append(f"{'만기일(Exp)':<11} | {'행사가':>6} | {'최신OI':>8} | {f'{w_long}일OI증감':>9} | {f'{w_short}일OI증감':>9} | {'1일OI증감':>9} | {f'{w_short}일거래량':>9} | {'유효IV변동(T-1결산)':>19} | {'당일IV변동(T)':>13} | {'실질BEP':>8} | {'OI×IV 4분면 수급 판정'}")
    lines.append("-" * 168)
    _p_valid_sub = p_tbl[p_tbl['Is_Clean_Contract'] & (p_tbl.index.get_level_values('Expiration Date') > latest_date) & (p_tbl['OI_Chg_Short'] > 0)]
    if len(_p_valid_sub) < 6:
        _p_valid_sub = p_tbl[p_tbl['Is_Clean_Contract'] & (p_tbl['OI_Chg_Short'] > 0)]
    top_p_inc = _p_valid_sub.reindex((_p_valid_sub['OI_Chg_Short'] + _p_valid_sub['OI_Chg_Long']*0.4).sort_values(ascending=False).index).head(14)
    for (exp_d, strk), r in top_p_inc.iterrows():
        eff_iv_str = f"{r['Eff_IV_Chg']*100:>+6.2f}%p (IV {r['IV_Prev1']*100:>4.1f}%)"
        rt_iv_str  = f"{r['IV_Chg_1D']*100:>+6.2f}%p({r['IV_Latest']*100:>4.1f}%)"
        bep_val = strk - r['Price_Latest']
        lines.append(
            f"{exp_d:<11} | ${strk:>5.1f} | {int(r['OI_Latest']):>8,d} | {int(r['OI_Chg_Long']):>+9,d} | "
            f"{int(r['OI_Chg_Short']):>+9,d} | {int(r['OI_Chg_1D']):>+9,d} | {int(r['Vol_ShortWin']):>9,d} | "
            f"{eff_iv_str:>19} | {rt_iv_str:>13} | ${bep_val:>7.2f} | {r['Quadrant']}"
        )
    lines.append("")

    lines.append(f"#### (2-3) Put 상위 감소(청산) 계약 해부: [Q3/Q4 풋 수익화(Monetization) vs 하방 롤다운 재원이동]")
    lines.append(f"{'만기일(Exp)':<11} | {'행사가':>6} | {'고점일OI':>9} | {'최신OI':>9} | {f'{w_long}일OI청산':>10} | {f'{w_short}일OI청산':>10} | {'1일OI청산':>10} | {f'{w_short}일거래량':>10} | {'현재가':>8} | {'OI×IV 4분면 수급 판정'}")
    lines.append("-" * 138)
    top_p_dec = p_tbl[p_tbl.index.get_level_values('Expiration Date') > latest_date].sort_values(by='OI_Chg_Short', ascending=True).head(8)  # ★ [V4.2.8 ④] 당일 소멸 만기 제외
    for (exp_d, strk), r in top_p_dec.iterrows():
        _mk23, _ls23 = _mark_price_v437([r['Bid_Latest']], [r['Ask_Latest']], [r['Price_Latest']], [max(0.0, float(strk) - latest_spot)])   # ★ [V4.3.7]
        _mk23, _ls23 = float(_mk23[0]), bool(_ls23[0])
        if (not _ls23) and abs(float(r['Price_Latest']) - _mk23) / max(_mk23, 0.05) > 0.15:
            _dq.setdefault('stale_list', []).append(f"{exp_d} {float(strk):.0f}P 체결가 {float(r['Price_Latest']):.2f}→중간호가 {_mk23:.2f}")
        lines.append(
            f"{exp_d:<11} | ${strk:>5.1f} | {int(r['OI_Peak']):>9,d} | {int(r['OI_Latest']):>9,d} | {int(r['OI_Chg_Long']):>+10,d} | "
            f"{int(r['OI_Chg_Short']):>+10,d} | {int(r['OI_Chg_1D']):>+10,d} | {int(r['Vol_ShortWin']):>10,d} | {_mk23:>7.2f}{'*' if _ls23 else ' '} | {r['Quadrant']}"
        )
    lines.append(" • [V4.3.7] 현재가 = 매수·매도 호가의 중간값(호가가 없으면 마지막 체결가, 뒤에 *). 체결이 없던 날 예전 체결가가 남는 문제를 막기 위한 것입니다.")
    lines.append("")

    # --------------------------------------------------------------------------
    # ★ [V4.2.3 업그레이드 B] (2-4) 현업 시그널 창(2025-01-02~) & 잔존물량 역추적 기반 합성 공매도 본대 · 매집당시주가 · 매집단가 계측 (손익 판정은 V4.3.2 평가손익 기준)
    # --------------------------------------------------------------------------
    _itm_sig_cutoff = SIGNAL_START_DATE if latest_date >= SIGNAL_START_DATE else first_date
    hist_puts = df_pit[
        (df_pit['Option Type'] == 'Put') &
        (df_pit['Expiration Date'] >= latest_date) &
        (df_pit['Quote Date'] >= _itm_sig_cutoff) &
        (df_pit['Quote Date'] <= latest_date)
    ].sort_values(['Expiration Date', 'Strike', 'Quote Date']).copy()

    if len(hist_puts) > 0:
        grp_p = hist_puts.groupby(['Expiration Date', 'Strike'], sort=False)
        hist_puts['dOI'] = grp_p['Open Interest'].diff().fillna(hist_puts['Open Interest'])
        hist_puts['dIV'] = grp_p['Implied Volatility'].diff().fillna(0.0)
        hist_puts['Mid_P'] = np.where(
            (hist_puts['Bid'] > 0) & (hist_puts['Ask'] > 0),
            0.5 * (hist_puts['Bid'] + hist_puts['Ask']),
            np.where(
                hist_puts['Last Price'] > 0,
                hist_puts['Last Price'],
                np.maximum(0.05, hist_puts['Strike'] - hist_puts['EWY Price'])
            )
        )
        # 1) 계약별 역사적 최고 미결제약정(Hist_Peak_OI) 및 고점 달성일(Peak_Date) 산출
        _idx_max_oi = grp_p['Open Interest'].idxmax()
        _peak_rows  = hist_puts.loc[_idx_max_oi].set_index(['Expiration Date', 'Strike'])
        hist_peak_oi_ser = _peak_rows['Open Interest']
        hist_peak_dt_ser = _peak_rows['Quote Date']

        # 2) 포지션 물갈이(Turnover) 보정: 최신일부터 역순 누적하여 현재 활성 사이클(Hist_Peak_OI * 1.15 이내) 매집분만 정밀 추출
        acc_puts = hist_puts[hist_puts['dOI'] > 0].copy()
        if len(acc_puts) > 0:
            acc_rev = acc_puts.iloc[::-1].copy()
            acc_rev['Rev_Cum_dOI'] = acc_rev.groupby(['Expiration Date', 'Strike'], sort=False)['dOI'].cumsum()
            acc_puts = acc_rev.iloc[::-1].copy()
            acc_puts['Contract_Peak_OI'] = acc_puts.set_index(['Expiration Date', 'Strike']).index.map(hist_peak_oi_ser).values
            acc_active = acc_puts[(acc_puts['Rev_Cum_dOI'] - acc_puts['dOI']) <= np.maximum(acc_puts['Contract_Peak_OI'] * 1.15, 500.0)].copy()

            acc_active['W_Spot']  = acc_active['dOI'] * acc_active['EWY Price']
            acc_active['W_Prem']  = acc_active['dOI'] * acc_active['Mid_P']
            acc_active['W_Q1_OI'] = np.where(acc_active['dIV'] >= -0.002, acc_active['dOI'], 0.0)
            acc_grp = acc_active.groupby(['Expiration Date', 'Strike'], sort=False).agg({
                'dOI': 'sum',
                'W_Spot': 'sum',
                'W_Prem': 'sum',
                'W_Q1_OI': 'sum'
            })
            acc_grp['Entry_Spot_VWAP'] = acc_grp['W_Spot'] / np.maximum(acc_grp['dOI'], 1.0)
            acc_grp['Entry_Prem_VWAP'] = acc_grp['W_Prem'] / np.maximum(acc_grp['dOI'], 1.0)
            acc_grp['Hist_Q1_Ratio']   = acc_grp['W_Q1_OI'] / np.maximum(acc_grp['dOI'], 1.0)
        else:
            acc_grp = pd.DataFrame()
    else:
        hist_peak_oi_ser = pd.Series(dtype=float)
        hist_peak_dt_ser = pd.Series(dtype=str)
        acc_grp = pd.DataFrame()

    _itm_min_oi = max(30, int(round(300 * s_oi)))
    _itm_min_pk = max(100, int(round(1000 * s_oi)))
    p_itm_df = p_tbl[
        (p_tbl.index.get_level_values('Expiration Date') > latest_date) &  # ★ [V4.2.8 ④] 당일 소멸 만기 제외
        (p_tbl.index.get_level_values('Strike') > latest_spot) &
        ((p_tbl['OI_Latest'] >= _itm_min_oi) | (p_tbl['OI_Peak'] >= _itm_min_pk))
    ].copy()

    if len(p_itm_df) > 0:
        p_itm_df['Hist_Peak_OI'] = hist_peak_oi_ser.reindex(p_itm_df.index).fillna(p_itm_df['OI_Peak'])
        p_itm_df['Hist_Peak_OI'] = np.maximum(p_itm_df['Hist_Peak_OI'], p_itm_df['OI_Latest'])
        p_itm_df['Hist_Peak_Dt'] = hist_peak_dt_ser.reindex(p_itm_df.index).fillna(peak_date).astype(str).str[5:]

        itm_strks = p_itm_df.index.get_level_values('Strike').values.astype(float)
        itm_T_yr  = np.maximum(p_itm_df['DTE_Latest'].values.astype(float) / 365.0, 1.0 / 365.0)
        itm_sig   = np.maximum(p_itm_df['IV_Latest'].values.astype(float), 0.20)
        itm_d1    = (np.log(latest_spot / np.maximum(itm_strks, 1.0)) + (0.048 + 0.5 * (itm_sig ** 2)) * itm_T_yr) / (itm_sig * np.sqrt(itm_T_yr))
        p_itm_df['BS_Delta_ITM'] = np.where(
            p_itm_df['Delta_Latest'].abs() > 0.05,
            p_itm_df['Delta_Latest'].values,
            stats.norm.cdf(itm_d1) - 1.0
        )
        intrinsic_val = np.maximum(0.0, itm_strks - latest_spot)
        # ★ [V4.3.7] 현재가 = 중간호가(호가 없으면 마지막 체결가) — 체결이 없던 날 예전 체결가가 그대로 남아 평가손익이 부풀던 문제 차단
        eff_put_price, _itm_last_used = _mark_price_v437(p_itm_df['Bid_Latest'].values, p_itm_df['Ask_Latest'].values, p_itm_df['Price_Latest'].values, intrinsic_val)
        _lp_itm = p_itm_df['Price_Latest'].values.astype(float)
        _stale_itm = (~_itm_last_used) & (np.abs(_lp_itm - eff_put_price) / np.maximum(eff_put_price, 0.05) > 0.15)
        for (_e24, _k24), _l24, _m24, _s24 in zip(p_itm_df.index, _lp_itm, eff_put_price, _stale_itm):
            if _s24:
                _dq.setdefault('stale_list', []).append(f"{_e24} {float(_k24):.0f}P 체결가 {_l24:.2f}→중간호가 {_m24:.2f}")
        p_itm_df['Eff_Price'] = eff_put_price
        p_itm_df['Eff_BEP']   = itm_strks - eff_put_price

        if len(acc_grp) > 0:
            e_spot = acc_grp['Entry_Spot_VWAP'].reindex(p_itm_df.index).fillna(latest_spot).values
            e_prem = acc_grp['Entry_Prem_VWAP'].reindex(p_itm_df.index).fillna(p_itm_df['Eff_Price']).values
            q1_rat = acc_grp['Hist_Q1_Ratio'].reindex(p_itm_df.index).fillna(0.5).values
        else:
            e_spot = np.full(len(p_itm_df), latest_spot)
            e_prem = eff_put_price
            q1_rat = np.full(len(p_itm_df), 0.5)

        p_itm_df['Entry_Spot_VWAP'] = e_spot
        p_itm_df['Entry_Prem_VWAP'] = e_prem
        p_itm_df['True_Entry_BEP']  = itm_strks - e_prem
        p_itm_df['Unwind_From_Peak_Pct'] = (1.0 - (p_itm_df['OI_Latest'].values / np.maximum(p_itm_df['Hist_Peak_OI'].values, 1.0))) * 100.0
        p_itm_df['Dealer_Short_Shares'] = p_itm_df['OI_Latest'].values * 100.0 * np.abs(p_itm_df['BS_Delta_ITM'].values)
        p_itm_df['Released_Cover_Shares_Short'] = np.maximum(0.0, -p_itm_df['OI_Chg_Short'].values) * 100.0 * np.abs(p_itm_df['BS_Delta_ITM'].values)

        # ★ 매집 당시 주가(Entry_Spot_VWAP) 대비 행사가 위치 및 델타에 따른 출신 성분 3분류
        origin_labels = []
        for idx_i, s_val in enumerate(itm_strks):
            if s_val >= e_spot[idx_i] * 0.99:   # ★ [V4.3.7] 매집 당시 이미 내가격 (오늘 주가 기준 'x1.15' 조건 삭제: 주가가 움직일 때 보유측이 뒤바뀌던 문제)
                origin_labels.append("1선:태생합성공매도")
            elif q1_rat[idx_i] >= 0.35:          # ★ [V4.3.7] 매집 때 IV 상승(매수 주도) 비중만 사용 (오늘 델타 조건 삭제)
                origin_labels.append("2선:공격롱풋->ITM")
            else:
                origin_labels.append("3선:포위된풋벙커")
        p_itm_df['Origin_Type'] = origin_labels

        # ★ [V4.3.2] 보유측 평가손익(Mark-to-Market) 판정
        #   '만기BEP(행사가-매집단가)'는 시간가치가 0이 되는 만기일에만 성립하므로, 만기 전 손익은 현재 옵션가와 매집단가의 차이로 판정한다.
        #   1선·2선 = 풋 매수측(+1), 3선 = 풋 매도측(-1: 매집 당시 IV 하락 = 풋 매도 벙커가 내가격으로 밀린 물량) -> 손익 부호와 딜러 헤지 방향을 반대로 계산
        _side = np.where(p_itm_df['Origin_Type'].str.startswith('3선').values, -1.0, 1.0)
        _abs_d = np.abs(p_itm_df['BS_Delta_ITM'].values.astype(float))
        p_itm_df['Pos_Side']    = _side
        p_itm_df['Time_Value']  = np.maximum(0.0, eff_put_price - intrinsic_val)
        p_itm_df['MTM_PnL']     = (eff_put_price - p_itm_df['Entry_Prem_VWAP'].values.astype(float)) * _side
        p_itm_df['MTM_PnL_Pct'] = p_itm_df['MTM_PnL'].values / np.maximum(p_itm_df['Entry_Prem_VWAP'].values.astype(float), 0.05) * 100.0
        # 매집 이력(매집단가)이 실제로 역산된 계약만 손익 판정 (이력 없는 계약은 매집단가=현재가로 채워져 있으므로 제외)
        _has_entry = acc_grp['Entry_Prem_VWAP'].reindex(p_itm_df.index).notna().values if len(acc_grp) > 0 else np.zeros(len(p_itm_df), dtype=bool)
        p_itm_df['Entry_Known'] = _has_entry & np.isfinite(p_itm_df['MTM_PnL'].values)
        # 딜러 헤지: 매수측 상대 딜러 = 풋 매도 -> 현물 공매도(-), 매도측 상대 딜러 = 풋 매수 -> 현물 매수(+)
        p_itm_df['Dealer_Hedge_Shares'] = -p_itm_df['OI_Latest'].values * 100.0 * _abs_d * _side
        p_itm_df['Dealer_Short_Shares'] = np.where(_side > 0, p_itm_df['OI_Latest'].values * 100.0 * _abs_d, 0.0)
        _rel_sh = np.maximum(0.0, -p_itm_df['OI_Chg_Short'].values) * 100.0 * _abs_d
        p_itm_df['Released_Cover_Shares_Short'] = np.where(_side > 0, _rel_sh, 0.0)   # 매수측 청산 -> 딜러 환매수(현물 매수)
        p_itm_df['Released_Sell_Shares_Short']  = np.where(_side < 0, _rel_sh, 0.0)   # 매도측 청산 -> 딜러 매수헤지 해소(현물 매도)

        tot_itm_put_oi       = int(p_itm_df['OI_Latest'].sum())
        tot_itm_peak_oi      = int(p_itm_df['Hist_Peak_OI'].sum())
        tot_itm_chg_1d       = int(p_itm_df['OI_Chg_1D'].sum())
        tot_itm_chg_short    = int(p_itm_df['OI_Chg_Short'].sum())
        tot_itm_chg_long     = int(p_itm_df['OI_Chg_Long'].sum())
        tot_dealer_short_sh  = int(round(p_itm_df['Dealer_Short_Shares'].sum()))
        tot_dealer_long_sh   = int(round(np.maximum(p_itm_df['Dealer_Hedge_Shares'].values, 0.0).sum()))
        tot_released_sh      = int(round(p_itm_df['Released_Cover_Shares_Short'].sum()))
        tot_released_sell_sh = int(round(p_itm_df['Released_Sell_Shares_Short'].sum()))
        weighted_itm_bep     = float(safe_weighted_avg(p_itm_df['True_Entry_BEP'].values, np.maximum(p_itm_df['OI_Latest'].values, 1.0)))   # 만기BEP 가중평균(참고)
        weighted_curr_bep    = float(safe_weighted_avg(p_itm_df['Eff_BEP'].values, np.maximum(p_itm_df['OI_Latest'].values, 1.0)))
        # ★ [V4.3.2] 평가손실 비중 = 현재 옵션가 기준으로 손실 중인 보유측 OI (매수측: 현재가<매집단가, 매도측: 현재가>매집단가)
        _oi_v   = p_itm_df['OI_Latest'].values.astype(float)
        _buy_m  = p_itm_df['Pos_Side'].values > 0
        _known  = p_itm_df['Entry_Known'].values.astype(bool)
        _loss_m = (p_itm_df['MTM_PnL'].values < 0) & _known
        _win_m  = (p_itm_df['MTM_PnL'].values >= 0) & _known
        mtm_buy_win_oi   = int(_oi_v[_buy_m & _win_m].sum())
        mtm_buy_loss_oi  = int(_oi_v[_buy_m & _loss_m].sum())
        mtm_sell_win_oi  = int(_oi_v[~_buy_m & _win_m].sum())
        mtm_sell_loss_oi = int(_oi_v[~_buy_m & _loss_m].sum())
        mtm_unknown_oi   = int(_oi_v[~_known].sum())
        weighted_mtm_pct = float(safe_weighted_avg(p_itm_df['MTM_PnL_Pct'].values[_known], np.maximum(_oi_v[_known], 1.0))) if _known.any() else 0.0
        trapped_itm_oi       = mtm_buy_loss_oi + mtm_sell_loss_oi
        trapped_itm_ratio    = (trapped_itm_oi / max(tot_itm_put_oi, 1)) * 100.0
    else:
        tot_itm_put_oi, tot_itm_peak_oi, tot_itm_chg_1d, tot_itm_chg_short, tot_itm_chg_long = 0, 0, 0, 0, 0
        tot_dealer_short_sh, tot_released_sh, weighted_itm_bep, weighted_curr_bep, trapped_itm_oi, trapped_itm_ratio = 0, 0, latest_spot, latest_spot, 0, 0.0
        tot_dealer_long_sh, tot_released_sell_sh, weighted_mtm_pct = 0, 0, 0.0
        mtm_buy_win_oi, mtm_buy_loss_oi, mtm_sell_win_oi, mtm_sell_loss_oi, mtm_unknown_oi = 0, 0, 0, 0, 0

    lines.append(f"#### (2-4) [V4.3.2 손익 판정 교정] 합성 공매도 본대(Deep ITM Put) 및 내가격 풋 지형 · 매집당시주가 · 매집단가 대비 평가손익 현황")
    lines.append(f" 📌 [표 핵심 독해 가이드] 현업 정밀 수급 창({_itm_sig_cutoff}~현재, 1일 OI=0 결측 복원 완료)에서 각 계약이 실제 매집된 날들의 가중평균 주가('매집당시주가')와 매집단가를 역산하고, 현재 옵션가와 비교해 보유측의 평가손익(Mark-to-Market)을 판정한 표입니다. ① '1선:태생합성공매도'(매집 당시부터 깊은 내가격)와 '2선:공격롱풋->ITM'은 풋 매수측, '3선:포위된풋벙커'는 풋 매도측(매집 당시 IV 하락 = 풋 매도)으로 보고 손익 부호를 반대로 계산합니다. ② '만기BEP(행사가-매집단가)'는 시간가치가 0이 되는 만기일에만 성립하는 참고치이므로 만기 전 손익은 '평가손익' 열로 판단하십시오. ③ 매수측이 평가손실이면 손절성 청산 시 딜러 환매수(현물 매수), 매도측이 평가손실이면 손절 환매 시 딜러 매수헤지 해소(현물 매도)로 이어집니다.")
    lines.append(f"  • 내가격(ITM) 풋 총 잔존OI : {tot_itm_put_oi:,}계약 (역사적최대OI 합계 {tot_itm_peak_oi:,}계약 대비 {tot_itm_put_oi - tot_itm_peak_oi:+,}계약 [{(1.0 - tot_itm_put_oi/max(tot_itm_peak_oi,1))*100:.1f}% 청산] / {w_short}일 {tot_itm_chg_short:+,}계약 / 1일 {tot_itm_chg_1d:+,}계약)")
    lines.append(f"  • 딜러 헤지 잔량: 매수측(1·2선) 상대 대리공매도 -{tot_dealer_short_sh:,}주 (명목원금 {tot_dealer_short_sh*latest_spot/1e6:.2f}백만달러) | 매도측(3선) 상대 매수헤지 +{tot_dealer_long_sh:,}주 | 최근 {w_short}일 청산 효과: 딜러 환매수(현물 매수) +{tot_released_sh:,}주 · 매수헤지 해소(현물 매도) -{tot_released_sell_sh:,}주")
    lines.append(f"  • 보유측 평가손익(현재 옵션가 기준): 매수측 평가수익 {mtm_buy_win_oi:,}계약 · 평가손실 {mtm_buy_loss_oi:,}계약 | 매도측 평가수익 {mtm_sell_win_oi:,}계약 · 평가손실 {mtm_sell_loss_oi:,}계약 | 매집이력 부족 {mtm_unknown_oi:,}계약 -> 평가손실 비중 {trapped_itm_ratio:.1f}% ({trapped_itm_oi:,}계약) · OI 가중 평균 평가손익 {weighted_mtm_pct:+.1f}%")
    lines.append(f"  • 참고 — 만기BEP 가중평균(행사가-매집단가, 시간가치 0 가정) {weighted_itm_bep:.2f}달러 / 현재 옵션가 기준 만기BEP {weighted_curr_bep:.2f}달러: 만기일에만 성립하므로 만기 전 손익 판정에는 쓰지 않습니다.")
    lines.append(f"{'출신성분(누적역산)':<16} | {'보유측':<3} | {'만기일(Exp)':<11} | {'행사가':>6} | {'역사적최대OI(고점일)':>17} | {'최신OI(청산율)':>14} | {f'{w_short}일OI증감':>9} | {'매집당시주가':>10} | {'매집단가(현가)':>14} | {'평가손익(계약당)':>17} | {'만기BEP(참고)':>11} | {'딜러헤지':>12} | {'보유측 평가손익 및 청산 압력 판정'}")
    lines.append("-" * 214)
    if len(p_itm_df) > 0:
        top_itm_puts = p_itm_df.sort_values(by=['Hist_Peak_OI', 'OI_Latest'], ascending=False).head(12)
        for (exp_d, strk), r in top_itm_puts.iterrows():
            orig_lbl = r['Origin_Type']
            bep_v    = float(r['True_Entry_BEP'])
            sh_cnt   = int(round(r['Dealer_Short_Shares']))
            unw_pct  = float(r['Unwind_From_Peak_Pct'])
            pk_str   = f"{int(r['Hist_Peak_OI']):>7,d}({r['Hist_Peak_Dt']})"
            oi_unw_s = f"{int(r['OI_Latest']):>6,d}({unw_pct:>3.0f}%)"
            prm_str  = f"{r['Entry_Prem_VWAP']:>5.2f}({r['Eff_Price']:>5.2f})"
            side_buy = float(r['Pos_Side']) > 0
            pnl_v, pnl_p = float(r['MTM_PnL']), float(r['MTM_PnL_Pct'])
            pnl_str = f"{pnl_v:+.2f}달러({pnl_p:+.1f}%)" if bool(r['Entry_Known']) else "매집이력 부족"
            hedge_sh = int(round(r['Dealer_Hedge_Shares']))
            if unw_pct >= 70.0 or r['OI_Chg_Short'] <= -max(100, int(round(1000 * s_oi))):
                st_str = f"🔥대량청산 진행(고점대비 {unw_pct:.0f}%청산 -> {'딜러 환매수(현물 매수)' if side_buy else '딜러 매수헤지 해소(현물 매도)'})"
            elif not bool(r['Entry_Known']):
                st_str = "⚪매집이력 부족(손익 판정 보류)"
            elif side_buy and pnl_v >= 0:
                st_str = f"🟢매수측 평가수익 {pnl_p:+.0f}% -> 손절 압력 없음(익절 청산 시에만 딜러 환매수)"
            elif side_buy:
                st_str = f"⚡매수측 평가손실 {pnl_p:+.0f}% -> 손절성 청산 시 딜러 환매수(현물 매수)"
            elif pnl_v >= 0:
                st_str = f"🟢매도측 평가수익 {pnl_p:+.0f}% -> 매도 포지션 유지 우위"
            else:
                st_str = f"⚡매도측 평가손실 {pnl_p:+.0f}% -> 손절 환매 시 딜러 매수헤지 해소(현물 매도)"
            lines.append(
                f"{orig_lbl:<16} | {'매수' if side_buy else '매도':<3} | {exp_d:<11} | {strk:>5.1f} | {pk_str:>17} | {oi_unw_s:>14} | "
                f"{int(r['OI_Chg_Short']):>+9,d} | {r['Entry_Spot_VWAP']:>9.2f}달러 | {prm_str:>14} | {pnl_str:>17} | {bep_v:>11.2f} | {hedge_sh:>+11,d}주 | {st_str}"
            )
    lines.append("")

    lines.append(f"### ③ 상단 저항벽(Call Wall) vs 하단 방어/가속선(Put Wall) 지형도 ({w_short}일 증감 & {w_long}일 증감 동시 비교)")
    lines.append(" 📌 [표 핵심 독해 가이드] 맨 오른쪽 '순OI(Put-Call)' 열을 보십시오. 양수(+)가 큰 행사가(예: +30,000 이상)는 바닥을 받치는 콘크리트 풋 요새이고, 음수(-)가 큰 행사가(예: -10,000 이하)는 상단 콜 저항벽입니다. 순OI의 부호가 (+)에서 (-)로 바뀌는 경계 행사가가 현재 시장의 핵심 공방 피벗(스위치)입니다.")
    lines.append(f"{'행사가(Strike)':<12} | {'현가괴리율':>9} | {'잔존Call_OI':>11} | {f'Call_{w_short}일증감':>12} | {f'Call_{w_long}일증감':>12} | {'잔존Put_OI':>11} | {f'Put_{w_short}일증감':>12} | {f'Put_{w_long}일증감':>12} | {'순OI(Put-Call)':>14}")
    lines.append("-" * 128)
    focus_strikes = wall_map.loc[(wall_map.index >= latest_spot * 0.78) & (wall_map.index <= latest_spot * 1.22)]
    focus_strikes = focus_strikes[(focus_strikes['Call_OI_Latest'] + focus_strikes['Put_OI_Latest']) >= max(150, int(round(3000 * s_oi)))].sort_index(ascending=False)
    for strk, r in focus_strikes.iterrows():
        dist_pct = (strk / latest_spot - 1.0) * 100.0
        lines.append(
            f"${strk:<11.1f} | {dist_pct:>+8.2f}% | {int(r['Call_OI_Latest']):>11,d} | {int(r['Call_Chg_Short']):>+12,d} | {int(r['Call_Chg_Long']):>+12,d} | "
            f"{int(r['Put_OI_Latest']):>11,d} | {int(r['Put_Chg_Short']):>+12,d} | {int(r['Put_Chg_Long']):>+12,d} | {int(r['Net_Put_Minus_Call']):>+14,d}"
        )
    lines.append("")

    lines.append(f"### ④ [당일 조기경보] 당일({latest_date}) 미결산 기습 거래량 · 실시간 그리스(Δ·Γ) · 딜러 초동 헤지주수 레이더 (OCC T+1 결산 전 포착)")
    lines.append(" 📌 [표 핵심 독해 가이드] 내일 아침 공식 장부(OI)에 찍히기 전에 오늘 장중 몰래 들어온 '암행어사 기습 자금'입니다. ① 'Vol/OI회전율'(≥1.0x)과 ② '당일IV변동(T)' 급등 여부뿐만 아니라, ③ [V4.1 신설] 현가 근접도(BS델타·감마)에 따라 마켓메이커가 즉시 현·선물 시장에 던져야 하는 '딜러초동헤지(주)' 규모를 확인하십시오.")
    lines.append(f" • [V4.3.3 데이터 정제] 거래량·종가가 전 거래일과 똑같이 복사된 야후 미체결 이월(Stale) 행은 체결이 없던 것으로 보고 거래량 0으로 처리해 이 표·④-B·⑤·[섹션 3-3]에서 제외했습니다 (당일 {n_stale_latest}건 · 전일 {n_stale_prev1}건). 회전율 분모는 당일OI와 전일OI 중 큰 값입니다.")
    lines.append(f"{'구분':<4} | {'만기일(Exp)':<11} | {'행사가':>6} | {'전일거래량':>9} | {'당일거래량':>9} | {'당일OI(1일증감)':>16} | {'Vol/OI회전율':>10} | {'당일IV변동(T)':>15} | {'BS델타(감마)':>14} | {'딜러초동헤지':>11} | {'최신종가':>7} | {'당일(T) 미결산 수급 조기경보 판정'}")
    lines.append("-" * 190)
    for _, r in top_ambush.iterrows():
        oi_str = f"{int(r['OI_Latest']):>6,d}({int(r['OI_Chg_1D']):>+6,d})"
        iv_str = f"{r['IV_Chg_1D']*100:>+6.2f}%p({r['IV_Latest']*100:>4.1f}%)"
        dg_str = f"{r['BS_Delta']:>+5.2f}({r['BS_Gamma']:>.3f})"
        hdg_sign = -1 if ("하방공습" in r['Intraday_Signal'] or "상단캡" in r['Intraday_Signal']) else (1 if ("상방매집" in r['Intraday_Signal'] or "풋매도" in r['Intraday_Signal']) else 0)
        hdg_sh_val = int(round(r['Hedge_Shares_Abs'])) * hdg_sign
        hdg_str = f"{hdg_sh_val:>+9,d}주" if hdg_sign != 0 else f"{int(round(r['Hedge_Shares_Abs'])):>9,d}주"
        lines.append(
            f"{r['Option Type']:<4} | {r['Expiration Date']:<11} | ${r['Strike']:>5.1f} | {int(r['Vol_Prev1']):>9,d} | {int(r['Vol_Latest']):>9,d} | "
            f"{oi_str:>16} | {r['Vol_OI_Ratio']:>9.2f}x | {iv_str:>15} | {dg_str:>14} | {hdg_str:>11} | ${r['Price_Latest']:>6.2f} | {r['Intraday_Signal']}"
        )
    lines.append("")

    # ★ [신설 ④-B] 전일(T-1) 기습 거래 상위 계약의 당일(T) 공식 장부(OI) 안착률 및 4분면 확정 추적 (과거 파일 첨부 불필요화)
    lines.append(f"#### ④-B [전일({prev1_date}) 기습 거래 상위 계약의 당일({latest_date}) 공식 장부(OI) 안착 및 4분면 확정 추적]")
    lines.append(" 📌 [표 핵심 독해 가이드] 어제(T-1) 장중 대량 거래가 터졌던 기습 계약들이 오늘(T) 아침 공식 미결제약정(1일OI증감)으로 실제 안착했는지 검증하는 표입니다. 'OI안착률(|1일OI증감|/전일거래량)'이 30% 이상이면 큰손의 진성 신규 포지션(또는 진성 청산)이고, 10% 미만이면 장중 단타(데이턴오버 허수)입니다.")
    lines.append(f"{'구분':<4} | {'만기일(Exp)':<11} | {'행사가':>6} | {'전일거래량(T-1)':>13} | {'전일OI->당일OI':>17} | {'1일OI확정증감':>11} | {'OI안착률(성격)':>16} | {'T-1유효IV변동':>12} | {'당일 확정 OI×IV 4분면 수급 판정'}")
    lines.append("-" * 165)
    prev_amb_candidates = amb_df[
        (amb_df['Vol_Prev1'] >= _amb_min_vol) &
        (amb_df['Expiration Date'] > latest_date)
    ].sort_values(by='Vol_Prev1', ascending=False).head(8)
    for _, r in prev_amb_candidates.iterrows():
        ot_v  = r['Option Type']
        exp_v = r['Expiration Date']
        stk_v = float(r['Strike'])
        v_p1  = int(r['Vol_Prev1'])
        oi_p1 = int(r['OI_Prev1'])
        oi_nw = int(r['OI_Latest'])
        doi_1 = int(r['OI_Chg_1D'])
        settle_rat = (abs(doi_1) / max(v_p1, 1)) * 100.0
        if settle_rat > 100.0:
            settle_tag = "거래량초과변동(행사·정정)"   # ★ [V4.3.3] OI 변동이 전일 거래량보다 크면 거래만으로 설명 불가 (조기 권리행사·배정, 데이터 정정)
        elif settle_rat >= 30.0:
            settle_tag = "진성신규" if doi_1 > 0 else "진성청산"
        elif settle_rat >= 10.0:
            settle_tag = "일부안착" if doi_1 > 0 else "일부청산"
        else:
            settle_tag = "단타소멸"
        ref_tbl = c_tbl if ot_v == 'Call' else p_tbl
        if (exp_v, stk_v) in ref_tbl.index:
            eff_iv_v = float(ref_tbl.loc[(exp_v, stk_v), 'Eff_IV_Chg']) * 100.0
            quad_v   = str(ref_tbl.loc[(exp_v, stk_v), 'Quadrant'])
        else:
            eff_iv_v = float(r['IV_Chg_1D']) * 100.0
            quad_v   = "데이터보류"
        lines.append(
            f"{ot_v:<4} | {exp_v:<11} | ${stk_v:>5.1f} | {v_p1:>13,d} | {f'{oi_p1:>7,d}->{oi_nw:>7,d}':>17} | "
            f"{doi_1:>+11,d} | {f'{settle_rat:>5.1f}%({settle_tag})':>16} | {eff_iv_v:>+10.2f}%p | {quad_v}"
        )
    lines.append("")

    lines.append(f"### ⑤ [클러스터 레이더] 만기(DTE ≤ {cluster_dte}일, 현가 ±15% 이내) 행사가 쪼개기(Strike-Splitting) 클러스터 집계")
    lines.append(" 📌 [표 핵심 독해 가이드] 큰손이 들키지 않으려고 인접 행사가 여러 개에 주문을 잘게 쪼개 넣은 것을 만기별로 합산한 표입니다. 같은 만기일에서 Call과 Put 중 어느 쪽의 '당일총거래량'과 '가중당일IV변동(웃돈)'이 더 강하게 튀어 올랐는지 비교하십시오.")
    lines.append(f"{'만기일(Exp)':<11} | {'구분':<4} | {'활성행사가수':>10} | {'전일총거래량':>11} | {'당일총거래량':>11} | {'잔존총OI(1일증감)':>18} | {'가중평균IV':>9} | {'가중당일IV변동':>13}")
    lines.append("-" * 115)
    for _, r in cluster_df.iterrows():
        oi_c_str = f"{int(r['OI_Latest']):>7,d}({int(r['OI_Chg_1D']):>+6,d})"
        lines.append(
            f"{r['Exp']:<11} | {r['Type']:<4} | {int(r['Active_Strikes']):>8d}개 | {int(r['Vol_Prev1']):>11,d} | {int(r['Vol_Latest']):>11,d} | "
            f"{oi_c_str:>18} | {r['W_IV_Latest']*100:>8.2f}% | {r['W_IV_Chg_1D']*100:>+11.2f}%p"
        )
    lines.append(sep_thin)
    lines.append("")

    # [섹션 3]
    def conv_kr(ewy_target):
        pct = (ewy_target / latest_spot - 1.0) * 100.0
        k_pt = derive_target_fn(ewy_target, 'KOSPI')
        s_krw = int(round(derive_target_fn(ewy_target, 'SAMSUNG'), -2))
        fx_krw = derive_target_fn(ewy_target, 'USDKRW')
        return pct, k_pt, s_krw, fx_krw

    # ★ [V4.3.4] 환율고정 KOSPI: EWY(달러) ≈ KOSPI(원) ÷ 환율 이므로 KOSPI 탄력성 βK = βK' × (1 + βFX) — 환율을 현재 수준에 고정하면 βK' = βK / (1 + βFX)
    _bK, _bF = float(km['beta_ew']), float(fm['beta_ew'])
    _bK_fx = _bK / (1.0 + _bF) if (1.0 + _bF) > 0.2 else _bK
    _ewy_anchor = float(rel_info.get('ewy_anchor_ref', latest_spot)) if float(rel_info.get('ewy_anchor_ref', 0.0) or 0.0) > 1.0 else float(latest_spot)
    def kospi_fx_fixed(ewy_target, k_reg):
        return float(k_reg) * (max(float(ewy_target), 1.0) / max(_ewy_anchor, 1.0)) ** (_bK_fx - _bK)

    c1_pct, c1_kospi, c1_sam, c1_fx = conv_kr(call_wall_1st)
    c2_pct, c2_kospi, c2_sam, c2_fx = conv_kr(call_wall_2nd)
    mp_pct, mp_kospi, mp_sam, mp_fx = conv_kr(mp_nearest)
    b1_pct, b1_kospi, b1_sam, b1_fx = conv_kr(put_bunker_1st)
    bc_pct, bc_kospi, bc_sam, bc_fx = conv_kr(put_bunker_core)
    nng_pct, nng_kospi, nng_sam, nng_fx = conv_kr(near_ng_strike)
    ng_pct, ng_kospi, ng_sam, ng_fx = conv_kr(neg_gamma_strike)

    lines.append("## [섹션 3] 시나리오별 핵심 가격 트리거 및 현물(EWY · KOSPI · 삼성전자) 환산 좌표")
    lines.append(sep_thin)
    lines.append(" 📌 [표 핵심 독해 가이드] EWY 옵션 핵심 행사가(지지선·저항선·Max Pain·감마트랩)에 도달했을 때 이에 대응하는 한국 KOSPI 지수·삼성전자 주가의 시계열 회귀 환산 타점입니다(원/달러 환율은 회귀 설명력이 낮아 환산하지 않고, 대신 '환율고정 KOSPI'로 환율 가정의 영향을 표시). 분할 매수(1·2차 방어선)와 분할 익절(단기MP·1차 Call Wall), 손절(실전 근접 감마트랩 및 실질BEP) 기준표로 활용하십시오.")
    lines.append(f" • [시계열 상관·회귀 관계식 ({rel_info['window_start']} ~ {rel_info['window_end']} | {rel_info.get('freq_unit_str', str(rel_info['n_obs']) + '거래일')})]")
    lines.append(f"   - KOSPI (^KS11)    : 상관계수 r={km['r_pearson']:+.4f} (R²={km['r2_pearson']*100:.1f}%, 미설명 고유리스크={km['unexplained_pct']:.1f}%) | 탄력성 Beta={km['beta_ew']:+.3f} | 회귀기울기={km['slope_ew']:+.2f}pt/$")
    lines.append(f"   - 삼성전자(005930) : 상관계수 r={sm['r_pearson']:+.4f} (R²={sm['r2_pearson']*100:.1f}%, 미설명 고유리스크={sm['unexplained_pct']:.1f}%) | 탄력성 Beta={sm['beta_ew']:+.3f} | 회귀기울기={sm['slope_ew']:+.1f}원/$")
    lines.append(f"   - 원/달러 (KRW=X)  : 상관계수 r={fm['r_pearson']:+.4f} (R²={fm['r2_pearson']*100:.1f}%, 미설명 고유리스크={fm['unexplained_pct']:.1f}%) | 탄력성 Beta={fm['beta_ew']:+.3f} | 회귀기울기={fm['slope_ew']:+.2f}원/$ {'-> 설명력 50% 미만: 환율 환산 미표시' if fm['r2_pearson'] < 0.5 else ''}")
    lines.append(f"   - 항등식 점검(EWY ≈ KOSPI ÷ 환율) : KOSPI 탄력성 {_bK:+.3f} - 환율 탄력성 {_bF:+.3f} = {_bK - _bF:+.3f} (1에 가까우면 세 회귀가 서로 일관) -> KOSPI·삼성전자 환산치에는 이 구간의 평균 환율 동조가 들어 있으므로, 원거리 목표가는 '환율고정 KOSPI'(현재 환율 유지 가정, 탄력성 {_bK_fx:+.3f})와 함께 범위로 읽으십시오.")
    lines.append("-" * 115)
    lines.append(f" • [상단 2차 Call Wall 목표가]      : EWY ${call_wall_2nd:>6.1f} ({c2_pct:>+6.2f}%) | Call OI {call_wall_2nd_oi:>7,d}계약 | KOSPI {c2_kospi:>7,.0f}pt | 삼성전자 {c2_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(call_wall_2nd, c2_kospi):>7,.0f}pt")
    lines.append(f" • [상단 1차 Call Wall 목표가]      : EWY ${call_wall_1st:>6.1f} ({c1_pct:>+6.2f}%) | Call OI {call_wall_1st_oi:>7,d}계약 | KOSPI {c1_kospi:>7,.0f}pt | 삼성전자 {c1_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(call_wall_1st, c1_kospi):>7,.0f}pt")
    lines.append(f" • [최근접 만기({nearest_exp}) Max Pain] : EWY ${mp_nearest:>6.1f} ({mp_pct:>+6.2f}%) | 전체만기 MP ${mp_all:>5.1f} | KOSPI {mp_kospi:>7,.0f}pt | 삼성전자 {mp_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(mp_nearest, mp_kospi):>7,.0f}pt")
    if has_ats_input and (not is_post_us_ovr):
        lines.append(f" • [15:30 동시간대 영점원점(ATS)]  : EWY ${ewy_anchor_ref:>6.2f} (영점원점) | 야간순변동 {overnight_us_gap_pct:>+6.2f}% | KOSPI {CURRENT_KOSPI_PT:>7,.0f}pt | 삼성전자 {CURRENT_SAMSUNG_KRW:>9,d}원 | 환율 {CURRENT_USDKRW:>6.1f}원")
        lines.append(f" • [현재 EWY 미국종가(09시내재가)] : EWY ${latest_spot:>6.2f} (  0.00%) | 당일변동 {daily_chg_pct:>+6.2f}%   | KOSPI {implied_krx_kospi:>7,.0f}pt | 삼성전자 {implied_krx_sam:>9,d}원 | {_fx_s6}")
    elif has_ats_input and is_post_us_ovr:
        post_gap_pct = (ewy_anchor_ref / max(latest_spot, 1e-6) - 1.0) * 100.0
        lines.append(f" • [주간장 실시간 ATS 오버라이드]  : EWY ${ewy_anchor_ref:>6.2f} ({post_gap_pct:>+6.2f}%) | 실시간 동시동기화  | KOSPI {CURRENT_KOSPI_PT:>7,.0f}pt | 삼성전자 {CURRENT_SAMSUNG_KRW:>9,d}원 | 환율 {CURRENT_USDKRW:>6.1f}원")
        lines.append(f" • [미국 정규장 마감종가({latest_date})] : EWY ${latest_spot:>6.2f} (  0.00%) | 당일변동 {daily_chg_pct:>+6.2f}%   | KOSPI {implied_krx_kospi:>7,.0f}pt | 삼성전자 {implied_krx_sam:>9,d}원 | {_fx_s6}")
    else:
        lines.append(f" • [현재 EWY 기준가 ({latest_date})]  : EWY ${latest_spot:>6.2f} (  0.00%) | 당일변동 {daily_chg_pct:>+6.2f}%   | KOSPI {CURRENT_KOSPI_PT:>7,.0f}pt | 삼성전자 {CURRENT_SAMSUNG_KRW:>9,d}원 | 환율 {CURRENT_USDKRW:>6.1f}원")
    lines.append(f" • [하단 1차 전방 Put 방어선]       : EWY ${put_bunker_1st:>6.1f} ({b1_pct:>+6.2f}%) | Put  OI {put_bunker_1st_oi:>7,d}계약 | KOSPI {b1_kospi:>7,.0f}pt | 삼성전자 {b1_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(put_bunker_1st, b1_kospi):>7,.0f}pt")
    lines.append(f" • [하단 2차 핵심 콘크리트 요새]    : EWY ${put_bunker_core:>6.1f} ({bc_pct:>+6.2f}%) | Put  OI {put_bunker_core_oi:>7,d}계약 | KOSPI {bc_kospi:>7,.0f}pt | 삼성전자 {bc_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(put_bunker_core, bc_kospi):>7,.0f}pt")
    lines.append(f" • [실전 근접 감마트랩(현가-15%내)] : EWY ${near_ng_strike:>6.1f} ({nng_pct:>+6.2f}%) | Q1롱풋 +{near_ng_chg:>7,d}계약 | KOSPI {nng_kospi:>7,.0f}pt | 삼성전자 {nng_sam:>9,d}원 | 실질BEP ${near_ng_bep:.2f}")
    if pos_gc_strike is not None:
        gc_pct, gc_kospi, gc_sam, _ = conv_kr(pos_gc_strike)
        lines.append(f" • [실전 근접 감마 방석(Q2풋매도최대)] : EWY ${pos_gc_strike:>6.1f} ({gc_pct:>+6.2f}%) | Q2풋매도 +{pos_gc_chg:>7,d}계약 | KOSPI {gc_kospi:>7,.0f}pt | 삼성전자 {gc_sam:>9,d}원 | 매도자BEP ${pos_gc_bep:.2f} ({pos_gc_exp}) -> 딜러 롱감마(하락 시 저가 매수 헤지)")
    else:
        lines.append(" • [실전 근접 감마 방석(Q2풋매도최대)] : 현가 -15% 이내 신규 Q2 풋 매도 물량 없음")
    lines.append(f" • [네거티브 감마 트랩(전체Q1최대)] : EWY ${neg_gamma_strike:>6.1f} ({ng_pct:>+6.2f}%) | Q1롱풋 +{neg_gamma_chg:>7,d}계약 | KOSPI {ng_kospi:>7,.0f}pt | 삼성전자 {ng_sam:>9,d}원 | 환율고정 KOSPI {kospi_fx_fixed(neg_gamma_strike, ng_kospi):>7,.0f}pt")
    lines.append("")

    # ★ [V4.1 핵심 신설: 월가 표준 5단계 눌림목 하락폭(Pullback Depth) 수치화 및 현물 분할매수 타점 모듈]
    # - 과거 7거래일(all_dates[-7:]) 옵션 데이터 및 근월 ATM IV(Rule of 16) 기반 무창작 월가 표준 수식 산출
    near_iv_dec = float(curr_ts['Near_ATM_IV']) if np.isfinite(curr_ts['Near_ATM_IV']) and curr_ts['Near_ATM_IV'] > 0.05 else 0.45
    imp_1d_drop_pct = -(near_iv_dec / np.sqrt(252.0)) * 100.0
    imp_2d_drop_pct = -(near_iv_dec * np.sqrt(2.0 / 252.0)) * 100.0
    # ★ [V4.3.4] 1단계: 기존 'Max Pain이 현가 아래면 MP, 위면 -1.5% 고정'(MP가 위일 때도 'MP 회귀'로 표기되는 모순) -> 1일 0.5σ 내재변동폭
    #   (최근접 만기 Max Pain 쪽으로 움직인 비율이 기저 상승·하락 비율과 같아 자석 효과가 확인되지 않음 — PB_CAL 실측)
    ewy_pb_stage1 = round(latest_spot * (1.0 + 0.5 * imp_1d_drop_pct / 100.0), 2)
    _mp_side = '위' if float(mp_nearest) >= float(latest_spot) else '아래'
    ewy_pb_stage2 = round(latest_spot * (1.0 + imp_1d_drop_pct / 100.0), 2)

    # 3단계: 1차 감마 방어벽(put_bunker_1st) 및 최근 단기/7일 신규 Put Q2 상위 계약의 실질 BEP(Strike - Price) 중 현가 아래 가장 근접한 본전 방어선
    p_q2_bep_series = p_tbl.index.get_level_values('Strike').values.astype(float) - p_tbl['Price_Latest'].values.astype(float)
    p_tbl_bep = p_tbl.copy()
    p_tbl_bep['Eff_BEP'] = p_q2_bep_series
    valid_q2_beps = p_tbl_bep[
        p_tbl_bep['Is_Clean_Contract'] &
        (p_tbl_bep.index.get_level_values('Expiration Date') > latest_date) &
        (p_tbl_bep['Quadrant'].str.startswith('Q2')) &
        (p_tbl_bep['OI_Chg_Short'] > max(30, int(round(500 * s_oi)))) &
        (p_tbl_bep['Eff_BEP'] < latest_spot * 0.99) &
        (p_tbl_bep['Eff_BEP'] >= latest_spot * 0.90)
    ].sort_values(by='OI_Chg_Short', ascending=False)
    put_q2_bep_1st = float(valid_q2_beps['Eff_BEP'].iloc[0]) if len(valid_q2_beps) > 0 else float(put_bunker_1st)
    ewy_pb_stage3 = round(0.5 * float(put_bunker_1st) + 0.5 * put_q2_bep_1st, 2)

    # 4단계: 만기 2일(OpEx) 1-Sigma 내재 변동폭 (방어율은 PB_CAL 실측치로 표기)
    ewy_pb_stage4 = round(latest_spot * (1.0 + imp_2d_drop_pct / 100.0), 2)

    # 5단계: 최근 7거래일 옵션 총거래량 가중 평균단가(7D Option-Volume VWAP) & Zero-Gamma 콘크리트 풋 요새
    lb_7_dates = all_dates[-7:] if len(all_dates) >= 7 else all_dates
    df_7d_vwap = df_pit[df_pit['Quote Date'].isin(lb_7_dates)].groupby('Quote Date').agg({'EWY Price': 'first', 'Volume': 'sum'})
    opt_vwap_7d = float(np.average(df_7d_vwap['EWY Price'].values, weights=np.maximum(df_7d_vwap['Volume'].values, 1.0)))
    # 순OI(Put-Call)가 양수로 전환되는 최상단 콘크리트 지지 행사가 탐색 (스케일 불변 동적 기준)
    pos_net_puts = wall_map.loc[(wall_map.index < latest_spot) & (wall_map['Net_Put_Minus_Call'] >= max(300.0, 10000.0 * s_oi))]
    zero_gamma_fortress = float(pos_net_puts.index.max()) if len(pos_net_puts) > 0 else float(put_bunker_core)
    ewy_pb_stage5 = round(0.5 * opt_vwap_7d + 0.5 * zero_gamma_fortress, 2)

    # ★ [V4.2 업그레이드 4 신설] 6단계: 1차 요새(put_bunker_1st) 붕괴 시 다단계 감마 도미노(Roll-Down)가 직행하는 '심층 콘크리트 진공 하단(Deep Gamma Vacuum Floor)'
    deep_fortress_candidates = wall_map.loc[
        (wall_map.index < min(put_bunker_1st * 0.96, latest_spot * 0.92)) &
        (wall_map['Net_Put_Minus_Call'] >= max(800.0, 25000.0 * s_oi))
    ].sort_values(by='Put_OI_Latest', ascending=False)
    if len(deep_fortress_candidates) > 0:
        ewy_pb_stage6 = float(deep_fortress_candidates.index[0])
        stage6_put_oi = int(deep_fortress_candidates['Put_OI_Latest'].iloc[0])
        stage6_net_oi = int(deep_fortress_candidates['Net_Put_Minus_Call'].iloc[0])
    else:
        ewy_pb_stage6 = round(min(put_bunker_core, latest_spot * 0.88), 2)
        stage6_put_oi = int(put_bunker_core_oi)
        stage6_net_oi = int(wall_map.loc[put_bunker_core, 'Net_Put_Minus_Call']) if put_bunker_core in wall_map.index else 0

    s1_pct, s1_k, s1_sam, s1_fx = conv_kr(ewy_pb_stage1)
    s2_pct, s2_k, s2_sam, s2_fx = conv_kr(ewy_pb_stage2)
    s3_pct, s3_k, s3_sam, s3_fx = conv_kr(ewy_pb_stage3)
    s4_pct, s4_k, s4_sam, s4_fx = conv_kr(ewy_pb_stage4)
    s5_pct, s5_k, s5_sam, s5_fx = conv_kr(ewy_pb_stage5)
    s6_pct, s6_k, s6_sam, s6_fx = conv_kr(ewy_pb_stage6)

    lines.append("### [섹션 3-2] 과거 7거래일 옵션 데이터 기반 '월가 표준 5단계 눌림목 하락폭 + [V4.2 신설] 6단계 감마 진공(Roll-Down) 최종 하단 조견표'")
    lines.append(" 📌 [표 핵심 독해 가이드] 상승장(레짐 A) 도중 단기 과열([섹션 1-4] 징후 점화)로 기술적 눌림목이 발생할 때는 2~4단계(방어율은 표 아래 실측치)에서 분할 매수하되, '🚨중기 상방 연료 고갈 & 고점 분배(Distribution Crash) 경보'가 켜진 상태에서 3단계(1차 Put 방어벽 및 실질 BEP)가 붕괴될 경우에는 기계적 물타기를 즉시 중단하고 '6단계: 다단계 감마 도미노 최종 하단(심층 콘크리트 풋 요새)'까지 하방을 열어두어야 합니다.")
    lines.append(f"{'눌림목 / 하락 단계 구분':<26} | {'월가 표준 산출 공식 및 미시구조 근거':<40} | {'예상하락률':>8} | {'EWY타깃':>8} | {'내재KOSPI':>9} | {'내재삼성전자':>11} | {'권장대응(레짐별 행동지침)'}")
    lines.append("-" * 148)
    _st_rows = []  # ★ [V4.2.8 ⑤] 단계 행을 모은 뒤 깊이 순으로 출력
    _st_rows.append((ewy_pb_stage1, f"{'1단계: 얕은 눌림(0.5σ)':<26} | {f'1일 0.5σ 내재변동폭 (참고 MP ${mp_nearest:.1f}: 현가 {_mp_side})':<40} | {s1_pct:>+7.2f}% | ${ewy_pb_stage1:>7.2f} | {s1_k:>7,.0f}pt | {s1_sam:>9,d}원 | {'관망(추격금지)' if is_distribution_crash_regime else '1차 가벼운 눌림목 (대기자금 20%)'}"))
    _st_rows.append((ewy_pb_stage2, f"{'2단계: 표준 1일 하단(1σ)':<26} | {f'1일 1σ 내재변동폭 (Rule of 16, IV {near_iv_dec*100:.1f}%)':<40} | {s2_pct:>+7.2f}% | ${ewy_pb_stage2:>7.2f} | {s2_k:>7,.0f}pt | {s2_sam:>9,d}원 | {'단기 지지 테스트 (매수 보류)' if is_distribution_crash_regime else '표준 1일 조정 하단 (대기자금 30%)'}"))
    _st_rows.append((ewy_pb_stage3, f"{'3단계: 기관 1차 본전방어선':<26} | {f'1차 Put방어벽(${put_bunker_1st:.1f}) & 신규Put BEP(${put_q2_bep_1st:.2f})':<40} | {s3_pct:>+7.2f}% | ${ewy_pb_stage3:>7.2f} | {s3_k:>7,.0f}pt | {s3_sam:>9,d}원 | {'🚨이탈 시 감마도미노 점화(손절/헤지)' if is_distribution_crash_regime else '기관 본전 수렴 지지선 (대기자금 30%)'}"))
    _st_rows.append((ewy_pb_stage4, f"{'4단계: 만기 2일 한계(2일 1σ)':<26} | {f'2일(OpEx) 1σ 내재변동폭 (만기 언더슈팅 한계)':<40} | {s4_pct:>+7.2f}% | ${ewy_pb_stage4:>7.2f} | {s4_k:>7,.0f}pt | {s4_sam:>9,d}원 | {'하방 롤다운 가속 구간 (관망)' if is_distribution_crash_regime else '만기 변동성 확대 한계 (잔여 20% 투입)'}"))
    _st_rows.append((ewy_pb_stage5, f"{'5단계: 코어 매집원가 피벗':<26} | {f'7일 옵션거래량 VWAP(${opt_vwap_7d:.2f}) & 풋요새(${zero_gamma_fortress:.1f})':<40} | {s5_pct:>+7.2f}% | ${ewy_pb_stage5:>7.2f} | {s5_k:>7,.0f}pt | {s5_sam:>9,d}원 | {'중기 추세 붕괴 분기점' if is_distribution_crash_regime else '스마트머니 7일 원가 (코어 홀딩 마지노선)'}"))
    _st_rows.append((ewy_pb_stage6, f"{'6단계: 감마진공 최종하단(신설)':<26} | {f'심층 콘크리트 요새(${ewy_pb_stage6:.1f}, PutOI {stage6_put_oi:,}/순OI +{stage6_net_oi:,})':<40} | {s6_pct:>+7.2f}% | ${ewy_pb_stage6:>7.2f} | {s6_k:>7,.0f}pt | {s6_sam:>9,d}원 | 1차요새 붕괴 시 최종 진바닥 타깃"))
    for _pv, _ln in sorted([t for t in _st_rows if t[0] <= float(latest_spot)], key=lambda t: -t[0]):
        lines.append(_ln)
    for _pv, _ln in [t for t in _st_rows if t[0] > float(latest_spot)]:
        lines.append(_ln + "  <- [현가 위: 눌림목 아닌 탈환선]")
    lines.append(f" • [실측 (2024-03~2026-11 {PB_CAL['n']}거래일, 종가 기준)] 다음 거래일 종가가 1단계 위 {PB_CAL['s1']}% · 2단계 위 {PB_CAL['s2']}% | 2거래일 뒤 종가가 4단계 위 {PB_CAL['s4']}% | 최근접 만기 Max Pain 쪽으로 만기까지 움직인 비율: MP가 위일 때 {PB_CAL['mp_up']}%(기저 상승 {PB_CAL['base_up']}%) · 아래일 때 {PB_CAL['mp_dn']}%(기저 하락 {PB_CAL['base_dn']}%) -> Max Pain 자석 효과 미확인")
    lines.append("")

    # ★ [V4.1 핵심 신설: 섹션 3-3] 당일 기습 풋(Ambush Put) 포착 시 '원인 ①(전면적 수급 역전·직하단 본대 연쇄 점화)' × '원인 ②(ATM 최대 감마·딜러 강제 헤지 매도량)' 통합 진단 및 완전판 하락폭 산출 공식
    amb_call_bull_cnt = int((top_ambush['Intraday_Signal'].str.contains('상방매집')).sum())
    amb_put_bear_cnt  = int((top_ambush['Intraday_Signal'].str.contains('하방공습')).sum())
    amb_call_cap_cnt  = int((top_ambush['Intraday_Signal'].str.contains('상단캡')).sum())
    tot_top_amb_cnt   = max(len(top_ambush), 1)
    bear_ambush_ratio = (amb_put_bear_cnt + amb_call_cap_cnt) / tot_top_amb_cnt * 100.0
    is_reg_b_top      = regime_ranking[0][0].startswith("레짐 B")

    # (A) 원인 ②: 현가 근접(-15% ~ +3%) 당일 최상위 기습 풋 탐색 (스케일 불변 동적 거래량 기준)
    near_amb_puts = amb_df[
        amb_df['Is_Valid_Quote'] &
        (amb_df['Option Type'] == 'Put') &
        (amb_df['DTE_Latest'] >= 1) &
        (amb_df['DTE_Latest'] <= 90) &
        (amb_df['Strike'] >= latest_spot * 0.85) &
        (amb_df['Strike'] <= latest_spot * 1.03) &
        (amb_df['Vol_Latest'] >= max(15, int(round(300 * s_vol))))
    ].copy()

    if len(near_amb_puts) > 0:
        near_amb_puts['Ambush_Impact_Score'] = (
            near_amb_puts['Hedge_Shares_Abs'] *
            (1.0 + np.maximum(0.0, near_amb_puts['IV_Chg_1D'] * 12.0)) *
            np.where(near_amb_puts['IV_Chg_1D'] > 0, 1.5, 0.5)
        )
        top_ap = near_amb_puts.sort_values(by='Ambush_Impact_Score', ascending=False).iloc[0]
        ap_exp    = str(top_ap['Expiration Date'])
        ap_strike = float(top_ap['Strike'])
        ap_vol    = int(top_ap['Vol_Latest'])
        ap_oi     = int(top_ap['OI_Latest'])
        ap_vol_oi = float(top_ap['Vol_OI_Ratio'])
        ap_iv     = float(top_ap['IV_Latest'] * 100.0)
        ap_div    = float(top_ap['IV_Chg_1D'] * 100.0)
        ap_delta0 = float(top_ap['BS_Delta'])
        ap_gamma0 = float(top_ap['BS_Gamma'])
        ap_shares_t0 = int(round(top_ap['Hedge_Shares_Abs']))
        ap_notional_usd = ap_vol * 100.0 * latest_spot
        # 1σ 하향 돌파 시점(Spot * (1 + imp_1d_drop_pct/100)) 및 스큐 +3%p 확대 시 팽창 델타 계산
        sp_stress = min(ap_strike, latest_spot * (1.0 + imp_1d_drop_pct / 100.0))
        T_ap = max(float(top_ap['DTE_Latest']) / 365.0, 1.0 / 365.0)
        sig_stress = max(float(top_ap['IV_Latest']) + 0.03, 0.15)
        d1_stress = (np.log(sp_stress / max(ap_strike, 1.0)) + (0.048 + 0.5 * sig_stress**2) * T_ap) / (sig_stress * np.sqrt(T_ap))
        ap_delta_stress = float(stats.norm.cdf(d1_stress) - 1.0)
        ap_shares_stress = int(round(ap_vol * 100.0 * abs(ap_delta_stress)))
        has_near_ambush_put = (ap_div >= 0.5) and (ap_vol >= max(25, int(round(500 * s_vol))))
    else:
        ap_exp, ap_strike, ap_vol, ap_oi, ap_vol_oi = nearest_exp, put_bunker_1st, 0, 0, 0.0
        ap_iv, ap_div, ap_delta0, ap_gamma0 = near_iv_dec * 100.0, 0.0, -0.30, 0.010
        ap_shares_t0, ap_notional_usd, ap_delta_stress, ap_shares_stress = 0, 0.0, -0.35, 0
        has_near_ambush_put = False

    # (B) 원인 ①: 기습 풋 직하단(현가 -1% ~ -8%)에 대기 중인 '풋 본대(Cascade Put Pool)' 탐색 및 연쇄 점화 물량 계산
    cascade_upper_bound = min(ap_strike - 0.5, latest_spot * 0.99) if has_near_ambush_put else latest_spot * 0.99
    q1_cascade_sub = p_tbl[
        p_tbl['Quadrant'].str.startswith('Q1') &
        (p_tbl.index.get_level_values('Strike') <= cascade_upper_bound) &
        (p_tbl.index.get_level_values('Strike') >= latest_spot * 0.90)
    ].sort_values(by='OI_Chg_Short', ascending=False)

    if len(q1_cascade_sub) > 0:
        cas_exp, cas_strike = q1_cascade_sub.index[0]
        cas_strike = float(cas_strike)
        cas_q1_chg = int(q1_cascade_sub['OI_Chg_Short'].iloc[0])
        cas_contract_oi = int(q1_cascade_sub['OI_Latest'].iloc[0])
        cas_tot_wall_oi = int(wall_map.loc[cas_strike, 'Put_OI_Latest']) if cas_strike in wall_map.index else cas_contract_oi
        cas_bep = float(cas_strike - q1_cascade_sub['Price_Latest'].iloc[0])
    else:
        # ★ [V4.2.8 ⑤] 기존: 만기·Q1·BEP는 감마트랩 계약, 행사가·OI는 1차 방어선 합산에서 가져와 존재하지 않는 계약 생성
        #               변경: 1차 방어선 행사가의 잔존 OI 최대 계약(당일 만기 제외) 한 개로 모든 값을 채움, 없으면 감마트랩 계약 한 개로 채움
        _cas_cand = p_tbl[(p_tbl.index.get_level_values('Strike') == float(put_bunker_1st)) & (p_tbl.index.get_level_values('Expiration Date') > latest_date)]
        if len(_cas_cand) > 0:
            _ck = _cas_cand['OI_Latest'].idxmax()
            cas_exp, cas_strike = _ck[0], float(_ck[1])
            cas_q1_chg = int(_cas_cand.loc[_ck, 'OI_Chg_Short']) if str(_cas_cand.loc[_ck, 'Quadrant']).startswith('Q1') else 0
            cas_contract_oi = int(_cas_cand.loc[_ck, 'OI_Latest'])
            cas_bep = float(cas_strike - _cas_cand.loc[_ck, 'Price_Latest'])
        else:
            cas_exp, cas_strike, cas_q1_chg, cas_contract_oi, cas_bep = near_ng_exp, float(near_ng_strike), int(near_ng_chg), 0, float(near_ng_bep)
        cas_tot_wall_oi = int(wall_map.loc[cas_strike, 'Put_OI_Latest']) if cas_strike in wall_map.index else cas_contract_oi

    # 기습 풋(ap_vol) + 직하단 신규 Q1 본대(cas_q1_chg) 합산 딜러 강제 헤지 매도 주수 산출
    cas_delta_est = -0.35
    cas_delta_stress = -0.45
    # ★ [V4.3.3] 원인 ① 본대 실재 검증: '작은 뇌관(기습 풋)이 아래의 더 큰 풋 본대를 깨운다'는 전제이므로,
    #   직하단 본대의 신규 Q1 물량이 만드는 딜러 헤지 매도 주수가 뇌관의 초동 헤지 매도 주수 이상일 때만 연쇄 점화 성립
    cas_army_shares = int(round(max(cas_q1_chg, 0) * 100.0 * abs(cas_delta_est)))
    cas_army_valid  = bool(has_near_ambush_put and (cas_army_shares >= max(ap_shares_t0, 1)))
    cas_army_ratio  = cas_army_shares / max(ap_shares_t0, 1)
    comb_shares_t0 = ap_shares_t0 + int(round(max(cas_q1_chg, 0) * 100.0 * abs(cas_delta_est)))
    comb_shares_stress = ap_shares_stress + int(round(max(cas_q1_chg, 0) * 100.0 * abs(cas_delta_stress)))
    comb_gamma_expansion = comb_shares_stress - comb_shares_t0

    # (C) 5팩터 완전판 기습 풋 하락폭 산출 공식 (Complete Ambush Gamma-Vanna-Cascade Formula)
    # - 1차 기본 3팩터 모델 (단독 기습 풋 충격): 0.807*(1일1σ%) - 0.207*(|Δ0|*min(ΔIV,15)) + 0.056*(순OI 양전환 피벗 거리%)
    pos_piv_strikes = wall_map.loc[(wall_map.index < latest_spot * 0.995) & (wall_map.index >= latest_spot * 0.88) & (wall_map['Net_Put_Minus_Call'] >= max(100.0, 2000.0 * s_oi))]
    pos_piv_strike = float(pos_piv_strikes.index.max()) if len(pos_piv_strikes) > 0 else float(put_bunker_1st)
    dist_pos_piv_pct = (pos_piv_strike / latest_spot - 1.0) * 100.0

    f1_base_sigma = 0.807 * imp_1d_drop_pct
    f2_vanna_shock = -0.207 * abs(ap_delta0) * min(max(ap_div, 0.0), 15.0) if has_near_ambush_put else 0.0
    f3_vacuum_pull = 0.056 * dist_pos_piv_pct
    # 1차 타깃 (단독 기습 풋 3팩터 예상 하락률)
    amb_drop_stage1_pct = f1_base_sigma + f2_vanna_shock + f3_vacuum_pull
    ewy_amb_target1 = round(latest_spot * (1.0 + amb_drop_stage1_pct / 100.0), 2)

    # 원인 ② 가속항 (딜러 초동 헤지 매도 주수 동적 스케일링: 2026년 10만 주 기준 -> 과거 거래량 비례 자동 축소)
    f4_cause2_gamma = -min(1.20, 0.35 * (ap_shares_t0 / max(2500.0, 100000.0 * s_vol)) * (ap_gamma0 / 0.015)) if has_near_ambush_put else 0.0
    # 원인 ① 가속항 (전면적 수급 역전 & 직하단 본대 연쇄 점화 동적 스케일링):
    # ★ [V4.3.3] 본대 실재 검증 추가: 수급 역전 조건(레이더 70%+ 또는 1순위 레짐 B)에 더해 직하단 본대의 헤지 매도가 뇌관 이상일 때만 점화
    is_bear_shift_active = has_near_ambush_put and cas_army_valid and ((bear_ambush_ratio >= 70.0) or is_reg_b_top)
    # ★ [V4.3.7] 병행(검증 중) 원인①② — 판정에는 쓰지 않고 신호 기록·데이터 품질 점검에만 남김
    try:
        _sh_o = shadow_ambush_v437(amb_df, p_tbl, ts_metrics, latest_date, prev1_date, latest_spot, daily_chg_pct, s_vol, s_oi, is_reg_b_top,
                                   latest_date, put_bunker_1st, near_ng_chg, mode='orig')
        _sh = shadow_ambush_v437(amb_df, p_tbl, ts_metrics, latest_date, prev1_date, latest_spot, daily_chg_pct, s_vol, s_oi, is_reg_b_top,
                                 latest_date, put_bunker_1st, near_ng_chg, mode='shadow')
        _sh['orig_ok'] = (_sh_o['c1'] == bool(is_bear_shift_active)) and (_sh_o['c2'] == bool(has_near_ambush_put))
        _dq['shadow'] = _sh
    except Exception as _sh_e:
        _sh = {}
        _dq['shadow_err'] = str(_sh_e)
    f5_cause1_cascade = -min(1.50, (0.30 + 0.12 * (max(cas_q1_chg, 0) / max(50.0, 1000.0 * s_oi)))) if is_bear_shift_active else 0.0

    # 2차 타깃 (원인 ① 본대 연쇄 점화 + 원인 ② ATM 최대 감마 팽창 결합 시 최대 확장 하락률)
    amb_drop_stage2_pct = amb_drop_stage1_pct + f4_cause2_gamma + f5_cause1_cascade
    ewy_amb_target2 = round(latest_spot * (1.0 + amb_drop_stage2_pct / 100.0), 2)

    amb1_pct, amb1_k, amb1_sam, amb1_fx = conv_kr(ewy_amb_target1)
    amb2_pct, amb2_k, amb2_sam, amb2_fx = conv_kr(ewy_amb_target2)
    sam_drop1_krw = amb1_sam - implied_krx_sam
    sam_drop2_krw = amb2_sam - implied_krx_sam

    lines.append("### [섹션 3-3] [V4.1 핵심 신설] 당일 기습 풋(Ambush Put) '원인 ①(수급역전·본대 연쇄점화)' × '원인 ②(ATM 최대감마·딜러 강제매도)' 진단 및 완전판 하락폭 공식 조견표")
    lines.append(" 📌 [표 핵심 독해 가이드] 당일 근접 기습 풋([섹션 2-④])이 포착됐을 때 딜러 헤지 매도가 하락을 키우는 2대 증폭 경로(원인 ①·②)와, 두 경로가 작동한다고 가정한 EWY·삼성전자 조건부 하방 시나리오입니다. 원인 ①은 수급 역전 조건(레이더 하방·상단캡 지배력 70% 이상 또는 1순위 레짐 B)을 충족하면서 직하단 본대의 헤지 매도 규모가 뇌관(기습 풋) 이상일 때만 점화됩니다. [섹션 5] 신뢰도표상 원인 ①·②는 '참고' 신호이므로 아래 타깃은 예측치가 아니라 원인이 작동할 경우의 하방 범위로 읽고, 표 아래 실측 도달률을 함께 확인하십시오.")
    _c1_rel = next((r_[9] for r_ in PHASE_REL['rows'] if r_[1] == 'c1'), '-')
    _c2_rel = next((r_[9] for r_ in PHASE_REL['rows'] if r_[1] == 'c2'), '-')
    lines.append(f" • [원인 ① 진단 — 전면적 수급 역전 & 직하단 풋 본대 연쇄 점화] : {'🚨점화(ON)' if is_bear_shift_active else '⚪미점화(OFF)'} (신뢰도표: {_c1_rel})")
    lines.append(f"   - 미결산 레이더 전면적 수급 역전도 : 상위 {tot_top_amb_cnt}개 중 🔥상방콜 {amb_call_bull_cnt}건 vs (🚨하방풋 {amb_put_bear_cnt}건 + 🧱커버드콜 {amb_call_cap_cnt}건) -> 하방·상단캡 지배력 {bear_ambush_ratio:.1f}% | 1순위 레짐: {regime_ranking[0][0]} -> 수급 역전 조건(70%+ 또는 레짐 B 1순위): {'충족(레이더 70%+)' if bear_ambush_ratio >= 70.0 else ('충족(레짐 B 1순위 경로)' if is_reg_b_top else '미충족')}")
    lines.append(f"   - {'직하단 연쇄 점화 대기 풋 본대    ' if has_near_ambush_put else '현가 아래 신규 Q1 풋 본대(원인② 미점화 · 현가 -1~-10% 탐색)'}: {cas_exp} ${cas_strike:.1f} Put (단기 Q1 +{cas_q1_chg:,}계약 / 계약OI {cas_contract_oi:,}계약 / 행사가 총Put OI {cas_tot_wall_oi:,}계약 / 실질BEP ${cas_bep:.2f})")
    if has_near_ambush_put:
        lines.append(f"   - 본대 실재 검증(본대 헤지 ≥ 뇌관 초동헤지) : {'충족' if cas_army_valid else '미충족'} — 본대 신규 Q1 헤지 -{cas_army_shares:,}주 vs 뇌관 초동헤지 -{ap_shares_t0:,}주 ({cas_army_ratio:.2f}배)")
    else:
        lines.append("   - 본대 실재 검증 : 해당 없음(원인② 미점화로 기폭 풋이 없어 비교하지 않음)")
    lines.append(f" • [원인 ② 진단 — 현가 코앞 Near-ATM 최대 감마 타격 & 딜러 기계적 헤지 매도량] : {'🚨점화(ON)' if has_near_ambush_put else '⚪미점화(OFF)'} (신뢰도표: {_c2_rel})")
    _c2_thr = max(25, int(round(500 * s_vol)))
    if has_near_ambush_put:
        lines.append(f"   - 최상위 근접 기습 풋(Detonator)   : {ap_exp} ${ap_strike:.1f} Put (당일거래량 {ap_vol:,}계약 / 당일OI {ap_oi:,}계약 / 회전율 {ap_vol_oi:.2f}x / 당일IV {ap_div:+.2f}%p 상승[IV {ap_iv:.1f}%] / 명목원금 ${ap_notional_usd/1e6:.2f}M)")
    elif ap_vol > 0:   # ★ [V4.3.7] 원인② 미점화일: 기폭 풋이 아니라 후보 계약임을 밝히고, IV 하락(풋 매도·청산 성격)이면 딜러 헤지 방향을 매수로 표기
        _dir_s = '상승' if ap_div > 0 else ('하락' if ap_div < 0 else '변화 없음')
        _hed_s = (f" · 레이더 분류상 풋 매도/청산 성격 -> 딜러 초동 헤지는 매수(+{ap_shares_t0:,}주)" if ap_div <= -0.5 else "")
        lines.append(f"   - 근접 풋 최다 거래 후보(기폭 풋 아님): {ap_exp} {ap_strike:.1f} Put (당일거래량 {ap_vol:,}계약 / 당일OI {ap_oi:,}계약 / 회전율 {ap_vol_oi:.2f}x / 당일IV {ap_div:+.2f}%p {_dir_s}[IV {ap_iv:.1f}%]) "
                     f"— 원인② 조건(당일 IV +0.5%p 이상 & 거래량 {_c2_thr:,}계약 이상) 미충족{_hed_s}")
    else:
        lines.append("   - 근접 풋 후보 : 현가 -15%~+3% 구간에 조건을 넘는 당일 거래 풋 없음")
    if has_near_ambush_put:
        lines.append(f"   - 실시간 그리스 & 딜러 강제 매도량 : 초기 델타(Δ0) {ap_delta0:+.3f}, 감마(Γ0) {ap_gamma0:.4f} -> 체결 즉시 딜러 초동 헤지 매도 -{ap_shares_t0:,}주 (본대 합산 -{comb_shares_t0:,}주) | 1σ 돌파 시 감마팽창 누적 -{comb_shares_stress:,}주 (추가 -{comb_gamma_expansion:,}주 강제 투매)")
    else:
        lines.append(f"   - 실시간 그리스 : 초기 델타(Δ0) {ap_delta0:+.3f}, 감마(Γ0) {ap_gamma0:.4f} — 원인② 미점화라 딜러 강제 매도량은 계산하지 않습니다.")
    lines.append("-" * 150)
    lines.append(f"{'완전판 공식 단계 구분':<26} | {'수리적 산출 공식 구성 팩터 (F1~F5 결합)':<42} | {'예상하락률':>8} | {'EWY타깃':>8} | {'내재KOSPI':>9} | {'내재삼성전자(하락폭)':>20} | {'실전대응 가이드'}")
    lines.append("-" * 150)
    lines.append(f"{'1차: 기습 풋 단독 타깃(3팩터)':<26} | {f'F1({f1_base_sigma:+.2f}%)+F2({f2_vanna_shock:+.2f}%)+F3({f3_vacuum_pull:+.2f}%)':<42} | {amb1_pct:>+7.2f}% | ${ewy_amb_target1:>7.2f} | {amb1_k:>7,.0f}pt | {f'{amb1_sam:>9,d}원({sam_drop1_krw:>+7,d}원)':>20} | {'조건부 1차 하방 시나리오 (원인② 작동 시)' if has_near_ambush_put else '원인② 미점화 — 1일 1σ 기본 하방폭 참고'}")
    lines.append(f"{'2차: 본대 연쇄점화 타깃(5팩터)':<26} | {f'1차+원인②감마({f4_cause2_gamma:+.2f}%)+원인①연쇄({f5_cause1_cascade:+.2f}%)':<42} | {amb2_pct:>+7.2f}% | ${ewy_amb_target2:>7.2f} | {amb2_k:>7,.0f}pt | {f'{amb2_sam:>9,d}원({sam_drop2_krw:>+7,d}원)':>20} | {f'${cas_strike:.1f} 본대 연쇄 점화 시 확장 시나리오' if is_bear_shift_active else '원인① 미점화 -> 원인② 감마 확장분만 반영'}")
    lines.append(f" • [실측 도달률 (2024-03~2026-11 {AMB_CAL['n']}거래일, 종가 기준)] 다음 거래일 종가 ≤ 1차 타깃: 전체 {AMB_CAL['t1_all']}% · 원인② 점화일 {AMB_CAL['t1_c2']}%(n={AMB_CAL['n_c2']}) | 5거래일 내 최저 종가 ≤ 1차 타깃: 전체 {AMB_CAL['t1_all5']}% · 원인② 점화일 {AMB_CAL['t1_c25']}% | 원인① 점화일(n={AMB_CAL['n_c1']}) 2차 타깃: 다음날 {AMB_CAL['t2_c1']}% · 5일 내 {AMB_CAL['t2_c15']}%")
    lines.append(sep_thin)
    lines.append("")

    # [섹션 4] AI 추론 한계점 검증 및 반대 시나리오(Devil's Advocate) 정량 스트레스 테스트 지표
    # [V4.1 4대 정제 규칙 작동 통계 산출]
    r1_put_cnt = int(p_tbl['Rule1_ZeroVol_Fail'].sum())
    r2_put_cnt = int(p_tbl['Rule2_Spread_Fail'].sum())
    r3_put_cnt = int(p_tbl['Rule3_Moneyness_Fail'].sum())
    clean_put_cnt = int(p_tbl['Is_Clean_Contract'].sum())

    lines.append("## [섹션 4] AI 추론 한계점 검증 및 반대 시나리오(Devil's Advocate) 정량 스트레스 테스트 지표")
    lines.append(sep_thin)
    lines.append(" 0) [V4.1 야후파이낸스 4대 가짜 IV 필터링 & 고정비율 행사가 추적(Rolling Strike) 정제 요약]")
    lines.append(f"    • 규칙1(Zero-Volume < {YF_MIN_VOLUME_CUTOFF}계약 유령호가 차단) : Put {r1_put_cnt:,}개 계약 IV 급등 무효화(NaN/0%)")
    lines.append(f"    • 규칙2(Bid-Ask 스프레드 비율 > {YF_MAX_SPREAD_RATIO*100:.0f}% 차단) : Put {r2_put_cnt:,}개 호가경직성 착시 계약 강등")
    lines.append(f"    • 규칙3(괴리율 기반 유사델타 < 0.1 노이즈 폐기)  : Put {r3_put_cnt:,}개 스마일 슬라이딩 계약 폐기 (최종 진성 유효 Put {clean_put_cnt:,}개)")
    lines.append(f"    • 규칙4(고정비율 행사가 추적 Rolling Strike)     : 전일 동일 괴리율(%) 행사가 보간 IV 대비 순수 IV 변동만 추출 완료")
    lines.append(f" 1) [일봉 스냅샷 한계 검증 (체결일 귀속 유효IV vs T 당일 실시간 IV 부호 역전 계약)]")
    lines.append(f"    • 부호 역전(Sign-Flip) 포착 건수 : Call {len(c_sign_flip)}건 / Put {len(p_sign_flip)}건 ({w_short}일 OI증가 > 300계약 중)")
    lines.append(f"    • 주요 역전 계약 상세            : {flip_summary_str}")
    lines.append(f"    • [V4.3.4 체결일 귀속 보정] 창 전체 IV로 분류했다면 분면이 바뀌었을 계약 : Put {len(p_reclass)}건 / Call {len(c_reclass)}건 — {reclass_summary_str}")
    lines.append(f" 2) [초외가격(Deep OTM, 현가 ±20% 바깥) 수량 왜곡 비중 검증]")
    lines.append(f"    • Put  Q1(원시총합 +{p_q1_raw_tot:,}계약) 중 현가 -20% 이하 초외가격 거품 : +{p_q1_deep_otm:,}계약 ({p_q1_deep_pct:.1f}% 제외됨) -> 모델 반영 실전 근접 Q1 풋은 +{p_q1_sum:,}계약({100.0-p_q1_deep_pct:.1f}%)")
    lines.append(f"    • Call Q2(원시총합 +{c_q2_raw_tot:,}계약) 중 현가 +20% 이상 초외가격 거품 : +{c_q2_deep_otm:,}계약 ({c_q2_deep_pct:.1f}% 제외됨) -> 모델 반영 실전 근접 Q2 콜은 +{c_q2_sum:,}계약({100.0-c_q2_deep_pct:.1f}%)")
    lines.append(f" 3) [단기창({w_short}D) vs 장기창({w_long}D) 수급 모멘텀 다이버전스 및 {traj_days}영업일 에너지 추이]")
    lines.append(f"    • Call Q1 진성매수 {traj_days}영업일 추이 : {cq1_first:+,}계약({traj_df.iloc[0]['Date']}) -> {cq1_last:+,}계약({latest_date}) [변화율 {cq1_trend_pct:+.1f}%] | {w_long}일 누적 +{c_q1_long:,}계약")
    lines.append(f"    • Put  Q2 바닥매도 {traj_days}영업일 추이 : {pq2_first:+,}계약({traj_df.iloc[0]['Date']}) -> {pq2_last:+,}계약({latest_date}) | {w_long}일 누적 +{p_q2_long:,}계약 (이월 탈락 착시 대조용)")
    lines.append(f" 4) [회귀 모델 미설명 고유 리스크(1 - R²) 및 매크로 오버라이드 경계]")
    lines.append(f"    • 한국 시장 독자 변동분(1 - R²)  : KOSPI {km['unexplained_pct']:.1f}% / 삼성전자 {sm['unexplained_pct']:.1f}% / 원달러 환율 {fm['unexplained_pct']:.1f}% (EWY 옵션만으로 설명 불가한 현물 고유 영역)")
    lines.append(f" 5) [Devil's Advocate 반증 트리거 (1순위 지배 전략 '{regime_ranking[0][0]}' 기각 조건)]")
    lines.append(f"    • 상방 돌파 반증선 (Bear->Bull 전환) : EWY ${mp_nearest:.1f}(단기MP, KOSPI {mp_kospi:,.0f}pt / 삼성전자 {mp_sam:,}원) 돌파 및 근월 IV {(curr_ts['Near_ATM_IV']-0.05)*100:.1f}% 이하 급락 시 하방 뷰 즉시 폐기")
    lines.append(f"    • 하방 붕괴 반증선 (Bull->Bear 전환) : EWY ${put_bunker_core:.1f}(2차요새, KOSPI {bc_kospi:,.0f}pt / 삼성전자 {bc_sam:,}원) 및 근접Q1 BEP ${near_ng_bep:.2f} 이탈 시 상방 뷰 즉시 폐기")
    lines.append(sep_thin)
    lines.append("")

    # --------------------------------------------------------------------------
    # [신규 V4.1 섹션 5] 투자자용 30초 실전 판독 3단계 순서 정리 (실시간 데이터 자동 대입본)
    # --------------------------------------------------------------------------
    fuel_state = "연속 증가(상승 연료 충전)" if cq1_last >= cq1_first else f"감소 추세({cq1_trend_pct:+.1f}%, 단기 상승 연료 소모/둔화)"
    _cq_r = (c_q1_sum + 1.0) / (c_q2_sum + 1.0)   # ★ [V4.3.7] 크기 비교만 하던 '압도' -> 배율 기준(1.5배 압도 · 1.15배 우위 · 그 사이 박빙)
    if _cq_r >= 1.5:
        cap_vs_fuel = f"상승 연료(Call Q1)가 천장 뚜껑(Call Q2)을 압도(x{_cq_r:.2f})하여 상방 돌파 우위"
    elif _cq_r >= 1.15:
        cap_vs_fuel = f"상승 연료(Call Q1)가 천장 뚜껑(Call Q2)보다 우위(x{_cq_r:.2f})"
    elif _cq_r <= 1.0 / 1.15:
        cap_vs_fuel = f"천장 뚜껑(Call Q2)이 연료(Call Q1)보다 두꺼워(x{1.0 / _cq_r:.2f}) 단기 돌파 시 눌림목 경계"
    else:
        cap_vs_fuel = f"상승 연료(Call Q1)와 천장 뚜껑(Call Q2)이 박빙(x{_cq_r:.2f})"
    regc_jump_str = f"전일 {prev_prob_c:.1f}% -> 당일 {prob_c:.1f}% ({prob_c - prev_prob_c:+.1f}%p)"
    if daily_chg_pct > 0 and (prob_c - prev_prob_c >= 5.0 or curr_ts['Term_Near_Back'] >= 0.05):
        siren_verdict = "🚨 [경보] 주가는 올랐으나 레짐C(감마폭발) 또는 단기 백워데이션이 치솟은 '화창한 날의 시한폭탄 설치' 구간 (추격 매수 금지)"
    elif daily_chg_pct < 0 and curr_ts['Term_Near_Back'] <= 0.02:
        siren_verdict = "✅ [안정] 주가는 조정받았으나 단기 과열(백워데이션)이 낮고 변동성이 동결/안정화된 '건전한 눌림목 소화' 구간"
    else:
        siren_verdict = f"⚡ [관찰] 주가({daily_chg_pct:+.2f}%)와 단기 백워데이션({curr_ts['Term_Near_Back']*100:+.2f}%p)이 동행하는 변동성 공방 구간"

    amb_call_cnt = int((top_ambush['Intraday_Signal'].str.contains('상방매집')).sum())
    amb_put_cnt  = int((top_ambush['Intraday_Signal'].str.contains('하방공습')).sum())
    if len(cluster_df) > 0:
        first_exp = cluster_df['Exp'].iloc[0]
        c_cl = cluster_df[(cluster_df['Exp'] == first_exp) & (cluster_df['Type'] == 'Call')]
        p_cl = cluster_df[(cluster_df['Exp'] == first_exp) & (cluster_df['Type'] == 'Put')]
        c_cl_str = f"Call 거래량 {int(c_cl['Vol_Latest'].iloc[0]):,}계약(IV {c_cl['W_IV_Chg_1D'].iloc[0]*100:+.2f}%p)" if len(c_cl) > 0 else "Call 없음"
        p_cl_str = f"Put 거래량 {int(p_cl['Vol_Latest'].iloc[0]):,}계약(IV {p_cl['W_IV_Chg_1D'].iloc[0]*100:+.2f}%p)" if len(p_cl) > 0 else "Put 없음"
        cluster_cmp_str = f"최근접 만기({first_exp}) 클러스터 비교: {c_cl_str} vs {p_cl_str}"
    else:
        cluster_cmp_str = "단기 클러스터 데이터 없음"

    lines.append("## [섹션 5] [투자자용 30초 실전 판독 요약] 데이터북 핵심 시그널 3단계 순서 정리 (자동 계측 가이드)")
    lines.append(sep_thin)
    lines.append(f" • 1단계 ([섹션 1-2] {traj_days}영업일 궤적표 확인 — 10초):")
    lines.append(f"   - 상승 로켓 연료인 Call_Q1({w_short}D)이 {traj_df.iloc[0]['Date']}({cq1_first:+,}계약) -> {latest_date}({cq1_last:+,}계약)로 [{fuel_state}] 상태입니다. (단, {w_long}일 누적 코어 연료는 +{c_q1_long:,}계약 생존)")
    lines.append(f"   - 동시에 머리 위 천장 뚜껑인 Call_Q2({w_short}D)는 +{c_q2_sum:,}계약, 바닥 현금 방석인 Put_Q2({w_short}D)는 +{p_q2_sum:,}계약({w_long}일 누적 +{p_q2_long:,}계약)으로 [{cap_vs_fuel}] 국면입니다.")
    lines.append(f" • 2단계 ([섹션 1-4] 단기 눌림목 4대 징후 & [섹션 3-2] 5단계 눌림목 하락폭 타점 확인 — 10초):")
    lines.append(f"   - 레짐 C 변화 [{regc_jump_str}], 근월-원월 응급실 경보등 [{curr_ts['Term_Near_Back']*100:+.2f}%p ({curr_ts['Term_Near_Back_pct']:.1f}%ile)], 단기 눌림목 사전 징후 [{pb_active_cnt}/4개 점화].")
    lines.append(f"   - 판정: {pb_alert_grade}")
    lines.append(f"   - 눌림목 단계 요약([섹션 3-2] 표와 같은 정의): 1단계(1일 0.5σ) {ewy_pb_stage1:.2f}달러({s1_pct:+.2f}%) -> 2단계(1일 1σ)·3단계(풋 벙커·기관 본전) {ewy_pb_stage2:.2f}~{ewy_pb_stage3:.2f}달러({s2_pct:+.2f}%~{s3_pct:+.2f}%, 삼성전자 {s2_sam:,}~{s3_sam:,}원) "
                 f"-> 4단계(2일 1σ)·5단계(7일 VWAP·제로감마) {ewy_pb_stage4:.2f}~{ewy_pb_stage5:.2f}달러({s4_pct:+.2f}%~{s5_pct:+.2f}%, 삼성전자 {s4_sam:,}~{s5_sam:,}원) "
                 f"| 실측(종가 기준, {PB_CAL['n']}거래일): 다음 거래일 종가가 1단계 위 {PB_CAL['s1']}% · 2단계 위 {PB_CAL['s2']}%, 2거래일 뒤 종가가 4단계 위 {PB_CAL['s4']}%")
    lines.append(f" • 3단계 ([섹션 2-④, ⑤] 당일 미결산 레이더 & [섹션 3-3] 기습 풋 원인 ①·② 완전판 하락폭 공식 확인 — 10초):")
    lines.append(f"   - 당일 미결산 상위 {tot_top_amb_cnt}개 중 '🔥당일 기습 상방매집(Call)'은 {amb_call_cnt}건 vs '🚨하방공습(Put) {amb_put_cnt}건 + 🧱커버드콜 {amb_call_cap_cnt}건' (하방·상단캡 비중 {bear_ambush_ratio:.1f}%).")
    if has_near_ambush_put:
        lines.append(f"   - [원인 ①·② 기습 풋 공식 타깃 (조건부 시나리오 · 원인① {'ON' if is_bear_shift_active else 'OFF'} · 원인② ON · 본대 실재 {'충족' if cas_army_valid else '미충족'})]: 최상위 근접 기습 풋({ap_exp} {ap_strike:.1f}P, {ap_vol:,}계약, Δ0={ap_delta0:+.2f}, 초동헤지 -{ap_shares_t0:,}주) 작동 시 1차 단독 타깃 EWY {ewy_amb_target1:.2f}달러({amb1_pct:+.2f}%, 삼성전자 {amb1_sam:,}원[{sam_drop1_krw:+,d}원])"
                     + (f" -> 직하단 {cas_strike:.1f}P 본대(Q1 +{cas_q1_chg:,}계약) 연쇄 점화 시 2차 확장 타깃 EWY {ewy_amb_target2:.2f}달러({amb2_pct:+.2f}%, 삼성전자 {amb2_sam:,}원[{sam_drop2_krw:+,d}원])." if is_bear_shift_active
                        else f" -> 원인① 미점화라 2차 타깃 EWY {ewy_amb_target2:.2f}달러({amb2_pct:+.2f}%)는 원인② 감마 확장분만 반영."))
    else:   # ★ [V4.3.7] 원인② 미점화일: 기습 풋 시나리오가 작동하지 않음을 밝힘
        lines.append(f"   - [원인 ①·② 기습 풋 공식 (원인① OFF · 원인② OFF)]: 근접 풋의 당일 IV +0.5%p 상승 조건이 충족되지 않아 기습 풋 시나리오는 작동하지 않습니다. "
                     f"1차 타깃 EWY {ewy_amb_target1:.2f}달러({amb1_pct:+.2f}%, 삼성전자 {amb1_sam:,}원)는 1일 1σ 기본 하방폭 참고치입니다.")
    lines.append(f"   - {cluster_cmp_str} -> 이 기습 수급 방향에 맞춰 [섹션 3]의 1·2차 방어선(${put_bunker_1st:.1f} / ${put_bunker_core:.1f}) 분할 매수 및 단기 Max Pain(${mp_nearest:.1f}) 목표가 대응을 집행합니다.")
    lines.append("")

    # ★ [V4.1 핵심 신설: 눌림목 미탐지 사각지대(25%)까지 완벽히 메우는 '실전 3중 체크법' 자동 계측 및 최종 정리 문단]
    # - 206거래일 전수 시뮬레이션에서 기본 4대 징후(75% 포착)가 놓쳤던 9건(25% 사각지대: 콘탱고/IV 안정화 속 눌림목)을 100% 보완하는 3대 체크 규칙
    cq2_to_cq1_ratio = float(c_q2_sum) / max(float(c_q1_sum), max(10.0, 100.0 * s_oi))
    tot_put_close_short = int(p_q3_sum + p_q4_sum)

    # 체크 1 [V4.2 보완]: 단기 MP 괴리율 >= +7.0% 이거나, (만기 이월 직후 단기 MP 괴리율 >= +5.0% & 전체 만기 MP 괴리율 >= +6.5% & Call Q1 비중 <= 15.0%)일 때 점화!
    bs_check1 = (mp_over_ext_pct >= 7.0) or ((mp_over_ext_pct >= 5.0) and (mp_all_over_pct >= 6.5) and (last_tr['CQ1SharePct'] <= 15.0))
    # 체크 2 [V4.2 보완]: Call Q2/Q1 >= 2.5배 & 콜점유율 <= 40.0% 이거나, 극단적 콜 캡(Call Q2/Q1 >= 5.0배) 상태에서 콜점유율 <= 46.0%일 때 점화!
    bs_check2 = ((cq2_to_cq1_ratio >= 2.5) and (last_tr['CallVolShare'] <= 40.0)) or ((cq2_to_cq1_ratio >= 5.0) and (last_tr['CallVolShare'] <= 46.0))
    # 체크 3 [V4.2.5 동적화]: 풋 수익화 청산(Put Q3+4) 급증 기반 '1일 바나(Vanna) 연료 일시 소진' (2026년 1.5만 계약 -> 과거 s_oi 비례)
    bs_check3 = (daily_chg_pct >= 3.5) and (tot_put_close_short >= max(450, int(round(15000 * s_oi)))) and (near_iv_chg_1d <= -5.0)
    bs_active_cnt = int(bs_check1) + int(bs_check2) + int(bs_check3)

    if is_distribution_crash_regime:
        full_coverage_verdict = (
            f"🚨 [중기 상방 연료 고갈 & 고점 분배 폭락(Distribution Crash) 경보 발령! (기본 징후 {pb_active_cnt}/4 + 사각지대 3중체크 {bs_active_cnt}/3 + 고점래치 {'ON' if high_dist_latch_on else 'OFF'})] "
            f"단기(3D {sh_3d_pct:.1f}%)·주간(7D {sh_7d_pct:.1f}%)·월간(20D {sh_20d_pct:.1f}%) 전 계층에서 진성 콜(Call Q1) 연료가 고갈되고 대규모 커버드콜(Q2)·롱콜청산(Q3) 분배가 확인되었습니다. "
            f"단순 2~3단계 눌림목에서의 기계적 분할매수를 엄금하며, 1차 방어선(EWY ${put_bunker_1st:.1f} / 실질BEP ${put_q2_bep_1st:.2f}) 하향 이탈 시 다단계 감마 진공 하단인 "
            f"6단계 심층 콘크리트 요새(EWY ${ewy_pb_stage6:.2f}[{s6_pct:+.2f}%] / 삼성전자 {s6_sam:,}원)까지 연쇄 하락이 열리므로 현물 비중 축소 및 풋 헤지로 대응하십시오!"
        )
    # ★ [V4.4] 3중 체크·고점래치 결합 승격(🚨 전방위) 삭제: 두 신호 모두 라벨·2024 검증 미달 (계산·표시는 유지)
    elif pb_active_cnt >= 2:
        full_coverage_verdict = (
            f"⚡ [기본 눌림목 경보 발령 (기본 징후 {pb_active_cnt}/4 점화 · 사각지대 3중체크 {bs_active_cnt}/3 · 고점래치 {'ON' if high_dist_latch_on else 'OFF'}는 참고)] "
            f"단기 과열/언와인딩 징후가 2개 이상 켜졌습니다(검증: 이런 날 10영업일 내 -5% 이상 하락 {PHASE_REL['alarm']['pb2'][0]}% vs 꺼진 날 {PHASE_REL['alarm']['pb2'][1]}%). "
            f"중기 레짐 A(상방) 코어 물량은 홀딩하되, 신규 진입은 1~3단계 눌림목 타점(EWY ${ewy_pb_stage1:.2f}~${ewy_pb_stage3:.2f})에서 분할 집행하십시오."
        )
    # ★ [V4.4] 사각지대 3중 체크 단독 승격(⚠️) 삭제: 라벨 기간 켜진 날 하락 비율이 꺼진 날보다 낮음 (신뢰도표에만 표시)
    else:
        if is_downtrend_state:
            full_coverage_verdict = (
                f"⚪ [고점 과열 경보 없음 (기본 징후 {pb_active_cnt}/4 · 사각지대 3중체크 {bs_active_cnt}/3) · 하락 국면 진행 중 (국면 D {_ph_p['D']:.0f}%)] "
                f"이 체크들은 고점 과열만 검사하므로 하락 국면에서는 0개가 정상입니다. 상승 순항으로 판정하지 않습니다 (국면 판정·지지선 확인 우선)."
            )
        elif is_sideways_state:
            full_coverage_verdict = (
                f"⚪ [고점 과열 경보 없음 (기본 징후 {pb_active_cnt}/4 · 사각지대 3중체크 {bs_active_cnt}/3) · 횡보 국면 (국면 S {_ph_p['S']:.0f}%)] "
                f"뚜렷한 추세가 없는 구간이므로 경보 부재를 상승 신호로 해석하지 말고 박스 상·하단 이탈 여부를 확인하십시오."
            )
        else:
            full_coverage_verdict = (
                f"✅ [상승 순항 (기본 징후 {pb_active_cnt}/4 & 사각지대 3중체크 {bs_active_cnt}/3 모두 PASS · 상승 국면 {_ph_p['U']:.0f}%)] "
                f"고점 과열 징후와 사각지대(극단적 MP 괴리·데드캣 콜캡·바나 일시소진) 모두에서 위험 신호가 없습니다."
            )

    lines.append(" • 4단계 ([최종 정리 문단] 눌림목 미탐지 사각지대(25%)까지 완벽히 메우는 '실전 3중 체크법' 설명 및 당일 체크 결과):")
    lines.append("   - [실전 3중 체크법 원리]: 기본 4대 징후([섹션 1-4])가 놓치는 눌림목은 변동성 기간구조가 평온(콘탱고)하거나 IV가 하락할 때 발생한다는 가정의 보완 체크입니다 (라벨 검증: 3중 체크 1개 이상 발생일의 10영업일 내 -5% 급락 빈도는 미발생일보다 높지 않음 -> 신호 신뢰도표 참조).")
    lines.append(f"     ① [체크 1 — 극단적 Max Pain 상방 괴리(≥+7.0%) 자석 회귀 체크] : {'🚨경보(ON)' if bs_check1 else '✅안정(PASS)'} | 당일 괴리율 {mp_over_ext_pct:+.2f}% (현가 ${latest_spot:.2f} vs 단기MP ${mp_nearest:.1f} / 기준선 +7.0% 이상 시 콘탱고 상태에서도 강한 자석 회귀 발생)")
    lines.append(f"     ② [체크 2 — IV 안정화 속 '데드캣 바운스 천장 캡'(Call Q2≥2.5×Q1 & 콜점유율≤40%)] : {'🚨경보(ON)' if bs_check2 else '✅안정(PASS)'} | 단기 Call Q2/Q1 비율 {cq2_to_cq1_ratio:.2f}배 (+{c_q2_sum:,} vs +{c_q1_sum:,}계약) & 당일 콜 점유율 {last_tr['CallVolShare']:.1f}% (반등 틈탄 기관 콜매도 폭격 여부)")
    lines.append(f"     ③ [체크 3 — 풋 청산 급증 기반 '1일 바나(Vanna) 연료 일시 소진'(주가≥+3.5% & Put청산≥1.5만 & ΔIV≤-5%p)] : {'🚨경보(ON)' if bs_check3 else '✅안정(PASS)'} | 당일 주가 {daily_chg_pct:+.2f}%, 단기 Put청산(Q3+4) -{tot_put_close_short:,}계약, 근월IV 1일변동 {near_iv_chg_1d:+.2f}%p (숏커버 1일 소진 후 숨고르기 여부)")
    lines.append(f"   - [최종 통합 판정 (분배 경보·기본 징후만 반영 · 3중 체크·고점래치는 참고)]: {full_coverage_verdict}")
    _v429_map = {
        ('D', '상'): "하락 국면 + 급락 위험도 상: 하락 추세가 진행 중이고 헤지 수요(풋/콜 OI·스큐)가 높아 추가 급락 빈도가 높은 구간입니다. 반등 대응은 국면 1순위가 바뀐 뒤로 미루십시오.",
        ('D', '중'): "하락 국면 · 급락 위험도 중: 하락 추세가 진행 중이며 헤지 수요는 평균 수준입니다. 지지선과 국면 확률 변화를 함께 확인하십시오.",
        ('D', '하'): "하락 국면 · 급락 위험도 하: 가격은 하락 추세이나 헤지 수요가 낮아 급락 빈도는 낮은 구간입니다.",
        ('U', '상'): "상승 국면 · 급락 위험도 상: 추세는 상승이나 헤지 수요가 쌓여 있어 급락 빈도가 높은 구간입니다. 추격 매수보다 위험 관리가 우선입니다.",
        ('U', '중'): "상승 국면 · 급락 위험도 중: 상승 추세 유지, 통상 수준의 조정 위험입니다.",
        ('U', '하'): "상승 국면 · 급락 위험도 하: 상승 추세 유지, 급락 빈도가 낮은 구간입니다.",
        ('S', '상'): "횡보 국면 · 급락 위험도 상: 방향성은 약하나 헤지 수요가 높아 하방 이탈 빈도가 높은 구간입니다.",
        ('S', '중'): "횡보 국면 · 급락 위험도 중: 박스권 대응 구간입니다.",
        ('S', '하'): "횡보 국면 · 급락 위험도 하: 박스권이며 급락 빈도가 낮은 구간입니다."}
    _v44_on = bool(is_distribution_crash_regime or pb_active_cnt >= 2)
    _v44_alarm = '분배 경보 ON' if is_distribution_crash_regime else (f'기본 징후 {pb_active_cnt}/4 ON' if pb_active_cnt >= 2 else '검증 경보 OFF')
    _v44_extra = (f" 검증 경보가 켜진 날은 10영업일 안에 -5% 이상 하락한 비율이 {PHASE_REL['alarm']['v44'][0]}%로 꺼진 날({PHASE_REL['alarm']['v44'][1]}%)보다 높았습니다(2024 {PHASE_REL['alarm']['v44'][2]}% vs {PHASE_REL['alarm']['v44'][3]}%)." if _v44_on else "")
    lines.append(f"   - [V4.4 최종 판정 (국면·급락 위험도·검증 경보)]: {'🔻' if _ph_top == 'D' else ('🔺' if _ph_top == 'U' else '↔️')} [{_ph_kr[_ph_top]} 국면 {_ph_p[_ph_top]:.0f}% · 급락 위험도 {_rk_lv}({_rs[_rk_lv]}%) · {_v44_alarm}] {_v429_map[(_ph_top, _rk_lv)]}{_v44_extra} (국면은 현재 상태 · 위험도와 경보는 과거 빈도이며 시점 예측이 아님)")

    # --------------------------------------------------------------------------
    # ★ [V4.2.2 신설: 섹션 5 내 5단계 — 합성 공매도 본대 5대 추적 포인트 자동 계측 및 독해 매뉴얼]
    # --------------------------------------------------------------------------
    rolldown_reinvest_ratio = (p_q1_sum / max(abs(tot_itm_chg_short), 1)) * 100.0 if tot_itm_chg_short < 0 else 100.0
    _synth_exit_cut = -max(150, int(round(3000 * s_oi)))
    if tot_itm_chg_short <= _synth_exit_cut and rolldown_reinvest_ratio < 50.0:
        synth_verdict = "✅ [합성 공매도 본대 대량 엑시트(Exit) & 숏커버 랠리 점화] 고행사가 내가격 풋이 대거 청산되고 하단 재매집(롤다운)도 미미하여 주가를 짓누르던 대리 공매도 대못이 뽑혔습니다!"
    elif tot_itm_chg_short <= _synth_exit_cut and rolldown_reinvest_ratio >= 50.0:
        synth_verdict = "⚡ [고행사가 익절 후 하단 롤다운(Roll-Down) 교체 경계] 상단 합성 공매도는 청산되었으나, 그 차익 자금의 상당 부분이 현가 아래 신규 Put Q1 매수로 이동하고 있어 하단 방어선 지지가 중요합니다."
    elif trapped_itm_ratio >= 60.0:
        synth_verdict = f"⚪ [내가격 풋 보유측 다수 평가손실 · 청산 미확인] 잔존 내가격 풋의 {trapped_itm_ratio:.0f}%가 현재 옵션가 기준 평가손실입니다(매수측 {mtm_buy_loss_oi:,}계약 · 매도측 {mtm_sell_loss_oi:,}계약). 손실 포지션의 손절 청산은 매수측이면 딜러 환매수(현물 매수), 매도측이면 딜러 매수헤지 해소(현물 매도)로 이어지므로, ITM 풋 OI가 실제로 줄어드는 날에만 수급 효과로 해석하십시오."
    else:
        synth_verdict = f"🚨 [합성 공매도 본대 잔존 압박 지속] 내가격 풋 보유측의 평가손실 비중이 {trapped_itm_ratio:.0f}%에 그쳐 손절성 청산 압력이 약하고, 매수측 상대 딜러 대리공매도 -{tot_dealer_short_sh:,}주가 남아 상단을 누르고 있습니다. 내가격 풋 OI의 실제 감소(청산)를 먼저 확인하십시오."

    lines.append("")
    lines.append(" • 5단계 ([V4.2.2 핵심 신설] '합성 공매도 본대(Deep ITM Put)' 지배력 진단 및 향후 보고서 5대 중점 독해 포인트):")
    lines.append(f"   ① [독해 포인트 1 — 지배 규모 & 딜러 헤지 잔량 ([섹션 2-(2-4)] 상단 요약 확인)] : 현재 현가 위 내가격(ITM) 풋 총 잔존량은 {tot_itm_put_oi:,}계약입니다. 풋 매수측(1·2선) 상대로 딜러가 매도해 둔 대리 공매도는 -{tot_dealer_short_sh:,}주(명목 {tot_dealer_short_sh*latest_spot/1e6:.2f}백만달러)이고, 풋 매도측(3선) 상대로는 반대로 +{tot_dealer_long_sh:,}주를 매수헤지로 들고 있습니다.")
    lines.append(f"   ② [독해 포인트 2 — 청산 속도 & 딜러 헤지 해소량 ([섹션 2-(2-3) & (2-4)] 1일/단기 OI청산 확인)] : 최근 {w_short}일간 내가격 풋에서 {tot_itm_chg_short:+,}계약(1일 {tot_itm_chg_1d:+,}계약)이 변동했습니다. 매수측 청산에 따른 딜러 환매수(현물 매수)는 +{tot_released_sh:,}주, 매도측 청산에 따른 매수헤지 해소(현물 매도)는 -{tot_released_sell_sh:,}주입니다.")
    lines.append(f"   ③ [독해 포인트 3 — 보유측 평가손익 ([섹션 2-(2-4)] '평가손익' 열 확인)] : 현재 옵션가 기준 잔존 내가격 풋의 {trapped_itm_ratio:.1f}%({trapped_itm_oi:,}계약)가 평가손실입니다(매수측 {mtm_buy_loss_oi:,}계약 · 매도측 {mtm_sell_loss_oi:,}계약, OI 가중 평균 평가손익 {weighted_mtm_pct:+.1f}%). 만기BEP 가중평균 {weighted_itm_bep:.2f}달러는 만기일 기준 참고치입니다.")
    if tot_itm_chg_short <= _synth_exit_cut:
        lines.append(f"   ④ [독해 포인트 4 — 하단 롤다운(Roll-Down) 재원 이동 여부 ([섹션 1-2] Put청산 vs Put_Q1 비교)] : 내가격 풋 청산({tot_itm_chg_short:+,}계약) 대비 현가 아래 신규 하방 베팅(Put Q1 +{p_q1_sum:,}계약) 재유입 비율은 {rolldown_reinvest_ratio:.1f}%입니다.")
    elif tot_itm_chg_short < 0:   # ★ [V4.3.7] 청산 규모가 엑시트 기준보다 작으면 비율이 수천 %로 튀므로 해석 생략
        lines.append(f"   ④ [독해 포인트 4 — 하단 롤다운(Roll-Down) 재원 이동 여부 ([섹션 1-2] Put청산 vs Put_Q1 비교)] : 최근 {w_short}일 내가격 풋 청산이 {tot_itm_chg_short:+,}계약으로 엑시트 기준({_synth_exit_cut:+,}계약)보다 작아 롤다운 재유입 비율은 해석하지 않습니다(현가 아래 신규 Put Q1 +{p_q1_sum:,}계약).")
    else:   # ★ [V4.3.7] 순증일에는 '청산 대비 비율'이 성립하지 않음
        lines.append(f"   ④ [독해 포인트 4 — 하단 롤다운(Roll-Down) 재원 이동 여부 ([섹션 1-2] Put청산 vs Put_Q1 비교)] : 최근 {w_short}일 내가격 풋은 청산되지 않고 {tot_itm_chg_short:+,}계약 순증해 롤다운 재유입 비율은 해당 없음입니다(현가 아래 신규 Put Q1 +{p_q1_sum:,}계약).")
    lines.append("   ⑤ [독해 포인트 5 — 향후 매 거래일 보고서 중점 확인 루틴] : 앞으로 보고서를 열람할 때는 1순위 [섹션 2-(2-4)]의 '1선:합성공매도' 계약들의 1일OI증감(-)과 평가손익 부호 변화 -> 2순위 [섹션 2-③ 지형도]에서 현가 위(+괴리율) 행사가의 Put 증감(-) -> 3순위 [섹션 2-④ 미결산 레이더]에서 내가격 풋의 장중 청산(🛡️) 유입 여부를 순서대로 대조하십시오.")
    lines.append(f"   - [합성 공매도 종합 판정]: {synth_verdict}")
    # ★ [V4.4] 라벨·2024 검증 신호 신뢰도표 (신호가 켜진 날의 10영업일 내 -5% 이상 하락 비율 · 반영: 경보/판정/상태/참고)
    _sq_now = (not (tot_itm_chg_short <= _synth_exit_cut)) and (trapped_itm_ratio >= 60.0)
    _now = {'dist': bool(is_distribution_crash_regime), 'pb2': pb_active_cnt >= 2, 'v44': bool(is_distribution_crash_regime or pb_active_cnt >= 2),
            'rkH': _rk_lv == '상', 'rkL': _rk_lv == '하', 'phD': _ph_top == 'D', 'phU': _ph_top == 'U', 'phS': _ph_top == 'S',
            'latch': bool(high_dist_latch_on), 'bs1': bs_active_cnt >= 1, 'c1': bool(is_bear_shift_active), 'c2': bool(has_near_ambush_put),
            'regB': regime_ranking[0][0].startswith('레짐 B'), 'regA': regime_ranking[0][0].startswith('레짐 A'), 'sq': bool(_sq_now)}
    lines.append(f"   - [V4.4 신호 신뢰도표] 신호가 켜진 날의 '10영업일 안에 -5% 이상 하락' 비율 (라벨 기간 2025-03~2026-11 기저 {PHASE_REL['base_lb']}% / 2024-04~2025-03 비학습 기간 기저 {PHASE_REL['base_ho']}%). 반영: 경보 = 최종 판정 승격, 판정·상태 = 최종 판정 문구, 참고 = 표시만")
    lines.append(f"     {'신호':<30} | 반영 | 오늘 | 라벨 발생빈도 | 라벨 하락%(꺼진 날) | 2024 하락%(꺼진 날) | 판정")
    for _nm, _k, _use, _fq, _on, _off, _hon, _hoff, _hn, _vd in PHASE_REL['rows']:
        _on_s = '-' if _on is None else f"{_on}%"
        _hon_s = '-' if _hon is None else f"{_hon}%"
        lines.append(f"     {_nm:<30} | {_use:<2} | {'ON ' if _now.get(_k) else 'OFF'}  | {_fq:>5}%       | {_on_s:>4} ({_off}%)        | {_hon_s:>4} ({_hoff}%) n={_hn:<4} | {_vd}")

    # --------------------------------------------------------------------------
    # ★ [V4.4 업그레이드: 섹션 5 내 6단계 — 월가 4대 퀀트 파이프라인 당일(T) & 전일(T-1) 동시 계측 및 1일 변화량 자동 산출]
    # --------------------------------------------------------------------------
    def _calc_pipeline_snapshot(day_surv_df, spot_val, ts_row):
        # [파이프라인 1] RND 주간 1시그마 레인지 및 양방향 2시그마 꼬리 확률
        _atm_iv = max(float(ts_row['Near_ATM_IV']) if np.isfinite(ts_row['Near_ATM_IV']) else 0.45, 0.15)
        _sk_25d = float(ts_row['Near_Skew_25D']) if np.isfinite(ts_row['Near_Skew_25D']) else 0.02
        _bf_25d = float(ts_row['Near_Bfly_25D']) if np.isfinite(ts_row['Near_Bfly_25D']) else 0.005
        _r_skew = float(np.clip(-6.0 * (_sk_25d / _atm_iv), -2.5, 2.5))
        _r_kurt = float(np.clip(24.0 * max(0.0, _bf_25d / _atm_iv), 0.0, 8.0))
        _s_5d   = _atm_iv * np.sqrt(5.0 / 252.0)
        _n_t2, _p_t2 = stats.norm.cdf(-2.0), stats.norm.pdf(2.0)
        l_tail = float(np.clip((_n_t2 - _p_t2 * (_r_skew * 0.5 - _r_kurt / 12.0)) * 100.0, 0.5, 25.0))
        r_tail = float(np.clip((_n_t2 + _p_t2 * (_r_skew * 0.5 + _r_kurt / 12.0)) * 100.0, 0.5, 25.0))
        r_low  = round(spot_val * (1.0 - _s_5d * (1.0 - 0.15 * _r_skew)), 2)
        r_high = round(spot_val * (1.0 + _s_5d * (1.0 + 0.15 * _r_skew)), 2)

        # [파이프라인 2] 풋-콜 패리티 내재 합성선물 및 베이시스
        _pcp_s = day_surv_df[(day_surv_df['DTE'] >= 1) & (day_surv_df['DTE'] <= 35)].copy()
        if len(_pcp_s) > 0:
            _pcp_s['Mid_P'] = np.where((_pcp_s['Bid'] > 0) & (_pcp_s['Ask'] > 0), 0.5 * (_pcp_s['Bid'] + _pcp_s['Ask']), _pcp_s['Last Price'])
            _piv_p = _pcp_s[_pcp_s['Mid_P'] > 0.05].pivot_table(index=['Expiration Date', 'DTE', 'Strike'], columns='Option Type', values=['Mid_P', 'Volume'], aggfunc='first').dropna()
            if len(_piv_p) > 0 and ('Mid_P', 'Call') in _piv_p.columns and ('Mid_P', 'Put') in _piv_p.columns:
                _k_p = _piv_p.index.get_level_values('Strike').values.astype(float)
                _m_p = np.abs(_k_p - spot_val) / spot_val <= 0.05
                if not np.any(_m_p):
                    _m_p = np.ones(len(_k_p), dtype=bool)
                _sb = _piv_p[_m_p]
                _ka = _sb.index.get_level_values('Strike').values.astype(float)
                _ta = np.maximum(_sb.index.get_level_values('DTE').values.astype(float) / 365.0, 1.0 / 365.0)
                _cm = _sb[('Mid_P', 'Call')].values.astype(float)
                _pm = _sb[('Mid_P', 'Put')].values.astype(float)
                _wp = (_sb[('Volume', 'Call')].values + _sb[('Volume', 'Put')].values + 10.0) / (np.abs(_ka - spot_val) + 0.5)
                # ★ [V4.3.7] 배당 반영 패리티 현물가 = C - P + K·e^-rT + PV(배당) (기존: 고정 금리·캐리 근사라 12월 배당이 '합성선물 저평가'로 보임)
                _r_p = GAMMA_RF_FALLBACK
                _sfp = pd.to_numeric(day_surv_df['Secured Overnight Financing Rate'], errors='coerce') if 'Secured Overnight Financing Rate' in day_surv_df.columns else pd.Series(dtype=float)
                _sfp = _sfp[_sfp > 0]
                if len(_sfp) > 0:
                    _r_p = float(_sfp.iloc[0]) / 100.0
                _qd_p = str(day_surv_df['Quote Date'].iloc[0])[:10]
                _ex_p = _sb.index.get_level_values('Expiration Date').astype(str).values
                _pvd = np.array([_pv_divs(_qd_p, e_, spot_val, _r_p) for e_ in _ex_p]) if USE_DIVIDEND_IV_FIX else np.zeros(len(_ex_p))
                _fs = (_cm - _pm) + _ka * np.exp(-_r_p * _ta) + _pvd
                _pre = _pvd <= 0
                if _pre.any() and (~_pre).any():
                    _fs, _wp = _fs[_pre], _wp[_pre]   # 배당락 전 만기가 있으면 그 만기로만 계산(배당 금액 추정 오차가 베이시스에 섞이지 않게)
                syn_f = float(np.average(_fs, weights=_wp))
            else:
                syn_f = spot_val
        else:
            syn_f = spot_val
        basis_p = (syn_f / max(spot_val, 1e-6) - 1.0) * 100.0

        # [파이프라인 3] 감마 플립 · 순감마(GEX) · 바나+참 — [V4.3.6] D 산식 (calc_gamma_flip_v436 참고)
        _gf = calc_gamma_flip_v436(day_surv_df, spot_val)
        gflip, gex_1pct, van_sh, chm_sh, vc_tot = _gf['gflip'], _gf['gex_1pct'], _gf['van_sh'], _gf['chm_sh'], _gf['vc_tot']

        return {
            'r_low': r_low, 'r_high': r_high, 'l_tail': l_tail, 'r_tail': r_tail,
            'syn_f': syn_f, 'basis_p': basis_p,
            'gflip': gflip, 'gex_1pct': gex_1pct, 'van_sh': van_sh, 'chm_sh': chm_sh, 'vc_tot': vc_tot,
            'gflip_none': _gf['gflip_none'], 'gflip_sign': _gf['gflip_sign'], 'gflip_a': _gf['gflip_a'], 'gflip_a_none': _gf['gflip_a_none']
        }

    prev1_surv = surv_df[surv_df['Quote Date'] == prev1_date]
    p_now  = _calc_pipeline_snapshot(latest_surv, latest_spot, curr_ts)
    p_prev = _calc_pipeline_snapshot(prev1_surv, prev1_spot, prev_ts) if len(prev1_surv) > 0 else p_now

    rnd_5d_low, rnd_5d_high = p_now['r_low'], p_now['r_high']
    rnd_left_tail_prob, rnd_right_tail_prob = p_now['l_tail'], p_now['r_tail']
    _, rnd_low_k, rnd_low_sam, _   = conv_kr(rnd_5d_low)
    _, rnd_high_k, rnd_high_sam, _ = conv_kr(rnd_5d_high)

    syn_spot_pcp, pcp_basis_pct = p_now['syn_f'], p_now['basis_p']
    pcp_arb_dir = "🔥합성선물 고평가(콘탱고) -> 한국장 시초가 프로그램 차익 매수 유입 우위" if pcp_basis_pct >= 0.15 else ("🚨합성선물 저평가(백워데이션) -> 시초가 차익 매도 경계" if pcp_basis_pct <= -0.25 else "⚡현·선물 균형(중립 베이시스)")

    exact_gflip, net_gex_1pct_sh = p_now['gflip'], p_now['gex_1pct']
    vanna_cover_sh, charm_cover_sh, tot_vc_1d_sh = p_now['van_sh'], p_now['chm_sh'], p_now['vc_tot']
    gflip_none = bool(p_now.get('gflip_none', False))
    if not gflip_none:
        gflip_pct, gflip_k, gflip_sam, _ = conv_kr(exact_gflip)
    else:
        gflip_pct, gflip_k, gflip_sam = float('nan'), float('nan'), 0

    # [파이프라인 4] 다년도 스케일 왜곡 제거 상대OI 비중(% of Total OI) 및 전일 대비 비교
    tot_active_oi_now  = max(int(latest_surv['Open Interest'].sum()), 1)
    tot_active_oi_prev = max(int(prev1_surv['Open Interest'].sum()), 1) if len(prev1_surv) > 0 else tot_active_oi_now
    cq1_rel_oi_pct = (c_q1_sum / tot_active_oi_now) * 100.0
    pq2_rel_oi_pct = (p_q2_sum / tot_active_oi_now) * 100.0
    pq1_rel_oi_pct = (p_q1_sum / tot_active_oi_now) * 100.0
    cq1_rel_prev   = (float(prev_tr['CQ1']) / tot_active_oi_prev) * 100.0

    lines.append("")
    lines.append(" • 6단계 ([V4.4 핵심 업그레이드] '월가 4대 퀀트 파이프라인' 실시간 통합 계측 및 전일(T-1) 대비 1일 변화량 요약):")
    lines.append(f"   ① [파이프라인 1단계: 변동성 곡면 역산 & RND 확률지도] : 향후 5영업일(1주) 1시그마(68.2%) 확률 레인지는 EWY {rnd_5d_low:.2f}~{rnd_5d_high:.2f}달러(전일 {p_prev['r_low']:.2f}~{p_prev['r_high']:.2f}달러 / 삼성전자 {rnd_low_sam:,}~{rnd_high_sam:,}원)이며, 스큐·버터플라이 4차 적률(Cornish-Fisher) 반영 시 하방 -2시그마 꼬리 폭락 확률은 {rnd_left_tail_prob:.1f}%(전일 {p_prev['l_tail']:.1f}%, {rnd_left_tail_prob - p_prev['l_tail']:+.1f}%p) vs 상방 +2시그마 급등 확률은 {rnd_right_tail_prob:.1f}%(전일 {p_prev['r_tail']:.1f}%, {rnd_right_tail_prob - p_prev['r_tail']:+.1f}%p)입니다.")
    lines.append(f"   ② [파이프라인 2단계: 비대칭 수급 & 풋-콜 패리티 시초가 베이시스] : 등가격 옵션 풋-콜 패리티로 역산한 내재 합성선물 가격은 {syn_spot_pcp:.2f}달러(현물대비 베이시스 {pcp_basis_pct:+.2f}%, 전일 베이시스 {p_prev['basis_p']:+.2f}% 대비 {pcp_basis_pct - p_prev['basis_p']:+.2f}%p)로 [{pcp_arb_dir}] 상태이며, 외가격 달러 거래대금 불균형은 {last_tr['OTMDVolImb']:+.1f}%(전일 {prev_tr['OTMDVolImb']:+.1f}%)입니다.")
    _gf_prev_s = ("전일 '구간 내 플립 없음'" if p_prev.get('gflip_none') else
                  (f"전일 {p_prev['gflip']:.2f}달러 대비 {exact_gflip - p_prev['gflip']:+.2f}달러 이동" if not gflip_none else f"전일 {p_prev['gflip']:.2f}달러"))
    _vc_s = (f" 현재 현가 1% 변동당 딜러 강제 헤지 물량은 {net_gex_1pct_sh:+,d}주(전일 {p_prev['gex_1pct']:+,d}주 대비 {net_gex_1pct_sh - p_prev['gex_1pct']:+,d}주)입니다. "
             f"내재변동성이 -3%p 안정되고 1일이 지난다고 가정한 시나리오 계산값인 '바나+참 숏커버 추정 물량'은 +{tot_vc_1d_sh:,d}주(전일 +{p_prev['vc_tot']:,d}주 대비 "
             f"{tot_vc_1d_sh - p_prev['vc_tot']:+,d}주 | 바나 +{vanna_cover_sh:,d}주 / 참 +{charm_cover_sh:,d}주)이며, 실제 매수를 보장하는 값은 아닙니다.")
    if not gflip_none:
        lines.append(f"   ③ [파이프라인 3단계: 딜러 헤지 시뮬레이션 (감마플립 · GEX · 바나 · 참)] : 딜러 순감마(GEX) 부호가 바뀌는 '정밀 감마 플립 마지노선'은 "
                     f"EWY {exact_gflip:.2f}달러({gflip_pct:+.2f}%, {_gf_prev_s} / KOSPI {gflip_k:,.0f}pt · 삼성전자 {gflip_sam:,}원)이며 EWY 종가는 선 {'아래' if latest_spot < exact_gflip else '위'}입니다. "
                     f"(D 산식: 당일 만기 제외 · IV 결측 스마일 보간 · 실제 배당 반영 — '마지노선'은 이전 버전과 같은 이름일 뿐 지지·저항을 단정하지 않습니다.) "
                     f"이 선은 방향(추세) 신호가 아니라 변동 폭 구간의 경계로 읽습니다(2026년 24시간 시세 측정: 선 아래에서 한국장 변동 폭이 커지는 경향, 상승장에서는 방향 정보 없음)." + _vc_s)
    else:
        lines.append(f"   ③ [파이프라인 3단계: 딜러 헤지 시뮬레이션 (감마플립 · GEX · 바나 · 참)] : 딜러 순감마(GEX) 부호가 바뀌는 '정밀 감마 플립 마지노선'(D 산식)은 오늘 '구간 내 플립 없음'입니다"
                     f"(현가 0.85~1.25배 전 구간 순감마 {'+ · 딜러 완충' if p_now.get('gflip_sign') == '+' else '- · 딜러 가속'} / {_gf_prev_s}). 딜러 감마가 이 범위 전체에서 한쪽으로 쏠린 상태라는 뜻이며, 지지·저항으로 쓸 플립 가격은 없습니다." + _vc_s)
    lines.append(f"   ④ [파이프라인 4단계: 다년도 스케일 정규화 & 레짐 전이 사령탑] : 전체 활성 미결제약정({tot_active_oi_now:,}계약, 전일 {tot_active_oi_prev:,}계약) 대비 상대 수급 비중은 상승연료(Call Q1) +{cq1_rel_oi_pct:.2f}%(전일 +{cq1_rel_prev:.2f}%), 바닥방석(Put Q2) +{pq2_rel_oi_pct:.2f}%, 하방폭탄(Put Q1) +{pq1_rel_oi_pct:.2f}%이며, 252일 롤링 백분위수 결합 결과 1순위 지배 전략은 전일 [{prev_tr['TopReg']}]에서 당일 [{regime_ranking[0][0]} ({regime_ranking[0][1]:.1f}%)]로 전환되었습니다.")
    lines.append(sep_bold)
    lines.append("")
    # ★ [이력 블록] [섹션 6] 이력 요약 블록 (여기서 오류가 나도 보고서 생성은 계속됩니다)
    # ★ [V4.3.6] 신호 기록·자동 채점 -> (6-5) (여기서 오류가 나도 보고서 생성은 계속됩니다)
    _sig_lines = []
    if USE_SIGNAL_LOG:
        try:
            _iv_now = float(curr_ts['Near_ATM_IV']) if np.isfinite(float(curr_ts['Near_ATM_IV'])) else np.nan
            _today_rec = {
                '기준일': str(latest_date), 'Tier': str(t_cfg.get('code', '')), '엔진버전': ENGINE_VERSION,
                'EWY종가': f"{latest_spot:.2f}", '근월ATM_IV': '' if not np.isfinite(_iv_now) else f"{_iv_now:.4f}",
                '레짐1순위': str(regime_ranking[0][0]), '국면1순위': _ph_kr[_ph_top], '하락국면': str(_ph_top == 'D'), '급락위험상': str(_rk_lv == '상'),
                '원인1': str(bool(is_bear_shift_active)), '원인2': str(bool(has_near_ambush_put)), '검증경보': str(bool(_now.get('v44'))),
                '기습1차타깃': f"{float(ewy_amb_target1):.2f}", '기습2차타깃': f"{float(ewy_amb_target2):.2f}",
                'D선': '' if p_now.get('gflip_none') else f"{float(p_now['gflip']):.2f}", 'D선없음': str(bool(p_now.get('gflip_none'))),
                'D선부호': str(p_now.get('gflip_sign', '')),
                'A선': '' if not np.isfinite(float(p_now.get('gflip_a', np.nan))) else f"{float(p_now['gflip_a']):.2f}",
                'A선없음': str(bool(p_now.get('gflip_a_none'))), 'GEX_D': str(int(p_now.get('gex_1pct', 0))),
                '원인1_병행': (str(bool(_sh.get('c1'))) if _sh else ''), '원인2_병행': (str(bool(_sh.get('c2'))) if _sh else ''),
                '병행_지배력': (f"{float(_sh.get('ratio', 0.0)):.0f}" if _sh else ''), 'D선정의': DLINE_DEF, 'D선_이전': ''}
            _sig_lines = run_signal_log_and_score(_today_rec, df_pit, pit_meta, latest_date)
        except Exception as _sl_e:
            _sig_lines = [f"### (6-5) 신호 기록·채점 생성 실패: {_sl_e}"]
    try:
        lines.extend(build_history_block(df_pit, all_dates, latest_date, ts_metrics, hist_traj_df, _ph_tbl, w_short,
                                         snap_fn=_calc_pipeline_snapshot, extra_lines=_sig_lines))
    except Exception as _hb_e:
        lines.append(f"## [섹션 6] 이력 요약 블록 생성 실패: {_hb_e}")
        lines.extend(_sig_lines)
    lines.append("")

    # ★ [PC버젼 vs 모바일버젼 최종 실행 지시문 분기]
    if view_version == "MOBILE":
        lines.append(
            "[최종 실행 지시 (📱 모바일버젼): "
            "1) 모든 정량 표(Table)는 이미 별도 뷰어로 생성되어 있으므로 마크다운 표나 HTML <table> 태그로 표를 다시 그리는 작업을 절대 하지 마십시오. "
            "2) 대화창 첫 줄에는 '[기준일] 1순위 레짐(확률) | 국면(확률) · 급락 위험도 | EWY 종가' 1줄만 출력하고, 본문 텍스트는 길어서 모바일 채팅창으로 보기 어려우므로 채팅창에 바로 출력하지 마십시오. "
            "3) 곧바로 [섹션 0]부터 [섹션 5]까지의 '핵심 독해 가이드'와 '투자자 눈높이 쉬운 해설 및 실전 판단'만 순수 텍스트(제목·글머리 기호·문단, 표 완전 제외)로 끝까지 작성하여 단일 모바일 HTML 파일(.html)로 생성·제출하십시오.]"
        )
    else:
        lines.append(
            "[최종 실행 지시 (💻 PC버젼): 대화창에는 1줄 요약만 출력하고, 파이썬 코드로 이 텍스트 파일의 표들을 직접 파싱해 HTML <table>로 변환한 뒤 섹션 0~1, 섹션 2, 섹션 3~5의 3단계 분할 이어쓰기 방식으로 단일 HTML 보고서 파일을 즉시 생성·제출하십시오.]"
        )

    # ★ [V4.3.7] [데이터 품질 점검] 블록 — [섹션 1] 바로 앞에 넣음 (여기서 오류가 나도 보고서 생성은 계속됩니다)
    try:
        _sch = _div_schedule(latest_date, latest_spot, (pd.Timestamp(latest_date) + pd.Timedelta(days=400)).strftime('%Y-%m-%d'))
        if _sch and (pd.Timestamp(_sch[0][0]) - pd.Timestamp(latest_date)).days <= 120:
            _ex1, _amt1, _est1 = _sch[0]
            _day_all = df_pit[df_pit['Quote Date'] == latest_date]
            _exps_after = sorted(set(_day_all.loc[(_day_all['Expiration Date'] >= _ex1) & (_day_all['Open Interest'] > 0), 'Expiration Date'].astype(str)))
            _pc = _parity_div_check_v437(_day_all, latest_spot, latest_date) or {}
            _dv = {'ex': _ex1, 'amt': _amt1, 'est': _est1, 'amt_pct': _amt1 / max(latest_spot, 1e-6) * 100.0, 'n_exp': len(_exps_after),
                   'first_exp': _exps_after[0] if _exps_after else '-', 'implied': _pc.get('implied', np.nan), 'n_post': _pc.get('n_post', 0)}
            if np.isfinite(_dv['implied']) and abs(_dv['implied'] - _amt1) > 0.35 * _amt1 and (pd.Timestamp(_ex1) - pd.Timestamp(latest_date)).days <= 45:
                _dv['warn'] = f"설정 {_amt1:.2f}달러 vs 역산 {_dv['implied']:.2f}달러"
            _dq['div'] = _dv
        if _DIV_FIX_INFO:
            _dq['fix'] = dict(_DIV_FIX_INFO)
        _known_div = {d_: a_ for d_, a_ in DIVIDEND_EVENTS}
        _ld = str(latest_date)[:10]
        _amt_today = _known_div.get(_ld)
        if _amt_today is None and _ld == _proj_exdate(int(_ld[:4])) and not any(d_[:4] == _ld[:4] for d_ in _known_div):
            _amt_today = DIV_PROJ_YIELD * latest_spot
        if _amt_today:
            _dq['exday'] = {'chg': float(daily_chg_pct), 'div_pct': float(_amt_today) / max(latest_spot / (1.0 + daily_chg_pct / 100.0), 1e-6) * 100.0}
        if _dq.get('stale_list'):
            _uniq = list(dict.fromkeys(_dq['stale_list']))
            _dq['stale'] = {'n': len(_uniq), 'ex': ', '.join(_uniq[:2])}
        _dq_lines = build_dq_block_v437(_dq)
        _i_s1 = next((i_ for i_, l_ in enumerate(lines) if str(l_).startswith('## [섹션 1]')), None)
        if _i_s1 is not None:
            lines[_i_s1:_i_s1] = _dq_lines
        else:
            lines.extend(_dq_lines)
    except Exception as _dq_e:
        lines.append(f"### [데이터 품질 점검] 생성 실패: {_dq_e}")

    return "\n".join(lines)

# ==============================================================================
# 11. 메인 실행 파이프라인 (Step 1: Tier 선택 -> Step 1-2: 버전 선택 -> Step 2: 기준일 선택 -> 결과 저장)
# ==============================================================================
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1) 입력 폴더 내 모든 CSV 병합 로드
    merged_data, file_names = load_and_merge_csv_files(INPUT_DIR)

    # 2) ★ [Step 1] 월가 4대 계층(Tier 1 ~ Tier 4 및 통합 마스터) 최우선 선택
    selected_tier_keys = select_analysis_tiers_interactively()

    # 2-B) ★ [Step 1-2] 출력 버전(PC버젼 vs 모바일버젼) 선택
    selected_view_version = select_view_version_interactively()

    # 3) ★ [Step 2] 분석 기준일(최신일 vs 과거 특정일/구간) 선택
    target_date_list = select_analysis_dates_interactively(merged_data)

    # 4) 선택된 Tier(들) × 선택된 기준일(들) 조합에 대해 미래참조 차단 분석 및 Text 파일 생성
    sync_override_cache = {}
    for t_date in target_date_list:
        df_pit, pit_meta = apply_point_in_time_cutoff(merged_data, t_date)

        for t_key in selected_tier_keys:
            t_cfg = TIER_CONFIGS[t_key]
            print(f"\n🚀 [{t_cfg['name']} | {selected_view_version} 버젼] 모델 기반 시계열 회귀 및 옵션 미시구조 연산(V4.4)을 시작합니다...")

            rel_info, derive_target_fn = fetch_yf_and_build_relationship_model(
                df_pit,
                pit_meta,
                lookback_days=t_cfg['corr_days'],
                halflife=t_cfg['halflife'],
                sync_override_cache=sync_override_cache
            )
            report_txt = generate_4regime_quant_report(
                df_pit,
                file_names,
                pit_meta,
                t_cfg,
                rel_info,
                derive_target_fn,
                view_version=selected_view_version
            )

            anchor_dt_compact = pit_meta['anchor_date'].replace("-", "")
            now_stamp = datetime.now().strftime("%H%M%S")
            ver_suffix = "_MOBILE" if selected_view_version == "MOBILE" else "_PC"
            output_filename = f"Tier{t_key}{ver_suffix}_{anchor_dt_compact}_{now_stamp}.txt"
            # ★ [기준일 폴더] 기준일 이름의 폴더(예: 20261112)를 만들어 그 안에 저장합니다.
            #    PC 프로그램의 3분할 모드는 분할 프롬프트 3개와 표 뷰어를 이 데이터북 옆(같은 폴더)에 만듭니다.
            date_dir = os.path.join(OUTPUT_DIR, anchor_dt_compact)
            os.makedirs(date_dir, exist_ok=True)
            output_filepath = os.path.join(date_dir, output_filename)

            with open(output_filepath, "w", encoding="utf-8-sig") as f:
                f.write(report_txt)

            print(report_txt)
            print(f"\n✅ [저장 완료] [{pit_meta['anchor_date']} 기준 | {t_cfg['short_tag']} | {selected_view_version} 버젼] V4.4 분석 Text 파일이 저장되었습니다 (엔진 V4.3.6):")
            print(f"   📂 {output_filepath}\n")