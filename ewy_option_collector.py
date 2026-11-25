# -*- coding: utf-8 -*-
r"""
EWY 옵션 데이터 수집기 — PC판 (구글 코랩 수집 코드 이식)
==============================================================================
- 야후파이낸스(yfinance)에서 EWY 전체 만기 옵션 체인을 받아 미국식 이항모형 IV와 블랙-숄즈 델타를 계산하고,
  코랩판과 같은 이름·열 구성의 CSV('EWY Option 분석데이터_YYYYMMDD.csv')로 저장합니다.
- 계산식은 코랩판과 똑같습니다 (이항모형 N=50, 이분법 최대 50회·허용오차 0.001, 배당수익률 2%, 잔존기간 = 영업일/252,
  가격 = 호가 중간값 또는 호가가 없으면 최종 체결가) -> 지금까지 쌓은 CSV와 값이 그대로 이어집니다.

PC판에서 달라진 점
  1) 저장 위치: '구글 드라이브 데스크톱' 폴더를 자동으로 찾아 코랩과 같은 경로(.../03. 클로드 옵션분석/daily)에 저장
     -> 드라이브로 동기화되므로 코랩 분석 엔진은 그대로 사용. 못 찾으면 이 프로그램 폴더의 data\daily에 저장
  2) 야후 접속: 실패하면 기다렸다가 다시 시도하고(접속 제한이면 더 길게), 만기 사이에 잠깐씩 쉼
  3) 현물 주가를 못 받으면 저장하지 않음 (코랩판은 주가 없이 저장해 IV·델타가 모두 빈칸인 파일이 생길 수 있었음)
     만기 일부를 못 받았거나 유효 IV가 너무 적으면 daily가 아닌 '검증실패' 하위 폴더에 저장
  4) SOFR 금리는 FRED에서 직접 받음 (pandas_datareader 불필요). 실패하면 직전 CSV 값 -> 기본값 순서로 대체
  5) 장 마감 뒤 수집해 둔 같은 기준일 파일은 휴장일·주말 재실행으로 덮어쓰지 않음 (강제: --overwrite)
  6) 복구 모드: 주가·IV가 빈칸인 CSV를 그날 종가로 다시 계산 (--repair)
  7) 실행 기록을 logs 폴더에 저장

사용법 (보통은 2_수집실행.bat 더블클릭. 명령 프롬프트에서는 아래처럼)
  python ewy_option_collector.py                          수집
  python ewy_option_collector.py --out "D:\옵션\daily"     저장 폴더 직접 지정
  python ewy_option_collector.py --overwrite              같은 기준일 파일 덮어쓰기
  python ewy_option_collector.py --repair "...\EWY Option 분석데이터_20261112.csv" [--price 123.45]
종료 코드: 0 정상 / 1 '검증실패' 폴더에 저장 / 2 저장하지 않고 중단 / 3 예기치 못한 오류
          / 4 복구에 쓸 그날 종가를 받지 못함(--price 로 직접 입력)
"""
import argparse
import io
import logging
import os
import random
import shutil
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ewy_paths import DRIVE_SUBPATH, detect_save_dir as _detect_dir   # noqa: E402  (저장 폴더 찾기 — 프로그램 창과 공용)

# ==============================================================================
# 설정 (필요하면 여기만 고치세요)
# ==============================================================================
SYMBOL             = 'EWY'
SAVE_DIR           = r''      # 비워 두면 자동 탐지. 직접 지정 예: r'G:\내 드라이브\00. 주가모니터링\02. 옵션데이터분석\03. 클로드 옵션분석\daily'
DIVIDEND_YIELD     = 0.02
SOFR_FALLBACK      = 3.62     # FRED와 직전 CSV 모두 실패할 때만 사용 (코랩판 기본값과 같음)
REQUEST_PAUSE_SEC  = 0.6      # 만기별 요청 사이 쉬는 시간(초) — 야후 접속 제한 예방
MAX_RETRY          = 3        # 요청 1건당 최대 시도 횟수
MIN_VALID_IV_SHARE = 0.10     # IV > 0.05 인 행 비율이 이보다 낮으면 '검증실패' 폴더에 저장
KEEP_LOGS          = 120      # logs 폴더에 남길 실행 기록 개수

BASE_DIR = Path(__file__).resolve().parent
NY = 'America/New_York'
LOG = logging.getLogger('ewy_collector')

# ---- 프로그램 창(GUI)과 연결하는 부분: 진행률 알림 · 중지 · 결과 요약 ----
PROGRESS_HOOK = None          # callable(stage:int, frac:float, text:str)
CANCEL = threading.Event()    # '중지' 버튼
LAST_RESULT = {}              # 마지막 수집·복구 결과 요약


