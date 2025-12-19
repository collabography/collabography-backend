# collabography-backend

FastAPI + PostgreSQL + MinIO + Celery 기반 백엔드.

## 프로젝트 개요

Collabography는 3명의 댄서(3개 Track)의 스켈레톤 클립(Skeleton Layer)을 절대 타임라인(음악) 위에 배치하여, 겹치는 구간에서는 priority(z-index) 최대 1개만 선택해 Front View를 즉시 렌더링하는 비동기 안무 협업/검증 편집기입니다.

## 기술 스택

- **FastAPI**: API 서버
- **PostgreSQL**: 데이터베이스
- **MinIO**: 객체 스토리지 (S3 호환)
- **Celery + Redis**: 비동기 작업 큐
- **Alembic**: 데이터베이스 마이그레이션

## 로컬 실행 (Docker Compose 권장)

### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/collabography

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=collabography
MINIO_SECURE=false

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 2. Docker Compose로 실행

```bash
cd docker
docker-compose up -d
```

이 명령은 다음 서비스를 시작합니다:
- PostgreSQL (포트 5432)
- MinIO (포트 9000, 콘솔 9001)
- Redis (포트 6379)
- API 서버 (포트 8000)
- Celery Worker

### 3. 데이터베이스 마이그레이션

```bash
# 컨테이너 내에서 실행
docker-compose exec api alembic upgrade head

# 또는 로컬에서 실행 (venv 활성화 후)
alembic upgrade head
```

### 4. MinIO 버킷 생성

MinIO 콘솔에 접속하여 버킷을 생성하거나, API가 자동으로 생성합니다.

- MinIO 콘솔: http://localhost:9001
- 로그인: minioadmin / minioadmin

## 로컬 실행 (venv - 개발용)

### 1. 가상환경 설정

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 위의 환경 변수를 설정하세요.

### 3. 데이터베이스 마이그레이션

```bash
alembic upgrade head
```

### 4. API 서버 실행

```bash
uvicorn app.main:app --reload
```

### 5. Celery Worker 실행 (별도 터미널)

```bash
celery -A worker.celery_app worker --loglevel=info
```

## API 엔드포인트

### 프로젝트
- `POST /projects` - 프로젝트 생성
- `GET /projects` - 프로젝트 목록 조회
- `GET /projects/{id}` - 프로젝트 조회
- `GET /projects/{id}/edit-state` - 프로젝트 edit-state 조회

### 음악
- `POST /projects/{id}/music/upload-init` - 음악 업로드 presigned URL 발급
- `POST /projects/{id}/music/commit` - 음악 업로드 완료 후 프로젝트에 연결

### 레이어
- `POST /tracks/{id}/layers/upload-init` - 레이어 업로드 presigned URL 발급
- `POST /tracks/{id}/layers` - 레이어 생성 (VIDEO 또는 JSON 기반)
- `GET /tracks/{id}/layers/{layer_id}` - 레이어 조회
- `PATCH /tracks/{id}/layers/{layer_id}` - 레이어 업데이트
- `DELETE /tracks/{id}/layers/{layer_id}` - 레이어 삭제

### 키프레임
- `PUT /tracks/{id}/position-keyframes` - 키프레임 전체 교체
- `GET /tracks/{id}/position-keyframes` - 키프레임 목록 조회

### 자산
- `POST /assets/presign` - 자산 presigned GET URL 발급
- `POST /assets/presign/batch` - 자산 presigned GET URL 일괄 발급

### 헬스 체크
- `GET /health` - 앱 헬스 체크
- `GET /health/db` - DB 커넥션 체크

## Swagger / API 문서

FastAPI 기본 Swagger UI 및 ReDoc 문서를 사용합니다.

- 브라우저에서 접속:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI 스펙(JSON):
  - `http://127.0.0.1:8000/openapi.json`

## 프로젝트 구조

```
collabography-backend/
  app/
    api/          # API 라우터
    core/         # 설정, 에러 처리
    db/           # 데이터베이스 연결
    models/       # SQLAlchemy 모델
    schemas/      # Pydantic 스키마
    services/     # 비즈니스 로직
    integrations/ # 외부 서비스 통합 (MinIO, Celery)
  worker/         # Celery 워커
    tasks/        # 작업 정의
    pipelines/    # 스켈레톤 추출 파이프라인
  migrations/     # Alembic 마이그레이션
  docker/         # Docker 설정
```

## 개발 가이드

### 데이터베이스 마이그레이션

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

### Celery 작업 모니터링

```bash
# Celery Flower (옵션)
pip install flower
celery -A worker.celery_app flower
```

## 참고사항

- MVP에서는 인증이 생략되어 있습니다 (1인 소유 가정)
- 스켈레톤 추출은 현재 더미 데이터를 생성합니다. 실제 pose 추출은 `worker/pipelines/pose_extractor.py`에 구현해야 합니다.
