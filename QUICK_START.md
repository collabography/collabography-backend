# 빠른 시작 가이드

## 문제: 패키지가 설치되어 있는데도 모듈을 찾을 수 없음

이 문제는 **가상환경이 활성화되지 않아서** 발생합니다.

## 해결 방법

### 1단계: 가상환경 활성화 확인

터미널에서 다음 명령어로 가상환경이 활성화되어 있는지 확인:

```bash
# 가상환경이 활성화되어 있으면 프롬프트에 (venv)가 표시됩니다
which python
```

가상환경이 활성화되어 있지 않다면:

```bash
# 프로젝트 디렉토리로 이동
cd /Users/kiminsoo/Desktop/04.MINPROJECT/00.collabography/collabography-backend

# 가상환경 활성화
source venv/bin/activate

# 활성화 확인 (프롬프트에 (venv)가 표시되어야 함)
```

### 2단계: 서버 실행

가상환경이 활성화된 상태에서:

```bash
uvicorn app.main:app --reload
```

## 확인 방법

가상환경이 제대로 활성화되었는지 확인:

```bash
# Python 경로 확인 (venv 경로가 포함되어야 함)
python -c "import sys; print(sys.executable)"

# 패키지 확인
python -c "import pydantic_settings; print('✅ pydantic_settings 설치됨')"
```

## 주의사항

- **새 터미널 창을 열 때마다** 가상환경을 다시 활성화해야 합니다
- 가상환경이 활성화되지 않으면 시스템 Python을 사용하게 되어 패키지를 찾을 수 없습니다

## 자동 활성화 (선택사항)

터미널을 열 때 자동으로 가상환경을 활성화하려면 `~/.zshrc`에 추가:

```bash
# 프로젝트 디렉토리로 이동하면 자동 활성화
cd() {
    builtin cd "$@"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
}
```

