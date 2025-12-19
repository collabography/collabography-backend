# API 테스트 가이드

이 디렉토리에는 API 엔드포인트를 테스트하는 예제 스크립트가 포함되어 있습니다.

## 방법 1: Swagger UI 사용 (가장 간단)

1. 서버 실행:
   ```bash
   uvicorn app.main:app --reload
   ```

2. 브라우저에서 접속:
   ```
   http://localhost:8000/docs
   ```

3. 각 엔드포인트를 클릭하여 "Try it out" 버튼을 누르고 테스트할 수 있습니다.

## 방법 2: Python 테스트 스크립트 사용

### 전체 테스트 실행

```bash
# 의존성 설치 (이미 설치되어 있다면 생략)
pip install httpx

# 전체 테스트 실행
python tests/test_api_examples.py
```

### 개별 엔드포인트 테스트

```bash
# Python 인터프리터에서
python -c "from tests.test_api_examples import test_create_project; test_create_project()"

# 또는 Python 스크립트로
python -c "
from tests.test_api_examples import *
test_health_check()
test_create_project()
"
```

## 방법 3: curl 명령어 사용

### 헬스 체크
```bash
curl -X GET http://localhost:8000/health
```

### 프로젝트 생성
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"title": "테스트 프로젝트"}'
```

### 프로젝트 목록 조회
```bash
curl -X GET http://localhost:8000/projects
```

### 프로젝트 조회
```bash
curl -X GET http://localhost:8000/projects/1
```

### Edit State 조회
```bash
curl -X GET http://localhost:8000/projects/1/edit-state
```

### 음악 업로드 Presigned URL 발급
```bash
curl -X POST http://localhost:8000/projects/1/music/upload-init \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.mp3", "content_type": "audio/mpeg"}'
```

### 레이어 생성 (JSON 기반)
```bash
curl -X POST http://localhost:8000/tracks/1/layers \
  -H "Content-Type: application/json" \
  -d '{
    "skeleton_object_key": "skeleton/test/source.json",
    "skeleton_fps": 30.0,
    "skeleton_num_frames": 100,
    "skeleton_num_joints": 33,
    "start_sec": 0.0,
    "end_sec": 10.0,
    "priority": 1,
    "label": "테스트 레이어"
  }'
```

### 키프레임 Upsert
```bash
curl -X PUT http://localhost:8000/tracks/1/position-keyframes \
  -H "Content-Type: application/json" \
  -d '{
    "keyframes": [
      {"time_sec": 0.0, "x": 0.0, "y": 0.0, "interp": "LINEAR"},
      {"time_sec": 5.0, "x": 100.0, "y": 100.0, "interp": "LINEAR"}
    ]
  }'
```

### 자산 Presigned URL 발급
```bash
curl -X POST http://localhost:8000/assets/presign \
  -H "Content-Type: application/json" \
  -d '{"object_key": "skeleton/test/source.json"}'
```

## 방법 4: HTTPie 사용 (curl 대안)

HTTPie는 더 읽기 쉬운 명령어를 제공합니다:

```bash
# 설치
pip install httpie

# 사용 예시
http POST localhost:8000/projects title="테스트 프로젝트"
http GET localhost:8000/projects
http GET localhost:8000/projects/1/edit-state
```

## 테스트 순서 권장사항

1. **헬스 체크** → 서버가 정상 작동하는지 확인
2. **프로젝트 생성** → 테스트용 프로젝트 생성
3. **Edit State 조회** → 트랙 ID 확인
4. **음악 업로드** → 프로젝트에 음악 연결
5. **레이어 생성** → 스켈레톤 레이어 추가
6. **키프레임 설정** → 트랙 위치 키프레임 설정
7. **자산 Presigned URL** → 스켈레톤 JSON 다운로드 URL 발급

## 주의사항

- 서버가 실행 중이어야 합니다 (`uvicorn app.main:app --reload`)
- 데이터베이스가 마이그레이션되어 있어야 합니다 (`alembic upgrade head`)
- MinIO와 Redis가 실행 중이어야 합니다 (Celery 작업 사용 시)

