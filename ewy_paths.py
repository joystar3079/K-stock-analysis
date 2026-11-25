# -*- coding: utf-8 -*-
"""저장 폴더 찾기 (표준 라이브러리만 사용 — 프로그램 창과 수집 코어가 함께 씀)"""
import csv
import glob
import json
import os
import re
import threading
import unicodedata
from datetime import datetime
from pathlib import Path

DRIVE_SUBPATH = ('00. 주가모니터링', '02. 옵션데이터분석', '03. 클로드 옵션분석', 'daily')
DRIVE_ROOT_NAMES = ('내 드라이브', 'My Drive')


def drive_roots():
    """구글 드라이브 데스크톱이 보여 주는 '내 드라이브' 후보 위치들"""
    home = Path.home()
    roots = [Path(f"{letter}:/") / name for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ' for name in DRIVE_ROOT_NAMES]
    roots += [home / p for p in ('내 드라이브', 'My Drive', 'Google Drive/내 드라이브', 'Google Drive/My Drive',
                                 'Google Drive')]
    roots += [Path(p) for p in glob.glob(str(home / 'Library' / 'CloudStorage' / 'GoogleDrive-*' / '*'))]
    return roots


def detect_save_dir(override='', fallback=None):
    """(폴더, 설명, 드라이브여부) — override가 있으면 그대로, 없으면 '00. 주가모니터링'이 있는 드라이브를 찾음"""
    if override:
        return Path(override), '직접 지정', True
    for root in drive_roots():
        try:
            if (root / DRIVE_SUBPATH[0]).is_dir():
                return root.joinpath(*DRIVE_SUBPATH), f'구글 드라이브 ({root})', True
        except OSError:
            continue
    fb = Path(fallback) if fallback else Path(__file__).resolve().parent / 'data' / 'daily'
    return fb, '프로그램 폴더 (구글 드라이브 폴더를 찾지 못함)', False


# ------------------------------------------------------------------------------
# 분석에 쓸 수 있는 날짜 — 분석 엔진과 똑같이 '폴더 안 모든 CSV의 Quote Date'를 봄
#   · 수집기가 만든 'EWY Option 분석데이터_YYYYMMDD.csv' 는 파일 이름의 날짜를 바로 씀 (빠름)
#   · 그 밖의 CSV(예전 기록을 모아 둔 파일 등)는 Quote Date 열을 한 번 읽고, 파일이 바뀌기 전까지 기억해 둠
# ------------------------------------------------------------------------------
DAILY_CSV_RE = re.compile(r'Option 분석데이터_(\d{8})\.csv$', re.I)
_DATE_PATTERNS = (
    (re.compile(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})(?:$|[ T])'), (1, 2, 3)),   # 2026-11-12, 2026/11/12 00:00:00
    (re.compile(r'^(\d{4})(\d{2})(\d{2})$'), (1, 2, 3)),                          # 20261112
    (re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})(?:$|[ T])'), (3, 1, 2)),            # 11/12/2026 (미국식)
)
_dates_lock = threading.Lock()
_dates_mem = {}          # 경로 -> [크기, 수정시각, [날짜...]]
_dates_disk = {}         # 디스크에 둔 기억 파일 -> 읽었는지


def _norm_quote_date(v):
    s = str(v or '').strip().strip('"')
    for rx, (yi, mi, di) in _DATE_PATTERNS:
        m = rx.match(s)
        if m:
            try:
                return datetime(int(m.group(yi)), int(m.group(mi)), int(m.group(di))).strftime('%Y-%m-%d')
            except ValueError:
                return ''
    return ''


def _scan_quote_dates(path):
    raw = set()
    with open(path, 'r', encoding='utf-8-sig', errors='replace', newline='') as fh:
        rd = csv.reader(fh)
        head = next(rd, None) or []
        cols = [c.strip() for c in head]
        if 'Quote Date' not in cols:
            return []
        i = cols.index('Quote Date')
        for row in rd:
            if len(row) > i:
                raw.add(row[i])
    return sorted({d for d in map(_norm_quote_date, raw) if d})


def _load_disk_cache(cache_file):
    key = str(cache_file)
    if key in _dates_disk:
        return
    _dates_disk[key] = True
    try:
        data = json.loads(Path(cache_file).read_text(encoding='utf-8'))
        for k, v in (data or {}).items():
            if k not in _dates_mem and isinstance(v, list) and len(v) == 3:
                _dates_mem[k] = v
    except (OSError, ValueError):
        pass


def _save_disk_cache(cache_file):
    try:
        Path(cache_file).parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(str(cache_file) + '.tmp')
        tmp.write_text(json.dumps(_dates_mem, ensure_ascii=False), encoding='utf-8')
        os.replace(tmp, cache_file)
    except OSError:
        pass


def csv_quote_dates(folder, cache_file=None):
    """폴더(하위 폴더 제외)의 CSV에 들어 있는 거래일들 -> 'YYYY-MM-DD' 집합"""
    out, changed = set(), False
    try:
        entries = [e for e in os.scandir(folder) if e.is_file() and e.name.lower().endswith('.csv')]
    except OSError:
        return out
    with _dates_lock:
        if cache_file:
            _load_disk_cache(cache_file)
        for e in entries:
            m = DAILY_CSV_RE.search(unicodedata.normalize('NFC', e.name))
            if m:
                d = _norm_quote_date(m.group(1))
                if d:
                    out.add(d)
                    continue
            try:
                stt = e.stat()
            except OSError:
                continue
            key = os.path.normcase(os.path.abspath(e.path))
            hit = _dates_mem.get(key)
            if hit and hit[0] == stt.st_size and hit[1] == stt.st_mtime_ns:
                out.update(hit[2])
                continue
            try:
                ds = _scan_quote_dates(e.path)
            except OSError:
                continue
            _dates_mem[key] = [stt.st_size, stt.st_mtime_ns, ds]
            out.update(ds)
            changed = True
        if changed and cache_file:
            _save_disk_cache(cache_file)
    return out


def csv_file_quote_dates(path, cache_file=None):
    """[2.2] CSV 파일 하나(예: 폴더 밖에 둔 마스터통합데이터)의 거래일 -> 'YYYY-MM-DD' 집합 (같은 기억 파일 사용)"""
    try:
        stt = os.stat(path)
    except OSError:
        return set()
    with _dates_lock:
        if cache_file:
            _load_disk_cache(cache_file)
        key = os.path.normcase(os.path.abspath(path))
        hit = _dates_mem.get(key)
        if hit and hit[0] == stt.st_size and hit[1] == stt.st_mtime_ns:
            return set(hit[2])
        try:
            ds = _scan_quote_dates(path)
        except OSError:
            return set()
        _dates_mem[key] = [stt.st_size, stt.st_mtime_ns, ds]
        if cache_file:
            _save_disk_cache(cache_file)
    return set(ds)