class Cancelled(Exception):
    """사용자가 '중지'를 눌렀을 때"""


def _progress(stage, frac=0.0, text=''):
    if CANCEL.is_set():
        raise Cancelled()
    if PROGRESS_HOOK is not None:
        try:
            PROGRESS_HOOK(stage, float(frac), text)
        except Exception:
            pass


def _sleep(sec):
    """기다리는 중에도 '중지'에 바로 반응"""
    if CANCEL.wait(sec):
        raise Cancelled()


def _result(**kw):
    LAST_RESULT.clear()
    LAST_RESULT.update(kw)


# ==============================================================================
# 계산식 — 코랩판과 한 글자도 다르지 않게 유지 (과거 데이터와의 연속성)
# ==============================================================================
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
    if target_price <= 0 or T <= 0:
        return np.nan
    low_vol, high_vol = 1e-4, 5.0
    for _ in range(max_iter):
        mid_vol = (low_vol + high_vol) / 2.0
        price = american_binomial_tree(S, K, T, r, q, mid_vol, opt_type)
        if abs(price - target_price) < tol:
            return mid_vol
        if price > target_price:
            high_vol = mid_vol
        else:
            low_vol = mid_vol
    return mid_vol


def calculate_bs_delta(S, K, T, r, q, sigma, opt_type):
    if pd.isna(sigma) or sigma <= 0 or T <= 0:
        return np.nan
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if opt_type.startswith('C'):
        return np.exp(-q * T) * norm.cdf(d1)
    else:
        return np.exp(-q * T) * (norm.cdf(d1) - 1.0)


def compute_iv_delta(df, price_col, r, rows=None):
    """코랩판 6단계 루프와 같은 규칙으로 IV·델타 계산 (rows: 계산할 행 번호, None이면 전체)"""
    iv_results = [np.nan] * len(df)
    delta_results = [np.nan] * len(df)
    idx = range(len(df)) if rows is None else rows
    total, t0 = len(idx), time.time()
    for n, i in enumerate(idx, 1):
        row = df.iloc[i]
        S = row[price_col]
        K = row['Strike']
        T = row['T']
        opt_type = row['Option Type']
        bid = row['Bid']
        ask = row['Ask']
        last_price = row['Last Price']

        if pd.notnull(bid) and pd.notnull(ask) and bid > 0 and ask > 0:
            target_price = (bid + ask) / 2.0
        else:
            target_price = last_price

        if target_price > 0 and pd.notnull(S) and pd.notnull(K) and T > 0:
            iv = calculate_iv_american(target_price, S, K, T, r, DIVIDEND_YIELD, opt_type)
            iv_results[i] = iv
            delta_results[i] = calculate_bs_delta(S, K, T, r, DIVIDEND_YIELD, iv, opt_type)
        if n % 20 == 0 or n == total:
            _progress(5, n / max(total, 1), f"IV·델타 계산 {n:,}/{total:,}")
        if n % 1000 == 0 or n == total:
            LOG.info(f"  - IV·델타 계산 {n:,}/{total:,} ({time.time() - t0:.0f}초)")
    return iv_results, delta_results


def busday_T(quote_dates, exp_dates):
    bus_days = np.busday_count(
        pd.to_datetime(quote_dates).values.astype('datetime64[D]'),
        pd.to_datetime(exp_dates).values.astype('datetime64[D]')
    )
    return np.maximum(bus_days, 0.5) / 252.0


def fmt4(x):
    return round(x, 4) if pd.notnull(x) else ""


# ==============================================================================
# 환경: 로그 · 저장 폴더 · SOFR · 야후 재시도
# ==============================================================================
def setup_logging(tag, console=True):
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    path = log_dir / f"{tag}_{datetime.now():%Y%m%d_%H%M%S}.log"
    LOG.setLevel(logging.INFO)
    for h in list(LOG.handlers):
        LOG.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass
    fh = logging.FileHandler(path, encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s  %(message)s', '%Y-%m-%d %H:%M:%S'))
    LOG.addHandler(fh)
    if console and sys.stdout is not None:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter('%(message)s'))
        LOG.addHandler(sh)
    for old in sorted(log_dir.glob('*.log'), key=os.path.getmtime)[:-KEEP_LOGS]:
        try:
            old.unlink()
        except OSError:
            pass
    return path


