#!/bin/bash

# 가상환경 활성화 (필요한 경우)
# source venv/bin/activate

# 필요한 패키지 설치
pip install -r requirements.txt

# PyInstaller를 사용하여 실행 파일 생성
pyinstaller build_mac.spec

# 빌드된 파일 위치 안내
echo "빌드가 완료되었습니다."
echo "실행 파일은 dist/CryptoAssistant 디렉토리에 있습니다." 