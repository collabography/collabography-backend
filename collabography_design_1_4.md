# Collabography Implementation Design Pack (for Agent)
> 목적: **Agent(또는 처음 합류한 개발자)** 가 이 문서만 읽고도 “프로젝트가 무엇을 하는지 / 어떤 데이터가 핵심인지 / 어떤 API가 필요한지 / 어떤 워커가 돌아가는지”를 한 번에 이해하고, 바로 구현을 시작할 수 있도록 하는 **실행 설계 묶음**이다.  
> 범위: (1) Agent 프롬프트, (2) 폴더 구조, (3) DB 모델(ORM) 설계, (4) Skeleton 추출 워커 설계

---

## 0) 프로젝트 한 줄 요약 & 핵심 철학

### 0.1 한 줄 요약
Collabography는 **3명의 댄서(3개 Track)의 스켈레톤 클립(Skeleton Layer)을 절대 타임라인(음악) 위에 배치**하여, 겹치는 구간에서는 **priority(z-index) 최대 1개만 선택**해 Front View를 즉시 렌더링하는 **비동기 안무 협업/검증 편집기**다.

### 0.2 핵심 철학 (반드시 지켜야 함)
- **Base/Patch 구분 없음**: 모든 스켈레톤 조각은 동일하게 `SkeletonLayer`로 취급한다.
- **선택 규칙 단순화**: 같은 시각에 겹치는 레이어 중 **priority가 가장 큰 것 1개만 활성**.
- **합성/재생은 프론트 책임**: 백엔드는 “어떤 레이어가 언제 적용되는지”만 제공한다.
- **대용량 자산은 MinIO, 상태/구조는 Postgres**: JSON 본문은 MinIO에, 타임라인 상태는 DB에.
- **SkeletonSource(자산) 1 : SkeletonLayer(사용) N**: 같은 source를 여러 layer에서 재사용 가능해야 한다.

---

## 1) Agent에게 줄 최종 프롬프트 (복사해서 그대로 사용)

> 아래 프롬프트는 “설계를 바꾸지 말고 그대로 구현”하도록 강하게 제한하는 형태로 작성되어 있다.

### 1.1 Agent Prompt
- 프로젝트: **Collabography Backend (FastAPI + PostgreSQL + MinIO)**
- 구현 목표: 로컬에서 `uvicorn` 실행 시 API가 동작하고, MinIO presign 업로드/다운로드 흐름 및 Skeleton 추출 워커(Celery)가 동작하도록 **최소 실행 가능 MVP**를 만든다.
- 절대 변경 금지 원칙:
  1) Base/Patch 개념을 만들지 말 것. 모든 편집 단위는 `SkeletonLayer`.
  2) 같은 시각에서 Track의 활성 레이어는 `priority` 최대 1개(=max).
  3) 프레임 합성/재생 로직은 API가 아니라 프론트(클라이언트) 책임. 서버는 프레임을 내려주지 않는다.
  4) 스켈레톤 JSON 본문은 MinIO에 저장하고, DB에는 object_key와 메타만 저장한다.
  5) `SkeletonSource : SkeletonLayer = 1 : N` 관계를 유지한다.
- MVP에서 반드시 구현해야 하는 엔드포인트:
  - Project: create/list/edit-state
  - Music: upload-init(presigned PUT) + commit(프로젝트에 연결)
  - Layer: upload-init(presigned PUT), create(비디오 기반/JSON 기반), patch, delete, get(상태 조회)
  - TopView Keyframes: put(전체 교체)
  - Assets: presign GET (단건 + batch)
  - (옵션) SSE events는 MVP에서 폴링으로 대체 가능
- 업로드/추출 흐름:
  - 프론트가 upload-init로 presigned PUT URL을 받아 MinIO에 업로드
  - 레이어 생성 요청 시:
    - VIDEO 업로드면 skeleton_sources를 PROCESSING으로 만들고 Celery 작업 enqueue
    - 워커가 video→skeleton JSON 생성 후 MinIO 저장, skeleton_sources를 READY로 갱신
  - 프론트는 `GET /layers/{id}` 폴링 또는 SSE로 READY 전환을 감지
  - 프론트는 `GET /assets/presign`(또는 batch)로 presigned GET URL을 발급받아 JSON을 직접 fetch
