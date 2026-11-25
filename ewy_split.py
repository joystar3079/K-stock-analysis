# -*- coding: utf-8 -*-
"""
3분할 프롬프트 · 최종 보고서 합치기 (V4.4 모바일분할팩 애드온을 프로그램용으로 옮김)
------------------------------------------------------------------------------
- 엔진 데이터북(Tier*_PC_*.txt / Tier*_MOBILE_*.txt)을 읽어
    {이름}_1of3.txt · _2of3.txt · _3of3.txt (섹션 0~1 / 섹션 2 / 섹션 3~5 분할 프롬프트)
    {이름}_표뷰어.html (데이터북의 모든 표를 미리 그린 모바일 HTML)
  을 만듭니다.
- 제미나이·클로드 등에서 받은 파트 1~3 답변을 합쳐
    {이름}_보고서.html (PC 보고서 양식: 섹션 0~5, 소제목마다 데이터북 표 + 바로 아래 해설, 부록 자동 검산)
    · {이름}_해설.md · {이름}_검산.txt
  를 만듭니다.
- 분해·프롬프트·HTML·검산 로직은 애드온 코드를 그대로 씁니다. (Gemini API·코랩 화면 부분만 뺐습니다)
- 표준 라이브러리만 씁니다.
"""
import html
import os
import re
from datetime import datetime

PART_CHAR_TARGET = {1: 4000, 2: 5500, 3: 6000}   # 파트별 해설 분량 목표(한글 글자 수, ±20%)
PART_TITLES = {1: '섹션 0~1', 2: '섹션 2', 3: '섹션 3~5'}
DATABOOK_RE = re.compile(r'^Tier(\d)_(PC|MOBILE)_(\d{8})_(\d{6})\.txt$')

# ------------------------------------------------------------------------------
# 1. 데이터북 읽기·분해
# ------------------------------------------------------------------------------
SEP_RE      = re.compile(r'^\s*[-=]{20,}\s*$')
SEC_RE      = re.compile(r'^## \[섹션 (\d)\]')
SUB6_RE     = re.compile(r'^### \((6-\d)\)')
UNIT_NUM_RE = re.compile(r'[+\-]?\d[\d,]*(?:\.\d+)?\s*(?:%|계약|주|달러|원|pt|x)')
NUM_CELL_RE = re.compile(r'^[+\-−]?\$?\s*[\d,]+(?:\.\d+)?')


def parse_databook(raw):
    lines = raw.replace('\r\n', '\n').split('\n')
    i_start = next((i for i, l in enumerate(lines) if '[첨부 정량 데이터북 시작]' in l), None)
    if i_start is None:
        raise ValueError("데이터북 시작 표지('[첨부 정량 데이터북 시작]')를 찾지 못했습니다. 엔진 출력 .txt가 맞는지 확인하세요.")
    if i_start > 0 and SEP_RE.match(lines[i_start - 1]):
        i_start -= 1
    i_end = next((i for i, l in enumerate(lines) if l.startswith('[최종 실행 지시')), len(lines))
    body = lines[i_start:i_end]

    sec_pos = [(k, int(SEC_RE.match(l).group(1))) for k, l in enumerate(body) if SEC_RE.match(l)]
    meta = body[:sec_pos[0][0]] if sec_pos else body
    sec = {}
    for n, (k, num) in enumerate(sec_pos):
        end = sec_pos[n + 1][0] if n + 1 < len(sec_pos) else len(body)
        sec[num] = body[k:end]

    sub6, cur = {'head': []}, 'head'
    for l in sec.get(6, []):
        m = SUB6_RE.match(l)
        if m:
            cur = m.group(1)
        sub6.setdefault(cur, []).append(l)

    text = '\n'.join(body)
    wins = [int(x) for x in re.findall(r'Call 4분면 \(최근\s*(\d+)일 합계\)', text)]
    m_traj = re.search(r'### \(1-2\)[^\n]*?최근 (\d+)영업일', text)
    return {
        'meta': meta, 'sec': sec, 'sub6': sub6, 'text': text, 'head': lines[:i_start],
        'ws': wins[0] if wins else 3, 'wl': wins[1] if len(wins) > 1 else 7,
        'traj': int(m_traj.group(1)) if m_traj else 7,
    }


def _cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def _is_header_at(lines, k):
    """표 머리행 = 파이프 2개 이상 줄 + 바로 아래 구분선 + 그 아래 같은 모양의 데이터 행"""
    if k + 2 >= len(lines):
        return False
    a, s, b = lines[k], lines[k + 1], lines[k + 2]
    if '|' not in a or SEP_RE.match(a) or a.count('|') < 2 or not SEP_RE.match(s):
        return False
    return '|' in b and not SEP_RE.match(b) and abs(b.count('|') - a.count('|')) <= 1


def parse_blocks(lines):
    """줄 목록 -> [('text', [줄...]) | ('table', 머리행 또는 None, [행...])]"""
    blocks, i, n = [], 0, len(lines)

    def add_text(l):
        if blocks and blocks[-1][0] == 'text':
            blocks[-1][1].append(l)
        else:
            blocks.append(('text', [l]))

    while i < n:
        ln = lines[i]
        if _is_header_at(lines, i):
            hdr, rows, j = _cells(ln), [], i + 2
            while j < n and '|' in lines[j] and not SEP_RE.match(lines[j]) and not _is_header_at(lines, j):
                rows.append(_cells(lines[j]))
                j += 1
            blocks.append(('table', hdr, rows))
            i = j
            continue
        if '|' in ln and not SEP_RE.match(ln):
            cnt, j, run = ln.count('|'), i, []
            while (j < n and '|' in lines[j] and not SEP_RE.match(lines[j])
                   and not _is_header_at(lines, j) and lines[j].count('|') == cnt):
                run.append(lines[j])
                j += 1
            if cnt >= 2 and len(run) >= 2:          # 같은 모양 줄이 2개 이상이면 머리행 없는 표
                first_is_hdr = UNIT_NUM_RE.search(run[0]) is None
                hdr = _cells(run[0]) if first_is_hdr else None
                rows = [_cells(r) for r in (run[1:] if first_is_hdr else run)]
                blocks.append(('table', hdr, rows))
            else:
                for r in run:
                    add_text(r)
            i = j
            continue
        add_text(ln)
        i += 1
    return blocks


# ------------------------------------------------------------------------------
# 2. AI 입력용 정리 (달러 기호 제거 · 정렬용 공백 제거 · 구분선 제거)
# ------------------------------------------------------------------------------
def dollar_to_text(s):
    s = re.sub(r'\$\s*([+\-]?\d[\d,]*(?:\.\d+)?)(?=[PC]\b)', r'\1', s)            # $145.0P -> 145.0P (행사가 표기)
    s = re.sub(r'\$\s*([+\-]?\d[\d,]*(?:\.\d+)?)\s*([MK])\b', r'\1\2달러', s)     # $20.15M -> 20.15M달러
    s = re.sub(r'\$\s*([+\-]?\d[\d,]*(?:\.\d+)?)', r'\1달러', s)                   # $159.83 -> 159.83달러
    return s.replace('$', '달러')                                                  # pt/$ -> pt/달러


def _clean(s, in_table=False):
    s = dollar_to_text(s.strip())
    s = re.sub(r'\s*\|\s*', '|' if in_table else ' | ', s)
    s = re.sub(r' {2,}', ' ', s)
    s = re.sub(r'\(\s+', '(', s)
    return s


def ai_text(lines):
    out = []
    for b in parse_blocks(lines):
        if b[0] == 'table':
            _, hdr, rows = b
            if hdr:
                out.append('|'.join(_clean(c, True) for c in hdr))
            out.extend('|'.join(_clean(c, True) for c in r) for r in rows)
            continue
        for l in b[1]:
            if SEP_RE.match(l):
                continue
            if not l.strip():
                if out and out[-1] != '':
                    out.append('')
                continue
            lead = len(l) - len(l.lstrip(' '))
            out.append(('  ' if lead >= 3 else (' ' if lead >= 1 else '')) + _clean(l))
    return '\n'.join(out).strip('\n')


