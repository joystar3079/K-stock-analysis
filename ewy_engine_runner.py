# -*- coding: utf-8 -*-
"""
분석 엔진(코랩용 .py)을 PC에서 실행
------------------------------------------------------------------------------
- 엔진 파일은 고치지 않고, 읽어 들인 뒤 맨 위 설정값만 바꿔 끼워 실행합니다.
    INPUT_DIR  -> 수집기 '저장 위치' 폴더 (엔진이 이 폴더의 CSV를 모두 읽음)
    OUTPUT_DIR -> 프롬프트(데이터북) 저장 폴더
    TIER_SELECTION_MODE / VIEW_VERSION_MODE / DATE_SELECTION_MODE / PRESET_TARGET_DATE / USE_BINANCE_KRX_HOURLY_SYNC
- 엔진의 print 출력은 화면 진행 기록으로 보내고(보고서 본문처럼 아주 긴 출력은 줄여서), 진행 단계를 짐작해 알려 줌
- 엔진이 사용자 입력(input)을 물으면 화면에서 고른 값으로 자동 응답
"""
import ast
import builtins
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ENGINE_PARAMS = ('OUTPUT_DIR', 'INPUT_DIR', 'TIER_SELECTION_MODE', 'VIEW_VERSION_MODE', 'DATE_SELECTION_MODE',
                 'PRESET_TARGET_DATE', 'USE_BINANCE_KRX_HOURLY_SYNC')

TIER_TEXT = {
    '1': 'Tier 1: 초단기 전술창 (T+0 ~ 1D)',
    '2': 'Tier 2: 단기 롤오버창 (3D vs 7D)',
    '3': 'Tier 3: 월간 감마창 (20D ~ 22D)',
    '4': 'Tier 4: 구조적 레짐창 (60D ~ 200D)',
    '5': 'Tier 5: 전 계층 통합 마스터창 (All-in-One)',
    'ALL': '대화형 메뉴로 실행 시점에 Tier 직접 선택 (Interactive Tier Prompt)',
}
VERSION_TEXT = {
    'PC': 'PC버젼: 정량 표 전체 포함 표준 보고서 (PC Version)',
    'MOBILE': '모바일버젼: 표 재출력 금지 & 순수 해설 텍스트 HTML 보고서 (Mobile Version)',
}
DATE_TEXT = {
    'latest': '최신 기준일 자동 실행 (Latest Date)',
    'date': '아래 지정한 과거 기준일로 바로 실행 (Preset Date)',
    'range': '대화형 메뉴로 실행 시점에 기준일 직접 선택 (Interactive Date Prompt)',
}