- 구현 범위:
  - 인증은 MVP에서 생략(1인 소유 가정)
  - DB 마이그레이션은 Alembic 사용(권장)
  - Settings는 pydantic-settings로 구성
  - 에러 응답은 공통 포맷 유지
- 산출물:
  - 실행 가능한 FastAPI 앱
  - SQLAlchemy 모델 + Alembic 마이그레이션
  - Celery 워커 + 작업 스켈레톤(실제 pose 추출은 더미로 시작해도 됨)
  - MinIO presign 발급 코드
  - README에 실행 방법(로컬 docker-compose 포함)

---

## 2) 프로젝트 폴더 구조 설계 (권장)

### 2.1 전체 구조 개요
- `app/` 는 FastAPI 서버 코드
- `worker/` 는 Celery 워커 코드(스켈레톤 추출 파이프라인)
- `migrations/` 는 Alembic 마이그레이션
- `docker/` 는 로컬 실행용 구성(선택)
- `tests/` 는 API 단위테스트(선택)

### 2.2 권장 디렉터리 트리
```text
collabography-backend/
  README.md
  pyproject.toml                # 또는 requirements.txt
  .env.example

  app/
    __init__.py
    main.py                      # FastAPI create_app / include_router
    api/
      __init__.py
      deps.py                    # DB session 의존성, 설정, 공통 유틸
      routers/
        __init__.py
        projects.py              # /projects, /projects/{id}/edit-state
        music.py                 # /projects/{id}/music/*
        layers.py                # /tracks/{id}/layers, /layers/{id}
        keyframes.py             # /tracks/{id}/position-keyframes
        assets.py                # /assets/presign, /assets/presign/batch
    core/
      __init__.py
      config.py                  # pydantic settings (DB, MinIO, Celery)
      logging.py                 # 로깅 설정
      errors.py                  # 공통 에러 포맷 + 예외 클래스
    db/
      __init__.py
      session.py                 # engine, SessionLocal
      base.py                    # Base = declarative_base()
    models/
      __init__.py
      enums.py                   # asset_status, interp_type
      project.py
      track.py
      video.py
      skeleton_source.py
      skeleton_layer.py
      keyframe.py
    schemas/
      __init__.py
      common.py                  # ErrorResponse, CursorResponse 등
      project.py
      music.py
      layer.py
      asset.py
      keyframe.py
    services/
      __init__.py
      projects_service.py        # edit-state 조합 로직
      music_service.py           # music commit/update
      layers_service.py          # layer create/patch/delete + enqueue
      assets_service.py          # minio presign get/put
      keyframes_service.py       # keyframe upsert(전체 교체)
      gc_service.py              # source orphan GC (옵션)
    integrations/
      __init__.py
      minio_client.py            # MinIO client + presign helpers
      celery_client.py           # celery app reference / enqueue helper

  worker/
    __init__.py
    celery_app.py                # Celery 인스턴스 생성
    tasks/
      __init__.py
      extract_skeleton.py        # video -> skeleton json 생성 작업
    pipelines/
      __init__.py
      pose_extractor.py          # (추후) mediapipe 등 실제 추출 구현 위치
      skeleton_writer.py         # JSON 포맷 생성/검증/저장 유틸

  migrations/
    env.py
    script.py.mako
    versions/
      0001_init_schema.py

  docker/
    docker-compose.yml           # postgres + minio + redis + api + worker
    api.Dockerfile
    worker.Dockerfile

  tests/
    test_projects.py
    test_layers.py
    test_assets.py
```

### 2.3 레이어 처리 로직이 들어가야 하는 위치
- API Router는 “입출력 검증 + 서비스 호출”까지만
- 핵심 편집 규칙/정합성은 `services/layers_service.py` 로 몰아넣기
- edit-state 조합은 `services/projects_service.py` 가 담당(조인/정렬/그룹핑)

---

## 3) DB 모델(ORM) 설계 (SQLAlchemy 2.0 기준)