# ------------------------------------------------------------------------------
# 3. 핵심 수치 카드 (파이썬 추출 -> AI 인용 기준값 + 생성 후 자동 검산 기준값)
# ------------------------------------------------------------------------------
def extract_key_facts(T):
    def g(p):
        return re.search(p, T)
    F = {}
    m = g(r'분석 기준 시점\s*:\s*[^\n(]*\((\d{4}-\d{2}-\d{2})\)') or g(r'유효 데이터기간\s*:\s*\S+\s*~\s*(\d{4}-\d{2}-\d{2})')
    F['date'] = m.group(1) if m else '기준일미상'
    m = g(r'선택된 분석 Tier\s*:\s*(.+)')
    F['tier'] = m.group(1).strip() if m else ''
    m = g(r'EWY 미국본장종가\s*:\s*\$\s*([\d.,]+)\s*\(전일비\s*([+\-]?[\d.]+%)')
    F['spot'] = m.groups() if m else None
    m1 = g(r'1순위 지배 전략\s*:\s*(.+?)\s*\(확률\s*([\d.]+)%\)')
    m2 = g(r'2순위 경계 전략\s*:\s*(.+?)\s*\(확률\s*([\d.]+)%\)')
    F['reg1'] = m1.groups() if m1 else None
    F['reg2'] = m2.groups() if m2 else None
    F['regs'] = dict(re.findall(r'\[레짐 ([ABCD])\][^\n]*?산출 확률:\s*([\d.]+)%', T))
    m = g(r'국면 확률\s*:\s*상승\(U\)\s*([\d.]+)%\s*\|\s*하락\(D\)\s*([\d.]+)%\s*\|\s*횡보\(S\)\s*([\d.]+)%\s*->\s*1순위\s*\[([^\]]+)\]')
    F['phase'] = m.groups() if m else None
    m = g(r'\[V4\.4 급락 위험도\][^\n]*->\s*평균\s*([\d.]+)\s*=\s*\[(상|중|하)\]')
    F['risk'] = m.groups() if m else None
    m = g(r'과거 빈도\(10영업일[^)]*\):\s*상\s*(\d+)%\s*·\s*중\s*(\d+)%\s*·\s*하\s*(\d+)%')
    F['risk_freq'] = m.groups() if m else None
    F['quad'] = {}
    for typ, win, q1, q2, q3, q4 in re.findall(
            r'(Call|Put)\s+4분면 \(최근\s*(\d+)일 합계\)\s*:\s*Q1\[[^\]]*\]\s*([+\-][\d,]+)계약\s*\|\s*'
            r'Q2\[[^\]]*\]\s*([+\-][\d,]+)계약\s*\|\s*Q3\[[^\]]*\]\s*([+\-][\d,]+)계약\s*\|\s*Q4\[[^\]]*\]\s*([+\-][\d,]+)계약', T):
        F['quad'][(typ, int(win))] = (q1, q2, q3, q4)
    m = g(r"감마 플립 마지노선'은 EWY ([\d.]+)달러\(([+\-][\d.]+%)")
    F['gflip'] = m.groups() if m else None
    m = g(r'세력 가중 매집원가 BEP\s*:\s*([\d.]+)달러')
    F['bep'] = m.group(1) if m else None
    m = g(r'\[최근접 만기\((\d{4}-\d{2}-\d{2})\) Max Pain\]\s*:\s*EWY \$\s*([\d.]+)[^\n]*?전체만기 MP \$\s*([\d.]+)')
    F['mp'] = m.groups() if m else None
    m = g(r'1시그마\(68\.2%\) 확률 레인지는 EWY ([\d.]+)~([\d.]+)달러')
    F['rng'] = m.groups() if m else None
    for key, lab in (('cw1', '상단 1차 Call Wall 목표가'), ('cw2', '상단 2차 Call Wall 목표가'),
                     ('pb1', '하단 1차 전방 Put 방어선'), ('pb2', '하단 2차 핵심 콘크리트 요새')):
        m = g(r'\[' + re.escape(lab) + r'\]\s*:\s*EWY \$\s*([\d.]+)')
        F[key] = m.group(1) if m else None
    m = g(r'\[V4\.4 최종 판정[^\]]*\]:\s*\S*\s*(\[[^\]]+\])')
    F['final'] = m.group(1) if m else None
    m = g(r'종합 눌림목/분배 경보 등급\s*:\s*(.+)')
    F['pb_grade'] = dollar_to_text(m.group(1).strip()) if m else None
    m = g(r'\[합성 공매도 종합 판정\]:\s*\S*\s*(\[[^\]]+\])')
    F['synth'] = m.group(1) if m else None
    return F


def card_lines(F, ws, wl):
    L = []
    if F['spot']:
        L.append(f"기준일 {F['date']} · EWY 종가 {F['spot'][0]}달러 (전일비 {F['spot'][1]})")
    if F['regs']:
        s = "레짐 확률: " + " · ".join(f"{k} {v}%" for k, v in sorted(F['regs'].items()))
        if F['reg1']:
            s += f" (1순위 {F['reg1'][0]} {F['reg1'][1]}%)"
        L.append(s)
    if F['phase']:
        L.append(f"국면 확률: 상승 {F['phase'][0]}% · 하락 {F['phase'][1]}% · 횡보 {F['phase'][2]}% -> 1순위 {F['phase'][3]}")
    if F['risk']:
        s = f"급락 위험도: [{F['risk'][1]}] (지표 평균 {F['risk'][0]})"
        if F['risk_freq']:
            s += f" · 과거 빈도(10영업일 내 -5% 이상 하락) 상 {F['risk_freq'][0]}% / 중 {F['risk_freq'][1]}% / 하 {F['risk_freq'][2]}%"
        L.append(s)
    for win in (ws, wl):
        c, p = F['quad'].get(('Call', win)), F['quad'].get(('Put', win))
        if c and p:
            L.append(f"4분면 {win}일 합계(계약): Call Q1 {c[0]} · Q2 {c[1]} · Q3 {c[2]} · Q4 {c[3]} | Put Q1 {p[0]} · Q2 {p[1]} · Q3 {p[2]} · Q4 {p[3]}")
    lv = []
    if F['gflip']:
        lv.append(f"감마 플립 {F['gflip'][0]}달러({F['gflip'][1]})")
    if F['bep']:
        lv.append(f"세력 가중 매집원가 BEP {F['bep']}달러")
    if F['mp']:
        lv.append(f"단기 Max Pain {F['mp'][1]}달러({F['mp'][0]} 만기) · 전체 만기 MP {F['mp'][2]}달러")
    if lv:
        L.append(" · ".join(lv))
    if F['rng']:
        L.append(f"1주 1시그마 확률 레인지: {F['rng'][0]}~{F['rng'][1]}달러")
    sup = " · ".join(f"{n} {F[k]}달러" for n, k in (("1차", 'pb1'), ("2차", 'pb2')) if F[k])
    res = " · ".join(f"{n} {F[k]}달러" for n, k in (("1차", 'cw1'), ("2차", 'cw2')) if F[k])
    if sup or res:
        L.append(" | ".join(x for x in (("지지: " + sup) if sup else "", ("저항: " + res) if res else "") if x))
    if F['final']:
        L.append(f"최종 판정 줄: {F['final']}")
    if F['pb_grade']:
        L.append(f"눌림목·분배 경보 등급: {F['pb_grade']}")
    if F['synth']:
        L.append(f"합성 공매도 종합 판정: {F['synth']}")
    return L


def build_checks(F, ws):
    C = [(f"레짐 {k}", v) for k, v in sorted(F['regs'].items())]
    if F['phase']:
        C += [("국면 상승", F['phase'][0]), ("국면 하락", F['phase'][1]), ("국면 횡보", F['phase'][2])]
    for typ in ('Call', 'Put'):
        q = F['quad'].get((typ, ws))
        if q:
            C += [(f"{typ} Q{i + 1} {ws}일", q[i]) for i in range(4)]
    if F['gflip']:
        C.append(("감마 플립", F['gflip'][0]))
    if F['bep']:
        C.append(("가중 BEP", F['bep']))
    if F['mp']:
        C.append(("단기 Max Pain", F['mp'][1]))
    if F['rng']:
        C += [("1시그마 하단", F['rng'][0]), ("1시그마 상단", F['rng'][1])]
    return C


# ------------------------------------------------------------------------------
# 4. 분할 프롬프트 (각 파일이 단독으로 실행 가능하도록 규칙·카드·해당 데이터 포함, AI 종류 무관 문구)
# ------------------------------------------------------------------------------
RULES = """[작성 지시 — EWY 옵션 데이터북 해설 · 파트 {k}/3 ({title})]
당신은 옵션 미시구조 데이터를 개인 투자자가 이해할 수 있는 쉬운 한국어로 풀어 주는 파생상품 애널리스트입니다.
아래 데이터는 파이썬 엔진이 계산과 판정까지 끝낸 결과입니다. 다시 계산하거나 표를 새로 만들 필요가 없습니다.

[규칙]
1. 수치는 아래 데이터의 값을 그대로 인용합니다. 데이터에 없는 값을 직접 계산해 쓰면 수치 뒤에 '(계산)'을 붙입니다. 계약은 '만기일 행사가 Call/Put'(예: 2026-11-20 150 Put)으로 적습니다.
2. 답은 이 대화창에 일반 텍스트로만 씁니다. 파일·HTML·캔버스·코드 실행·표(마크다운 표 포함)는 쓰지 않습니다. 형식은 제목(##, ###), 글머리표(-), 굵게(**)만 씁니다.
3. 달러 기호와 LaTeX 수식 기호를 쓰지 않습니다. 가격은 '159.83달러', 변화는 '+3.04%', '+2.50%p', 지수는 '5,871pt', 주가는 '225,600원'처럼 씁니다.
4. 분량은 한글 약 {chars:,}자(±20%)입니다. 이번 파트의 목차만 쓰고, 마지막 줄에 '— 파트 {k}/3 끝 —'을 쓰고 멈춥니다. 같은 수치·문장을 되풀이하지 않습니다.
5. 각 항목은 '📖 독해 가이드'(표가 말하는 것, 1~3문장) 다음에 '💡 해설 & 실전 판단'(조건 -> 행동 -> 무효화 가격 순서, 근거 수치는 괄호)을 씁니다.
6. 국면 확률은 현재 상태 지표(예측 아님), 급락 위험도는 과거 빈도입니다. 신호 신뢰도표에서 반영이 '참고'이거나 판정이 '약함·불확실'·'기간 의존'인 신호는 결론의 단독 근거로 쓰지 않습니다. 레짐과 국면이 엇갈리면 '국면 = 가격 추세 상태, 레짐 = 옵션 수급 해석'으로 구분합니다.
7. 목차의 제목 줄(##·### 과 ①②·★ 번호)은 그대로 씁니다. 프로그램이 이 제목을 보고 각 해설을 해당 데이터 표 바로 아래에 붙여 최종 보고서를 만듭니다.

[쉬운 말 번역 — 처음 나올 때 괄호로 함께 표기]
Call Q1 = 상승 연료 · Call Q2 = 머리 위 천장(커버드콜) · Put Q2 = 바닥 방석(풋 매도) · Put Q1 = 하락 시한폭탄(롱풋) · 근월-원월 = 단기 응급실 경보등 · 25D 스큐 = 하방 공포 온도계 · 25D 버터플라이 = 급등락 지진계 · 감마 플립 = 딜러가 방어군(+감마)에서 가속군(-감마)으로 바뀌는 경계선 · 바나·참 = IV 안정과 시간 경과만으로 딜러가 되사는 물량 · 합성 공매도 본대(Deep ITM Put) = 딜러에게 대리 공매도를 강제하는 내가격 풋 · 매집원가 BEP = 세력의 본전선 · RND 레인지 = 옵션 가격에 담긴 1주 확률 범위
"""

