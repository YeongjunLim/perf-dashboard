@echo off
echo [perf-dashboard] 패키지 설치 중...
pip install -r requirements.txt

echo.
echo [perf-dashboard] 서버 시작 중...
echo 브라우저에서 http://localhost:8000 접속하세요.
echo.
uvicorn app:app --host 0.0.0.0 --port 8000
pause
