"""미국 증시 거래일 (표준 라이브러리) — 데이터가 최신인지 · 빠진 거래일이 있는지 점검용"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

SPECIAL_CLOSURES = {date(2025, 1, 9)}        # 정규 휴장일 밖의 임시 휴장


def _easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return date(y, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)


def _nth_weekday(y, month, weekday, n):
    if n > 0:
        d = date(y, month, 1)
        return d + timedelta(days=(weekday - d.weekday()) % 7 + 7 * (n - 1))
    d = (date(y + 1, 1, 1) if month == 12 else date(y, month + 1, 1)) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d):
    return d - timedelta(days=1) if d.weekday() == 5 else (d + timedelta(days=1) if d.weekday() == 6 else d)


@lru_cache(maxsize=16)
def us_market_holidays(y):
    h = {_nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3), _easter(y) - timedelta(days=2), _nth_weekday(y, 5, 0, -1),
         _observed(date(y, 7, 4)), _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 11, 3, 4), _observed(date(y, 12, 25))}
    if date(y, 1, 1).weekday() != 5:
        h.add(_observed(date(y, 1, 1)))
    if y >= 2022:
        h.add(_observed(date(y, 6, 19)))
    return frozenset(h | {d for d in SPECIAL_CLOSURES if d.year == y})


def is_trading_day(d):
    return d.weekday() < 5 and d not in us_market_holidays(d.year)


def us_eastern_now():
    u = datetime.now(timezone.utc).replace(tzinfo=None)
    on = datetime.combine(_nth_weekday(u.year, 3, 6, 2), datetime.min.time()) + timedelta(hours=7)
    off = datetime.combine(_nth_weekday(u.year, 11, 6, 1), datetime.min.time()) + timedelta(hours=6)
    return u - timedelta(hours=4 if on <= u < off else 5)


def last_closed_trading_day(now_et=None):
    """장 마감(동부 16:15)이 지난 가장 최근 거래일"""
    et = now_et or us_eastern_now()
    d = et.date()
    if not (is_trading_day(d) and (et.hour, et.minute) >= (16, 15)):
        d -= timedelta(days=1)
        while not is_trading_day(d):
            d -= timedelta(days=1)
    return d


def trading_days_after(last, upto, limit=60):
    try:
        d = datetime.strptime(str(last)[:10], "%Y-%m-%d").date() + timedelta(days=1)
    except ValueError:
        return []
    out = []
    while d <= upto and len(out) < limit:
        if is_trading_day(d):
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def missing_trading_days(dates, lookback_days=120):
    if not dates:
        return []
    ds = sorted(str(x)[:10] for x in dates)
    end = datetime.strptime(ds[-1], "%Y-%m-%d").date()
    start = max(datetime.strptime(ds[0], "%Y-%m-%d").date(), end - timedelta(days=lookback_days))
    have, out, d = set(ds), [], start
    while d <= end:
        if is_trading_day(d) and d.isoformat() not in have:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out
