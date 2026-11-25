"""분석 엔진(여러 버전 중 선택)을 스트림잇 앱에서 실행 · 3분할 프롬프트 · 최종 보고서 · 신호 기록 갱신

- 엔진 파일: 저장소 engine/ 폴더의 .py 파일들 (예: analysis_engine.py = V4.3.7, analysis_engine_V4.3.6.py, analysis_engine_V4.3.5.py)
  · 버전은 파일 첫 줄의 '[V4.3.7 · 날짜]' 표시로 알아냄 -> 화면에서 골라 실행
  · 고른 엔진을 저장소에서 읽어 임시 폴더에 두고, PC 프로그램과 같은 실행기(ewy_engine_runner.py)로 돌림 (엔진 파일은 고치지 않음)
  · 앱에서 새 엔진 파일을 올리면 engine/ 에 저장되어 바로 목록에 나옴
- 입력: 앱이 합친 마스터(마스터 + 날짜별 파일)를 CSV 한 개로 넘김 -> V34 분석과 같은 데이터
- 신호 기록 (엔진마다 방식이 다름)
  · V4.3.7 이후 (EWY_SIGNAL_LOG_DIR을 앎): 저장소 data/EWY_신호기록_채점.csv를 함께 씀
  · V4.3.6 (출력 폴더의 기록 파일만 앎): data/EWY_신호기록_채점_V4.3.6.csv를 따로 씀
    (V4.3.6은 자기 열만 남기고 같은 기준일·Tier 기록을 덮어써서, 기본 기록과 섞으면 V4.3.7 기록이 망가짐)
  · V4.3.5 이전: 신호 기록 없음
- 결과: 데이터북은 reports/기준일/ 에 'Tier5_PC_20261124_093412__V4.3.7.txt'처럼 엔진 버전을 붙여 보관
- 엔진은 작업 폴더·sys.argv를 바꾸므로 앱과 다른 프로세스(engine_job.py)에서 실행
"""
from __future__ import annotations

import ast
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
ENGINE_DIR = "engine"
ENGINE_JOB = os.path.join(HERE, "engine_job.py")
DATABOOK_RE = re.compile(r"^Tier(\d)_(PC|MOBILE)_(\d{8})_(\d{6})(?:__(V\d+(?:\.\d+)*))?\.txt$")
TIERS = [("5", "Tier 5 · 전 계층 통합 마스터 (기본)"), ("1", "Tier 1 · 초단기 전술창 (T+0~1D)"),
         ("2", "Tier 2 · 단기 롤오버창 (3D vs 7D)"), ("3", "Tier 3 · 월간 감마창 (20D~22D)"),
         ("4", "Tier 4 · 구조적 레짐창 (60D~200D)")]
SIGNAL_TEXT = {"main": "신호 기록·채점: 기본 기록 파일에 함께 씀",
               "own": "신호 기록·채점: 이 버전 전용 파일에 따로 씀 (기본 기록과 섞지 않음)",
               "none": "신호 기록·채점 기능이 없는 버전"}
_LOCK = threading.Lock()
_SRC = {}        # (경로, sha) -> 엔진 파일 내용
_INFO = {}       # (경로, sha) -> 엔진 정보
if HERE not in sys.path:
    sys.path.insert(0, HERE)