def detect_save_dir():
    """구글 드라이브 데스크톱(가상 드라이브 G: 등 / 미러링 폴더 / macOS) 안에서 '00. 주가모니터링' 폴더가 있는 곳을 찾음"""
    d, where, _ = _detect_dir(SAVE_DIR, BASE_DIR / 'data' / 'daily')
    return d, where


def fetch_sofr(save_dir=None, upto=None):
    """FRED CSV 직접 조회 -> 실패하면 직전 CSV의 SOFR -> 기본값. (값은 코랩판처럼 소수 둘째 자리 반올림)"""
    try:
        req = urllib.request.Request('https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR',
                                     headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8', 'replace')
        s = pd.read_csv(io.StringIO(raw))
        s = pd.DataFrame({'d': pd.to_datetime(s.iloc[:, 0], errors='coerce'),
                          'v': pd.to_numeric(s.iloc[:, 1], errors='coerce')}).dropna()
        if upto is not None:
            s = s[s['d'] <= pd.Timestamp(str(upto))]
        if len(s):
            return round(float(s['v'].iloc[-1]), 2), f"FRED {s['d'].iloc[-1]:%Y-%m-%d}"
    except Exception as e:
        LOG.info(f"  - FRED SOFR 조회 실패({type(e).__name__}) -> 직전 CSV 값으로 대체 시도")
    if save_dir is not None and Path(save_dir).is_dir():
        for f in sorted(Path(save_dir).glob(f"{SYMBOL} Option 분석데이터_*.csv"), reverse=True):
            try:
                v = pd.to_numeric(pd.read_csv(f, encoding='utf-8-sig', nrows=5)['Secured Overnight Financing Rate'],
                                  errors='coerce').dropna()
                if len(v) and v.iloc[0] > 0:
                    return round(float(v.iloc[0]), 2), f"직전 CSV({f.name})"
            except Exception:
                continue
    return SOFR_FALLBACK, '기본값'


def _is_rate_limited(e):
    t = f"{type(e).__name__} {e}"
    return ('RateLimit' in t) or ('Too Many Requests' in t) or (' 429' in t) or ('429 ' in t)


def call_with_retry(fn, what, tries=MAX_RETRY):
    for i in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            if i == tries:
                raise
            if isinstance(e, Cancelled):
                raise
            wait = (30 if _is_rate_limited(e) else 3) * (2 ** (i - 1)) + random.uniform(0, 2)
            LOG.info(f"  - {what} 실패({type(e).__name__}: {str(e)[:100]}) -> {wait:.0f}초 후 재시도 ({i}/{tries - 1})")
            _sleep(wait)


def spot_from_history(ticker):
    def _get():
        h = ticker.history(period="1d")
        if h is None or h.empty or 'Close' not in h.columns or pd.isna(h['Close'].iloc[-1]):
            raise RuntimeError('주가 이력이 비어 있음')
        return h
    try:
        hist = call_with_retry(_get, '현물 주가 조회')
        return round(hist['Close'].iloc[-1], 2), hist.index[-1].date(), 'history(1d)'
    except Exception as e:
        LOG.info(f"  - 현물 주가(history) 실패: {type(e).__name__} -> 옵션 체인의 기초자산 시세로 대체 시도")
        return None, None, None


def spot_from_chain(chain):
    und = getattr(chain, 'underlying', None) or {}
    p, t = und.get('regularMarketPrice'), und.get('regularMarketTime')
    if p is None or not np.isfinite(float(p)) or float(p) <= 0:
        return None, None, None
    qd = pd.Timestamp(int(t), unit='s', tz='UTC').tz_convert(NY).date() if t else pd.Timestamp.now(tz=NY).date()
    return round(float(p), 2), qd, 'option_chain.underlying'


def existing_is_final(path, quote_date):
    """같은 기준일 파일이 이미 '장 마감 뒤' 수집본이고, 지금이 그다음 날 이후(휴장일·주말 재실행)면 True"""
    if not path.exists():
        return False
    mt = pd.Timestamp(path.stat().st_mtime, unit='s', tz='UTC').tz_convert(NY)
    close_ny = pd.Timestamp(str(quote_date)).tz_localize(NY) + pd.Timedelta(hours=16, minutes=15)
    return (mt >= close_ny) and (pd.Timestamp.now(tz=NY).date() > mt.date())


def atomic_to_csv(df, path):
    """임시 파일에 다 쓴 뒤 한 번에 바꿔치기 -> 드라이브가 반쯤 쓴 파일을 동기화하는 일을 막음.
    줄바꿈은 코랩(리눅스)과 같은 LF로 고정 — 윈도우 기본값(CRLF)을 쓰면 코랩판과 파일이 달라짐"""
    tmp = path.with_name(path.name + '.tmp')
    df.to_csv(tmp, index=False, encoding='utf-8-sig', lineterminator='\n')
    for attempt in range(1, 6):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 5:
                tmp.unlink(missing_ok=True)
                raise PermissionError(f"'{path.name}' 파일이 엑셀 등 다른 프로그램에 열려 있어 저장하지 못했습니다. "
                                      f"닫고 다시 실행하세요.")
            time.sleep(2)      # 드라이브 동기화·백신 검사로 잠깐 잠긴 경우
        except OSError:
            shutil.copyfile(tmp, path)     # 바꿔치기를 지원하지 않는 드라이브면 복사로 저장
            tmp.unlink(missing_ok=True)
            return


# ==============================================================================
# 수집
# ==============================================================================
def collect(out=None, overwrite=False):
    t_start = time.time()
    save_dir, where = (Path(out), '직접 지정') if out else detect_save_dir()
    save_dir.mkdir(parents=True, exist_ok=True)
    base = dict(kind='collect', save_dir=str(save_dir), where=where)
    _result(**base, rc=3, status='error', title='진행 중 오류', message='')
    LOG.info("=" * 70)
    LOG.info(f" EWY 옵션 데이터 수집기 (PC판) · 기초자산 {SYMBOL}")
    LOG.info(f" 저장 폴더: {save_dir}  [{where}]")
    LOG.info("=" * 70)

    _progress(1, 0.0, '준비')
    import yfinance as yf
    LOG.info(f"[1/5] 준비: yfinance {getattr(yf, '__version__', '?')} · pandas {pd.__version__} · Python {sys.version.split()[0]}")

    _progress(2, 0.0, 'SOFR 금리 조회')
    sofr_rate, sofr_src = fetch_sofr(save_dir)
    LOG.info(f"[2/5] SOFR 금리 {sofr_rate}% ({sofr_src})")

    _progress(3, 0.0, '현물 주가 조회')
    ticker = yf.Ticker(SYMBOL)
    etf_price, quote_date, price_src = spot_from_history(ticker)
    expirations = list(call_with_retry(lambda: ticker.options, '만기 목록 조회') or [])
    if not expirations:
        LOG.info("[중단] 옵션 만기 목록을 받지 못했습니다. 잠시 뒤 다시 실행하세요. (저장하지 않음)")
        _result(**base, rc=2, status='aborted', title='수집 중단 — 저장하지 않음',
                message='옵션 만기 목록을 받지 못했습니다. 야후 접속이 잠시 막혔을 수 있으니 30분~몇 시간 뒤 다시 시도하세요.')
        return 2

    first_chain = None
    if etf_price is None:
        try:
            first_chain = call_with_retry(lambda: ticker.option_chain(expirations[0]), f"만기 {expirations[0]} 옵션 체인")
            etf_price, quote_date, price_src = spot_from_chain(first_chain)
        except Exception as e:
            LOG.info(f"  - 옵션 체인 조회도 실패: {type(e).__name__}")
    if etf_price is None:
        LOG.info("[중단] 현물 주가를 받지 못해 저장하지 않았습니다. 주가 없이 저장하면 IV·델타가 모두 빈칸이 되어 "
                 "분석 엔진에서 오류가 납니다. 잠시 뒤 다시 실행하세요.")
        _result(**base, rc=2, status='aborted', title='수집 중단 — 저장하지 않음',
                message='EWY 현물 주가를 받지 못했습니다. 주가 없이 저장하면 IV·델타가 빈칸이 되어 분석 엔진에서 오류가 나므로 '
                        '저장하지 않았습니다. 잠시 뒤 다시 시도하세요.')
        return 2
    LOG.info(f"[3/5] {SYMBOL} 현물 {etf_price} 달러 · 기준 거래일 {quote_date} ({price_src})")
    base.update(quote_date=str(quote_date), spot=float(etf_price))

    date_str = quote_date.strftime('%Y%m%d')
    save_csv_name = f"{SYMBOL} Option 분석데이터_{date_str}.csv"
    target = save_dir / save_csv_name
    if existing_is_final(target, quote_date) and not overwrite:
        LOG.info(f"[건너뜀] 장 마감 뒤에 수집한 같은 기준일 파일이 이미 있습니다: {save_csv_name}")
        LOG.info("         (휴장일·주말 재실행으로 보임. 그래도 새로 받으려면 --overwrite 를 붙여 실행)")
        _result(**base, rc=0, status='skipped', file=str(target), title='이미 받은 데이터 — 건너뜀',
                message=f'{quote_date} 기준 파일을 장 마감 뒤에 이미 받아 두었습니다. 휴장일·주말이라 새 데이터가 없습니다. '
                        f'그래도 다시 받으려면 "같은 날짜 파일도 다시 받기"를 켜고 수집하세요.')
        return 0

    LOG.info(f"[4/5] 전체 만기 {len(expirations)}개 옵션 체인 수집 중...")
    all_options, failed, streak = [], [], 0
    for n, exp_date in enumerate(expirations, 1):
        _progress(4, (n - 1) / len(expirations), f"옵션 체인 {n}/{len(expirations)} (만기 {exp_date})")
        try:
            if n == 1 and first_chain is not None:
                opt_chain = first_chain
            else:
                opt_chain = call_with_retry(lambda e=exp_date: ticker.option_chain(e), f"만기 {exp_date} 옵션 체인")
            streak = 0
        except Exception as e:
            failed.append(exp_date)
            streak += 1
            LOG.info(f"  - [실패] 만기 {exp_date}: {type(e).__name__}: {str(e)[:120]}")
            if streak >= 3:
                LOG.info("[중단] 연속 3개 만기를 받지 못했습니다. 야후가 접속을 제한 중일 수 있습니다. "
                         "30분~몇 시간 뒤 다시 실행하세요. (저장하지 않음)")
                _result(**base, rc=2, status='aborted', title='수집 중단 — 저장하지 않음',
                        message='옵션 체인을 연속으로 받지 못했습니다. 야후가 접속을 잠시 제한 중일 수 있습니다. '
                                '30분~몇 시간 뒤 다시 시도하세요.')
                return 2
            continue
        calls = opt_chain.calls.copy()
        calls['Option Type'] = 'Call'
        calls['Expiration Date'] = exp_date
        all_options.append(calls)
        puts = opt_chain.puts.copy()
        puts['Option Type'] = 'Put'
        puts['Expiration Date'] = exp_date
        all_options.append(puts)
        if n % 5 == 0 or n == len(expirations):
            LOG.info(f"  - {n}/{len(expirations)} 만기 수집")
        if n < len(expirations):
            _sleep(REQUEST_PAUSE_SEC)

    if not all_options:
        LOG.info("[중단] 받은 옵션 데이터가 없습니다. (저장하지 않음)")
        _result(**base, rc=2, status='aborted', title='수집 중단 — 저장하지 않음',
                message='받은 옵션 데이터가 없습니다. 잠시 뒤 다시 시도하세요.')
        return 2

    # ---- 이하 코랩판 4~7단계와 같은 가공 ----
    df = pd.concat(all_options, ignore_index=True)
    df.rename(columns={
        'contractSymbol': 'Contract Name',
        'strike': 'Strike',
        'bid': 'Bid',
        'ask': 'Ask',
        'lastPrice': 'Last Price',
        'volume': 'Volume',
        'openInterest': 'Open Interest'
    }, inplace=True)
    for col in ['Bid', 'Ask', 'Last Price', 'Volume', 'Open Interest']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Quote Date'] = quote_date
    df['Secured Overnight Financing Rate'] = sofr_rate
    price_col_name = f"{SYMBOL} Price"
    df[price_col_name] = etf_price
    df['Expiration Date'] = pd.to_datetime(df['Expiration Date']).dt.date
    df['T'] = busday_T(df['Quote Date'], df['Expiration Date'])
    r = sofr_rate / 100.0

    LOG.info(f"[5/5] 계약 {len(df):,}개 IV·델타 계산 중 (코랩판과 같은 미국식 이항모형)...")
    _progress(5, 0.0, f"IV·델타 계산 0/{len(df):,}")
    iv_results, delta_results = compute_iv_delta(df, price_col_name, r)
    df['Implied Volatility'] = iv_results
    df['Delta'] = delta_results
    iv_num = pd.to_numeric(df['Implied Volatility'], errors='coerce')
    valid_share = float((iv_num > 0.05).mean()) if len(df) else 0.0
    no_quote_share = float(((df['Bid'] <= 0) & (df['Ask'] <= 0)).mean()) if len(df) else 0.0
    df['Implied Volatility'] = df['Implied Volatility'].apply(fmt4)
    df['Delta'] = df['Delta'].apply(fmt4)

    final_columns = ['Contract Name', 'Quote Date', 'Expiration Date', 'Option Type', 'Strike', 'Bid', 'Ask',
                     'Last Price', 'Volume', 'Open Interest', 'Secured Overnight Financing Rate', price_col_name,
                     'Implied Volatility', 'Delta']
    df_final = df[final_columns].copy()
    df_final['Volume'] = df_final['Volume'].astype(int)
    df_final['Open Interest'] = df_final['Open Interest'].astype(int)
    df_final['Quote Date'] = pd.to_datetime(df_final['Quote Date']).dt.strftime('%Y-%m-%d')
    df_final['Expiration Date'] = pd.to_datetime(df_final['Expiration Date']).dt.strftime('%Y-%m-%d')

    problems = []
    if failed:
        problems.append(f"만기 {len(failed)}개를 받지 못함({', '.join(failed)}) — 그대로 쓰면 OI 합계가 줄어 가짜 청산 신호가 생김")
    if valid_share < MIN_VALID_IV_SHARE:
        problems.append(f"IV가 0.05를 넘는 행이 {valid_share:.1%}뿐 — 정상 파일이 아닐 가능성")
    if problems:
        bad_dir = save_dir / '검증실패'
        bad_dir.mkdir(exist_ok=True)
        target = bad_dir / save_csv_name
    _progress(6, 0.0, '파일 저장')
    atomic_to_csv(df_final, target)
    stats = dict(file=str(target), contracts=int(len(df_final)), valid_iv=round(valid_share, 4),
                 no_quote=round(no_quote_share, 4), expirations=f"{len(expirations) - len(failed)}/{len(expirations)}",
                 seconds=round(time.time() - t_start), problems=problems, sofr=sofr_rate,
                 drive_missing=where.startswith('프로그램 폴더'))
    if problems:
        _result(**base, **stats, rc=1, status='invalid', title="불완전한 데이터 — '검증실패' 폴더에 저장",
                message="아래 이유로 daily 폴더가 아닌 '검증실패' 폴더에 저장했습니다. 잠시 뒤 다시 수집하세요.")
    else:
        _result(**base, **stats, rc=0, status='ok', title='수집 완료 — 정상 저장', message='')

    LOG.info("=" * 70)
    LOG.info(f" 계약 {len(df_final):,}개 · 만기 {len(expirations) - len(failed)}/{len(expirations)}개 · "
             f"유효 IV(>0.05) {valid_share:.1%} · 호가 없는 계약 {no_quote_share:.1%} · 소요 {time.time() - t_start:.0f}초")
    if problems:
        LOG.info(" [검증실패] 아래 이유로 daily가 아닌 '검증실패' 폴더에 저장했습니다. 다시 실행해 정상 파일을 받으세요.")
        for p in problems:
            LOG.info(f"   - {p}")
    else:
        LOG.info(" [완료] 정상 저장")
    LOG.info(f" 파일: {target}")
    if where.startswith('프로그램 폴더'):
        LOG.info(" [주의] 구글 드라이브 폴더를 찾지 못해 프로그램 폴더에 저장했습니다. 코랩 분석 엔진에서 쓰려면 "
                 "구글 드라이브 데스크톱이 켜져 있는지 확인하거나 저장 폴더를 직접 지정하세요.")
    LOG.info("=" * 70)
    return 1 if problems else 0


# ==============================================================================
# 복구: 주가·IV가 빈칸인 CSV를 그날 종가로 다시 계산
# ==============================================================================
def fetch_close_for_date(quote_date):
    import yfinance as yf
    start = pd.Timestamp(str(quote_date))
    end = start + pd.Timedelta(days=1)

    def _get():
        h = yf.Ticker(SYMBOL).history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), auto_adjust=False)
        if h is None or h.empty:
            raise RuntimeError('해당일 주가가 비어 있음')
        return h
    try:
        h = call_with_retry(_get, f"{quote_date} 종가 조회")
    except Exception as e:
        LOG.info(f"  - {quote_date} 종가 조회 실패: {type(e).__name__}")
        return None
    hit = h[[d.date() == quote_date for d in h.index]]
    return round(float(hit['Close'].iloc[-1]), 2) if len(hit) else None


