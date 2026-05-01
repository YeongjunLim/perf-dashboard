# perf-dashboard

> JMeter 성능 측정 데이터를 분석하고, **Power Law 외삽법**으로 서버 용량을 예측하는 웹 대시보드

---

## 배경 및 문제 정의

B2B 소프트웨어를 납품할 때마다 고객사로부터 동일한 질문이 반복됩니다.

> "우리 데이터가 500만 건인데, 목표 TPS 300을 맞추려면 서버가 몇 대 필요한가요?"

기존에는 QA 엔지니어가 JMeter로 스펙별 성능 측정 → 엑셀로 수치 정리 → 수작업으로 추정값 계산 → 담당자에게 전달하는 방식으로 처리했습니다.
이 과정은 매 납품마다 반복되었고, 계산 기준이 명확하지 않아 팀 내 혼선이 발생하기도 했습니다.

이 문제를 해결하기 위해 **측정 데이터 기반 서버 용량 예측 도구**를 직접 개발하여 팀 서버에 배포했습니다.

---

## 주요 기능

### 📊 성능 분석
서버 스펙(core/memory)별 TPS, 응답시간, 에러율을 차트와 테이블로 시각화합니다.

![성능 분석 탭](#) ← 스크린샷 추가 예정

### 🖥 서버 대수 계산기
목표 데이터 건수와 TPS를 입력하면 Power Law 외삽법으로 필요한 서버 대수를 자동 산출합니다.

- 측정 데이터에서 `TPS = a × (data_size)^b` 계수 자동 피팅
- 피팅 곡선과 측정값을 차트로 비교 확인
- 목표 지점을 시각적으로 표시

![서버 계산기 탭](#) ← 스크린샷 추가 예정

### 📈 버전 추이
동일 제품의 버전별 성능 변화(TPS, 응답시간, 에러율)를 추적합니다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python, FastAPI, uvicorn |
| 예측 모델 | Power Law 외삽법 (numpy 선형 회귀) |
| Database | SQLite (Python 내장) |
| Frontend | HTML/CSS/JavaScript, Chart.js |

> Java, Node.js, 별도 DB 서버 불필요. Python 3.9 이상만 있으면 실행 가능합니다.

---

## 설치 및 실행

### 요구사항

- Python 3.9 이상

### Windows

```bat
run.bat
```

### 수동 실행 (Windows / Linux / macOS 공통)

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

브라우저에서 `http://localhost:8000` 접속

---

## 샘플 데이터

`sample_data/sample.json`에 SearchEngine 제품의 가상 측정 데이터가 포함되어 있습니다.
앱 최초 실행 시 자동으로 DB에 로드됩니다.

```
스펙:   8Core16GB / 16Core32GB / 24Core64GB
버전:   v1.0 / v1.1 / v2.0
데이터: 100K / 500K / 1M / 5M / 10M 건
```

### 직접 데이터 추가 (API)

```bash
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '[
    {
      "product": "MyProduct",
      "version": "v1.0",
      "config": "16Core32GB",
      "data_size": 1000000,
      "threads": 200,
      "tps": 458.9,
      "response_sec": 0.22,
      "error_pct": 0.0,
      "cpu_avg": 78.4
    }
  ]'
```

---

## 프로젝트 구조

```
perf-dashboard/
├── app.py              # FastAPI 라우터
├── database.py         # SQLite CRUD
├── models.py           # Pydantic 모델
├── predictor.py        # Power Law 피팅 및 예측
├── static/
│   └── index.html      # SPA 대시보드
├── sample_data/
│   └── sample.json     # 샘플 측정 데이터
├── requirements.txt
├── run.bat
└── .gitignore
```

---

## Power Law 외삽법 개요

데이터 건수가 늘어날수록 TPS는 감소하는 비선형 관계를 Power Law로 모델링합니다.

```
TPS = a × (data_size)^b
```

양변에 로그를 취하면 선형 회귀로 계수 a, b를 산출할 수 있습니다.

```python
log(TPS) = log(a) + b × log(data_size)
```

산출된 계수로 측정 범위 외의 데이터 건수에서의 TPS를 예측하고,
`서버 대수 = ceil(목표 TPS / 서버 1대당 예측 TPS)` 로 필요 서버 대수를 계산합니다.

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/products` | 제품 목록 |
| GET | `/api/versions/{product}` | 버전 목록 |
| GET | `/api/configs/{product}` | 스펙 목록 |
| GET | `/api/report/{product}/{version}` | 성능 분석 결과 |
| POST | `/api/predict` | 서버 대수 예측 |
| GET | `/api/trend/{product}` | 버전별 성능 추이 |
| POST | `/api/data` | 측정 데이터 직접 등록 |
