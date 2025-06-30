@echo off
chcp 65001 > nul
title 회상치료 AI 아바타 - 감정비서

echo.
echo ============================================================
echo 🎯 회상치료 AI 아바타 - 감정비서
echo    치매 어르신을 위한 따뜻한 회상치료 서비스
echo ============================================================
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    https://python.org 에서 Python을 다운로드하여 설치하세요.
    pause
    exit /b 1
)

REM 가상환경 존재 확인
if not exist "venv\" (
    echo 📦 가상환경을 생성하고 있습니다...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo 🔧 가상환경을 활성화하고 있습니다...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

REM 필요한 패키지 설치
if exist "requirements.txt" (
    echo 📦 필요한 패키지를 설치하고 있습니다...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
) else (
    echo ❌ requirements.txt 파일이 없습니다.
    pause
    exit /b 1
)

REM .env 파일 확인
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️  .env 파일이 없습니다.
        echo    .env.example 파일을 .env로 복사합니다...
        copy ".env.example" ".env"
        echo.
        echo ✏️  이제 .env 파일을 열어서 실제 API 키로 수정해주세요:
        echo    - GEMINI_API_KEY=your-gemini-api-key-here
        echo.
        set /p continue="계속 진행하시겠습니까? (y/n): "
        if /i not "%continue%"=="y" if /i not "%continue%"=="yes" (
            echo 설정을 완료한 후 다시 실행해주세요.
            pause
            exit /b 0
        )
    ) else (
        echo ❌ .env.example 파일이 없습니다.
        pause
        exit /b 1
    )
)

REM 비디오 파일 확인
if not exist "static\videos\avatar_idle.mp4" (
    echo ⚠️  아바타 비디오 파일이 없습니다.
    echo    static\videos\ 폴더의 README.md를 확인하여 비디오 파일을 준비해주세요.
    echo.
    set /p continue="비디오 파일 없이 계속 진행하시겠습니까? (y/n): "
    if /i not "%continue%"=="y" if /i not "%continue%"=="yes" (
        echo 비디오 파일을 준비한 후 다시 실행해주세요.
        pause
        exit /b 0
    )
)

echo.
echo ✅ 모든 준비가 완료되었습니다!
echo 🚀 서버를 시작합니다...
echo.
echo 💡 서버가 시작되면 브라우저에서 http://localhost:5000 으로 접속하세요.
echo 💡 서버를 종료하려면 Ctrl+C를 누르세요.
echo.

REM Flask 서버 시작
python run.py

echo.
echo 👋 서버가 종료되었습니다.
echo    이용해 주셔서 감사합니다.
pause
