# 프로젝트 설정 가이드

## 문제: ModuleNotFoundError: No module named 'pydantic_settings'

이 에러는 필요한 Python 패키지가 설치되지 않아서 발생합니다.

## 해결 방법

### 방법 1: 가상환경 사용 (권장)

```bash
# 1. 가상환경 생성
python3.11 -m venv .venv

# 2. 가상환경 활성화
source .venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
uvicorn app.main:app --reload
```

### 방법 2: 직접 설치 (가상환경 없이)

```bash
# 필요한 패키지 설치
pip3.11 install -r requirements.txt

# 또는 개별 설치
pip3.11 install pydantic-settings==2.6.1
pip3.11 install fastapi==0.115.6
pip3.11 install uvicorn[standard]==0.32.1
```

### 방법 3: Conda 환경 사용 (Anaconda 사용 시)

```bash
# Conda 환경 생성
conda create -n collabography python=3.11
conda activate collabography

# 패키지 설치
pip install -r requirements.txt
```

## 설치 확인

패키지가 제대로 설치되었는지 확인:

```bash
python3.11 -c "import pydantic_settings; print('pydantic_settings 설치됨')"
python3.11 -c "import fastapi; print('fastapi 설치됨')"
```

## 서버 실행

설치가 완료되면:

```bash
uvicorn app.main:app --reload
```

## 추가 문제 해결

### 권한 문제가 발생하는 경우

```bash
# 사용자 디렉토리에 설치
pip install --user -r requirements.txt
```

### 여러 Python 버전이 있는 경우

```bash
# Python 3.11이 어디에 있는지 확인
which python3.11

# 특정 Python 버전으로 설치
python3.11 -m pip install -r requirements.txt
```

