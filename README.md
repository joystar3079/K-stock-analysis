# EWY Quant Analytics V28

기존 단일 파일(532줄)을 7개 모듈로 분리하고, 속도·상태관리·가독성을 개선한 버전입니다.

## 파일 구조

| 파일 | 역할 |
|---|---|
| `app.py` | Streamlit UI만 |
| `config.py` | 심볼, 임계값 상수, 버전별 엔진 설정 |
| `pricing.py` | 벡터화된 미국식 이항트리 / IV / 델타 |
| `data_io.py` | 시세·마스터 파일 IO, 일일 옵션 추출 |
| `features.py` | 미결제약정 집계 (캐싱) |
| `phases.py` | 국면 판정 |
| `presenters.py` | 표시 문자열 |

## 배포

GitHub 저장소 루트에 위 7개 파일 + `requirements.txt` 를 두고
Streamlit Cloud에서 `app.py` 를 진입점으로 지정합니다.

Secrets 에 다음 두 개가 필요합니다.

```toml
GITHUB_TOKEN = "ghp_..."
GITHUB_REPO  = "owner/repo"
```

## 주요 변경

**속도**
- IV 연산 전량 벡터화 (옵션별 루프 → 배열 일괄 처리)
- ThreadPoolExecutor 제거 (CPU 연산에 GIL이 걸려 효과 없었음)
- 호가·미결제 없는 종목 사전 필터
- 미결제약정 집계 결과 캐싱
- `nlargest` 3회 호출 → 1회
- 시세 결측 보정 O(n²) 루프 → map

**상태 관리**
- 마스터 읽기/쓰기를 GitHub 기준으로 통일 (기존: GitHub 쓰기 + 로컬 읽기)
- 업로드 후 세션 추출 데이터 정리 (기존: 계속 재병합)
- 히스토리 삭제를 인덱스 → id 기반으로 변경
- 위젯 키를 초 단위 타임스탬프 → UUID
- 히스토리 상한 10건

**가독성**
- 매직넘버 40여 개를 `TH` 클래스로 집약
- 버전 분기를 `EngineConfig` 데이터클래스로 분리
- 계산 로직과 표시 문자열 분리
- bare `except:` 6곳 제거
- IV/Delta 컬럼에서 빈 문자열 제거 (NaN 유지)
