@echo off

REM 가상환경 활성화 (필요한 경우)
REM call venv\Scripts\activate

REM 필요한 패키지 설치
pip install -r requirements.txt

REM PyInstaller를 사용하여 실행 파일 생성
pyinstaller build_windows.spec

echo 빌드가 완료되었습니다.
echo 실행 파일은 dist\CryptoAssistant.exe 에 있습니다.
pause 