### 3.1 관계 요약 (가장 중요한 부분)
- `Project 1 -> Track 3`
- `Track 1 -> SkeletonLayer N`
- `Track 1 -> SkeletonSource N`
- `SkeletonSource 1 -> SkeletonLayer N` (**재사용 핵심**)
- `Track 1 -> PositionKeyframe N`
- (선택) `Track 1 -> Video N` (업로드 원본 보관)

### 3.2 Enums
- `AssetStatus`: `UPLOADED | PROCESSING | READY | FAILED`
- `InterpType`: `STEP | LINEAR`

### 3.3 모델별 필드 정의 (의미 중심)

#### 3.3.1 Project
- `id`: PK
- `title`: 프로젝트 이름
- `music_object_key`: MinIO key (없으면 음악 미설정)
- `music_duration_sec`: 타임라인 총 길이(초)
- `music_bpm`: optional
- `created_at`, `updated_at`

#### 3.3.2 Track
- `id`: PK
- `project_id`: FK
- `slot`: 1~3 (프로젝트당 고정)
- `display_name`: optional
- `created_at`

#### 3.3.3 SkeletonSource (불변 자산 메타)
- `id`: PK
- `track_id`: FK (MVP에서는 트랙 귀속; 추후 project 귀속으로 확장 가능)
- `object_key`: MinIO key (READY일 때 유효)
- `fps`, `num_frames`, `num_joints`, `pose_model`: 렌더/프레임 계산에 필요한 메타
- `status`: PROCESSING/READY/FAILED...
- `error_message`: 실패 원인
- `created_at`

#### 3.3.4 SkeletonLayer (편집 단위)
- `id`: PK
- `track_id`: FK
- `skeleton_source_id`: FK (**1:N 구조를 위해 unique 금지**)
- `start_sec`, `end_sec`: 타임라인 구간(겹침/공백 허용)
- `priority`: z-index (클수록 위)
- `label`: UI 표시용
- `created_at`

> 참고: fade_in/out은 현재 스키마에서 주석 처리되어 있으므로 MVP에서는 제외한다. 필요 시 다음 마이그레이션에서 추가.

#### 3.3.5 TrackPositionKeyframe
- `id`: PK
- `track_id`: FK
- `time_sec`: 키프레임 시각
- `x`, `y`: Top View 좌표
- `interp`: 보간 방식(기본 LINEAR)
- `created_at`
- unique(track_id, time_sec)

#### 3.3.6 Video (선택)
- `id`: PK
- `track_id`: FK
- `object_key`: MinIO key
- `duration_sec`, `fps`: optional
- `status`, `error_message`
- `created_at`

### 3.4 SQLAlchemy 2.0 매핑 설계 가이드 (구현 시 주의)
- 숫자 정밀도:
  - `start_sec/end_sec/time_sec`는 `Numeric(10, 3)` 권장
  - `x/y`는 `Numeric(10, 4)` 권장
- 인덱스:
  - `skeleton_layers(track_id, start_sec)`
  - `skeleton_layers(track_id, priority desc)`
  - `keyframes(track_id, time_sec)`
- 관계 로딩:
  - edit-state는 Track → Layers → Sources → Keyframes를 한 번에 가져오므로
  - `selectinload` 또는 적절한 join + group-by 조합을 사용해 N+1 회피
- 삭제 정책:
  - Layer 삭제는 `cascade`로 가능
  - Source 삭제는 레퍼런스 0개일 때만(GC 서비스/배치로 처리)

---

## 4) Skeleton 추출 워커 설계 (Celery 권장)

### 4.1 왜 워커가 필요한가?
- 영상 → 스켈레톤 추출은 CPU/GPU 비용이 크고 오래 걸릴 수 있다.
- API 서버와 분리하여:
  - API 응답 속도 안정화
  - 실패 재시도/관측성 확보
  - 추후 스케일링(워커 수 증설) 가능

### 4.2 권장 구성
- Broker/Backend:
  - MVP: Redis (간단)
  - 또는 RabbitMQ (운영 확장성)
- 구성 요소:
  - `worker/celery_app.py`: Celery 인스턴스
  - `worker/tasks/extract_skeleton.py`: 작업 함수
  - `app/services/layers_service.py`: enqueue 담당

