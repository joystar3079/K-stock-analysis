"""옵션 데이터 저장소 — 깃허브 저장소에 누적 관리 (스트림잇 앱 · 깃허브 예약 수집 공용)

저장 구조 (저장소 안)
  data/master_base.csv.gz          누적 마스터 (수집기 CSV와 같은 열 · gzip 압축)
  data/daily/EWY Option 분석데이터_YYYYMMDD.csv
                                   마스터 이후에 받은 날짜별 파일 (수집기·코랩과 같은 이름·형식)
  data/EWY_신호기록_채점.csv        분석 엔진 V4.3.7 신호 기록·채점
  reports/YYYYMMDD/...              분석 엔진이 만든 프롬프트(데이터북) · 최종 보고서

합치는 규칙
  - 마스터 -> 날짜별 파일(이름순) 순서로 읽고, 같은 날짜가 여러 파일에 있으면 나중 파일이 그 날짜를 통째로 대신함
    (한 날짜 = 한 번의 수집본. 서로 다른 시각의 수집본이 섞이지 않게)
  - 한 파일 안의 같은 계약·같은 날 중복은 뒤 행 기준으로 제거 (분석 엔진 V4.3.7 규칙)
  - 날짜별 파일이 많아지면(COMPACT_AFTER개 초과) 깃허브 예약 수집이 마스터에 합치고 날짜별 파일을 지움
    -> 저장소가 매일 수 MB씩 불어나지 않게 함 (마스터 전체를 다시 올리는 것은 한 달에 한 번꼴)

저장소 종류
  GithubStore  스트림잇 앱: 깃허브 API로 읽고 씀 (secrets의 GITHUB_TOKEN · GITHUB_REPO)
  LocalStore   깃허브 예약 수집(저장소를 받아 둔 폴더) · PC에서 시험 실행
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd

SYMBOL = "EWY"
PRICE_COL = f"{SYMBOL} Price"
DATA_DIR = "data"
BASE_NAME = "master_base.csv.gz"
BASE_PATH = f"{DATA_DIR}/{BASE_NAME}"
DAILY_DIR = f"{DATA_DIR}/daily"
SIGNAL_NAME = "EWY_신호기록_채점.csv"
SIGNAL_PATH = f"{DATA_DIR}/{SIGNAL_NAME}"
REPORT_DIR = "reports"
LEGACY_PKL = "EWY_Options_V27_App_Master.pkl.gz"      # V34까지 쓰던 마스터 (새 마스터가 없을 때만 읽음)
DAILY_RE = re.compile(r"Option 분석데이터_(\d{8})\.csv$", re.I)
COMPACT_AFTER = 40

CSV_COLS = ["Contract Name", "Quote Date", "Expiration Date", "Option Type", "Strike", "Bid", "Ask", "Last Price",
            "Volume", "Open Interest", "Secured Overnight Financing Rate", PRICE_COL, "Implied Volatility", "Delta"]
NEEDED = ("Quote Date", "Expiration Date", "Option Type", "Strike", "Open Interest", PRICE_COL)
NUM_COLS = ("Strike", "Bid", "Ask", "Last Price", "Volume", "Open Interest", "Secured Overnight Financing Rate",
            PRICE_COL, "Implied Volatility", "Delta")


class StoreError(Exception):
    """화면에 그대로 보여 줄 저장소 오류"""


@dataclass
class Entry:
    name: str
    path: str
    sha: str
    size: int


def daily_name(date_str):
    """'2026-11-24' 또는 '20261124' -> 'EWY Option 분석데이터_20261124.csv'"""
    return f"{SYMBOL} Option 분석데이터_{str(date_str).replace('-', '')[:8]}.csv"


# ==============================================================================
# 1. 저장소
# ==============================================================================
class LocalStore:
    """저장소를 받아 둔 폴더 (깃허브 예약 수집 · PC 시험 실행)"""
    kind = "local"

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def label(self):
        return f"이 폴더 ({self.root})"

    def _abs(self, path):
        return os.path.join(self.root, *[p for p in str(path).split("/") if p])

    def list(self, d):
        p, out = self._abs(d), []
        if os.path.isdir(p):
            for n in sorted(os.listdir(p)):
                fp = os.path.join(p, n)
                if os.path.isfile(fp):
                    st = os.stat(fp)
                    out.append(Entry(n, f"{d}/{n}".lstrip("/"), f"{st.st_size}-{st.st_mtime_ns}", st.st_size))
        return out

    def list_dirs(self, d):
        p = self._abs(d)
        return sorted(n for n in os.listdir(p) if os.path.isdir(os.path.join(p, n))) if os.path.isdir(p) else []

    def read(self, path, sha=None):
        try:
            with open(self._abs(path), "rb") as fh:
                return fh.read()
        except FileNotFoundError:
            return None

    def write(self, path, data, message=""):
        fp = self._abs(path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        tmp = fp + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, fp)

    def delete(self, path, message=""):
        try:
            os.remove(self._abs(path))
        except FileNotFoundError:
            pass

    def modified(self, path):
        """마지막으로 바뀐 때(UTC). 깃 저장소면 마지막 커밋 시각 (예약 수집에서 파일 시각은 받은 시각이라 쓸 수 없음)"""
        fp = self._abs(path)
        if not os.path.exists(fp):
            return None
        if os.path.isdir(os.path.join(self.root, ".git")):
            try:
                out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path], cwd=self.root,
                                     capture_output=True, text=True, timeout=30).stdout.strip()
                if out:
                    return datetime.fromtimestamp(int(out), tz=timezone.utc)
            except Exception:
                pass
        return datetime.fromtimestamp(os.path.getmtime(fp), tz=timezone.utc)


class GithubStore:
    """깃허브 저장소 (스트림잇 앱). 토큰은 저장소 내용 쓰기 권한이 있어야 함"""
    kind = "github"

    def __init__(self, token, repo_name, branch=None):
        try:
            from github import Auth, Github
            gh = Github(auth=Auth.Token(token))
        except ImportError:                                  # PyGithub 1.x
            from github import Github
            gh = Github(token)
        self.token, self.repo_name = token, repo_name
        self.repo = gh.get_repo(repo_name)
        self.branch = branch or self.repo.default_branch or "main"

    def label(self):
        return f"깃허브 {self.repo_name} ({self.branch})"

    @staticmethod
    def _status(e):
        return getattr(e, "status", None)

    def _contents(self, path):
        from github import GithubException
        try:
            return self.repo.get_contents(path, ref=self.branch)
        except GithubException as e:
            if self._status(e) == 404:
                return None
            raise

    def list(self, d):
        items = self._contents(d)
        if items is None:
            return []
        if not isinstance(items, list):
            items = [items]
        return sorted((Entry(i.name, i.path, i.sha, int(i.size or 0)) for i in items if i.type == "file"),
                      key=lambda e: e.name)

    def list_dirs(self, d):
        items = self._contents(d)
        if not isinstance(items, list):
            return []
        return sorted(i.name for i in items if i.type == "dir")

    def _meta(self, path):
        d, _, n = path.rpartition("/")
        return next((e for e in self.list(d) if e.name == n), None)      # 폴더 목록으로 찾음 (1MB 넘는 파일도 됨)

    def read(self, path, sha=None):
        import base64
        import requests
        if sha is None:
            e = self._meta(path)
            if e is None:
                return None
            sha = e.sha
        r = requests.get(f"https://api.github.com/repos/{self.repo_name}/git/blobs/{sha}", timeout=120,
                         headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.raw+json",
                                  "X-GitHub-Api-Version": "2022-11-28"})
        if r.status_code == 404:
            return None
        r.raise_for_status()
        if "json" in r.headers.get("Content-Type", ""):               # 원본 대신 base64 JSON이 오면 풀어서
            j = r.json()
            if isinstance(j, dict) and j.get("encoding") == "base64":
                return base64.b64decode(j.get("content", ""))
        return r.content

    def write(self, path, data, message=""):
        from github import GithubException
        message = message or f"update {path}"
        for attempt in range(3):
            e = self._meta(path)
            try:
                if e is None:
                    self.repo.create_file(path, message, data, branch=self.branch)
                else:
                    self.repo.update_file(path, message, data, e.sha, branch=self.branch)
                return
            except GithubException as ex:                        # 같은 때 다른 곳(예약 수집)이 먼저 고친 경우 -> 다시 시도
                if self._status(ex) in (409, 422) and attempt < 2:
                    time.sleep(1.5)
                    continue
                raise StoreError(f"깃허브에 저장하지 못했습니다 ({self._status(ex)}): {ex}") from ex

    def delete(self, path, message=""):
        e = self._meta(path)
        if e is not None:
            self.repo.delete_file(path, message or f"delete {path}", e.sha, branch=self.branch)

    def modified(self, path):
        try:
            commits = self.repo.get_commits(sha=self.branch, path=path)
            c = commits[0]
            dt = c.commit.committer.date
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None


def open_store(secrets=None, root=None):
    """스트림잇 secrets에 GITHUB_TOKEN·GITHUB_REPO가 있으면 깃허브, 없으면 이 폴더"""
    s = secrets or {}
    try:
        token, repo = s.get("GITHUB_TOKEN"), s.get("GITHUB_REPO")
        branch = s.get("GITHUB_BRANCH")
    except Exception:
        token = repo = branch = None
    if token and repo:
        return GithubStore(token, repo, branch)
    return LocalStore(root or os.path.dirname(os.path.abspath(__file__)))


# ==============================================================================
# 2. 마스터 읽기 · 합치기
# ==============================================================================
def master_sources(store):
    """(마스터 Entry 또는 None, 날짜별 파일 Entry 목록(이름순), 예전 pkl Entry 또는 None)"""
    data = {e.name: e for e in store.list(DATA_DIR)}
    base = data.get(BASE_NAME)
    daily = [e for e in store.list(DAILY_DIR) if DAILY_RE.search(e.name)]
    legacy = None
    if base is None:
        legacy = next((e for e in store.list("") if e.name == LEGACY_PKL), None)
    return base, daily, legacy


def sources_key(base, daily, legacy=None):
    h = hashlib.sha1(b"ewy-master-v1")
    for e in ([base] if base else []) + ([legacy] if legacy else []) + list(daily):
        h.update(f"{e.path}|{e.sha}\n".encode("utf-8"))
    return h.hexdigest()[:16]


def _read_csv_bytes(data):
    for enc in ("utf-8-sig", "cp949"):
        try:
            df = pd.read_csv(io.BytesIO(data), encoding=enc, low_memory=False)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except UnicodeDecodeError:
            continue
    raise StoreError("CSV 인코딩을 읽지 못했습니다.")


def read_frame(store, entry):
    raw = store.read(entry.path, sha=entry.sha)
    if raw is None:
        raise StoreError(f"{entry.path} 파일을 읽지 못했습니다.")
    if entry.name.endswith(".pkl.gz"):
        df = pd.read_pickle(io.BytesIO(raw), compression="gzip")
        df = df.copy()
        df["Option Type"] = np.where(df["Option Type"].astype(str).str.upper().str[0] == "C", "Call", "Put")
        return df
    if entry.name.endswith(".gz"):
        raw = gzip.decompress(raw)
    return _read_csv_bytes(raw)


def build_master(frames):
    """[(이름, DataFrame), ...] (앞 -> 뒤 순서) -> (분석용 마스터, 요약)
    분석용 마스터: Option Type 'C'/'P', 날짜는 datetime, 날짜순 안정 정렬(같은 날 안의 순서는 파일 순서 그대로 —
    방어벽 가격(OI 상위 10개) 동점 처리를 원본과 같게)"""
    parts, used, skipped = [], [], []
    for rank, (name, df) in enumerate(frames):
        miss = [c for c in NEEDED if c not in df.columns]
        if miss:
            skipped.append({"name": name, "reason": "옵션 CSV가 아님(없는 열: " + ", ".join(miss) + ")"})
            continue
        d = df.copy()
        if "Contract Name" not in d.columns:
            d["Contract Name"] = ""
        d["_rank"] = rank
        parts.append(d)
        used.append({"name": name, "rows": int(len(d)), "daily": bool(DAILY_RE.search(name))})
    if not parts:
        raise StoreError("읽을 옵션 데이터가 없습니다. 먼저 데이터를 수집하거나 마스터 파일을 올리세요.")
    m = pd.concat(parts, ignore_index=True)
    raw = len(m)
    m["Contract Name"] = m["Contract Name"].astype(str).str.strip()
    m["Quote Date"] = pd.to_datetime(m["Quote Date"].astype(str).str.strip(), errors="coerce", format="mixed").dt.normalize()
    m["Expiration Date"] = pd.to_datetime(m["Expiration Date"].astype(str).str.strip(), errors="coerce",
                                          format="mixed").dt.normalize()
    bad = int(m["Quote Date"].isna().sum() + m["Expiration Date"].isna().sum())
    m = m.dropna(subset=["Quote Date", "Expiration Date"])
    # 날짜마다 가장 나중 파일만 남김 (한 날짜 = 한 수집본)
    top = m.groupby("Quote Date")["_rank"].transform("max")
    replaced = int((m["_rank"] < top).sum())
    m = m[m["_rank"] == top]
    first = m["Option Type"].astype(str).str.strip().str.upper().str[0]
    m["Option Type"] = np.where(first == "C", "C", "P")
    before = len(m)
    m = m.drop_duplicates(subset=["Contract Name", "Quote Date"], keep="last")
    dups = before - len(m)
    for c in NUM_COLS:
        m[c] = pd.to_numeric(m[c], errors="coerce") if c in m.columns else np.nan
    m["Volume"] = m["Volume"].fillna(0)
    m["Open Interest"] = m["Open Interest"].fillna(0)
    m = m.dropna(subset=["Strike"])
    m = m.sort_values("Quote Date", kind="mergesort").drop(columns="_rank").reset_index(drop=True)
    days = m["Quote Date"]
    stats = {"files": used, "skipped": skipped, "raw_rows": int(raw), "rows": int(len(m)), "duplicates": int(dups),
             "replaced": replaced, "bad_dates": bad, "days": int(days.nunique()),
             "start": days.min().strftime("%Y-%m-%d") if len(m) else "",
             "end": days.max().strftime("%Y-%m-%d") if len(m) else "",
             "daily_files": sum(1 for u in used if u["daily"])}
    return m, stats


def load_master(store, base=None, daily=None, legacy=None):
    if base is None and daily is None and legacy is None:
        base, daily, legacy = master_sources(store)
    frames = []
    if base is not None:
        frames.append((base.name, read_frame(store, base)))
    elif legacy is not None:
        frames.append((legacy.name, read_frame(store, legacy)))
    for e in daily or []:
        frames.append((e.name, read_frame(store, e)))
    return build_master(frames)


def to_csv_frame(m):
    """분석용 마스터 -> 수집기 CSV 형식 (Call/Put · 날짜 글자 · 정수 거래량/미결제약정)"""
    out = m.copy()
    out["Quote Date"] = pd.to_datetime(out["Quote Date"]).dt.strftime("%Y-%m-%d")
    out["Expiration Date"] = pd.to_datetime(out["Expiration Date"]).dt.strftime("%Y-%m-%d")
    out["Option Type"] = np.where(out["Option Type"].astype(str).str.upper().str[0] == "C", "Call", "Put")
    out["Volume"] = pd.to_numeric(out["Volume"], errors="coerce").fillna(0).round().astype("int64")
    out["Open Interest"] = pd.to_numeric(out["Open Interest"], errors="coerce").fillna(0).round().astype("int64")
    return out[[c for c in CSV_COLS if c in out.columns]]


def csv_bytes(df, gz=False):
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    data = buf.getvalue().encode("utf-8-sig")
    if not gz:
        return data
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0, compresslevel=9, filename="") as g:
        g.write(data)
    return out.getvalue()


# ==============================================================================
# 3. 날짜별 파일 · 마스터 합치기
# ==============================================================================
def daily_entries(store):
    return [e for e in store.list(DAILY_DIR) if DAILY_RE.search(e.name)]


def save_daily(store, name, data, message=""):
    if not DAILY_RE.search(name):
        raise StoreError(f"날짜별 파일 이름 형식이 아닙니다: {name}")
    store.write(f"{DAILY_DIR}/{name}", data, message or f"옵션 데이터 {DAILY_RE.search(name).group(1)}")
    return f"{DAILY_DIR}/{name}"


def compact(store, log=print):
    """날짜별 파일을 마스터에 합치고 지움 (예약 수집에서 COMPACT_AFTER개를 넘으면 실행)"""
    base, daily, legacy = master_sources(store)
    if not daily:
        return None
    m, stats = load_master(store, base, daily, legacy)
    store.write(BASE_PATH, csv_bytes(to_csv_frame(m), gz=True), f"마스터 합치기: 날짜별 파일 {len(daily)}개")
    for e in daily:
        store.delete(e.path, f"마스터에 합침: {e.name}")
    log(f"[마스터 합치기] 날짜별 파일 {len(daily)}개 -> 마스터 {stats['rows']:,}행 · {stats['start']} ~ {stats['end']} ({stats['days']}거래일)")
    return stats


def latest_snapshot(store):
    """가장 최근 날짜의 수집본 (이름, CSV 바이트, 바뀐 시각) — 수집기의 '이미 받은 날' 판정과 SOFR 대체값에 씀"""
    daily = daily_entries(store)
    if daily:
        e = daily[-1]
        return e.name, store.read(e.path, sha=e.sha), store.modified(e.path)
    base, _, legacy = master_sources(store)
    src = base or legacy
    if src is None:
        return None
    df = read_frame(store, src)
    q = pd.to_datetime(df["Quote Date"].astype(str), errors="coerce", format="mixed")
    last = q.max()
    if pd.isna(last):
        return None
    day = df[q == last]
    return daily_name(last.strftime("%Y%m%d")), csv_bytes(to_csv_frame(build_master([("base", day)])[0])), store.modified(src.path)


# ==============================================================================
# 4. 신호 기록 · 보고서
# ==============================================================================
def read_signal(store):
    return store.read(SIGNAL_PATH)


def save_signal(store, data, message=""):
    store.write(SIGNAL_PATH, data, message or "신호 기록·채점 갱신")


def report_dates(store, n=15):
    return sorted(store.list_dirs(REPORT_DIR), reverse=True)[:n]


def report_files(store, date_dir):
    return store.list(f"{REPORT_DIR}/{date_dir}")


def save_report(store, date_dir, name, data, message=""):
    path = f"{REPORT_DIR}/{date_dir}/{name}"
    store.write(path, data, message or f"분석 결과 저장: {name}")
    return path


def summary_json(stats):
    return json.dumps(stats, ensure_ascii=False, default=str)
