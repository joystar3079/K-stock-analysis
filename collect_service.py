"""옵션 데이터 수집 -> 저장소(깃허브)에 날짜별 파일로 누적 (스트림잇 [지금 수집] 버튼 · 깃허브 예약 수집 공용)

수집·계산은 PC 수집기(ewy_option_collector.py, 코랩판과 같은 계산식)를 고치지 않고 그대로 씁니다.
  1) 저장소의 가장 최근 수집본을 임시 폴더에 놓음 -> 수집기의 '장 마감 뒤 이미 받은 날이면 건너뜀' 판정과
     SOFR 금리 대체값(FRED 실패 시 직전 CSV 값)이 PC판과 똑같이 동작
  2) 수집기가 임시 폴더에 'EWY Option 분석데이터_YYYYMMDD.csv'를 만들면 그 파일을 그대로 저장소 data/daily/ 에 올림
  3) 만기 일부를 못 받았거나 유효 IV가 너무 적은 '검증실패' 데이터는 누적하지 않음
"""
from __future__ import annotations

import logging
import os
import shutil
import tempfile
import threading
import time

import storage

_LOCK = threading.Lock()          # 수집기 모듈의 진행 상태는 하나뿐이라 한 번에 하나만


class _ListHandler(logging.Handler):
    def __init__(self, sink):
        super().__init__()
        self.sink = sink

    def emit(self, record):
        try:
            self.sink(record.getMessage())
        except Exception:
            pass


def run_collect(store, overwrite=False, progress=None, log=None):
    """반환: 수집기 결과 요약 dict (status: ok · skipped · invalid · aborted · error · busy)
    ok이면 'saved'에 저장소 경로, invalid이면 'invalid_bytes'에 받은 CSV(내려받기용)"""
    log = log or (lambda *_: None)
    if not _LOCK.acquire(blocking=False):
        return {"status": "busy", "title": "다른 수집이 진행 중입니다", "message": "끝난 뒤에 다시 누르세요."}
    tmp = tempfile.mkdtemp(prefix="ewy_collect_")
    import ewy_option_collector as C
    handler = _ListHandler(log)
    C.LOG.setLevel(logging.INFO)
    C.LOG.addHandler(handler)
    try:
        # 1) 가장 최근 수집본을 임시 폴더에 (파일 시각 = 저장소에 올라간 시각)
        try:
            snap = storage.latest_snapshot(store)
        except Exception as e:
            snap = None
            log(f"  - 직전 수집본을 읽지 못함({type(e).__name__}) — 건너뜀 판정 없이 수집합니다.")
        if snap and snap[1]:
            name, data, when = snap
            fp = os.path.join(tmp, name)
            with open(fp, "wb") as fh:
                fh.write(data)
            if when is not None:
                ts = when.timestamp()
                os.utime(fp, (ts, ts))
        # 2) 수집 (PC 수집기 그대로)
        C.CANCEL.clear()
        C.PROGRESS_HOOK = progress
        try:
            rc = C.collect(out=tmp, overwrite=overwrite)
        except C.Cancelled:
            return {"status": "cancelled", "title": "중지했습니다", "message": "저장하지 않았습니다."}
        except Exception as e:
            log(f"[오류] {type(e).__name__}: {e}")
            if C._is_rate_limited(e) or "Rate limit" in str(e):
                return {"status": "aborted", "title": "야후 접속 제한 — 저장하지 않음",
                        "message": "야후가 잠시 접속을 막았습니다. 30분~몇 시간 뒤 다시 시도하세요. "
                                   "매일 아침 자동 수집은 그대로 진행됩니다."}
            return {"status": "error", "title": "수집 중 오류", "message": f"{type(e).__name__}: {e}"[:400]}
        finally:
            C.PROGRESS_HOOK = None
        res = dict(C.LAST_RESULT)
        res["rc"] = rc
        status = res.get("status")
        f = res.get("file")
        if status == "ok" and f and os.path.isfile(f):
            with open(f, "rb") as fh:
                data = fh.read()
            name = os.path.basename(f)
            path = storage.save_daily(store, name, data,
                                      f"옵션 데이터 수집 {res.get('quote_date', '')} · 계약 {res.get('contracts', 0):,}개")
            res["saved"] = path
            res["name"] = name
            res["csv_bytes"] = data
            log(f"[저장] {store.label()} -> {path}")
        elif status == "invalid":
            res["title"] = "불완전한 데이터 — 누적하지 않음"
            res["message"] = ("만기 일부를 받지 못했거나 유효 IV가 너무 적어 누적하지 않았습니다. 잠시 뒤 다시 수집하세요. "
                              + " / ".join(res.get("problems") or []))
            if f and os.path.isfile(f):
                with open(f, "rb") as fh:
                    res["invalid_bytes"] = fh.read()
                res["name"] = os.path.basename(f)
        return res
    finally:
        C.LOG.removeHandler(handler)
        _LOCK.release()
        shutil.rmtree(tmp, ignore_errors=True)


def us_market_note():
    """화면 안내용: 지금 미국 동부 시각"""
    import pandas as pd
    now = pd.Timestamp.now(tz="America/New_York")
    return now.strftime("%Y-%m-%d %H:%M (미국 동부)")


if __name__ == "__main__":       # PC에서 시험: python collect_service.py
    t0 = time.time()
    r = run_collect(storage.LocalStore(os.path.dirname(os.path.abspath(__file__))), log=print,
                    progress=lambda s, f, t: None)
    print({k: v for k, v in r.items() if not k.endswith("_bytes")}, f"{time.time() - t0:.0f}초")