TOC = {
    1: ("섹션 0~1", """[이번 파트(1/3) 목차 — 아래 제목 줄(##·###)을 번호까지 그대로 쓰고, 각 제목 아래에 내용을 쓰십시오]
- 첫 줄: "[기준일] 1순위 레짐(확률) | 국면(확률) · 급락 위험도 | EWY 종가" 한 줄 (핵심 수치 카드 값 사용)
## 섹션 0. 분석 모델 개요
### ① 분석 시계와 핵심 파라미터
### ② 이 Tier의 강점과 약점(한계), 활용 목적
### ③ 장중 틱 없이 수급을 추정한 방법 — 월가 4단계 파이프라인(고정 괴리율 IV 보간, OI×IV 4분면 부호 추론, 풋-콜 패리티 합성선물, 바나·참)과 쉬운 말 번역
## 섹션 1. 레짐 판독과 최근 {traj}영업일 수급 궤적
### ① (1-1) 레짐 4개 확률과 1·2순위, 국면 판정·급락 위험도
### ② (1-2)·(1-3) 궤적표: Call Q1 증감, Put Q2 vs Put 청산(Q3+4), {ws}D 합계와 {wl}D 합계의 이월 착시 — (6-1) 일별 지표로 확인
### ③ 정면충돌 행사가와 단기 Max Pain 이동
### ④ (1-4)·(1-5) 눌림목·분배 징후 진단 (판정 문구가 국면과 어긋나 보이면 그 이유를 짚을 것)
### ⑤ 국면 판정·급락 위험도 (상태 지표와 과거 빈도의 차이)"""),
    2: ("섹션 2", """[이번 파트(2/3) 목차 — 아래 제목 줄(##·###)을 번호까지 그대로 쓰고, 각 제목 아래에 내용을 쓰십시오]
## 섹션 2. 세부 미시구조 해부
### ① 변동성 곡면(근월·중기·원월 IV, 근월-원월, 25D 스큐, 버터플라이) 추세와 주가와의 선행 다이버전스
### ② 4분면 수급 진위: (2-1) Call 상위, (2-2) Put 증가, (2-3) Put 청산, (2-4) 합성 공매도 본대·매집당시주가·매집원가 BEP
- (2-1)~(2-4)를 한 세트로 해설. (2-4)는 1선·2선 물량과 딜러 대리 공매도 주식 수, BEP 대비 손익 포위, 청산으로 풀린 숏커버를 짚을 것
### ③ 감마 지형도: Call Wall·Put Wall, 순OI 부호가 바뀌는 피벗 행사가
### ④ 당일 미결산 레이더 + ④-B 전일 기습 계약의 OI 안착 + ⑤ 클러스터를 한 세트로
- 보조: (6-2) 계약 패널·(6-3) 행사가 패널로 핵심 포지션의 형성 시점과 벽 이동을 확인 (패널을 옮겨 적지 말고 근거 수치로만 인용)"""),
    3: ("섹션 3~5", """[이번 파트(3/3) 목차 — 아래 제목 줄(##·###)을 번호까지 그대로 쓰고, 각 제목 아래에 내용을 쓰십시오]
## 섹션 3. 실전 종합 판정과 플레이북
### ① (3-1) 회귀 관계식과 가격 트리거 환산
### ② (3-2) 눌림목 단계표 (표에 적힌 순서와 '현가 위' 표시를 그대로 따를 것)
### ③ (3-3) 기습 풋 공식과 양방향 플레이북: 1) 상방 플레이북 2) 하방 손절·헤지 데드라인 3) 만기일 체크리스트
## 섹션 4. 비판적 검증
### ① 5대 구조적 한계점: 가짜 IV 필터 통계, 부호 역전 계약, 초외가격 비중, 단기 vs 장기 다이버전스, 1 - R제곱, 상·하방 반증 트리거
### ② 신호 신뢰도표의 '참고' 신호 한계와 (6-1) 이상치 점검·(6-4) 채점으로 본 1시그마 범위 신뢰도
## 섹션 5. 30초 실전 요약
### ★ 우선 원칙: 최종 판정 줄과 신호 신뢰도표를 우선 근거로 한 결론
### ① 1단계 궤적
### ② 2단계 징후·눌림목 타점
### ③ 3단계 미결산·기습 풋 타깃
### ④ 4단계 실전 3중 체크
### ⑤ 5단계 합성 공매도 5대 포인트
### ⑥ 6단계 4대 파이프라인 전일 대비 변화와 최종 매매 실행 명령
- 맨 끝에 투자 책임 문구 한 줄"""),
}


def build_part_prompts(book, F, stem):
    ws, wl, traj = book['ws'], book['wl'], book['traj']
    card = "[핵심 수치 카드 — 파이썬이 데이터북에서 자동 추출. 인용할 때 이 값을 기준으로 삼으십시오]\n" + \
           "\n".join("- " + x for x in card_lines(F, ws, wl))
    short_meta = f"[기준 정보] 기준일 {F['date']} · {F['tier']}"
    s6 = book['sub6']
    data = {
        1: book['meta'] + book['sec'].get(1, []) + s6.get('head', []) + s6.get('6-1', []),
        2: book['sec'].get(2, []) + s6.get('6-2', []) + s6.get('6-3', []),
        3: book['sec'].get(3, []) + book['sec'].get(4, []) + book['sec'].get(5, []) + s6.get('6-4', []),
    }
    out = []
    for k in (1, 2, 3):
        title, toc = TOC[k]
        txt = [RULES.format(k=k, title=title, chars=PART_CHAR_TARGET[k]).strip(),
               toc.format(traj=traj, ws=ws, wl=wl),
               card]
        if k > 1:
            txt.append(short_meta)
        txt.append(f"[데이터 — 파트 {k}/3에 필요한 부분만 발췌 (원본: {stem}.txt)]\n" + ai_text(data[k]))
        txt.append(f"[지금 할 일] 위 목차의 파트 {k}/3만 작성하고 '— 파트 {k}/3 끝 —'으로 마치십시오. "
                   f"표·파일·HTML·달러 기호는 쓰지 않습니다.")
        out.append("\n\n".join(txt) + "\n")
    return out


# ------------------------------------------------------------------------------
# 5. HTML (표 뷰어 · 최종 보고서)
# ------------------------------------------------------------------------------
CSS = """
:root{--bg:#fff;--fg:#1c1c1e;--mut:#6b7280;--ln:#d9dde3;--hd:#f1f3f6;--card:#fff8e1;--cardln:#f1d27a;--g:#f4f7fb}
@media (prefers-color-scheme:dark){:root{--bg:#121315;--fg:#e8e8ea;--mut:#9aa0a6;--ln:#33363b;--hd:#1d2024;--card:#2a2416;--cardln:#6b5a26;--g:#1a1e24}}
body{margin:0;padding:12px;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,"Noto Sans KR","Malgun Gothic",sans-serif;word-break:keep-all;overflow-wrap:anywhere}
h1{font-size:18px;margin:4px 0 8px}h2{font-size:16px;margin:16px 0 6px}h3{font-size:15px;margin:14px 0 4px}h4{font-size:14px;margin:12px 0 4px}
details{border-top:1px solid var(--ln);padding:6px 0}summary{font-weight:700;cursor:pointer;padding:4px 0}
.note,.meta{color:var(--mut);font-size:13px}.t{white-space:pre-wrap;font-size:13px}.g{background:var(--g);border-left:3px solid var(--mut);padding:4px 8px;margin:4px 0;font-size:12.5px}
.card{background:var(--card);border:1px solid var(--cardln);border-radius:8px;padding:8px 10px;margin:8px 0;font-size:13.5px}.card ul{margin:4px 0;padding-left:18px}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:6px 0 10px}table{border-collapse:collapse;font-size:12px;white-space:nowrap}
th,td{border:1px solid var(--ln);padding:3px 6px;vertical-align:top}th{background:var(--hd);position:sticky;top:0}
table:not(.nh) td:first-child,table:not(.nh) th:first-child{position:sticky;left:0;background:var(--bg)}table:not(.nh) th:first-child{background:var(--hd)}
td.n{text-align:right;font-variant-numeric:tabular-nums}td.w{white-space:normal;min-width:15em}
li{margin:2px 0}p{margin:6px 0}
"""


def _page(title, body):
    return ("<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>")


