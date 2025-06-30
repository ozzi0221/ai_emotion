@echo off
REM 회상치료 AI 아바타 Windows 설정 스크립트

title 회상치료 AI 아바타 - 설정

echo.
echo ============================================================
echo 🚀 회상치료 AI 아바타 - 감정비서 설정
echo    치매 어르신을 위한 따뜻한 회상치료 서비스
echo ============================================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 관리자 권한으로 실행 중
) else (
    echo ⚠️  일부 기능을 위해 관리자 권한이 필요할 수 있습니다.
)

REM 현재 디렉토리로 이동
cd /d "%~dp0"

echo 📋 시스템 요구사항 확인 중...

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    https://python.org 에서 Python 3.8 이상을 다운로드하여 설치하세요.
    echo.
    set /p continue="Python 없이 계속하시겠습니까? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
) else (
    echo ✅ Python 설치 확인됨
    python --version
)

REM Git 설치 확인
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git이 설치되어 있지 않습니다.
    echo    https://git-scm.com 에서 Git을 다운로드할 수 있습니다.
) else (
    echo ✅ Git 설치 확인됨
)

REM Node.js 확인 (선택적)
node --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Node.js가 설치되어 있지 않습니다 (선택적)
) else (
    echo ✅ Node.js 사용 가능
)

echo.
echo 📦 프로젝트 설정 시작...

REM 가상환경 생성
if not exist "venv\" (
    echo 🔧 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
) else (
    echo ℹ️  가상환경이 이미 존재합니다.
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

REM pip 업그레이드
echo 📦 pip 업그레이드 중...
python -m pip install --upgrade pip

REM 의존성 설치
if exist "requirements.txt" (
    echo 📦 Python 패키지 설치 중...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ Python 패키지 설치 완료
) else (
    echo ❌ requirements.txt 파일이 없습니다.
)

REM .env 파일 확인 및 생성
if not exist ".env" (
    if exist ".env.example" (
        echo 🔧 환경 설정 파일 생성 중...
        copy ".env.example" ".env"
        echo ✅ .env 파일이 생성되었습니다.
        echo.
        echo ⚠️  중요: .env 파일을 편집하여 실제 API 키를 설정해주세요!
        echo    특히 GEMINI_API_KEY를 실제 값으로 변경하세요.
        echo.
    ) else (
        echo ❌ .env.example 파일이 없습니다.
    )
) else (
    echo ✅ .env 파일이 이미 존재합니다.
)

REM 필요한 디렉토리 생성
echo 📁 필요한 디렉토리 생성 중...
if not exist "logs\" mkdir logs
if not exist "memory_data\" mkdir memory_data
if not exist "backups\" mkdir backups
if not exist "static\videos\" mkdir static\videos
if not exist "static\images\" mkdir static\images
if not exist "static\uploads\" mkdir static\uploads

echo ✅ 디렉토리 생성 완료

REM 로그 파일 생성
echo 📝 로그 파일 초기화 중...
echo. > logs\app.log
echo. > logs\security.log
echo. > logs\error.log

REM 비디오 파일 안내
if not exist "static\videos\avatar_idle.mp4" (
    echo.
    echo ⚠️  아바타 비디오 파일이 없습니다.
    echo    다음 파일들을 static\videos\ 디렉토리에 추가해주세요:
    echo    - avatar_idle.mp4 (대기 상태 비디오)
    echo    - avatar_speaking.mp4 (말하기 상태 비디오)
    echo    - avatar_idle.webm (대기 상태 비디오, WebM)
    echo    - avatar_speaking.webm (말하기 상태 비디오, WebM)
    echo.
    echo    비디오 사양:
    echo    - 해상도: 720x1280 (9:16 비율)
    echo    - 길이: 5-10초 루프
    echo    - 크기: 5MB 이하 권장
    echo.
)

REM 개발 도구 설치 (선택적)
echo.
set /p install_dev="개발 도구를 설치하시겠습니까? (코드 품질 검사 등) (y/n): "
if /i "%install_dev%"=="y" (
    echo 🛠️  개발 도구 설치 중...
    pip install black isort flake8 mypy pytest coverage bandit safety
    if errorlevel 1 (
        echo ⚠️  일부 개발 도구 설치에 실패했습니다.
    ) else (
        echo ✅ 개발 도구 설치 완료
    )
)

REM Docker 확인
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ℹ️  Docker가 설치되어 있지 않습니다.
    echo    Docker를 사용하려면 https://docker.com 에서 Docker Desktop을 설치하세요.
) else (
    echo ✅ Docker 사용 가능
    docker --version
    
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Docker Compose가 설치되어 있지 않습니다.
    ) else (
        echo ✅ Docker Compose 사용 가능
    )
)

echo.
echo ============================================================
echo 🎉 설정 완료!
echo ============================================================
echo.
echo 다음 단계:
echo.
echo 1. API 키 설정:
echo    .env 파일을 편집하여 GEMINI_API_KEY를 실제 값으로 변경하세요.
echo.
echo 2. 아바타 비디오 추가:
echo    static\videos\ 디렉토리에 아바타 비디오 파일들을 추가하세요.
echo.
echo 3. 개발 서버 실행:
echo    venv\Scripts\activate
echo    python app.py
echo    또는
echo    start.bat
echo.
echo 4. 브라우저 접속:
echo    http://localhost:5000
echo.
echo 5. 테스트 실행 (선택적):
echo    python -m pytest tests\
echo.
echo 문제가 발생하면 README.md를 참고하거나 이슈를 등록해주세요.
echo.

REM 자동 실행 여부 묻기
set /p auto_start="지금 개발 서버를 시작하시겠습니까? (y/n): "
if /i "%auto_start%"=="y" (
    echo.
    echo 🚀 개발 서버를 시작합니다...
    echo 💡 서버를 중지하려면 Ctrl+C를 누르세요.
    echo 💡 브라우저에서 http://localhost:5000 으로 접속하세요.
    echo.
    pause
    python app.py
) else (
    echo.
    echo 준비가 완료되면 다음 명령으로 서버를 시작하세요:
    echo   start.bat
    echo 또는
    echo   venv\Scripts\activate ^&^& python app.py
)

echo.
pause
