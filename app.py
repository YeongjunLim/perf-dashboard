from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import database as db
import predictor
from models import Measurement, PredictRequest

app = FastAPI(title="Performance Analysis Dashboard")

# 앱 시작 시 DB 초기화 및 샘플 데이터 로드
@app.on_event("startup")
def startup():
    db.init_db()
    if db.is_empty():
        db.load_sample_data()

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
def root():
    return "static/index.html"


# ── 제품 / 버전 / 스펙 목록 ──────────────────────────────

@app.get("/api/products")
def get_products():
    return db.get_products()


@app.get("/api/versions/{product}")
def get_versions(product: str):
    return db.get_versions(product)


@app.get("/api/configs/{product}")
def get_configs(product: str):
    return db.get_configs(product)


# ── 성능 분석 ─────────────────────────────────────────────

@app.get("/api/report/{product}/{version}")
def get_report(product: str, version: str):
    """특정 제품·버전의 스펙별 측정 데이터 반환"""
    rows = db.get_measurements(product, version)
    if not rows:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

    # 스펙별로 그룹화
    configs = {}
    for r in rows:
        cfg = r["config"]
        if cfg not in configs:
            configs[cfg] = []
        configs[cfg].append(r)

    return {"product": product, "version": version, "configs": configs}


# ── 서버 대수 예측 ────────────────────────────────────────

@app.post("/api/predict")
def predict(req: PredictRequest):
    """Power Law 외삽법으로 필요 서버 대수 예측"""
    rows = db.get_measurements(req.product)
    if not rows:
        raise HTTPException(status_code=404, detail="해당 제품의 측정 데이터가 없습니다.")

    try:
        result = predictor.predict_server_count(
            measurements=rows,
            target_data_size=req.target_data_size,
            target_tps=req.target_tps,
            config=req.config,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


# ── 버전 추이 ─────────────────────────────────────────────

@app.get("/api/trend/{product}")
def get_trend(product: str):
    """제품의 버전별 TPS·응답시간·에러율 변화"""
    rows = db.get_measurements(product)
    if not rows:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

    # 버전·스펙별 평균 집계
    summary = {}
    for r in rows:
        key = (r["version"], r["config"])
        if key not in summary:
            summary[key] = {"tps": [], "response_sec": [], "error_pct": []}
        summary[key]["tps"].append(r["tps"])
        summary[key]["response_sec"].append(r["response_sec"])
        summary[key]["error_pct"].append(r["error_pct"])

    trend = []
    for (version, config), vals in sorted(summary.items()):
        trend.append({
            "version": version,
            "config": config,
            "avg_tps": round(sum(vals["tps"]) / len(vals["tps"]), 2),
            "avg_response_sec": round(sum(vals["response_sec"]) / len(vals["response_sec"]), 3),
            "avg_error_pct": round(sum(vals["error_pct"]) / len(vals["error_pct"]), 2),
        })

    return {"product": product, "trend": trend}


# ── 데이터 직접 등록 ──────────────────────────────────────

@app.post("/api/data")
def add_data(measurements: List[Measurement]):
    """JSON으로 측정 데이터 직접 등록"""
    db.insert_measurements([m.dict() for m in measurements])
    return {"inserted": len(measurements)}
