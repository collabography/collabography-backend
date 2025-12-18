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
