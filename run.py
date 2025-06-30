#!/usr/bin/env python3
"""
회상치료 AI 아바타 서비스 실행 스크립트

이 스크립트는 서비스를 쉽게 시작할 수 있도록 도와주는 런처입니다.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"   현재 버전: {sys.version}")
        return False
    return True

def check_virtual_env():
    """가상환경 확인"""
    if sys.prefix == sys.base_prefix:
        print("⚠️  가상환경이 활성화되지 않았습니다.")
        print("   다음 명령어로 가상환경을 생성하고 활성화하세요:")
        if platform.system() == "Windows":
            print("   python -m venv venv")
            print("   venv\\Scripts\\activate")
        else:
            print("   python -m venv venv")
            print("   source venv/bin/activate")
        return False
    return True

def install_requirements():
    """필요한 패키지 설치"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt 파일이 없습니다.")
        return False
    
    print("📦 필요한 패키지를 설치하고 있습니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 패키지 설치가 완료되었습니다.")
        return True
    except subprocess.CalledProcessError:
        print("❌ 패키지 설치에 실패했습니다.")
        return False

def check_env_file():
    """환경 변수 파일 확인"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env 파일이 없습니다.")
            print("   .env.example 파일을 참고하여 .env 파일을 생성하세요.")
            
            # 자동으로 .env 파일 생성 여부 묻기
            response = input("   .env.example을 복사하여 .env 파일을 생성하시겠습니까? (y/n): ")
            if response.lower() in ['y', 'yes', '예']:
                try:
                    import shutil
                    shutil.copy(env_example, env_file)
                    print("✅ .env 파일이 생성되었습니다.")
                    print("   이제 .env 파일을 열어서 실제 API 키로 수정해주세요.")
                    return True
                except Exception as e:
                    print(f"❌ .env 파일 생성 실패: {e}")
                    return False
            return False
        else:
            print("❌ .env.example 파일도 없습니다.")
            return False
    return True

def check_video_files():
    """아바타 비디오 파일 확인"""
    video_dir = Path("static/videos")
    required_videos = ["avatar_idle.mp4", "avatar_speaking.mp4"]
    
    missing_videos = []
    for video in required_videos:
        if not (video_dir / video).exists():
            missing_videos.append(video)
    
    if missing_videos:
        print("⚠️  다음 아바타 비디오 파일들이 필요합니다:")
        for video in missing_videos:
            print(f"   - static/videos/{video}")
        print("   static/videos/README.md 파일을 참고하여 비디오 파일을 준비해주세요.")
        
        response = input("   비디오 파일 없이 계속 진행하시겠습니까? (y/n): ")
        if response.lower() not in ['y', 'yes', '예']:
            return False
    
    return True

def start_server():
    """Flask 서버 시작"""
    print("🚀 회상치료 AI 아바타 서버를 시작합니다...")
    print("💝 어르신들의 소중한 추억과 함께하는 감정비서")
    print("-" * 50)
    
    try:
        # Flask 앱 실행
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("🎯 회상치료 AI 아바타 - 감정비서")
    print("   치매 어르신을 위한 따뜻한 회상치료 서비스")
    print("=" * 60)
    
    # 시스템 체크
    if not check_python_version():
        return
    
    print("✅ Python 버전 확인 완료")
    
    if not check_virtual_env():
        return
    
    print("✅ 가상환경 확인 완료")
    
    if not install_requirements():
        return
    
    if not check_env_file():
        return
    
    print("✅ 환경 설정 확인 완료")
    
    if not check_video_files():
        return
    
    print("✅ 리소스 파일 확인 완료")
    
    # 서버 시작
    start_server()

if __name__ == "__main__":
    main()
