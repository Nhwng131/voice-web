# FastAPI + PostgreSQL + JWT (voice_web)

## Yêu cầu
- Python 3.11+
- Docker + Docker Compose

## Cài đặt

```powershell
git clone https://github.com/Nhwng131/voice-web.git
cd voice_web

# 1) Tạo venv & cài lib
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2) Chạy Postgres bằng Docker
docker compose up -d
# NOTE: compose map cổng 55432 -> 5432 trong container

# 3) Tạo file env

# 4) Chạy app
python -m uvicorn app.main:app --reload
# mở http://127.0.0.1:8000/docs
