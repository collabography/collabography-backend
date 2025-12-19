"""
프로젝트 관련 API만 테스트하는 스크립트

사용법:
    python tests/test_projects_only.py
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
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_db_health():
    """DB 헬스 체크 테스트"""
    print("\n[2] DB 헬스 체크 테스트")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health/db")
        print_response(response, "DB Health Check")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


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
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        assert result is not None, "Response body is None"
        assert "id" in result, "Response should contain 'id'"
        assert result["title"] == "테스트 프로젝트", "Title should match"
        print(f"✅ 프로젝트 생성 성공! ID: {result['id']}")
        return result["id"]


def test_list_projects():
    """프로젝트 목록 조회 테스트"""
    print("\n[4] 프로젝트 목록 조회 테스트")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects")
        result = print_response(response, "List Projects")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert result is not None, "Response body is None"
        assert "items" in result, "Response should contain 'items'"
        print(f"✅ 프로젝트 목록 조회 성공! 총 {len(result['items'])}개")
        return result


def test_get_project(project_id: int):
    """프로젝트 조회 테스트"""
    print(f"\n[5] 프로젝트 조회 테스트 (ID: {project_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects/{project_id}")
        result = print_response(response, "Get Project")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert result is not None, "Response body is None"
        assert result["id"] == project_id, "Project ID should match"
        print(f"✅ 프로젝트 조회 성공! 제목: {result.get('title', 'N/A')}")
        return result


def test_get_edit_state(project_id: int):
    """프로젝트 edit-state 조회 테스트"""
    print(f"\n[6] 프로젝트 Edit State 조회 테스트 (ID: {project_id})")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects/{project_id}/edit-state")
        result = print_response(response, "Get Edit State")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert result is not None, "Response body is None"
        assert "project" in result, "Response should contain 'project'"
        assert "tracks" in result, "Response should contain 'tracks'"
        assert len(result["tracks"]) == 3, "Should have 3 tracks"
        print(f"✅ Edit State 조회 성공! 트랙 수: {len(result['tracks'])}")
        return result


def test_create_multiple_projects():
    """여러 프로젝트 생성 테스트"""
    print("\n[7] 여러 프로젝트 생성 테스트")
    project_ids = []
    with httpx.Client() as client:
        for i in range(3):
            data = {
                "title": f"프로젝트 {i+1}"
            }
            response = client.post(
                f"{BASE_URL}/projects",
                json=data
            )
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"
            result = response.json()
            project_ids.append(result["id"])
            print(f"  - 프로젝트 {i+1} 생성: ID={result['id']}, 제목={result['title']}")
    print(f"✅ {len(project_ids)}개 프로젝트 생성 완료!")
    return project_ids


def test_list_projects_with_pagination():
    """페이지네이션 테스트"""
    print("\n[8] 페이지네이션 테스트")
    with httpx.Client() as client:
        # limit=2로 조회
        response = client.get(f"{BASE_URL}/projects?limit=2")
        result = print_response(response, "List Projects (limit=2)")
        assert response.status_code == 200
        assert len(result["items"]) <= 2, "Should return at most 2 items"
        
        if result.get("next_cursor"):
            print(f"  - 다음 커서: {result['next_cursor']}")
            # 다음 페이지 조회
            response2 = client.get(f"{BASE_URL}/projects?limit=2&cursor={result['next_cursor']}")
            result2 = response2.json()
            print(f"  - 다음 페이지: {len(result2['items'])}개 항목")
        print("✅ 페이지네이션 테스트 완료!")


def test_get_nonexistent_project():
    """존재하지 않는 프로젝트 조회 테스트 (404 에러 확인)"""
    print("\n[9] 존재하지 않는 프로젝트 조회 테스트 (404 에러 확인)")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/projects/99999")
        print_response(response, "Get Nonexistent Project")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ 404 에러 정상 반환!")


def run_project_tests():
    """프로젝트 관련 모든 테스트 실행"""
    print("\n" + "="*60)
    print("프로젝트 API 테스트 시작")
    print("="*60)

    try:
        # 1. 헬스 체크
        test_health_check()
        test_db_health()

        # 2. 프로젝트 생성
        project_id = test_create_project()
        
        # 3. 프로젝트 목록 조회
        test_list_projects()
        
        # 4. 프로젝트 조회
        test_get_project(project_id)
        
        # 5. Edit State 조회
        test_get_edit_state(project_id)
        
        # 6. 여러 프로젝트 생성
        test_create_multiple_projects()
        
        # 7. 페이지네이션 테스트
        test_list_projects_with_pagination()
        
        # 8. 에러 케이스 테스트
        test_get_nonexistent_project()

        print("\n" + "="*60)
        print("✅ 모든 프로젝트 API 테스트 완료!")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_project_tests()