# ==============================================================================
# 엔진 목록
# ==============================================================================
def _decode(raw):
    for enc in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def version_key(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")) or (0,)


def _parse_version(src, name):
    for line in src.splitlines()[:15]:
        m = re.search(r"\[(V\d+(?:\.\d+)+)", line)
        if m:
            return m.group(1)
    m = re.search(r"^ENGINE_VERSION\s*=\s*[\"'](V\d+(?:\.\d+)+)[\"']", src, re.M)
    if m:
        return m.group(1)
    m = re.search(r"V(\d+(?:[._]\d+)+)", name)
    return "V" + m.group(1).replace("_", ".") if m else ""


def inspect_source(src, name):
    """엔진 파일 내용 -> {ok, error, title, version, signal_mode, signal_filename}"""
    info = {"name": name, "ok": False, "error": "", "title": "", "version": "", "signal_mode": "none",
            "signal_filename": storage.SIGNAL_NAME}
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        info["error"] = f"파이썬 문법 오류 (줄 {e.lineno}): {e.msg}"
        return info
    params = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            n = node.targets[0].id
            if n in ("OUTPUT_DIR", "INPUT_DIR", "USE_SIGNAL_LOG", "SIGNAL_LOG_FILENAME") and n not in params:
                params[n] = node.value.value if isinstance(node.value, ast.Constant) else None
    for line in src.splitlines()[:12]:
        s = line.strip().lstrip("#").strip()
        if s and not set(s) <= set("=-_ "):
            info["title"] = s[:300]
            break
    info["version"] = _parse_version(src, name) or "V0"
    if "EWY_SIGNAL_LOG_DIR" in src:
        info["signal_mode"] = "main"
    elif "USE_SIGNAL_LOG" in params:
        info["signal_mode"] = "own"
        if isinstance(params.get("SIGNAL_LOG_FILENAME"), str) and params["SIGNAL_LOG_FILENAME"].strip():
            info["signal_filename"] = params["SIGNAL_LOG_FILENAME"].strip()
    info["ok"] = "OUTPUT_DIR" in params and "INPUT_DIR" in params
    if not info["ok"]:
        info["error"] = "분석 엔진 파일이 아닙니다 (입력·출력 폴더 설정 OUTPUT_DIR · INPUT_DIR이 없음)."
    return info


def inspect_bytes(data, name):
    return inspect_source(_decode(data), name)


def engine_source(store, path, sha):
    key = (path, sha)
    if key not in _SRC:
        data = store.read(path, sha=sha)
        if data is None:
            raise FileNotFoundError(path)
        _SRC[key] = data
    return _SRC[key]


def list_engines(store):
    """저장소 engine/ 의 엔진들 (새 버전 먼저). 각 dict: path·sha·name·size·version·title·signal_mode·ok·error·latest"""
    out = []
    for e in store.list(ENGINE_DIR):
        if not e.name.lower().endswith(".py"):
            continue
        key = (e.path, e.sha)
        if key not in _INFO:
            try:
                info = inspect_source(_decode(engine_source(store, e.path, e.sha)), e.name)
            except Exception as ex:
                info = {"name": e.name, "ok": False, "error": f"읽지 못함: {type(ex).__name__}: {ex}", "title": "",
                        "version": "V0", "signal_mode": "none", "signal_filename": storage.SIGNAL_NAME}
            info.update(path=e.path, sha=e.sha, size=e.size)
            _INFO[key] = info
        out.append(dict(_INFO[key]))
    out.sort(key=lambda i: (i["ok"], version_key(i["version"]), i["name"]), reverse=True)
    for i, x in enumerate(out):
        x["latest"] = i == 0 and x["ok"]
    return out


def engine_label(info, all_engines=()):
    """화면에 보일 이름: 'V4.3.7 (최신)' — 같은 버전이 둘 이상이면 파일 이름을 붙임"""
    v = info["version"] if info["version"] != "V0" else "버전 미상"
    same = sum(1 for x in all_engines if x["version"] == info["version"]) > 1
    return v + (" (최신)" if info.get("latest") else "") + (f" · {info['name']}" if same or v == "버전 미상" else "") + \
        ("" if info["ok"] else " — 실행 불가")


def engine_file_name(version):
    return f"{ENGINE_DIR}/analysis_engine_{version}.py"


def add_engine(store, name, data, overwrite=False):
    """앱에서 올린 엔진 파일을 engine/analysis_engine_<버전>.py 로 저장 -> (저장 경로, 정보). 문제가 있으면 ValueError"""
    info = inspect_source(_decode(data), name)
    if not info["ok"]:
        raise ValueError(info["error"])
    if info["version"] == "V0":
        raise ValueError("엔진 첫 줄에서 버전 표시([V4.3.8 · 날짜] 같은)를 찾지 못했습니다.")
    existing = [x for x in list_engines(store) if x["version"] == info["version"]]
    if existing and not overwrite:
        raise FileExistsError(", ".join(x["name"] for x in existing))
    path = existing[0]["path"] if existing else engine_file_name(info["version"])
    store.write(path, data, f"분석 엔진 {info['version']} 추가")
    return path, info


# ==============================================================================
# 실행
# ==============================================================================
def run(store, master_df, engine=None, tier="5", split=False, date="latest", binance=True, on_progress=None,
        on_log=None, timeout=1200):
    """engine: list_engines()의 항목 (None이면 최신). 반환 dict: status · title · message · hint · seconds · engine_version ·
    files[{name, data, kind}] · splits · signal_saved · signal_file · saved"""
    on_progress = on_progress or (lambda *_: None)
    on_log = on_log or (lambda *_: None)
    if engine is None:
        runnable = [x for x in list_engines(store) if x["ok"]]
        if not runnable:
            return {"status": "error", "title": "분석 엔진 파일이 없습니다", "message": "저장소 engine/ 폴더에 엔진 파일(.py)을 올리세요."}
        engine = runnable[0]
    if not engine.get("ok"):
        return {"status": "error", "title": "이 엔진 파일은 실행할 수 없습니다", "message": engine.get("error", "")}
    ver = engine["version"]
    if not _LOCK.acquire(blocking=False):
        return {"status": "busy", "title": "다른 분석이 실행 중입니다", "message": "끝난 뒤에 다시 누르세요."}
    work = tempfile.mkdtemp(prefix="ewy_engine_")
    t0 = time.time()
    try:
        in_dir, out_dir, sig_dir, eng_dir = (os.path.join(work, x) for x in ("in", "out", "sig", "engine"))
        for d in (in_dir, out_dir, sig_dir, eng_dir):
            os.makedirs(d)
        on_progress(1, 0.0, "데이터 준비")
        eng_file = os.path.join(eng_dir, engine["name"])
        with open(eng_file, "wb") as fh:
            fh.write(engine_source(store, engine["path"], engine["sha"]))
        with open(os.path.join(in_dir, "EWY_master_merged.csv"), "wb") as fh:
            fh.write(storage.csv_bytes(storage.to_csv_frame(master_df)))

        # 신호 기록 파일: 엔진 방식에 따라 놓는 곳과 저장소 파일이 다름
        mode = engine.get("signal_mode", "none")
        sig_store_path = storage.SIGNAL_PATH if mode == "main" else storage.signal_path_for(ver) if mode == "own" else None
        sig_file = (os.path.join(sig_dir, storage.SIGNAL_NAME) if mode == "main" else
                    os.path.join(out_dir, engine.get("signal_filename") or storage.SIGNAL_NAME) if mode == "own" else None)
        sig_before = None
        if sig_store_path:
            try:
                sig_before = storage.read_signal(store, sig_store_path)
            except Exception as e:
                on_log(f"[주의] 신호 기록 파일을 읽지 못했습니다({type(e).__name__}) — 새로 만듭니다.")
            if sig_before:
                with open(sig_file, "wb") as fh:
                    fh.write(sig_before)

        cmd = [sys.executable, "-u", ENGINE_JOB, "--file", eng_file, "--input", in_dir, "--output", out_dir,
               "--tier", str(tier), "--version", "PC", "--date", date or "latest", "--binance", "1" if binance else "0",
               "--split", "1" if split else "0"]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        env.pop("EWY_SIGNAL_LOG_DIR", None)
        if mode == "main":
            env["EWY_SIGNAL_LOG_DIR"] = sig_dir
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
        res["engine_version"] = ver
        res["engine_name"] = engine["name"]

        def tagged(name):
            """'Tier5_PC_20261124_093412…' -> 'Tier5_PC_20261124_093412__V4.3.6…' (보관·내려받기 이름에 엔진 버전)"""
            m = re.match(r"^(Tier\d_(?:PC|MOBILE)_\d{8}_\d{6})(?!__V)", name)
            return f"{m.group(1)}__{ver}{name[m.end():]}" if m else name

        # 결과 파일을 메모리로 (임시 폴더는 지움)
        files = []
        for p in res.get("files") or []:
            if os.path.isfile(p):
                with open(p, "rb") as fh:
                    n = os.path.basename(p)
                    files.append({"name": tagged(n), "data": fh.read(), "kind": "databook" if DATABOOK_RE.match(n) else "other"})
        res["files"] = files
        splits = []
        for s in res.get("splits") or []:
            item = {"databook": tagged(os.path.basename(s["databook"])), "date": s.get("date"), "chars": s.get("chars"),
                    "tables": s.get("tables"), "parts": [], "viewer": None}
            for k, p in enumerate(s.get("parts") or [], 1):
                if os.path.isfile(p):
                    with open(p, "rb") as fh:
                        item["parts"].append({"k": k, "name": tagged(os.path.basename(p)), "data": fh.read()})
            if s.get("viewer") and os.path.isfile(s["viewer"]):
                with open(s["viewer"], "rb") as fh:
                    item["viewer"] = {"name": tagged(os.path.basename(s["viewer"])), "data": fh.read()}
            splits.append(item)
        res["splits"] = splits
        # 신호 기록이 바뀌었으면 저장소에 저장
        res["signal_saved"], res["signal_file"] = False, sig_store_path
        if sig_file and os.path.isfile(sig_file):
            with open(sig_file, "rb") as fh:
                after = fh.read()
            if after and after != sig_before:
                try:
                    storage.save_signal(store, after, f"신호 기록·채점 갱신 {ver} ({res.get('date') or date})", path=sig_store_path)
                    res["signal_saved"] = True
                except Exception as e:
                    res["signal_error"] = f"{type(e).__name__}: {e}"[:300]
        # 데이터북을 저장소에 보관 (이름에 엔진 버전)
        saved = []
        if res.get("status") == "ok":
            for f in files:
                m = DATABOOK_RE.match(f["name"])
                if m and f["kind"] == "databook":
                    try:
                        saved.append(storage.save_report(store, m.group(3), f["name"], f["data"],
                                                         f"분석 엔진 {ver} 프롬프트 {m.group(3)} Tier{m.group(1)}"))
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