# ==============================================================================
# 엔진 파일 읽기 (화면에서 기본값을 보여 줄 때도 씀 — 표준 라이브러리만)
# ==============================================================================
def read_engine_source(path):
    raw = Path(path).read_bytes()
    for enc in ('utf-8-sig', 'cp949'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', 'replace')


def inspect_engine(path):
    """엔진 파일의 제목 줄과 맨 위 설정값을 읽어 옴"""
    info = {'path': str(path), 'name': Path(path).name, 'ok': False, 'params': {}, 'title': '', 'error': ''}
    try:
        src = read_engine_source(path)
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        info['error'] = f'파이썬 문법 오류 (줄 {e.lineno}): {e.msg}'
        return info
    except OSError as e:
        info['error'] = f'파일을 읽지 못했습니다: {e}'
        return info
    for line in src.splitlines()[:12]:
        s = line.strip().lstrip('#').strip()
        if s and not set(s) <= set('=-_ '):
            info['title'] = s[:200]
            break
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ENGINE_PARAMS and name not in info['params']:
                v = node.value
                info['params'][name] = v.value if isinstance(v, ast.Constant) else ast.unparse(v)
    p = info['params']
    info['ok'] = 'OUTPUT_DIR' in p and 'INPUT_DIR' in p
    if not info['ok']:
        info['error'] = '엔진 파일에서 입력·출력 폴더 설정(OUTPUT_DIR, INPUT_DIR)을 찾지 못했습니다.'
    b = p.get('USE_BINANCE_KRX_HOURLY_SYNC', True)
    info['defaults'] = {
        'tier': next((k for k in ('1', '2', '3', '4', '5') if str(p.get('TIER_SELECTION_MODE', '')).startswith(f'Tier {k}')), '5'),
        'version': 'MOBILE' if str(p.get('VIEW_VERSION_MODE', '')).startswith('모바일') else 'PC',
        'binance': b if isinstance(b, bool) else True,
    }
    return info


def compile_engine(path, overrides):
    """맨 위 설정값(최상위 대입문)만 바꿔 끼워 컴파일"""
    src = read_engine_source(path)
    tree = ast.parse(src, filename=str(path))
    found = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in overrides:
                node.value = ast.copy_location(ast.Constant(overrides[name]), node.value)
                found.add(name)
    ast.fix_missing_locations(tree)
    return compile(tree, str(path), 'exec'), found


# ==============================================================================
# 실행
# ==============================================================================
class _Progress:
    """엔진 출력 문구로 진행 단계를 짐작: 1 데이터 불러오기 · 2 분석 준비 · 3 시장 데이터·분석 · 4 보고서 저장"""

    def __init__(self, emit, total_items):
        self.emit = emit
        self.total = max(1, total_items)
        self.n_files = 0
        self.loaded = 0
        self.started = 0
        self.done = 0
        self.outputs = []
        self._expect_path = False

    def send(self, stage, frac, text):
        frac = round(max(0.0, min(0.99, frac)), 4)
        if (stage, frac) < getattr(self, '_last', (0, 0.0)):      # 진행률이 뒤로 가지 않게
            return
        self._last = (stage, frac)
        self.emit({'t': 'progress', 'stage': stage, 'frac': frac, 'text': text})

    def feed(self, text):
        if self._expect_path:
            m = re.search(r'📂\s*(.+\S)', text)
            if m:
                self.outputs.append(m.group(1).strip())
                self._expect_path = False
        if '[데이터 로드]' in text:
            m = re.search(r'총\s*([\d,]+)\s*개', text)
            self.n_files = int(m.group(1).replace(',', '')) if m else 0
            self.send(1, 0.0, f'CSV 파일 {self.n_files:,}개 불러오는 중')
        elif '로드 완료' in text:
            self.loaded += 1
            if self.n_files:
                self.send(1, self.loaded / self.n_files, f'CSV 파일 불러오는 중 {self.loaded:,}/{self.n_files:,}')
        elif '[병합 완료]' in text:
            self.send(2, 0.0, '분석 준비 (기준일·분석 창 확인)')
        elif '🚀' in text:
            self.started += 1
            label = f'분석 {self.started}/{self.total}' if self.total > 1 else '분석'
            self.send(3, (self.started - 1) / self.total, f'{label}: 계산 시작')
        elif '야후파이낸스' in text and '조회' in text:
            label = f'분석 {self.started}/{self.total}' if self.total > 1 else '분석'
            self.send(3, (self.started - 1 + 0.15) / self.total, f'{label}: 야후·바이낸스 시세 조회')
        elif '시계열 관계' in text and '완료' in text:
            label = f'분석 {self.started}/{self.total}' if self.total > 1 else '분석'
            self.send(3, (self.started - 1 + 0.35) / self.total, f'{label}: 옵션 미시구조 계산')
        elif '[저장 완료]' in text:
            self.done += 1
            self._expect_path = True
            self.send(3 if self.done < self.total else 4, self.done / self.total, f'프롬프트 {self.done}/{self.total} 저장')


def _count_range_dates(input_dir, d_from, d_to):
    """기간 안 거래일 수 — 엔진과 같게 폴더의 모든 CSV 안 날짜로 셈"""
    from ewy_paths import csv_quote_dates
    return max(1, sum(1 for d in csv_quote_dates(input_dir) if d_from <= d <= d_to))


def _hint_for(exc):
    msg = f'{type(exc).__name__}: {exc}'
    m = re.search(r'(\d{4}-\d{2}-\d{2})', str(exc)) if isinstance(exc, KeyError) else None
    if m:
        d = m.group(1)
        return (f'{d} 데이터의 주가·IV가 비어 있으면 이 오류가 납니다. ‘데이터 점검’에서 {d} 파일을 확인하고 '
                f'복구한 뒤 다시 실행하세요.')
    if isinstance(exc, FileNotFoundError) and 'CSV' in msg:
        return '저장 위치 폴더에 CSV 파일이 없습니다. 먼저 수집하거나 저장 위치를 확인하세요.'
    if isinstance(exc, MemoryError):
        return '메모리가 부족합니다. 다른 프로그램을 닫고 다시 실행하세요.'
    return '진행 기록의 마지막 부분에 오류 위치가 나옵니다. 엔진 코드 쪽 문제일 수 있습니다.'


def run_engine(args, emit, log_file=None):
    """args: file, input, output, tier, version, date, binance — 결과 dict 반환"""
    t0 = time.time()
    log_fh = open(log_file, 'a', encoding='utf-8') if log_file else None

    def log(text, kind='info'):
        text = str(text)
        if log_fh:
            try:
                log_fh.write(text + '\n')
                log_fh.flush()
            except Exception:
                pass
        for line in text.split('\n'):
            emit({'t': 'log', 'lv': 'ERROR' if kind == 'err' else 'INFO', 'msg': line})

    engine = Path(args.file)
    in_dir, out_dir = Path(args.input), Path(args.output)
    base = {'kind': 'engine', 'engine': engine.name, 'input_dir': str(in_dir), 'output_dir': str(out_dir),
            'tier': args.tier, 'version': args.version, 'date': args.date}
    log('=' * 70)
    log(f' 분석 엔진 실행: {engine.name}')
    log(f' 읽는 데이터: {in_dir}')
    log(f' 프롬프트 저장: {out_dir}')
    log('=' * 70)

    if not engine.is_file():
        return dict(base, status='error', rc=3, title='엔진 파일이 없습니다', message=str(engine))
    if not in_dir.is_dir() or not any(in_dir.glob('*.csv')):
        return dict(base, status='error', rc=2, title='읽을 데이터가 없습니다',
                    message=f'{in_dir} 폴더에 CSV 파일이 없습니다. 먼저 수집하거나 저장 위치를 확인하세요.')
    out_dir.mkdir(parents=True, exist_ok=True)

    date = (args.date or 'latest').strip()
    if date == 'latest':
        date_mode, preset, range_answer, total = 'latest', '', None, 1
    elif '~' in date:
        d_from, d_to = [x.strip() for x in date.split('~', 1)]
        if d_from > d_to:
            d_from, d_to = d_to, d_from
        date_mode, preset = 'range', d_to
        range_answer = f"{d_from.replace('-', '')}~{d_to.replace('-', '')}"
        total = int(getattr(args, 'count', 0) or 0) or _count_range_dates(in_dir, d_from, d_to)
    else:
        date_mode, preset, range_answer, total = 'date', date, None, 1
    tier = args.tier if args.tier in TIER_TEXT else '5'
    if tier == 'ALL':
        total *= 4

    overrides = {'OUTPUT_DIR': str(out_dir), 'INPUT_DIR': str(in_dir), 'TIER_SELECTION_MODE': TIER_TEXT[tier],
                 'VIEW_VERSION_MODE': VERSION_TEXT.get(args.version, VERSION_TEXT['PC']),
                 'DATE_SELECTION_MODE': DATE_TEXT[date_mode], 'PRESET_TARGET_DATE': preset or '',
                 'USE_BINANCE_KRX_HOURLY_SYNC': bool(int(args.binance))}
    try:
        code, found = compile_engine(engine, overrides)
    except SyntaxError as e:
        return dict(base, status='error', rc=3, title='엔진 파일을 읽지 못했습니다',
                    message=f'파이썬 문법 오류 (줄 {e.lineno}): {e.msg}')
    if not {'OUTPUT_DIR', 'INPUT_DIR'} <= found:
        return dict(base, status='error', rc=3, title='엔진 파일 형식이 다릅니다',
                    message='엔진 파일에서 OUTPUT_DIR·INPUT_DIR 설정을 찾지 못해 실행하지 않았습니다.')
    missing = [k for k in ('TIER_SELECTION_MODE', 'VIEW_VERSION_MODE', 'DATE_SELECTION_MODE') if k not in found]
    if missing:
        log(f'[주의] 엔진 파일에 {", ".join(missing)} 설정이 없어 그 부분은 엔진 기본값으로 실행합니다.')

    prog = _Progress(emit, total)
    answers = []
    if tier == 'ALL':
        answers.append(('Tier', 'ALL'))
    if range_answer:
        answers.append(('메뉴 번호', range_answer))

    def eng_print(*a, sep=' ', end='\n', file=None, flush=False):
        text = sep.join(str(x) for x in a)
        if file not in (None, sys.stdout, sys.stderr):
            return builtins.print(*a, sep=sep, end=end, file=file, flush=flush)
        lines = text.split('\n')
        prog.feed(text)
        if len(lines) > 60:      # 보고서 본문 같은 아주 긴 출력은 화면에는 줄여서
            if log_fh:
                try:
                    log_fh.write(text + '\n')
                except Exception:
                    pass
            for line in lines[:2]:
                emit({'t': 'log', 'lv': 'INFO', 'msg': line})
            emit({'t': 'log', 'lv': 'INFO', 'msg': f'   … (프롬프트 본문 {len(lines):,}줄 — 파일로 저장됩니다)'})
        else:
            log(text)

    def eng_input(prompt=''):
        log(str(prompt).rstrip())
        for key, val in answers:
            if key in str(prompt):
                log(f'   → 자동 입력: {val}')
                return val
        raise EOFError

    before = {}
    for f in out_dir.glob('*'):
        try:
            before[f.name] = f.stat().st_mtime
        except OSError:
            pass
    g = {'__name__': '__main__', '__file__': str(engine), '__builtins__': builtins,
         'print': eng_print, 'input': eng_input}
    old_argv, old_cwd = sys.argv, os.getcwd()
    sys.argv = [str(engine)]
    try:
        os.chdir(str(out_dir))
    except OSError:
        pass
    prog.send(1, 0.0, '엔진 시작')
    error = None
    try:
        exec(code, g)
    except SystemExit as e:
        if e.code not in (None, 0):
            error = e
    except BaseException as e:   # 엔진 안의 모든 오류를 화면에 보여 주기 위해
        error = e
        log(''.join(traceback.format_exception(type(e), e, e.__traceback__)).rstrip(), 'err')
    finally:
        sys.argv = old_argv
        try:
            os.chdir(old_cwd)
        except OSError:
            pass

    made = []
    for f in sorted(out_dir.glob('*')):
        try:
            if f.is_file() and f.suffix.lower() in ('.txt', '.html', '.htm', '.md') and \
                    (f.name not in before or f.stat().st_mtime > before[f.name] + 0.5):
                made.append(str(f))
        except OSError:
            pass
    for pth in prog.outputs:
        if pth not in made and Path(pth).is_file():
            made.append(pth)
    secs = round(time.time() - t0)
    if log_fh:
        log_fh.close()
    if error is not None:
        if isinstance(error, KeyboardInterrupt):
            return dict(base, status='cancelled', rc=2, title='중지했습니다', message='', files=made, seconds=secs)
        return dict(base, status='error', rc=3, title='분석 엔진 실행 중 오류',
                    message=f'{type(error).__name__}: {error}'[:400], hint=_hint_for(error), files=made, seconds=secs)
    if not made:
        return dict(base, status='error', rc=3, title='프롬프트 파일이 만들어지지 않았습니다',
                    message='엔진은 끝났지만 새 프롬프트 파일이 없습니다. 진행 기록을 확인하세요.', seconds=secs)
    return dict(base, status='ok', rc=0, title=f'분석 완료 — 프롬프트 {len(made)}개 저장', message='', files=made,
                seconds=secs)
