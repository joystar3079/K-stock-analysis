"""분석 엔진 V4.3.7을 스트림잇 앱에서 실행 · 3분할 프롬프트 · 최종 보고서 · 신호 기록 갱신

- 엔진 파일(engine/analysis_engine.py)은 고치지 않고 PC 프로그램과 같은 실행기(ewy_engine_runner.py)로 돌립니다.
  · 입력: 앱이 합친 마스터(마스터 + 날짜별 파일)를 CSV 한 개로 임시 폴더에 써서 넘김 -> V34 분석과 같은 데이터
  · 신호 기록: 저장소의 data/EWY_신호기록_채점.csv를 임시 폴더에 놓고 EWY_SIGNAL_LOG_DIR로 넘김 -> 엔진이 기록·채점하면 저장소에 다시 저장
  · 결과: 데이터북(프롬프트 .txt)은 저장소 reports/기준일/ 에 보관 (휴대폰 화면이 끊겨도 다시 열 수 있게)
- 엔진은 작업 폴더·sys.argv를 바꾸므로 앱과 다른 프로세스(engine_job.py)에서 실행합니다.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import storage

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_FILE = os.path.join(HERE, "engine", "analysis_engine.py")
ENGINE_JOB = os.path.join(HERE, "engine_job.py")
DATABOOK_RE = re.compile(r"^Tier(\d)_(PC|MOBILE)_(\d{8})_(\d{6})\.txt$")
TIERS = [("5", "Tier 5 · 전 계층 통합 마스터 (기본)"), ("1", "Tier 1 · 초단기 전술창 (T+0~1D)"),
         ("2", "Tier 2 · 단기 롤오버창 (3D vs 7D)"), ("3", "Tier 3 · 월간 감마창 (20D~22D)"),
         ("4", "Tier 4 · 구조적 레짐창 (60D~200D)")]
_LOCK = threading.Lock()
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def engine_info():
    import ewy_engine_runner as runner
    if not os.path.isfile(ENGINE_FILE):
        return {"ok": False, "error": "engine/analysis_engine.py 파일이 없습니다.", "name": "", "title": ""}
    info = runner.inspect_engine(ENGINE_FILE)
    info["version"] = (re.search(r"\[(V\d+(?:\.\d+)+)", info.get("title") or "") or [None, ""])[1]
    return info


def run(store, master_df, tier="5", split=False, date="latest", binance=True, on_progress=None, on_log=None,
        timeout=1200):
    """반환 dict: status · title · message · hint · seconds · files[{name, data, kind}] · splits · signal_saved · saved"""
    on_progress = on_progress or (lambda *_: None)
    on_log = on_log or (lambda *_: None)
    if not os.path.isfile(ENGINE_FILE):
        return {"status": "error", "title": "엔진 파일이 없습니다", "message": "저장소에 engine/analysis_engine.py를 올리세요."}
    if not _LOCK.acquire(blocking=False):
        return {"status": "busy", "title": "다른 분석이 실행 중입니다", "message": "끝난 뒤에 다시 누르세요."}
    work = tempfile.mkdtemp(prefix="ewy_engine_")
    t0 = time.time()
    try:
        in_dir, out_dir, sig_dir = (os.path.join(work, x) for x in ("in", "out", "sig"))
        for d in (in_dir, out_dir, sig_dir):
            os.makedirs(d)
        on_progress(1, 0.0, "데이터 준비")
        with open(os.path.join(in_dir, "EWY_master_merged.csv"), "wb") as fh:
            fh.write(storage.csv_bytes(storage.to_csv_frame(master_df)))
        sig_before = None
        try:
            sig_before = storage.read_signal(store)
        except Exception as e:
            on_log(f"[주의] 신호 기록 파일을 읽지 못했습니다({type(e).__name__}) — 새로 만듭니다.")
        sig_file = os.path.join(sig_dir, storage.SIGNAL_NAME)
        if sig_before:
            with open(sig_file, "wb") as fh:
                fh.write(sig_before)
        cmd = [sys.executable, "-u", ENGINE_JOB, "--file", ENGINE_FILE, "--input", in_dir, "--output", out_dir,
               "--tier", str(tier), "--version", "PC", "--date", date or "latest", "--binance", "1" if binance else "0",
               "--split", "1" if split else "0"]
        env = dict(os.environ, EWY_SIGNAL_LOG_DIR=sig_dir, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=HERE, env=env)
        res, logs = None, []
        killer = threading.Timer(timeout, proc.kill)
        killer.start()
        try:
            for raw in iter(proc.stdout.readline, b""):
                line = raw.decode("utf-8", "replace").rstrip("\r\n")
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    logs.append(line)
                    on_log(line)
                    continue
                t = obj.get("t")
                if t == "progress":
                    on_progress(int(obj.get("stage", 0)), float(obj.get("frac", 0.0)), obj.get("text", ""))
                elif t == "log":
                    logs.append(obj.get("msg", ""))
                    on_log(obj.get("msg", ""))
                elif t == "result":
                    res = obj.get("data")
            proc.wait()
        finally:
            killer.cancel()
        if not isinstance(res, dict):
            res = {"status": "error", "title": "분석 엔진이 비정상 종료되었습니다",
                   "message": f"종료 코드 {proc.returncode}" + (" (시간 초과로 멈춤)" if time.time() - t0 >= timeout else "")}
        res["seconds"] = round(time.time() - t0)
        res["log_tail"] = logs[-80:]
        # 결과 파일을 메모리로 (임시 폴더는 지움)
        files = []
        for p in res.get("files") or []:
            if os.path.isfile(p):
                with open(p, "rb") as fh:
                    files.append({"name": os.path.basename(p), "data": fh.read(), "kind": "databook" if DATABOOK_RE.match(os.path.basename(p)) else "other"})
        res["files"] = files
        splits = []
        for s in res.get("splits") or []:
            item = {"databook": os.path.basename(s["databook"]), "date": s.get("date"), "chars": s.get("chars"),
                    "tables": s.get("tables"), "parts": [], "viewer": None}
            for k, p in enumerate(s.get("parts") or [], 1):
                if os.path.isfile(p):
                    with open(p, "rb") as fh:
                        item["parts"].append({"k": k, "name": os.path.basename(p), "data": fh.read()})
            if s.get("viewer") and os.path.isfile(s["viewer"]):
                with open(s["viewer"], "rb") as fh:
                    item["viewer"] = {"name": os.path.basename(s["viewer"]), "data": fh.read()}
            splits.append(item)
        res["splits"] = splits
        # 신호 기록이 바뀌었으면 저장소에 저장
        res["signal_saved"] = False
        if os.path.isfile(sig_file):
            with open(sig_file, "rb") as fh:
                after = fh.read()
            if after and after != sig_before:
                try:
                    storage.save_signal(store, after, f"신호 기록·채점 갱신 ({res.get('date') or date})")
                    res["signal_saved"] = True
                except Exception as e:
                    res["signal_error"] = f"{type(e).__name__}: {e}"[:300]
        # 데이터북을 저장소에 보관
        saved = []
        if res.get("status") == "ok":
            for f in files:
                m = DATABOOK_RE.match(f["name"])
                if m:
                    try:
                        saved.append(storage.save_report(store, m.group(3), f["name"], f["data"],
                                                         f"분석 엔진 프롬프트 {m.group(3)} Tier{m.group(1)}"))
                    except Exception as e:
                        res["save_error"] = f"{type(e).__name__}: {e}"[:300]
        res["saved"] = saved
        return res
    finally:
        _LOCK.release()
        shutil.rmtree(work, ignore_errors=True)


def make_split(databook_name, databook_bytes):
    """보관한 데이터북 -> 3분할 프롬프트 3개 + 표 뷰어 (빠름 · 표준 라이브러리)"""
    import ewy_split
    work = tempfile.mkdtemp(prefix="ewy_split_")
    try:
        src = os.path.join(work, databook_name)
        with open(src, "wb") as fh:
            fh.write(databook_bytes)
        r = ewy_split.make_split_pack(src, out_dir=work)
        parts = []
        for k in (1, 2, 3):
            with open(r["paths"][f"part{k}"], "rb") as fh:
                parts.append({"k": k, "name": os.path.basename(r["paths"][f"part{k}"]), "data": fh.read()})
        with open(r["paths"]["viewer"], "rb") as fh:
            viewer = {"name": os.path.basename(r["paths"]["viewer"]), "data": fh.read()}
        return {"databook": databook_name, "date": r["date"], "chars": r["chars"], "tables": r["tables"],
                "parts": parts, "viewer": viewer}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def make_final_report(databook_name, databook_bytes, answers):
    """AI 답변 3개(파트 1/3 · 2/3 · 3/3) -> 최종 보고서 HTML · 해설 MD · 검산 TXT"""
    import ewy_split
    ewy_split.DISCLAIMER = ""          # 보고서 끝 투자 유의 문구는 넣지 않음 (엔진 V4.3.7의 '면책 문구 금지'와 같게)
    work = tempfile.mkdtemp(prefix="ewy_report_")
    try:
        src = os.path.join(work, databook_name)
        with open(src, "wb") as fh:
            fh.write(databook_bytes)
        r = ewy_split.merge_answers(list(answers), src, os.path.join(work, "out"))
        out = {"date": r["date"], "checks": r["checks"], "meta": r["meta"], "files": []}
        for key in ("report", "md", "check"):
            p = r["paths"].get(key)
            if p and os.path.isfile(p):
                with open(p, "rb") as fh:
                    out["files"].append({"key": key, "name": os.path.basename(p), "data": fh.read()})
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)
