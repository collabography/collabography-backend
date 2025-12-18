# collabography-backend

FastAPI + Python 3.11 기반 백엔드.

## 로컬 실행 (venv)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## API

- `GET /health` : 앱 헬스 체크
- `GET /health/db` : DB 커넥션 체크 (`SELECT 1`)

예시:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/health/db
```

## Swagger / API 문서

FastAPI 기본 Swagger UI 및 ReDoc 문서를 사용합니다.

- 브라우저에서 접속:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI 스펙(JSON):
  - `http://127.0.0.1:8000/openapi.json`

로컬에서 `uvicorn app.main:app --reload` 로 서버를 실행한 뒤 위 주소로 접속하면 됩니다.

## Railway 배포

### 환경변수

- `DATABASE_URL` : Railway Postgres에서 제공되는 값을 그대로 사용
  - `postgresql://...` 또는 `postgres://...` 형태여도 자동으로 async 드라이버(`postgresql+asyncpg://...`)로 변환합니다.

### 실행 커맨드

Railway의 Start Command 또는 `Procfile` 기준으로 아래 커맨드를 사용합니다.

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