def repair_csv(path_str, manual_price=None):
    path = Path(path_str)
    base = dict(kind='repair', file=str(path), name=path.name)
    LOG.info("=" * 70)
    LOG.info(f" 복구 모드: {path}")
    LOG.info("=" * 70)
    _progress(1, 0.0, '파일 진단')
    if not path.is_file():
        LOG.info("[오류] 파일이 없습니다.")
        _result(**base, rc=2, status='error', title='파일이 없습니다', message=str(path))
        return 2
    df = pd.read_csv(path, encoding='utf-8-sig')
    price_col = next((c for c in df.columns if c.endswith(' Price') and c != 'Last Price'), None)
    need = ['Quote Date', 'Expiration Date', 'Option Type', 'Strike', 'Bid', 'Ask', 'Last Price', 'Implied Volatility', 'Delta']
    missing = [c for c in need if c not in df.columns]
    if price_col is None or missing:
        LOG.info(f"[오류] 수집기 CSV 형식이 아닙니다 (없는 열: {missing or [SYMBOL + ' Price']})")
        _result(**base, rc=2, status='error', title='수집기 CSV 형식이 아닙니다',
                message=f"없는 열: {', '.join(missing or [SYMBOL + ' Price'])}")
        return 2

    quote_date = pd.to_datetime(sorted(df['Quote Date'].dropna().astype(str).unique())[-1]).date()
    base.update(quote_date=str(quote_date))
    n = len(df)
    S = pd.to_numeric(df[price_col], errors='coerce')
    iv = pd.to_numeric(df['Implied Volatility'], errors='coerce')
    before = float((iv > 0.05).mean()) if n else 0.0
    LOG.info(f"[진단] 기준일 {quote_date} · {n:,}행 · 주가 있는 행 {int((S > 0).sum()):,} · "
             f"IV 있는 행 {int(iv.notna().sum()):,} · IV>0.05 행 {int((iv > 0.05).sum()):,} ({before:.1%})")
    need_price = int((S > 0).sum()) == 0
    if not need_price and before >= MIN_VALID_IV_SHARE:
        LOG.info("[이상 없음] 주가와 IV가 정상이라 고칠 것이 없습니다.")
        _result(**base, rc=0, status='clean', title='이상 없음 — 고칠 것이 없습니다', valid_iv=round(before, 4),
                message='주가와 IV가 정상입니다.')
        return 0

    spot = None
    if need_price:
        _progress(2, 0.0, '그날 종가 확인')
        spot = round(float(manual_price), 2) if manual_price else fetch_close_for_date(quote_date)
        if spot is None:
            LOG.info("[중단] 그날 종가를 받지 못했습니다. --price 종가 로 직접 넣어 다시 실행하세요.")
            _result(**base, rc=4, status='need_price', title=f'{quote_date} 종가를 받지 못했습니다',
                    message='그날 EWY 종가를 직접 입력하면 그 값으로 복구합니다.')
            return 4
        LOG.info(f"  - {SYMBOL} {quote_date} 종가 {spot} 달러 사용 ({'직접 입력' if manual_price else '야후 조회'})")
        df[price_col] = spot
    sofr_col = 'Secured Overnight Financing Rate'
    sv = pd.to_numeric(df[sofr_col], errors='coerce').dropna() if sofr_col in df.columns else pd.Series(dtype=float)
    if len(sv) and sv.iloc[0] > 0:
        sofr, sofr_src = round(float(sv.iloc[0]), 2), 'CSV에 있던 값'
    else:
        sofr, sofr_src = fetch_sofr(path.parent, upto=quote_date)
        df[sofr_col] = sofr
    LOG.info(f"  - SOFR {sofr}% ({sofr_src})")

    work = df.copy()
    for col in ['Bid', 'Ask', 'Last Price', 'Strike', price_col]:
        work[col] = pd.to_numeric(work[col], errors='coerce').fillna(0)
    work['T'] = busday_T(work['Quote Date'], work['Expiration Date'])
    rows = list(range(n)) if need_price else [int(i) for i in np.where(iv.isna())[0]]
    LOG.info(f"  - {len(rows):,}개 행 IV·델타 다시 계산 (코랩판과 같은 계산식)")
    _progress(5, 0.0, f"IV·델타 계산 0/{len(rows):,}")
    new_iv, new_delta = compute_iv_delta(work, price_col, sofr / 100.0, rows=rows)
    old_delta = pd.to_numeric(df['Delta'], errors='coerce')
    redo = set(rows)
    iv_out = [new_iv[i] if i in redo else iv.iloc[i] for i in range(n)]
    dl_out = [new_delta[i] if i in redo else old_delta.iloc[i] for i in range(n)]
    df['Implied Volatility'] = [fmt4(x) for x in iv_out]
    df['Delta'] = [fmt4(x) for x in dl_out]

    _progress(6, 0.0, '파일 저장')
    bak = path.with_name(path.name + '.bak')
    if bak.exists():
        bak = path.with_name(path.name + f".{datetime.now():%Y%m%d%H%M%S}.bak")
    shutil.copy2(path, bak)
    atomic_to_csv(df, path)
    iv2 = pd.to_numeric(df['Implied Volatility'], errors='coerce')
    after = float((iv2 > 0.05).mean()) if n else 0.0
    LOG.info(f"[완료] IV>0.05 행 {int((iv2 > 0.05).sum()):,}개 ({after:.1%}) · 원본 백업: {bak.name}")
    _result(**base, rc=0, status='repaired', title='복구 완료', spot=spot, recomputed=len(rows),
            valid_before=round(before, 4), valid_iv=round(after, 4), backup=bak.name,
            message=f'원본은 {bak.name} 로 보관했습니다.')
    return 0


