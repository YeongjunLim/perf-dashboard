import math
import numpy as np
from typing import List


def fit_power_law(x_data: List[float], y_data: List[float]):
    """
    Power Law 곡선 피팅: TPS = a * (data_size)^b
    log 변환 후 선형 회귀로 계수(a, b) 산출
    """
    log_x = np.log(x_data)
    log_y = np.log(y_data)
    b, log_a = np.polyfit(log_x, log_y, 1)
    a = np.exp(log_a)
    return float(a), float(b)


def predict_tps(a: float, b: float, data_size: float) -> float:
    """Power Law로 특정 데이터 건수에서의 TPS 예측"""
    return a * (data_size ** b)


def predict_server_count(measurements: list, target_data_size: int, target_tps: float, config: str) -> dict:
    """
    목표 TPS와 데이터 건수 기준으로 필요한 서버 대수 예측

    Args:
        measurements: 해당 제품의 측정 데이터 목록
        target_data_size: 목표 데이터 건수
        target_tps: 목표 TPS
        config: 서버 스펙 (예: '16Core32GB')

    Returns:
        예측 결과 딕셔너리
    """
    config_data = [m for m in measurements if m["config"] == config]

    if len(config_data) < 2:
        raise ValueError(f"'{config}' 스펙의 측정 데이터가 부족합니다 (최소 2개 필요).")

    x = [m["data_size"] for m in config_data]
    y = [m["tps"] for m in config_data]

    a, b = fit_power_law(x, y)
    predicted_tps_per_server = predict_tps(a, b, target_data_size)
    server_count = math.ceil(target_tps / predicted_tps_per_server)

    # Power Law 곡선 포인트 (차트용)
    x_min, x_max = min(x), max(x)
    curve_points = []
    for i in range(20):
        cx = x_min + (x_max - x_min) * i / 19
        curve_points.append({"x": int(cx), "y": round(predict_tps(a, b, cx), 2)})

    return {
        "config": config,
        "target_data_size": target_data_size,
        "target_tps": target_tps,
        "predicted_tps_per_server": round(predicted_tps_per_server, 2),
        "server_count": server_count,
        "power_law_a": round(a, 4),
        "power_law_b": round(b, 4),
        "curve_points": curve_points,
        "measured_points": [{"x": xi, "y": yi} for xi, yi in zip(x, y)],
    }
