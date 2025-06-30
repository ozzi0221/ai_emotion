#!/usr/bin/env python3
"""
회상치료 AI 아바타 시스템 설정 스크립트

이 스크립트는 처음 설치 시 필요한 초기 설정을 자동으로 수행합니다.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

class ColorPrint:
    """컬러 출력을 위한 클래스"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def print_colored(cls, text, color):
        print(f"{color}{text}{cls.ENDC}")

    @classmethod
    def success(cls, text):
        cls.print_colored(f"✅ {text}", cls.GREEN)

    @classmethod
    def error(cls, text):
        cls.print_colored(f"❌ {text}", cls.RED)

    @classmethod
    def warning(cls, text):
        cls.print_colored(f"⚠️  {text}", cls.YELLOW)

    @classmethod
    def info(cls, text):
        cls.print_colored(f"ℹ️  {text}", cls.BLUE)

    @classmethod
    def header(cls, text):
        print("\n" + "=" * 60)
        cls.print_colored(text, cls.BOLD + cls.CYAN)
        print("=" * 60)

def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        ColorPrint.error(f"Python 3.8 이상이 필요합니다. 현재 버전: {version.major}.{version.minor}")
        return False
    
    ColorPrint.success(f"Python 버전 확인 완료: {version.major}.{version.minor}.{version.micro}")
    return True

def check_system_dependencies():
    """시스템 종속성 확인"""
    ColorPrint.info("시스템 종속성 확인 중...")
    
    dependencies = {
        'git': 'Git 버전 관리 시스템',
        'curl': 'HTTP 클라이언트',
        'tar': '압축 도구'
    }
    
    missing = []
    for cmd, description in dependencies.items():
        if not shutil.which(cmd):
            missing.append(f"{cmd} ({description})")
        else:
            ColorPrint.success(f"{cmd} 확인됨")
    
    if missing:
        ColorPrint.warning(f"다음 도구들이 필요합니다: {', '.join(missing)}")
        return False
    
    return True

