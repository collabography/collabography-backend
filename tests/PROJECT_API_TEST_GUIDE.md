# 프로젝트 API 테스트 가이드

프로젝트 관련 API를 체계적으로 테스트하는 방법을 안내합니다.

## 테스트할 엔드포인트

1. `POST /projects` - 프로젝트 생성
2. `GET /projects` - 프로젝트 목록 조회
3. `GET /projects/{id}` - 프로젝트 조회
4. `GET /projects/{id}/edit-state` - 프로젝트 edit-state 조회

## 방법 1: Swagger UI 사용 (가장 추천)

### 1단계: 서버 실행

```bash
# 가상환경 활성화 (필요시)
source .venv/bin/activate

# 서버 실행
uvicorn app.main:app --reload
```

### 2단계: Swagger UI 접속

브라우저에서 다음 주소로 접속:
```
http://localhost:8000/docs
```

### 3단계: 각 엔드포인트 테스트

#### 프로젝트 생성 (`POST /projects`)
1. `POST /projects` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. Request body에 다음 입력:
   ```json
   {
     "title": "테스트 프로젝트"
   }
   ```
4. "Execute" 버튼 클릭
5. Response 확인 (201 Created)

#### 프로젝트 목록 조회 (`GET /projects`)
1. `GET /projects` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. (선택) `limit` 파라미터 설정 (기본값: 50)
4. "Execute" 버튼 클릭
5. Response 확인 (200 OK, items 배열 확인)

#### 프로젝트 조회 (`GET /projects/{id}`)
1. `GET /projects/{project_id}` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. `project_id`에 위에서 생성한 프로젝트 ID 입력
4. "Execute" 버튼 클릭
5. Response 확인 (200 OK)

#### Edit State 조회 (`GET /projects/{id}/edit-state`)
1. `GET /projects/{project_id}/edit-state` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. `project_id`에 프로젝트 ID 입력
4. "Execute" 버튼 클릭
5. Response 확인 (200 OK, project와 tracks 배열 확인)

## 방법 2: Python 테스트 스크립트 사용

### 전체 테스트 실행

```bash
python tests/test_projects_only.py
```

### 개별 테스트 실행

```bash
# Python 인터프리터에서
python -c "from tests.test_projects_only import test_create_project; test_create_project()"
```

## 방법 3: curl 명령어 사용

### 1. 헬스 체크
```bash
curl -X GET http://localhost:8000/health
```

### 2. 프로젝트 생성
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"title": "테스트 프로젝트"}'
```

응답 예시:
```json
{
  "id": 1,
  "title": "테스트 프로젝트",
  "music_object_key": null,
  "music_duration_sec": null,
  "music_bpm": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 3. 프로젝트 목록 조회
```bash
curl -X GET http://localhost:8000/projects
```

페이지네이션 사용:
```bash
curl -X GET "http://localhost:8000/projects?limit=10&cursor=5"
```

### 4. 프로젝트 조회
```bash
curl -X GET http://localhost:8000/projects/1
```

### 5. Edit State 조회
```bash
curl -X GET http://localhost:8000/projects/1/edit-state
```

응답 예시:
```json
{
  "project": {
    "id": 1,
    "title": "테스트 프로젝트",
    ...
  },
  "tracks": [
    {
      "id": 1,
      "slot": 1,
      "display_name": null,
      "layers": [],
      "keyframes": []
    },
    {
      "id": 2,
      "slot": 2,
      "display_name": null,
      "layers": [],
      "keyframes": []
    },
    {
      "id": 3,
      "slot": 3,
      "display_name": null,
      "layers": [],
      "keyframes": []
    }
  ]
}
```

## 체크리스트

테스트 시 다음 사항들을 확인하세요:

### 프로젝트 생성 (`POST /projects`)
- [ ] 201 Created 상태 코드 반환
- [ ] 생성된 프로젝트 ID 확인
- [ ] 제목이 올바르게 저장되었는지 확인
- [ ] 자동으로 3개의 트랙이 생성되었는지 확인 (edit-state 조회로 확인)

### 프로젝트 목록 조회 (`GET /projects`)
- [ ] 200 OK 상태 코드 반환
- [ ] `items` 배열이 반환되는지 확인
- [ ] `next_cursor`와 `has_more` 필드 확인
- [ ] 페이지네이션 동작 확인

### 프로젝트 조회 (`GET /projects/{id}`)
- [ ] 200 OK 상태 코드 반환
- [ ] 올바른 프로젝트 정보 반환
- [ ] 존재하지 않는 ID에 대해 404 반환 확인

### Edit State 조회 (`GET /projects/{id}/edit-state`)
- [ ] 200 OK 상태 코드 반환
- [ ] `project` 객체 포함 확인
- [ ] `tracks` 배열에 3개 트랙 포함 확인
- [ ] 각 트랙에 `slot` (1, 2, 3) 확인
- [ ] 각 트랙에 `layers`와 `keyframes` 배열 포함 확인

## 예상되는 문제 및 해결 방법

### 1. 서버가 실행되지 않음
**증상**: `Connection refused` 에러
**해결**: `uvicorn app.main:app --reload` 실행

### 2. 데이터베이스 연결 오류
**증상**: `500 Internal Server Error` 또는 DB 관련 에러
**해결**: 
- 데이터베이스가 실행 중인지 확인
- `.env` 파일의 `DATABASE_URL` 확인
- 마이그레이션 실행: `alembic upgrade head`

### 3. 404 에러
**증상**: 엔드포인트를 찾을 수 없음
**해결**: 
- 서버가 재시작되었는지 확인
- 엔드포인트 경로 확인 (`/projects` vs `/project`)

### 4. 422 Validation Error
**증상**: 요청 데이터 검증 실패
**해결**: 
- Request body 형식 확인 (JSON)
- 필수 필드 확인 (`title` 필수)

## 다음 단계

프로젝트 API 테스트가 완료되면:
1. 음악 업로드 API 테스트
2. 레이어 업로드 API 테스트
3. 키프레임 API 테스트
4. 자산 Presigned URL API 테스트