def _table_html(hdr, rows):
    ncol = max([len(hdr or [])] + [len(r) for r in rows] + [1])
    out = ["<div class='tw'><table" + ("" if hdr else " class='nh'") + ">"]
    if hdr:
        out.append("<thead><tr>" + "".join("<th>" + html.escape(c) + "</th>" for c in hdr) + "</tr></thead>")
    out.append("<tbody>")
    for r in rows:
        r = r + [''] * (ncol - len(r))
        tds = []
        for c in r:
            cls = [x for x, ok in (('n', NUM_CELL_RE.match(c) is not None), ('w', len(c) > 28)) if ok]
            attr = (" class='" + " ".join(cls) + "'") if cls else ""
            tds.append("<td" + attr + ">" + html.escape(c) + "</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _lines_html(lines):
    out = []
    for b in parse_blocks(lines):
        if b[0] == 'table':
            out.append(_table_html(b[1], b[2]))
            continue
        for l in b[1]:
            if SEP_RE.match(l) or not l.strip():
                continue
            st = l.strip()
            m = re.match(r'^(#{2,4})\s+(.*)$', st)
            if m:
                lvl = min(4, len(m.group(1)) + 1)
                out.append(f"<h{lvl}>" + html.escape(m.group(2)) + f"</h{lvl}>")
            else:
                out.append("<div class='" + ("g" if '📌' in st else "t") + "'>" + html.escape(l.rstrip()) + "</div>")
    return "\n".join(out)


def _card_html(F, ws, wl):
    return ("<div class='card'><b>핵심 수치 카드</b> (파이썬 자동 추출)<ul>" +
            "".join("<li>" + html.escape(x) + "</li>" for x in card_lines(F, ws, wl)) + "</ul></div>")


def viewer_inner(book):
    parts = ["<details open><summary>기준 정보 · Tier 프로필</summary>" + _lines_html(book['meta']) + "</details>"]
    for num in sorted(book['sec']):
        lines = book['sec'][num]
        title = lines[0][3:].strip() if lines else f"[섹션 {num}]"
        parts.append("<details" + (" open" if num <= 5 else "") + "><summary>" + html.escape(title) +
                     "</summary>" + _lines_html(lines[1:]) + "</details>")
    return "\n".join(parts)


def count_tables(book):
    return sum(1 for num in book['sec'] for b in parse_blocks(book['sec'][num]) if b[0] == 'table')


def md_to_html(md):
    out, stack = [], []

    def close(to=0):
        while len(stack) > to:
            out.append("</" + stack.pop() + ">")

    def inline(s):
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(s))

    for raw in md.replace('\r\n', '\n').split('\n'):
        line = raw.rstrip()
        if not line.strip():
            close()
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line.strip())
        if m:
            close()
            lvl = min(4, max(2, len(m.group(1))))
            out.append(f"<h{lvl}>" + inline(m.group(2)) + f"</h{lvl}>")
            continue
        if re.match(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$', line):
            close()
            out.append("<hr>")
            continue
        m = re.match(r'^(\s*)([-*•]|\d+[.)])\s+(.*)$', line)
        if m:
            level = 1 if len(m.group(1).expandtabs(4)) < 2 else 2
            typ = 'ol' if m.group(2)[0].isdigit() else 'ul'
            close(level)
            if len(stack) == level and stack[-1] != typ:
                close(level - 1)
            while len(stack) < level:
                out.append("<" + typ + ">")
                stack.append(typ)
            out.append("<li>" + inline(m.group(3)) + "</li>")
            continue
        close()
        out.append("<p>" + inline(line.strip()) + "</p>")
    close()
    return "\n".join(out)


# ------------------------------------------------------------------------------
# 6. 생성 후 자동 검산
# ------------------------------------------------------------------------------
def verify_commentary(md_all, F, book_text, ws):
    L = []
    n_dollar = md_all.count('$')
    L.append(f"- 달러 기호($): {n_dollar}개" + (" (정상)" if n_dollar == 0 else " -> 보고서 HTML에서는 '달러'로 바꿔 표시"))
    n_tbl = len(re.findall(r'^\s*\|.*\|\s*$', md_all, flags=re.M)) + md_all.lower().count('<table')
    L.append(f"- 표 형식 줄: {n_tbl}개" + (" (정상)" if n_tbl == 0 else " (표 금지 규칙 위반)"))
    plain = md_all.replace(',', '')

    def has(v):
        v = v.replace(',', '').lstrip('+-')
        cands = {v, v.rstrip('0').rstrip('.') if '.' in v else v}     # 63.0 -> 63 도 인정
        return any(re.search(r'(?<![\d.])' + re.escape(c) + r'(?![\d])', plain) for c in cands if c)

    checks = build_checks(F, ws)
    miss = [f"{lab}({v})" for lab, v in checks if not has(v)]
    L.append(f"- 핵심 수치 인용: {len(checks) - len(miss)}/{len(checks)}개 확인" +
             (" · 본문에 없음(오기·누락 여부 확인): " + ", ".join(miss) if miss else ""))
    if F['risk'] and not re.search(r'위험도[^\n]{0,12}' + F['risk'][1], md_all):
        L.append(f"- 급락 위험도 등급 [{F['risk'][1]}]이 본문에서 확인되지 않음")
    data_plain = book_text.replace(',', '').replace('$', '')
    sus = []
    for m in re.finditer(r'([+\-]?\d[\d,]*\.?\d*)\s*(달러|%p|%|계약|주|pt|원)', md_all):
        num = m.group(1).replace(',', '').lstrip('+-')
        if len(num.replace('.', '')) < 3 or '계산' in md_all[m.end():m.end() + 12]:
            continue
        num2 = num.rstrip('0').rstrip('.') if '.' in num else num
        if num not in data_plain and num2 not in data_plain:
            sus.append(m.group(0))
    uniq = list(dict.fromkeys(sus))
    L.append(f"- 데이터북에서 찾을 수 없고 '(계산)' 표시도 없는 수치: {len(uniq)}건" +
             (" -> " + ", ".join(uniq[:20]) + (" …" if len(uniq) > 20 else "") if uniq else " (정상)"))
    return L




# ------------------------------------------------------------------------------
# 7. 최종 보고서 — PC 보고서 양식
#    섹션 0~5를 <details open>으로, 소제목(①②…)마다 데이터북 표를 넣고 바로 아래에 AI 해설을 붙입니다.
#    표는 데이터북에서 파이썬이 그대로 옮기므로(달러 기호 -> '달러') AI가 수치를 옮겨 적다 틀릴 일이 없습니다.
# ------------------------------------------------------------------------------
REPORT_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Malgun Gothic", sans-serif; line-height: 1.65; margin: 12px; color: #111827; background: #f8fafc; font-size: 14px; }
details { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 14px; padding: 12px; }
summary { font-weight: 700; font-size: 16px; cursor: pointer; color: #0f172a; padding: 4px 0; }
h3, h4 { color: #1e3a8a; margin-top: 16px; margin-bottom: 8px; border-left: 4px solid #1e3a8a; padding-left: 8px; }
table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12.5px; display: block; overflow-x: auto; white-space: nowrap; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; text-align: left; }
th { background: #f1f5f9; font-weight: 700; color: #0f172a; }
tr:nth-child(even) { background: #f8fafc; }
ul, ol, p { margin: 6px 0; }
td.w { white-space: normal; min-width: 11em; }
td.ww { white-space: normal; min-width: 22em; }
"""

REPORT_TITLE = "EWY 옵션 미시구조 4대 전략 정밀 판독 보고서"
DISCLAIMER = "본 보고서는 옵션 미시구조 정량 데이터에 기반한 통계적 분석 자료이며, 최종 투자 판단과 책임은 투자자 본인에게 있습니다."

DEFAULT_SEC_TITLES = {
    0: "0. [분석 모델 개요] 선택된 월가 퀀트 계층({tier}) 및 월가 4단계 파이프라인 작동 원리 브리핑",
    1: "1. 월가 4대 전략 레짐 판독 및 최근 {traj}영업일 수급 모멘텀 궤적 해부 (파이프라인 4단계 사령탑)",
    2: "2. 세부 미시구조 데이터 정밀 해부 (파이프라인 1단계 곡면 역산 · 2단계 비대칭 수급 · 3단계 합성공매도 및 감마 지형)",
    3: "3. 실전 종합 판정 · 월가 표준 5~6단계 눌림목 조견표 · 기습 풋(원인 ①·②) 완전판 하락폭 공식 및 양방향 플레이북",
    4: "4. [비판적 검증] AI 추론의 5대 구조적 한계점 및 반대 시나리오(Devil's Advocate) 스트레스 테스트",
    5: "5. [투자자용 30초 실전 판독 요약 & 최종 정리] 핵심 3단계 요약 · '실전 3중 체크법' · '합성 공매도 5대 포인트' · '월가 4대 파이프라인 최종 실행 사령탑'",
}

# (기호, 소제목, 넣을 데이터북 조각, 첫 조각 제목도 h4로 보일지)
LAYOUT = {
    0: [('①', "분석 시계 및 핵심 메타데이터 파라미터", ['meta'], False),
        ('②', "{tier_short}의 핵심 강점 및 약점(한계)", ['?meta-tier'], False),
        ('③', "장중 틱(Tick) 부재를 극복한 '월가 4단계 실전 파이프라인' 작동 원리 및 쉬운 일상 언어(Easy-Quant) 동시 번역", [], False)],
    1: [('①', "기준일({date}) 4대 전략 레짐 확률 요약표 및 국면 판정·급락 위험도 ([섹션 1-1])", ['1-1'], False),
        ('②', "최근 {traj}영업일 레짐 및 4분면(Q1~Q4, {ws}D 기준) 수급 추세 궤적표 ([섹션 1-2] & [섹션 1-3])", ['1-2', '1-3'], False),
        ('③', "현재 정면충돌 행사가 및 단기 Max Pain 이동 역학", [], False),
        ('④', "상승장 속 단기 눌림목(Pullback) & 고점 분배 4대 사전 징후 진단표 ([섹션 1-4]{and15})", ['1-4', '1-5'], False),
        ('⑤', "[V4.4 국면 판정 · 급락 위험도] 상태 지표와 레짐 해석의 정밀 구분 ([섹션 1-1] 하단)", [], False)],
    2: [('①', "[파이프라인 1단계] 변동성 곡면(Term Structure · 25D Skew · Butterfly) 추세 및 선행 다이버전스 해부 ([섹션 2-①])", ['2-①'], False),
        ('②', "[파이프라인 2·3단계] OI × IV 4분면 수급 진위 및 '합성 공매도 본대(Deep ITM Put) · 매집당시주가 · 진성 매집원가 BEP' 정밀 해부 ([섹션 2-②])", ['2-②'], False),
        ('③', "[파이프라인 3단계] 딜러 감마(Gamma) 지형도의 중심축 이동과 네거티브 감마 트랩 분석 ([섹션 2-③])", ['2-③'], False),
        ('④', "[파이프라인 2단계] 당일({date}) 미결산 기습 거래량 레이더, 전일 기습 거래의 공식 OI 안착 검증 및 단기 만기 클러스터 해부 ([섹션 2-④, ④-B, ⑤])", ['2-④', '2-⑤'], True)],
    3: [('①', "시계열 상관·회귀 관계식 및 시나리오별 핵심 가격 트리거 환산표 ([섹션 3-1])", ['3-1'], False),
        ('②', "월가 표준 5~6단계 눌림목 분할매수 및 감마 진공 하단 조견표 ([섹션 3-2])", ['3-2'], False),
        ('③', "당일 기습 풋(Ambush Put) '원인 ① × 원인 ②' 진단 및 완전판 하락폭 공식 조견표 ([섹션 3-3])", ['3-3'], False)],
    4: [('①', "AI 추론 5대 구조적 한계점 및 정량 스트레스 테스트 요약표 ([섹션 4])", ['4'], False),
        ('②', "[필수 검증] 신호 신뢰도표 한계 명시 및 [섹션 6] 이력 요약 블록(이상치 점검 · 1시그마 채점) 교차 검증", [], False)],
    5: [('★', "[우선 원칙 선언] V4.4 최종 판정 컨트롤 타워", ['5-final'], False),
        ('①', "1단계 ([섹션 1-2] {traj}영업일 궤적표 확인 — 10초)", [], False),
        ('②', "2단계 ([섹션 1-4] 단기 눌림목 4대 징후 & [섹션 3-2] 5단계 눌림목 하락폭 타점 확인 — 10초)", [], False),
        ('③', "3단계 ([섹션 2-④, ⑤] 당일 미결산 레이더 & [섹션 3-3] 기습 풋 원인 ①·② 완전판 하락폭 공식 확인 — 10초)", [], False),
        ('④', "4단계: 눌림목 미탐지 사각지대(25%) 보완 '실전 3중 체크법' 원리 해설 및 당일 체크 결과 요약표", ['5-4'], False),
        ('⑤', "5단계: '합성 공매도 본대(Deep ITM Put)'의 지배력 및 숏커버 전환을 추적하는 5대 핵심 독해 포인트 실시간 진단 및 신호 신뢰도표", ['5-5'], False),
        ('⑥', "6단계: '월가 4대 퀀트 파이프라인' 전일(T-1) 대비 1일 변화 통합 계측 요약표 및 투자자 활용 매뉴얼", ['5-6'], False)],
}
PART_SECS = {1: (0, 1), 2: (2,), 3: (3, 4, 5)}
_SYM = (('Δ', '델타'), ('Γ', '감마'), ('σ', '시그마'), ('²', '제곱'), ('≥', '>='), ('≤', '<='))
_GLYPH = '①②③④⑤⑥⑦⑧⑨'
_esc = html.escape


def _fix(s):
    """데이터북 글자 정리: 달러 기호 -> '달러', 그리스 문자 -> 한글, 정렬용 공백 제거"""
    s = dollar_to_text(str(s).strip())
    for a, b in _SYM:
        s = s.replace(a, b)
    s = re.sub(r' {2,}', ' ', s)
    return re.sub(r'\(\s+', '(', s)


def _tier_short(tier):
    m = re.match(r'^(.*?)\s*\[([^|\]]+)', tier or '')
    if not m:
        return (tier or '').strip() or 'Tier'
    pre, first = m.group(1).strip(), m.group(2).strip()
    return f"{pre} {first}" if re.fullmatch(r'Tier\s*\d', pre) else pre


def _split_by(lines, rx, first='_pre'):
    out, key = {}, first
    for l in lines:
        m = re.match(rx, l)
        if m:
            key = m.group(1)
        out.setdefault(key, []).append(l)
    return out


def _pieces(book):
    """데이터북 섹션을 보고서 소제목 단위 조각으로 나눔"""
    tier_rx = re.compile(r'^\s*•\s*Tier (핵심 강점|약점|활용 목적)')
    S = book['sec']
    P = {'meta': [l for l in book['meta'] if not tier_rx.match(l)],
         'meta-tier': [l for l in book['meta'] if tier_rx.match(l)]}
    P.update(_split_by(S.get(1, [])[1:], r'^###\s*\((1-\d)\)'))
    P.update({'2-' + k: v for k, v in _split_by(S.get(2, [])[1:], r'^###\s*([①②③④⑤])').items()})
    P.update(_split_by(S.get(3, [])[1:], r'^###\s*\[섹션\s*(3-\d)\]', first='3-1'))
    P['4'] = S.get(4, [])[1:]
    P.update({'5-' + k: v for k, v in _split_by(S.get(5, [])[1:], r'^\s{0,2}•\s*(\d)단계').items()})
    # 5단계 4) 안의 최종 판정 두 줄은 ★(우선 원칙)으로 옮김
    fin, rest = [], []
    for l in P.get('5-4', []):
        (fin if re.match(r'^\s*-\s*\[(?:최종 통합 판정|V4\.4 최종 판정)', l) else rest).append(l)
    if fin:
        P['5-4'], P['5-final'] = rest, sorted(fin, key=lambda l: 0 if 'V4.4' in l else 1)
    return P


def _section_titles(head, tier, traj):
    T = {}
    for l in head or []:
        m = re.match(r'^##\s*([0-5])\.\s*(.+)$', l.strip())
        if m:
            T[int(m.group(1))] = f"{m.group(1)}. " + m.group(2).replace('[신설] ', '').strip()
    return {k: T.get(k) or DEFAULT_SEC_TITLES[k].format(tier=tier, traj=traj) for k in range(6)}


# ---- 데이터북 조각 -> HTML ----------------------------------------------------
def _cell(c):
    return '<br>'.join(_esc(_fix(x)) for x in str(c).split('\n'))


def _td(c, wrap=True):
    """열이 적은 표의 긴 글 칸만 줄바꿈 허용 (숫자 위주의 넓은 표는 첨부 양식처럼 한 줄 + 가로 스크롤)"""
    n = max(len(_fix(x)) for x in str(c).split('\n')) if wrap else 0
    return ('<td class="ww">' if n > 80 else '<td class="w">' if n > 30 else '<td>') + _cell(c) + '</td>'


def _table(hdr, rows):
    out = ['<table>']
    if hdr:
        out.append('<thead><tr>' + ''.join('<th>' + _cell(c) + '</th>' for c in hdr) + '</tr></thead>')
    ncol = max([len(hdr or [])] + [len(r) for r in rows] + [1])
    out.append('<tbody>')
    if not rows:
        out.append(f'<tr><td colspan="{ncol}">해당 계약 없음</td></tr>')
    for r in rows:
        r = list(r) + [''] * (ncol - len(r))
        out.append('<tr>' + ''.join(_td(c, ncol <= 7) for c in r) + '</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


_QCELL = re.compile(r'^(Q\d)\[([^\]]+)\]\s*(.+)$')


def _table_block(hdr, rows):
    """머리행 없는 표는 '• 이름 : 값' 첫 칸을 나누고, 4분면 요약·가격 트리거 표는 머리행을 붙임"""
    if hdr is None and rows:
        first = [re.match(r'^[•\-]?\s*(.+?)\s*:\s*(.+)$', r[0].strip()) for r in rows]
        if all(first):
            rows = [[m.group(1), m.group(2)] + list(r[1:]) for m, r in zip(first, rows)]
            qs = [[_QCELL.match(c.strip()) for c in r[2:]] for r in rows]
            q1 = [_QCELL.match(r[1].strip()) for r in rows]
            if all(q1) and all(all(q) for q in qs) and len({len(q) for q in qs}) == 1:
                hdr = ['옵션 구분 및 집계 시계'] + [q1[0].group(1)] + [q.group(1) for q in qs[0]]
                rows = [[r[0], f"{a.group(3)} ({a.group(2)})"] + [f"{q.group(3)} ({q.group(2)})" for q in qq]
                        for r, a, qq in zip(rows, q1, qs)]
            elif all(r[1].strip().startswith('상관계수') for r in rows):
                ncol = max(len(r) for r in rows)
                hdr = (['회귀 대상', '상관계수 · R제곱 · 미설명 고유리스크', '탄력성', '회귀기울기'] + [''] * ncol)[:ncol]
            elif all(r[1].strip().startswith('EWY') for r in rows):
                names = ['시나리오별 핵심 가격 트리거 구분', 'EWY 타깃 (현가괴리율)', '옵션 OI 및 핵심 미시구조 근거',
                         '내재 KOSPI', '내재 삼성전자', '내재 원/달러 환율']
                ncol = max(len(r) for r in rows)
                pref = {1: r'^EWY\s*', 3: r'^KOSPI\s*', 4: r'^삼성전자\s*', 5: r'^환율\s*'}
                rows = [[re.sub(pref.get(j, r'^$'), '', c.strip()) for j, c in enumerate(list(r) + [''] * (ncol - len(r)))]
                        for r in rows]
                hdr = names[:ncol] + [''] * max(0, ncol - len(names))
    return _table(hdr, rows)


def _blocks(lines):
    """parse_blocks + '머리행만 있고 행이 없는 표'를 빈 표로 인식"""
    out = []
    for b in parse_blocks(lines):
        if b[0] != 'text':
            out.append(b)
            continue
        buf, ls, i = [], b[1], 0
        while i < len(ls):
            l = ls[i]
            if l.count('|') >= 2 and i + 1 < len(ls) and SEP_RE.match(ls[i + 1]) and not SEP_RE.match(l):
                if buf:
                    out.append(('text', buf))
                    buf = []
                out.append(('table', _cells(l), []))
                i += 2
                continue
            buf.append(l)
            i += 1
        if buf:
            out.append(('text', buf))
    return out


def _kv_html(st):
    """'이름 : 값' -> <strong>이름</strong>: 값"""
    m = re.match(r'^(\S{0,3}\s*\[[^\]]{1,140}\])\s*[:：]\s*(.*)$', st) or \
        re.match(r'^(.{1,70}?)\s*[:：]\s+(.+)$', st) or re.match(r'^(.{1,70}?)\s*[:：]\s*$', st)
    if m and not re.search(r'\d$', m.group(1)) and '(' not in m.group(1)[-1:]:
        val = (m.group(2) or '') if m.lastindex and m.lastindex >= 2 else ''
        return '<strong>' + _esc(_fix(m.group(1))) + '</strong>: ' + _esc(_fix(val)) if val else \
               '<strong>' + _esc(_fix(m.group(1))) + '</strong>'
    return _esc(_fix(st))


def _list_html(items):
    """[(들여쓰기, html)] -> 중첩 <ul>"""
    leads = sorted({a for a, _ in items})
    out, depth = [], 0
    for lead, h in items:
        lvl = min(leads.index(lead) + 1, depth + 1)
        if lvl > depth:
            out.append('<ul>')
            depth += 1
        else:
            out.append('</li>')
            while depth > lvl:
                out.append('</ul></li>')
                depth -= 1
        out.append('<li>' + h)
    if depth:
        out.append('</li>')
        while depth > 1:
            out.append('</ul></li>')
            depth -= 1
        out.append('</ul>')
    return ''.join(out)


def _r_generic(lines, show_first_heading=True):
    out, items, seen_head = [], [], False

    def flush():
        if items:
            out.append(_list_html(items))
            items.clear()

    for b in _blocks(lines):
        if b[0] == 'table':
            flush()
            out.append(_table_block(b[1], b[2]))
            continue
        for l in b[1]:
            st = l.strip()
            if not st or SEP_RE.match(l):
                flush()
                continue
            if st.startswith('📌'):
                continue
            m = re.match(r'^#{2,4}\s*(.+)$', st)
            if m:
                flush()
                if seen_head or show_first_heading:
                    out.append('<h4>' + _esc(_fix(m.group(1))) + '</h4>')
                seen_head = True
                continue
            mb = re.match(r'^([•\-·])\s*(.*)$', st)
            if mb or re.match(r'^(\d\)|[①-⑨])\s', st):
                lead = len(l) - len(l.lstrip(' '))
                items.append((lead, _kv_html(mb.group(2) if mb else st)))
                continue
            flush()
            out.append('<p>' + _kv_html(st) + '</p>')
    flush()
    return '\n'.join(out)


def _r_meta(lines, date):
    rows = []
    for l in lines:
        m = re.match(r'^\s*•\s*(.+?)\s*:\s*(.+)$', l)
        if m:
            rows.append([m.group(1), m.group(2)])
    if not rows:
        return _r_generic(lines)
    return _table(['메타데이터 구분', f'기준일({date}) 적용 파라미터 및 계측 수치'], rows)


def _r_regime(lines, date):
    rows, regs, i, ls = [], [], 0, [l for l in lines if l.strip() and not SEP_RE.match(l)]
    rank = {}
    for l in ls:
        m = re.match(r'^\s*•\s*(\d순위 [^:]+?)\s*:\s*(레짐 [ABCD])', l)
        if m:
            rank[m.group(2)] = m.group(1)

    def subs(j):
        out = []
        while j < len(ls) and re.match(r'^\s*-\s', ls[j]):
            out.append(ls[j].strip()[1:].strip())
            j += 1
        return out, j

    while i < len(ls):
        l = ls[i].strip()
        m = re.match(r'^\[(레짐 [ABCD])\]\s*(.+?)\s*\|\s*산출 확률:\s*([\d.]+)%', l)
        if m:
            sub, i = subs(i + 1)
            detail = ' / '.join(re.sub(r'^핵심 수치\s*:\s*', '', s) for s in sub)
            regs.append([f"[{m.group(1)}] {m.group(2)}", float(m.group(3)), m.group(1), detail])
            continue
        m = re.match(r'^\[V4\.4 국면 판정\]\s*(.*)$', l)
        if m:
            sub, i = subs(i + 1)
            kv = dict((a.strip(), b.strip()) for a, b in (s.split(':', 1) for s in sub if ':' in s))
            prob = kv.get('국면 확률', '')
            p1, _, p2 = prob.partition('->')
            rows.append(["[V4.4 국면 판정] 현재 가격 추세 상태 인식 지표", p1.strip(), p2.strip() or '-',
                         ' / '.join([m.group(1).strip()] + [f"{k}: {v}" for k, v in kv.items() if k != '국면 확률'])])
            continue
        m = re.match(r'^\[V4\.4 급락 위험도\]\s*(.*?)(?:->\s*(평균\s*[\d.]+\s*=\s*\[(.)\]))?\s*$', l)
        if m:
            sub, i = subs(i + 1)
            grade = m.group(3) or ''
            rows.append(["[V4.4 급락 위험도] 향후 10영업일 내 -5% 이상 하락 과거 빈도 수준 지표", m.group(2) or '-',
                         f"위험 수준 [{grade}]" if grade else '-', ' / '.join([m.group(1).strip()] + sub)])
            continue
        i += 1
    if not regs:
        return _r_generic(lines, show_first_heading=False)
    order = sorted(regs, key=lambda r: -r[1])
    labels = {}
    for n, r in enumerate(order, 1):
        labels[r[2]] = rank.get(r[2]) or f"{n}순위 전략"
    body = [[r[0], f"{r[1]:.1f}%", labels[r[2]], r[3]] for r in order] + rows
    return _table(['구분 / 전략 레짐 명칭', '산출 확률 / 등급', '순위 / 상태', '핵심 정량 수급·가격 근거 및 검증 지표'], body)


def _r_signs(lines, date):
    rows = []
    for l in lines:
        st = l.strip()
        m = re.match(r'^•\s*(종합 눌림목/분배 경보 등급)\s*:\s*(.+)$', st)
        if m:
            v = re.match(r'^(\S*\s*\[[^\]]*\])\s*(.*)$', m.group(2))
            rows.append([m.group(1), v.group(1) if v else m.group(2), v.group(2) if v else ''])
            continue
        m = re.match(r'^(\d\)\s*\[[^\]]+\])\s*:\s*([^|]+?)\s*\|\s*(.+)$', st)
        if m:
            rows.append([m.group(1), m.group(2), m.group(3)])
    if len(rows) < 2:
        return _r_generic(lines, show_first_heading=False)
    return _table(['진단 항목 구분 ([섹션 1-4] 4대 사전 징후)', '점화 상태', f'기준일({date}) 정량 계측 수치 및 세부 판정 근거'], rows)


def _r_limits(lines, date):
    rows, cur = [], None
    for l in lines:
        st = l.strip()
        if not st or SEP_RE.match(l) or st.startswith('📌'):
            continue
        m = re.match(r'^(\d\))\s*(\[.+\])\s*$', st)
        if m:
            cur = [f"{m.group(1)} {m.group(2)}", []]
            rows.append(cur)
            continue
        if cur is not None:
            mm = re.match(r'^[•\-]\s*(.+)$', st)
            cur[1].append('• ' + re.sub(r'\s+:\s+', ': ', mm.group(1) if mm else st))
    if not rows:
        return _r_generic(lines)
    return _table(['구조적 한계점 검증 항목', f'기준일({date}) 정량 계측 및 필터링 통계'], [[a, '\n'.join(b)] for a, b in rows])


def _r_checks(lines, date):
    out, rows = [], []
    for l in lines[1:]:
        st = l.strip()
        m = re.match(r'^([①②③])\s*(\[[^\]]+\])\s*:\s*([^|]+?)\s*\|\s*(.+)$', st)
        if m:
            rows.append([f"{m.group(1)} {m.group(2)}", m.group(3), m.group(4)])
            continue
        m = re.match(r'^-\s*(.+)$', st)
        if m:
            out.append('<p>' + _kv_html(m.group(1)) + '</p>')
    if rows:
        out.append(_table(['실전 3중 체크 항목', '당일 판정', f'기준일({date}) 정량 계측 수치 및 세부 작동 원리'], rows))
    return '\n'.join(out) if out else _r_generic(lines, show_first_heading=False)


def _r_final(lines):
    items = []
    for l in lines:
        m = re.match(r'^\s*-\s*(\[[^\]]+\])\s*:\s*(.+)$', l)
        if not m:
            continue
        head, rest = m.group(1), m.group(2)
        tag = ' — 최우선 결론 근거' if 'V4.4' in head else ' — 보조 참고용'
        v = re.match(r'^(\S*\s*\[[^\]]+\])\s*(.*)$', rest)
        val = ('<strong>' + _esc(_fix(v.group(1))) + '</strong> ' + _esc(_fix(v.group(2)))) if v else _esc(_fix(rest))
        items.append('<li><strong>' + _esc(_fix(head)) + tag + '</strong>: ' + val + '</li>')
    return '<ul>' + ''.join(items) + '</ul>' if items else ''


def _r_points(lines, date):
    """5단계: 독해 포인트 목록 + 신호 신뢰도표"""
    body, tbl = [], []
    for b in _blocks(lines[1:]):
        if b[0] == 'table':
            tbl.append(_table_block(b[1], b[2]))
            continue
        for l in b[1]:
            st = l.strip()
            m = re.match(r'^-\s*\[V4\.4 신호 신뢰도표\]\s*(.*)$', st)
            if m:
                tbl.insert(0, '<h4>[V4.4 신호 신뢰도표]</h4><p>' + _esc(_fix(m.group(1))) + '</p>')
            elif st and not SEP_RE.match(l):
                body.append(l)
    return _r_generic(body) + '\n' + '\n'.join(tbl)


def _r_pipeline(lines, date):
    rows = []
    for l in lines:
        m = re.match(r'^([①②③④])\s*(\[[^\]]+\])\s*:\s*(.+)$', l.strip())
        if m:
            rows.append([f"{m.group(1)} {m.group(2)}", m.group(3)])
    if not rows:
        return _r_generic(lines, show_first_heading=False)
    return _table(['월가 4대 퀀트 파이프라인 단계', f'기준일({date}) 실시간 계측치 및 전일(T-1) 대비 1일 변화'], rows)


_SPECIAL = {'meta': _r_meta, '1-1': _r_regime, '1-4': _r_signs, '4': _r_limits,
            '5-4': _r_checks, '5-5': _r_points, '5-6': _r_pipeline}


def _piece_html(key, lines, date, show_heading):
    if key == '5-final':
        return _r_final(lines)
    if key in _SPECIAL:
        h = ''
        if show_heading and lines and re.match(r'^#{2,4}\s', lines[0].strip()):
            h = '<h4>' + _esc(_fix(lines[0].strip().lstrip('#').strip())) + '</h4>'
        return h + _SPECIAL[key](lines, date)
    return _r_generic(lines, show_first_heading=show_heading)


# ---- AI 답변 나누기 -----------------------------------------------------------
def _heading(line):
    """마크다운 제목(#)·줄 전체 굵게(**…**) -> (수준, 제목 글자). 아니면 None"""
    st = line.strip()
    m = re.match(r'^(#{1,6})\s*(.+?)\s*#*$', st)
    if m:
        lvl, t = len(m.group(1)), m.group(2)
    else:
        m = re.match(r'^(\*\*|__)(.+?)\1\s*[:：]?\s*$', st)
        if not m:
            return None
        lvl, t = 0, m.group(2)
    t = re.sub(r'^(\*\*|__)+|(\*\*|__)+$', '', t.strip()).strip()
    return (lvl, t) if t else None


def _sec_of(h, allowed):
    lvl, t = h
    m = re.match(r'^\[?\s*섹션\s*([0-5])(?![\d\-–])', t) or (re.match(r'^([0-5])\.\s', t) if lvl in (1, 2) else None)
    if m and int(m.group(1)) in allowed:
        return int(m.group(1))
    return None


def _glyph_of(t, sec):
    t = t.strip().lstrip('[').strip()
    if t[:1] in _GLYPH or t[:1] == '★':
        return t[:1]
    m = re.match(r'^([1-9])\uFE0F?\u20E3', t)          # 1️⃣ 같은 숫자 이모지
    if m:
        return _GLYPH[int(m.group(1)) - 1]
    if sec == 1:
        m = re.match(r'^\(?1-([1-5])\)?', t)
        if m:
            return {'1': '①', '2': '②', '3': '②', '4': '④', '5': '④'}[m.group(1)]
    if sec == 3:
        m = re.match(r'^\(?(?:섹션\s*)?3-([1-3])', t)
        if m:
            return _GLYPH[int(m.group(1)) - 1]
    if sec == 5:
        m = re.match(r'^(\d)\s*단계', t)
        if m and 1 <= int(m.group(1)) <= 6:
            return _GLYPH[int(m.group(1)) - 1]
        if t.startswith('우선 원칙') or '최종 판정' in t[:12]:
            return '★'
    return None


def _parse_part(text, part):
    allowed = PART_SECS[part]
    lines = END_MARK_RE.sub('', dollar_to_text(text.replace('\r\n', '\n'))).split('\n')
    head, secs, cur, sub = [], {}, None, None
    for l in lines:
        h = _heading(l)
        s = _sec_of(h, allowed) if h else None
        if s is not None:
            cur, sub = s, None
            secs.setdefault(cur, {'intro': [], 'subs': {}, 'order': []})
            continue
        if cur is None and h and h[0] >= 2 and _glyph_of(h[1], allowed[0]):
            cur = allowed[0]
            secs.setdefault(cur, {'intro': [], 'subs': {}, 'order': []})
        if cur is not None and h:
            g = _glyph_of(h[1], cur)
            if g:
                sub = g
                S = secs[cur]
                if g not in S['subs']:
                    S['subs'][g] = {'title': h[1], 'lines': []}
                    S['order'].append(g)
                continue
        if cur is None:
            head.append(l)
        elif sub is None:
            secs[cur]['intro'].append(l)
        else:
            secs[cur]['subs'][sub]['lines'].append(l)
    # 제목(#) 없이 '① …' 같은 줄로만 나눈 답이면 그 줄을 소제목으로 봄
    for s, S in secs.items():
        if S['subs'] or not S['intro']:
            continue
        intro, sub = [], None
        for l in S['intro']:
            st = l.strip().replace('**', '')
            g = _glyph_of(st, s) if st else None
            if g and len(st) <= 70 and not re.search(r'(다|요|음|니다)[.!]?$', st):
                sub = g
                if g not in S['subs']:
                    S['subs'][g] = {'title': st, 'lines': []}
                    S['order'].append(g)
                continue
            (intro if sub is None else S['subs'][sub]['lines']).append(l)
        S['intro'] = intro
    return head, secs


def _parse_answers(texts):
    A = {'headline': None, 'secs': {}, 'loose': {}, 'tail': None}
    for part, t in enumerate(texts, 1):
        head, secs = _parse_part(t, part)
        if part == 1:
            for l in head + (secs.get(0, {}).get('intro', []) if not head else []):
                st = l.strip().strip('*').strip()
                st = re.sub(r'^[-•>#\s]+', '', st).strip().strip('"“”').replace('**', '')
                if re.match(r'^\[?\d{4}-\d{2}-\d{2}', st) or ('1순위' in st and '|' in st):
                    A['headline'] = st
                    break
        if not secs:
            A['loose'][part] = [l for l in head if A['headline'] is None or A['headline'] not in l.replace('**', '')]
        for s, S in secs.items():
            A['secs'][s] = S
    # 마지막 투자 책임 문구는 보고서 맨 끝으로
    S5 = A['secs'].get(5)
    bucket = (S5['subs'][S5['order'][-1]]['lines'] if S5['order'] else S5['intro']) if S5 else A['loose'].get(3)
    if bucket:
        for j in range(len(bucket) - 1, -1, -1):
            st = bucket[j].strip()
            if not st:
                continue
            if '책임' in st and '투자' in st and len(st) < 160:
                A['tail'] = re.sub(r'^[-*•>\s]+', '', st).replace('**', '').strip()
                del bucket[j]
            break
    return A


# ---- AI 해설 -> HTML (첨부 PC 보고서의 독해 가이드·실전 판단 문단 모양) -------------
_LBL = {'📖': '[📖 표 핵심 독해 가이드]', '💡': '[💡 투자자 눈높이 쉬운 해설 & 실전 판단]'}


def _inline(s):
    s = _esc(s.replace('`', ''))
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![>\w])\[실전 판단\]', '<strong>[실전 판단]</strong>', s)
    if '-&gt;' in s or '→' in s:
        s = re.sub(r'(?<![가-힣<>/\w])(무효화 조건|무효화|조건|행동)(?=\s*[(\[:：])', r'<strong>\1</strong>', s)
    return s


def _label_para(st):
    """'📖 독해 가이드: …' · '**💡 해설 & 실전 판단**: …' -> 고정 라벨 + 본문"""
    s = re.sub(r'^[-*•]\s+', '', st.strip())
    k = next((e for e in _LBL if e in s[:6]), None)
    if not k:
        return None
    i = s.index(k)
    rest = s[i + 1:]
    cut = next((j for j, ch in enumerate(rest[:40]) if ch in ':：'), None)
    if cut is None:
        cut = next((j for j, ch in enumerate(rest[:40]) if ch == ']'), -1)
    if cut is not None and cut >= 0:
        body = rest[cut + 1:]
    else:
        body = re.sub(r'^[\s*\]]*(?:표 핵심 )?(?:독해 가이드|(?:투자자 눈높이 )?(?:쉬운 )?해설\s*&\s*실전 판단)', '', rest)
        body = re.sub(r'^[\s*\]—\-–]+', '', body)
    body = re.sub(r'^[\s*\]]+', '', body)
    return '<p><strong>' + _esc(_LBL[k]) + '</strong>: ' + _inline(body) + '</p>'


def _ai_html(lines):
    out, items, tbl = [], [], []

    def flush():
        if items:
            out.append(_list_html(items))
            items.clear()
        if tbl:
            rows = [_cells(r) for r in tbl if not re.match(r'^\s*\|?\s*:?-{2,}', r)]
            out.append(_table(rows[0], rows[1:]) if len(rows) > 1 else '<p>' + _esc(tbl[0]) + '</p>')
            tbl.clear()

    for l in lines:
        st = l.strip()
        if not st or re.match(r'^(-{3,}|\*{3,}|_{3,})$', st):
            flush()
            continue
        if st.startswith('|') and st.endswith('|'):
            if items:
                out.append(_list_html(items))
                items.clear()
            tbl.append(st)
            continue
        if tbl:
            flush()
        lp = _label_para(st)
        if lp:
            flush()
            out.append(lp)
            continue
        h = _heading(l)
        if h and h[0] >= 1:
            flush()
            out.append('<h4>' + _inline(h[1]) + '</h4>')
            continue
        m = re.match(r'^(\s*)([-*•])\s+(.*)$', l)
        if m:
            items.append((len(m.group(1).expandtabs(4)), _inline(m.group(3))))
            continue
        flush()
        out.append('<p>' + _inline(st) + '</p>')
    flush()
    return '\n'.join(out)


def _headline_from(F):
    bits = []
    if F.get('reg1'):
        bits.append(f"1순위 {F['reg1'][0]}({F['reg1'][1]}%)")
    if F.get('phase'):
        u, d, s_, name = F['phase']
        p = {'상승': u, '하락': d, '횡보': s_}.get(name[:2], '')
        ph = f"{name}({p}%)" if p else name
        bits.append(ph + (f" · 급락 위험도 {F['risk'][1]}" if F.get('risk') else ''))
    if F.get('spot'):
        bits.append(f"EWY 종가 {F['spot'][0]}달러 ({F['spot'][1]})")
    return f"[{F['date']}] " + " | ".join(bits)


def build_report_html(book, F, texts, vlines, meta):
    date, ws, traj = F['date'], book['ws'], book['traj']
    tier_short = _tier_short(F.get('tier'))
    titles = _section_titles(book.get('head'), F.get('tier') or tier_short, traj)
    P = _pieces(book)
    A = _parse_answers(texts)
    fmt = dict(date=date, traj=traj, ws=ws, tier_short=tier_short, and15=' 및 [섹션 1-5]' if '1-5' in P else '')
    body = [f"<h1>[{REPORT_TITLE}] {_esc(tier_short)} (기준일: {_esc(date)})</h1>",
            "<p><strong>" + _inline(A['headline'] or _headline_from(F)) + "</strong></p>"]
    for sec in range(6):
        S = A['secs'].get(sec) or {'intro': [], 'subs': {}, 'order': []}
        body.append(f"\n<details open>\n<summary>{_esc(titles[sec])}</summary>")
        if S['subs'] and S['intro']:
            body.append(_ai_html(S['intro']))
        used = set()
        for glyph, ttl, keys, h4_first in LAYOUT[sec]:
            ai = S['subs'].get(glyph)
            has_ai = bool(ai and any(l.strip() for l in ai['lines']))
            ks = [k.lstrip('?') for k in keys if P.get(k.lstrip('?')) and not (k.startswith('?') and has_ai)]
            data = [_piece_html(k, P[k], date, show_heading=(n > 0 or h4_first)) for n, k in enumerate(ks)]
            if not any(data) and not has_ai:
                continue
            used.add(glyph)
            body.append(f"\n<h3>{glyph} {_esc(ttl.format(**fmt))}</h3>")
            body += [d for d in data if d]
            if ai:
                body.append(_ai_html(ai['lines']))
        for g in S['order']:
            if g not in used and any(l.strip() for l in S['subs'][g]['lines']):
                body.append(f"\n<h3>{_esc(S['subs'][g]['title'])}</h3>")
                body.append(_ai_html(S['subs'][g]['lines']))
        if S['intro'] and not S['subs']:
            body.append(_ai_html(S['intro']))
        for part, secs_ in PART_SECS.items():
            if sec == secs_[-1] and A['loose'].get(part):
                body.append(f"\n<h3>해설 (파트 {part}/3)</h3>")
                body.append(_ai_html(A['loose'][part]))
        body.append("</details>")
    if book['sec'].get(6):
        body.append("\n<details>\n<summary>[부록] 이력 요약 블록 ([섹션 6] · 해설의 근거 자료)</summary>")
        body.append(_r_generic(book['sec'][6][1:]))
        body.append("</details>")
    body.append("\n<details>\n<summary>[부록] 자동 검산 결과</summary>")
    body.append("<p>" + _esc(meta) + "</p><ul>" +
                ''.join('<li>' + _esc(v.lstrip('- ').strip().replace('($)', '')) + '</li>' for v in vlines) + "</ul>")
    body.append("</details>")
    body.append("\n<p>" + _esc(A['tail'] or DISCLAIMER) + "</p>")
    return ("<!DOCTYPE html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"<title>{_esc(REPORT_TITLE)} (기준일: {_esc(date)})</title>\n<style>{REPORT_CSS}</style>\n</head>\n<body>\n"
            + "\n".join(body) + "\n</body>\n</html>\n")


# ------------------------------------------------------------------------------
# 9. 보고서 저장 (API 생성분·앱 답변 붙여넣기 공용) + 앱 답변 3개 합치기
# ------------------------------------------------------------------------------
END_MARK_RE = re.compile(r'^[\s—–\-]*파트\s*\d\s*/\s*3\s*끝[\s—–\-]*$', re.M)


def _date_mentioned(date_str, text):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str or '')
    if not m:
        return True
    y, mo, d = m.groups()
    pats = [f"{y}-{mo}-{d}", f"{y}.{mo}.{d}", f"{y}/{mo}/{d}", f"{int(mo)}월 {int(d)}일", f"{int(mo)}/{int(d)}", f"{mo}-{d}"]
    return any(p in text for p in pats)


def _save_report(book, F, stem, out_dir, texts, meta, extra_checks=None, log=print):
    md_all = "\n\n".join(texts)
    vlines = verify_commentary(md_all, F, book['text'], book['ws'])
    for k, t in enumerate(texts, 1):
        if not re.search(r'파트\s*%d\s*/\s*3\s*끝' % k, t):
            vlines.append(f"- 파트 {k}/3 끝 표시가 없음: 답이 중간에 끊겼거나 다른 파트를 붙였는지 확인")
    if not _date_mentioned(F['date'], md_all):
        vlines.append(f"- 해설에서 기준일 {F['date']}이 보이지 않음: 다른 날짜의 답변을 붙였는지 확인")
    vlines += list(extra_checks or [])
    clean = [END_MARK_RE.sub('', t).strip() for t in texts]
    page = build_report_html(book, F, texts, vlines, meta)
    paths = {'report': os.path.join(out_dir, f"{stem}_보고서.html"),
             'md': os.path.join(out_dir, f"{stem}_해설.md"),
             'check': os.path.join(out_dir, f"{stem}_검산.txt")}
    with open(paths['report'], 'w', encoding='utf-8') as f:
        f.write(page)
    with open(paths['md'], 'w', encoding='utf-8') as f:
        f.write(f"# EWY 옵션 해설 — {F['date']}\n\n> {meta}\n\n" + dollar_to_text("\n\n".join(clean)) + "\n")
    with open(paths['check'], 'w', encoding='utf-8') as f:
        f.write(meta + "\n" + "\n".join(vlines) + "\n")
    log("  - " + meta)
    for v in vlines:
        log("    " + v)
    log(f"  - 보고서: {paths['report']}")
    log(f"  - 해설 원문(NotebookLM 소스용): {paths['md']}")
    return paths, page


# ==============================================================================
# 프로그램에서 부르는 함수
# ==============================================================================
def pack_paths(src_path, out_dir=None):
    stem = os.path.splitext(os.path.basename(src_path))[0]
    out_dir = out_dir or os.path.dirname(os.path.abspath(src_path))
    p = {f'part{k}': os.path.join(out_dir, f"{stem}_{k}of3.txt") for k in (1, 2, 3)}
    p['viewer'] = os.path.join(out_dir, f"{stem}_표뷰어.html")
    return stem, out_dir, p


def report_paths(src_path, out_dir):
    stem = os.path.splitext(os.path.basename(src_path))[0]
    return {'report': os.path.join(out_dir, f"{stem}_보고서.html"),
            'md': os.path.join(out_dir, f"{stem}_해설.md"),
            'check': os.path.join(out_dir, f"{stem}_검산.txt")}


def make_split_pack(src_path, out_dir=None, log=None):
    """데이터북 1개 -> 3분할 프롬프트 + 표 뷰어"""
    log = log or (lambda *a: None)
    raw = open(src_path, encoding='utf-8-sig').read()
    book = parse_databook(raw)
    F = extract_key_facts(book['text'])
    stem, out_dir, paths = pack_paths(src_path, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    parts = build_part_prompts(book, F, stem)
    for k, p in enumerate(parts, 1):
        with open(paths[f'part{k}'], 'w', encoding='utf-8') as f:
            f.write(p)
    inner = viewer_inner(book)
    with open(paths['viewer'], 'w', encoding='utf-8') as f:
        f.write(_page(f"표 뷰어 {F['date']}", f"<h1>EWY 옵션 데이터북 표 뷰어 — {html.escape(F['date'])}</h1>"
                      "<div class='note'>엔진 데이터북의 모든 표를 파이썬이 미리 그린 파일입니다. 표는 좌우로 밀어서 봅니다.</div>"
                      + _card_html(F, book['ws'], book['wl']) + inner))
    n_tables = count_tables(book)
    log(f"[3분할 프롬프트] {os.path.basename(src_path)} (기준일 {F['date']})")
    log(f"  - 원본 {len(raw):,}자 -> 파트1 {len(parts[0]):,}자 / 파트2 {len(parts[1]):,}자 / 파트3 {len(parts[2]):,}자 "
        f"(달러 기호 {raw.count('$')}개 -> {sum(p.count('$') for p in parts)}개)")
    log(f"  - 표 뷰어: 표 {n_tables}개 · 저장 폴더: {out_dir}")
    return {'stem': stem, 'date': F['date'], 'tier': F['tier'], 'paths': paths,
            'chars': [len(p) for p in parts], 'tables': n_tables, 'databook': os.path.abspath(src_path)}


def merge_answers(texts, src_path, out_dir, log=None):
    """AI 답변 3개(파트 1/3 · 2/3 · 3/3) + 데이터북 -> 최종 보고서(_보고서.html · _해설.md · _검산.txt)"""
    texts = [str(t or '').strip() for t in texts]
    if len(texts) != 3 or any(len(t) < 50 for t in texts):
        raise ValueError("파트 1/3 · 2/3 · 3/3 답변 세 개를 모두 붙여넣어 주세요.")
    book = parse_databook(open(src_path, encoding='utf-8-sig').read())
    F = extract_key_facts(book['text'])
    stem = os.path.splitext(os.path.basename(src_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    meta = (f"합친 시각 {datetime.now().strftime('%Y-%m-%d %H:%M')} · 해설: AI 답변 붙여넣기(제미나이·클로드 등) · "
            f"데이터북: {os.path.basename(src_path)}")
    lines = []
    paths, _page_html = _save_report(book, F, stem, out_dir, texts, meta, None, log=lines.append)
    checks = [x.strip()[2:] for x in lines if x.startswith('    - ')]
    if log:
        for x in lines:
            log(x)
    return {'stem': stem, 'date': F['date'], 'paths': paths, 'checks': checks, 'meta': meta}
