"""
API 엔드포인트 테스트 예제 스크립트

사용법:
    python tests/test_api_examples.py

또는 개별 함수를 실행:
    python -c "from tests.test_api_examples import test_create_project; test_create_project()"
"""
import json
from typing import Any

import httpx

# API 기본 URL
BASE_URL = "http://localhost:8000"


def print_response(response: httpx.Response, title: str = "Response") -> dict[str, Any] | None:
    """응답을 보기 좋게 출력"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        data = response.json()
        print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception:
        print(f"Body: {response.text}")
        return None


def test_health_check():
    """헬스 체크 테스트"""
    print("\n[1] 헬스 체크 테스트")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        print_response(response, "Health Check")
        assert response.status_code == 200


def test_db_health():
    """DB 헬스 체크 테스트"""
    print("\n[2] DB 헬스 체크 테스트")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health/db")
        print_response(response, "DB Health Check")
        assert response.status_code == 200


def test_create_project():
    """프로젝트 생성 테스트"""
    print("\n[3] 프로젝트 생성 테스트")
    with httpx.Client() as client:
        data = {
            "title": "테스트 프로젝트"
        }
        response = client.post(
            f"{BASE_URL}/projects",
            json=data
        )
        result = print_response(response, "Create Project")
        assert response.status_code == 201
        return result["id"] if result else None


def test_list_projects():
    """프로젝트 목록 조회 테스트"""
    print("\n[4] 프로젝트 목록 조회 테스트")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects")
        result = print_response(response, "List Projects")
        assert response.status_code == 200
        return result


def test_get_project(project_id: int):
    """프로젝트 조회 테스트"""
    print(f"\n[5] 프로젝트 조회 테스트 (ID: {project_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects/{project_id}")
        result = print_response(response, "Get Project")
        assert response.status_code == 200
        return result


def test_get_edit_state(project_id: int):
    """프로젝트 edit-state 조회 테스트"""
    print(f"\n[6] 프로젝트 Edit State 조회 테스트 (ID: {project_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects/{project_id}/edit-state")
        result = print_response(response, "Get Edit State")
        assert response.status_code == 200
        return result


def test_music_upload(project_id: int):
    """음악 파일 업로드 테스트"""
    print(f"\n[7] 음악 파일 업로드 테스트 (Project ID: {project_id})")
    with httpx.Client() as client:
        # 더미 파일 생성
        files = {
            "file": ("test_music.mp3", b"fake audio content", "audio/mpeg")
        }
        data = {
            "duration_sec": "180.5",
            "bpm": "120.0"
        }
        response = client.post(
            f"{BASE_URL}/projects/{project_id}/music/upload",
            files=files,
            data=data
        )
        result = print_response(response, "Music Upload")
        assert response.status_code == 201
        return result


def test_layer_upload(track_id: int):
    """레이어 파일 업로드 테스트"""
    print(f"\n[9] 레이어 파일 업로드 테스트 (Track ID: {track_id})")
    with httpx.Client() as client:
        # 더미 파일 생성
        files = {
            "file": ("test_video.mp4", b"fake video content", "video/mp4")
        }
        data = {
            "start_sec": "0.0",
            "end_sec": "10.0",
            "priority": "1",
            "label": "테스트 레이어"
        }
        response = client.post(
            f"{BASE_URL}/tracks/{track_id}/layers/upload",
            files=files,
            data=data
        )
        result = print_response(response, "Layer Upload")
        assert response.status_code == 201
        return result


def test_get_layer(layer_id: int):
    """레이어 조회 테스트"""
    print(f"\n[11] 레이어 조회 테스트 (Layer ID: {layer_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/tracks/1/layers/{layer_id}")
        result = print_response(response, "Get Layer")
        assert response.status_code == 200
        return result


def test_update_layer(layer_id: int):
    """레이어 업데이트 테스트"""
    print(f"\n[12] 레이어 업데이트 테스트 (Layer ID: {layer_id})")
    with httpx.Client() as client:
        data = {
            "priority": 2,
            "label": "업데이트된 레이어"
        }
        response = client.patch(
            f"{BASE_URL}/tracks/1/layers/{layer_id}",
            json=data
        )
        result = print_response(response, "Update Layer")
        assert response.status_code == 200
        return result


def test_upsert_keyframes(track_id: int):
    """키프레임 전체 교체 테스트"""
    print(f"\n[13] 키프레임 Upsert 테스트 (Track ID: {track_id})")
    with httpx.Client() as client:
        data = {
            "keyframes": [
                {
                    "time_sec": 0.0,
                    "x": 0.0,
                    "y": 0.0,
                    "interp": "LINEAR"
                },
                {
                    "time_sec": 5.0,
                    "x": 100.0,
                    "y": 100.0,
                    "interp": "LINEAR"
                },
                {
                    "time_sec": 10.0,
                    "x": 200.0,
                    "y": 200.0,
                    "interp": "STEP"
                }
            ]
        }
        response = client.put(
            f"{BASE_URL}/tracks/{track_id}/position-keyframes",
            json=data
        )
        result = print_response(response, "Upsert Keyframes")
        assert response.status_code == 200
        return result


def test_get_keyframes(track_id: int):
    """키프레임 목록 조회 테스트"""
    print(f"\n[14] 키프레임 목록 조회 테스트 (Track ID: {track_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/tracks/{track_id}/position-keyframes")
        result = print_response(response, "Get Keyframes")
        assert response.status_code == 200
        return result


def test_asset_presign():
    """자산 presigned GET URL 발급 테스트"""
    print("\n[15] 자산 Presigned GET URL 발급 테스트")
    with httpx.Client() as client:
        data = {
            "object_key": "skeleton/test/track_1/source_1.json"
        }
        response = client.post(
            f"{BASE_URL}/assets/presign",
            json=data
        )
        result = print_response(response, "Asset Presign")
        assert response.status_code == 200
        return result


def test_asset_presign_batch():
    """자산 presigned GET URL 일괄 발급 테스트"""
    print("\n[16] 자산 Presigned GET URL 일괄 발급 테스트")
    with httpx.Client() as client:
        data = {
            "object_keys": [
                "skeleton/test/track_1/source_1.json",
                "skeleton/test/track_2/source_2.json"
            ]
        }
        response = client.post(
            f"{BASE_URL}/assets/presign/batch",
            json=data
        )
        result = print_response(response, "Asset Presign Batch")
        assert response.status_code == 200
        return result


def run_all_tests():
    """모든 테스트를 순차적으로 실행"""
    print("\n" + "="*60)
    print("API 엔드포인트 통합 테스트 시작")
    print("="*60)

    try:
        # 1. 헬스 체크
        test_health_check()
        test_db_health()

        # 2. 프로젝트 관련
        project_id = test_create_project()
        test_list_projects()
        test_get_project(project_id)
        edit_state = test_get_edit_state(project_id)

        # 3. 트랙 ID 추출 (첫 번째 트랙)
        track_id = edit_state["tracks"][0]["id"] if edit_state and edit_state.get("tracks") else 1

        # 4. 음악 관련
        test_music_upload(project_id)

        # 5. 레이어 관련
        layer = test_layer_upload(track_id)
        if layer:
            layer_id = layer["id"]
            test_get_layer(layer_id)
            test_update_layer(layer_id)

        # 6. 키프레임 관련
        test_upsert_keyframes(track_id)
        test_get_keyframes(track_id)

        # 7. 자산 관련
        test_asset_presign()
        test_asset_presign_batch()

        print("\n" + "="*60)
        print("모든 테스트 완료!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

