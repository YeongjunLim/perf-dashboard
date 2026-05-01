from pydantic import BaseModel
from typing import Optional


class Measurement(BaseModel):
    product: str
    version: str
    config: str
    data_size: int
    threads: int
    tps: float
    response_sec: float
    error_pct: float
    cpu_avg: float


class PredictRequest(BaseModel):
    product: str
    config: str
    target_data_size: int
    target_tps: float