# ==============================================================================
# 데이터 점검: 저장된 CSV가 분석 엔진에서 쓸 수 있는 상태인지 빠르게 확인
# ==============================================================================
def check_csv(path):
    import re
    p = Path(path)
    st = p.stat()
    m = re.search(r'_(\d{8})\.csv$', p.name)
    info = dict(path=str(p), name=p.name, size=st.st_size, mtime=st.st_mtime, in_bad_dir=(p.parent.name == '검증실패'),
                date=f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}" if m else '', repairable=False)
    try:
        head = pd.read_csv(p, encoding='utf-8-sig', nrows=0)
        price_col = next((c for c in head.columns if c.endswith(' Price') and c != 'Last Price'), None)
        need = ['Quote Date', 'Expiration Date', 'Implied Volatility', 'Open Interest']
        if price_col is None or any(c not in head.columns for c in need):
            info.update(status='bad', status_text='형식이 다름')
            return info
        df = pd.read_csv(p, encoding='utf-8-sig', usecols=need + [price_col])
        S = pd.to_numeric(df[price_col], errors='coerce')
        iv = pd.to_numeric(df['Implied Volatility'], errors='coerce')
        rows = int(len(df))
        price_ok = bool((S > 0).any())
        valid = float((iv > 0.05).mean()) if rows else 0.0
        info.update(rows=rows, spot=(float(S[S > 0].iloc[0]) if price_ok else None), valid_iv=round(valid, 4),
                    iv_blank=int(iv.isna().sum()), expirations=int(df['Expiration Date'].nunique()),
                    oi=int(pd.to_numeric(df['Open Interest'], errors='coerce').fillna(0).sum()))
        if rows == 0:
            info.update(status='bad', status_text='빈 파일')
        elif not price_ok:
            info.update(status='no_price', status_text='주가 없음 — 복구 필요', repairable=True)
        elif valid < MIN_VALID_IV_SHARE:
            if info['iv_blank'] > 0:
                info.update(status='low_iv', status_text='IV 빈칸 많음 — 복구 필요', repairable=True)
            else:
                info.update(status='low_iv', status_text='IV 이상 — 다시 수집 필요')
        elif info['in_bad_dir']:
            info.update(status='invalid', status_text='검증실패 폴더')
        else:
            info.update(status='ok', status_text='정상')
    except Exception as e:
        info.update(status='bad', status_text='읽기 실패', error=f"{type(e).__name__}: {str(e)[:160]}")
    return info