def create_virtual_environment():
    """가상환경 생성"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        ColorPrint.info("가상환경이 이미 존재합니다.")
        return True
    
    ColorPrint.info("가상환경 생성 중...")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        ColorPrint.success("가상환경 생성 완료")
        return True
    except subprocess.CalledProcessError:
        ColorPrint.error("가상환경 생성 실패")
        return False

def install_dependencies():
    """의존성 설치"""
    ColorPrint.info("Python 패키지 설치 중...")
    
    # 가상환경의 Python 경로 결정
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python.exe")
        pip_path = Path("venv/Scripts/pip.exe")
    else:  # Unix-like
        python_path = Path("venv/bin/python")
        pip_path = Path("venv/bin/pip")
    
    if not python_path.exists():
        ColorPrint.error("가상환경 Python을 찾을 수 없습니다")
        return False
    
    try:
        # pip 업그레이드
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # requirements.txt 설치
        if Path("requirements.txt").exists():
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
            ColorPrint.success("Python 패키지 설치 완료")
        else:
            ColorPrint.warning("requirements.txt를 찾을 수 없습니다")
        
        return True
    except subprocess.CalledProcessError:
        ColorPrint.error("Python 패키지 설치 실패")
        return False

def create_env_file():
    """환경 변수 파일 생성"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        ColorPrint.info(".env 파일이 이미 존재합니다.")
        return True
    
    if not env_example.exists():
        ColorPrint.error(".env.example 파일을 찾을 수 없습니다")
        return False
    
    ColorPrint.info(".env 파일 생성 중...")
    
    try:
        shutil.copy(env_example, env_file)
        ColorPrint.success(".env 파일 생성 완료")
        ColorPrint.warning("실제 API 키로 .env 파일을 수정해주세요!")
        return True
    except Exception as e:
        ColorPrint.error(f".env 파일 생성 실패: {e}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    ColorPrint.info("필요한 디렉토리 생성 중...")
    
    directories = [
        "logs",
        "memory_data",
        "backups",
        "static/videos",
        "static/images",
        "static/uploads",
        "docker/ssl"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            ColorPrint.success(f"디렉토리 생성: {directory}")
        else:
            ColorPrint.info(f"디렉토리 존재: {directory}")
    
    return True

def create_placeholder_files():
    """플레이스홀더 파일 생성"""
    ColorPrint.info("플레이스홀더 파일 생성 중...")
    
    # 로그 파일 플레이스홀더
    log_files = [
        "logs/app.log",
        "logs/security.log",
        "logs/error.log"
    ]
    
    for log_file in log_files:
        log_path = Path(log_file)
        if not log_path.exists():
            log_path.touch()
            ColorPrint.success(f"로그 파일 생성: {log_file}")
    
    # 비디오 파일 README
    video_readme = Path("static/videos/README_VIDEOS.md")
    if not video_readme.exists():
        video_readme.write_text("""# 아바타 비디오 파일

이 디렉토리에는 다음 아바타 비디오 파일들이 필요합니다:

- `avatar_idle.mp4` - 대기 상태 비디오
- `avatar_speaking.mp4` - 말하기 상태 비디오  
- `avatar_idle.webm` - 대기 상태 비디오 (WebM)
- `avatar_speaking.webm` - 말하기 상태 비디오 (WebM)

## 비디오 사양
- 해상도: 720x1280 (9:16 비율)
- 길이: 5-10초 루프
- 포맷: MP4 + WebM
- 크기: 5MB 이하 권장

비디오 파일이 없으면 기본 플레이스홀더가 사용됩니다.
""")
        ColorPrint.success("비디오 README 생성")
    
    return True

def setup_git_hooks():
    """Git 훅 설정"""
    if not Path(".git").exists():
        ColorPrint.info("Git 저장소가 아닙니다. Git 훅 설정을 건너뜁니다.")
        return True
    
    ColorPrint.info("Git 훅 설정 중...")
    
    try:
        # pre-commit 설치 확인
        subprocess.run(["pre-commit", "--version"], check=True, capture_output=True)
        
        # pre-commit 훅 설치
        subprocess.run(["pre-commit", "install"], check=True)
        ColorPrint.success("Git 훅 설정 완료")
        return True
    except subprocess.CalledProcessError:
        ColorPrint.warning("pre-commit이 설치되지 않았습니다. 수동으로 설치하세요: pip install pre-commit")
        return True
    except FileNotFoundError:
        ColorPrint.warning("pre-commit 명령을 찾을 수 없습니다")
        return True

def create_systemd_service():
    """Systemd 서비스 파일 생성 (Linux만)"""
    if os.name == 'nt':
        return True
    
    ColorPrint.info("Systemd 서비스 파일 생성 중...")
    
    current_dir = Path.cwd()
    service_content = f"""[Unit]
Description=회상치료 AI 아바타 서비스
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={current_dir}
Environment=PATH={current_dir}/venv/bin
ExecStart={current_dir}/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("avatar-emotion-assistant.service")
    service_file.write_text(service_content)
    
    ColorPrint.success("Systemd 서비스 파일 생성: avatar-emotion-assistant.service")
    ColorPrint.info("설치하려면: sudo cp avatar-emotion-assistant.service /etc/systemd/system/")
    
    return True

def check_optional_tools():
    """선택적 도구들 확인"""
    ColorPrint.info("선택적 도구 확인 중...")
    
    optional_tools = {
        'docker': 'Docker 컨테이너화',
        'docker-compose': 'Docker Compose 오케스트레이션',
        'jq': 'JSON 처리 도구',
        'nginx': 'Nginx 웹 서버'
    }
    
    for tool, description in optional_tools.items():
        if shutil.which(tool):
            ColorPrint.success(f"{tool} 사용 가능")
        else:
            ColorPrint.info(f"{tool} 없음 ({description})")

def generate_setup_report():
    """설정 보고서 생성"""
    ColorPrint.info("설정 보고서 생성 중...")
    
    report = {
        "setup_date": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "directories_created": [
            "logs", "memory_data", "backups", 
            "static/videos", "static/images", "static/uploads"
        ],
        "files_created": [
            ".env", "logs/app.log", "logs/security.log"
        ],
        "next_steps": [
            "Edit .env file with actual API keys",
            "Add avatar video files to static/videos/",
            "Run 'make test' to verify installation",
            "Start development server with 'make run'"
        ]
    }
    
    report_file = Path("setup_report.json")
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    ColorPrint.success("설정 보고서 생성: setup_report.json")
    return True

def print_next_steps():
    """다음 단계 안내"""
    ColorPrint.header("🎉 설정 완료! 다음 단계")
    
    steps = [
        "1. .env 파일을 편집하여 실제 API 키를 설정하세요",
        "2. static/videos/ 디렉토리에 아바타 비디오 파일을 추가하세요",
        "3. 가상환경을 활성화하세요:",
        "   Windows: venv\\Scripts\\activate",
        "   Linux/Mac: source venv/bin/activate",
        "4. 개발 서버를 실행하세요:",
        "   python app.py 또는 make run",
        "5. 브라우저에서 http://localhost:5000 접속",
        "6. 테스트 실행: make test"
    ]
    
    for step in steps:
        if step.startswith("   "):
            ColorPrint.info(step)
        else:
            ColorPrint.print_colored(step, ColorPrint.CYAN)

def main():
    """메인 함수"""
    ColorPrint.header("🚀 회상치료 AI 아바타 - 감정비서 설정")
    
    # 체크리스트
    checks = [
        ("Python 버전 확인", check_python_version),
        ("시스템 종속성 확인", check_system_dependencies),
        ("가상환경 생성", create_virtual_environment),
        ("Python 패키지 설치", install_dependencies),
        ("환경 변수 파일 생성", create_env_file),
        ("디렉토리 생성", create_directories),
        ("플레이스홀더 파일 생성", create_placeholder_files),
        ("Git 훅 설정", setup_git_hooks),
        ("Systemd 서비스 생성", create_systemd_service),
        ("선택적 도구 확인", check_optional_tools),
        ("설정 보고서 생성", generate_setup_report)
    ]
    
    failed_checks = []
    
    for description, check_func in checks:
        ColorPrint.info(f"진행 중: {description}")
        
        try:
            if not check_func():
                failed_checks.append(description)
                ColorPrint.error(f"실패: {description}")
            else:
                ColorPrint.success(f"완료: {description}")
        except Exception as e:
            failed_checks.append(description)
            ColorPrint.error(f"오류 발생 ({description}): {e}")
    
    # 결과 요약
    ColorPrint.header("📊 설정 결과")
    
    if failed_checks:
        ColorPrint.warning(f"실패한 항목: {len(failed_checks)}")
        for item in failed_checks:
            ColorPrint.error(f"  - {item}")
        
        ColorPrint.info("실패한 항목들을 수동으로 해결해주세요.")
    else:
        ColorPrint.success("모든 설정이 성공적으로 완료되었습니다!")
    
    print_next_steps()

if __name__ == "__main__":
    main()
