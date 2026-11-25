"""분석 엔진(V4.3.7) 실행 — 스트림잇 앱이 별도 프로세스로 띄움 (엔진이 작업 폴더·sys.argv를 바꾸므로 앱과 분리)

  python engine_job.py --file engine/analysis_engine.py --input 입력폴더 --output 출력폴더
                       [--tier 5] [--version PC] [--date latest|YYYY-MM-DD] [--binance 1] [--split 1]
진행 상황과 결과를 JSON 한 줄씩 출력: {"t": "progress"|"log"|"result", ...}
신호 기록 폴더는 환경변수 EWY_SIGNAL_LOG_DIR (엔진 V4.3.7이 읽음)
"""
import argparse
import json
import os
import sys
import traceback
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True, default=str) + "\n")
    sys.stdout.flush()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--tier", default="5")
    ap.add_argument("--version", default="PC")
    ap.add_argument("--date", default="latest")
    ap.add_argument("--binance", default="1")
    ap.add_argument("--split", default="0")
    ap.add_argument("--count", type=int, default=1)
    args = ap.parse_args(argv)
    import ewy_engine_runner as runner
    try:
        res = runner.run_engine(args, emit)
    except Exception as ex:
        res = {"kind": "engine", "status": "error", "rc": 3, "title": "분석 엔진을 시작하지 못했습니다",
               "message": f"{type(ex).__name__}: {ex}"[:400]}
        emit({"t": "log", "lv": "ERROR", "msg": traceback.format_exc()})
    res["split_mode"] = args.split == "1"
    if args.split == "1" and res.get("status") == "ok":
        import ewy_split
        books = [f for f in res.get("files", []) if ewy_split.DATABOOK_RE.match(Path(f).name)]
        splits, errs = [], []
        for i, f in enumerate(books, 1):
            emit({"t": "progress", "stage": 4, "frac": round((i - 1) / max(1, len(books)), 4),
                  "text": f"3분할 프롬프트 만들기 {i}/{len(books)}"})
            try:
                r = ewy_split.make_split_pack(f, out_dir=str(Path(f).parent),
                                              log=lambda m: emit({"t": "log", "lv": "INFO", "msg": m}))
                splits.append({"databook": f, "date": r["date"], "chars": r["chars"], "tables": r["tables"],
                               "parts": [r["paths"][f"part{k}"] for k in (1, 2, 3)], "viewer": r["paths"]["viewer"]})
            except Exception as ex:
                errs.append(f"{Path(f).name}: {type(ex).__name__}: {ex}")
                emit({"t": "log", "lv": "ERROR", "msg": traceback.format_exc()})
        res["splits"], res["split_errors"] = splits, errs
    emit({"t": "result", "data": res})
    return 0 if res.get("status") == "ok" else 3


if __name__ == "__main__":
    sys.exit(main())