def list_csvs(folder, include_bad_dir=True, limit=60):
    """폴더(와 '검증실패' 하위 폴더)의 수집기 CSV 경로를 최신 날짜순으로"""
    folder = Path(folder)
    files = list(folder.glob(f"{SYMBOL} Option 분석데이터_*.csv"))
    if include_bad_dir and (folder / '검증실패').is_dir():
        files += list((folder / '검증실패').glob(f"{SYMBOL} Option 분석데이터_*.csv"))
    files.sort(key=lambda f: (f.name[-12:-4], f.parent.name != '검증실패'), reverse=True)
    return files[:limit]


# ==============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description='EWY 옵션 데이터 수집기 (PC판)')
    ap.add_argument('--out', help='저장 폴더 (기본: 구글 드라이브 데스크톱 자동 탐지)')
    ap.add_argument('--overwrite', action='store_true', help='같은 기준일 파일이 있어도 덮어쓰기')
    ap.add_argument('--repair', metavar='CSV', help='주가·IV가 빈칸인 CSV 복구')
    ap.add_argument('--price', type=float, help='복구할 때 쓸 그날 종가 (야후 조회가 안 될 때)')
    args = ap.parse_args(argv)
    log_path = setup_logging('복구' if args.repair else '수집')
    try:
        rc = repair_csv(args.repair, args.price) if args.repair else collect(args.out, args.overwrite)
    except (KeyboardInterrupt, Cancelled):
        LOG.info("[중단] 사용자가 멈췄습니다.")
        rc = 2
    except Exception:
        LOG.exception("[오류] 예기치 못한 오류가 났습니다. 아래 내용을 확인하세요.")
        rc = 3
    LOG.info(f" 실행 기록: {log_path}")
    return rc


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except Exception:
        pass
    sys.exit(main())
