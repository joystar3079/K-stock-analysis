"""깃허브 예약 수집 (GitHub Actions에서 실행: .github/workflows/collect.yml)

  python collect_job.py            저장소 폴더의 data/ 에 오늘 옵션 데이터를 날짜별 파일로 추가
  OVERWRITE=1 python collect_job.py  같은 날짜 데이터가 있어도 다시 받기

- 커밋·푸시는 워크플로가 함 (이 파일은 data/ 폴더만 바꿈)
- 날짜별 파일이 storage.COMPACT_AFTER개를 넘으면 마스터(data/master_base.csv.gz)에 합침
- 종료 코드: 0 정상 저장·이미 받음 / 1 저장하지 못함(야후 접속 제한·검증실패 등 -> 깃허브가 실패 알림 메일을 보냄)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import collect_service  # noqa: E402
import storage  # noqa: E402


def main():
    t0 = time.time()
    store = storage.LocalStore(HERE)
    overwrite = os.environ.get("OVERWRITE", "0").strip().lower() in ("1", "true", "yes")
    last = {"p": -1}

    def progress(stage, frac, text):
        p = int(((stage - 1) + frac) / 6 * 100)
        if p >= last["p"] + 10 or stage != last.get("s"):
            last.update(p=p, s=stage)
            print(f"  [{p:3d}%] {text}", flush=True)

    res = collect_service.run_collect(store, overwrite=overwrite, progress=progress, log=lambda m: print(m, flush=True))
    status = res.get("status")
    print(f"\n결과: {status} · {res.get('title', '')} {res.get('message', '')}".rstrip(), flush=True)
    if status == "ok":
        n = len(storage.daily_entries(store))
        if n > storage.COMPACT_AFTER:
            try:
                storage.compact(store, log=lambda m: print(m, flush=True))
            except Exception as e:      # 합치기는 다음 날 다시 해도 됨 — 오늘 받은 데이터는 그대로 저장
                print(f"  - 마스터에 합치지 못함({type(e).__name__}: {e}) — 날짜별 파일로 둡니다.", flush=True)
    print(f"걸린 시간 {time.time() - t0:.0f}초", flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"### EWY 옵션 데이터 수집: {res.get('title', status)}\n\n")
                for k, label in (("quote_date", "기준일"), ("contracts", "계약 수"), ("valid_iv", "유효 IV 비율"),
                                 ("expirations", "만기"), ("sofr", "SOFR"), ("saved", "저장")):
                    if res.get(k) not in (None, ""):
                        fh.write(f"- {label}: {res[k]}\n")
                if res.get("message"):
                    fh.write(f"\n{res['message']}\n")
        except OSError:
            pass
    return 0 if status in ("ok", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())