### 4.3 작업 입력/출력 계약(Contract)

#### 4.3.1 enqueue 시점
`POST /tracks/{track_id}/layers`에서 VIDEO 기반 입력이면:
1) `Video` row 생성(선택)
2) `SkeletonSource` row 생성:
   - `status=PROCESSING`
   - `object_key`는 아직 null 또는 임시 경로(정책)
3) `SkeletonLayer` row 생성(사용 구간/priority 등)
4) Celery task enqueue: `extract_skeleton(source_id, video_object_key, project_id, track_slot, ...)`

#### 4.3.2 worker 처리 흐름 (표준)
1) DB에서 `SkeletonSource` 로드
2) MinIO에서 영상 다운로드(또는 스트리밍)
3) pose extraction 수행(초기에는 더미 생성 가능)
4) 스켈레톤 JSON 생성(표준 포맷)
5) MinIO에 JSON 업로드  
   - key: `skeleton/{project_id}/track_{slot}/{source_id}.json`
6) DB 업데이트  
   - `object_key` 세팅  
   - `status=READY`
7) 실패 시:  
   - `status=FAILED`  
   - `error_message` 저장  
   - (선택) Celery retry 정책 적용

### 4.4 JSON 포맷 버전/검증(최소)
MVP라도 아래는 권장:
- JSON 루트에 `meta` 포함
- meta에 `fps`, `num_joints`, `pose_model`, `num_frames_raw/sample` 최소 포함
- frames는 `frame_idx`, `time_sec`, `keypoints[]` 형태 유지
- 워커가 저장하기 전 간단한 검증:
  - frames 길이 == num_frames
  - keypoints 길이 == num_joints

### 4.5 관측성/재처리 전략
- 상태 조회는 `GET /layers/{id}` (source join)로 가능
- 실패한 경우:
  - 프론트는 status=FAILED를 표시
  - (추후) `POST /sources/{id}/retry` 같은 재시도 API 추가 가능
- 로그:
  - source_id, project_id, track_slot, minio_key를 반드시 로그에 남긴다.

### 4.6 SSE(옵션) vs 폴링(MVP)
- MVP는 폴링이 가장 단순:
  - 레이어 생성 직후 `GET /layers/{layer_id}`를 몇 초 간격으로 호출
  - READY 되면 asset presign 후 JSON fetch
- SSE는 2차:
  - 워커 완료 이벤트를 API 서버가 브로드캐스트하도록 구현

---

## 5) 실행 단위(서비스별 책임) 요약

### 5.1 API 서버가 집중해야 할 것
- Edit State 응답(조합/성능)
- presign PUT/GET 발급 (MinIO 접근 제어)
- layer CRUD + 정합성 검증(시간 범위/priority)
- 워커 enqueue + 상태 업데이트 흐름을 확실히 연결

### 5.2 워커가 집중해야 할 것
- 영상→스켈레톤 변환의 신뢰성/재시도
- 결과 JSON 포맷 표준화/검증
- MinIO 업로드 및 DB 상태 갱신의 원자성(가능한 한)

---

## 6) 최소 구현 체크리스트 (Agent가 바로 수행할 수 있게)
- [ ] docker-compose: postgres + minio + redis + api + worker
- [ ] Alembic 마이그레이션: enums + tables + indexes
- [ ] `/projects/{id}/edit-state` 구현(한 번에 필요한 데이터 제공)
- [ ] `/tracks/{id}/layers/upload-init` (presigned PUT)
- [ ] `/tracks/{id}/layers` (VIDEO/JSON 입력 분기)
- [ ] Celery task 실행 → skeleton_sources READY 전환
- [ ] `/assets/presign` + `/assets/presign/batch` (presigned GET)
- [ ] `/layers/{id}` 상태 조회(프론트 폴링)
- [ ] `/tracks/{id}/position-keyframes` 전체 교체

---

## 7) “확정 스펙” 선언
이 문서는 **MVP 구현을 위한 확정 설계**다.  
Agent는 기능을 추가하거나 모델을 재설계하지 말고, 위 구조를 그대로 코드로 옮겨 실행 가능 상태를 만드는 것을 우선 목표로 한다.
