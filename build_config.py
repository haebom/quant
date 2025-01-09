import sys
import os
from PyInstaller.__main__ import run

if __name__ == '__main__':
    sys.setrecursionlimit(sys.getrecursionlimit() * 5)
    
    # 기본 옵션 설정
    opts = [
        'app.py',  # 메인 스크립트
        '--name=QuantAnalysis',  # 실행 파일 이름
        '--onedir',  # 단일 디렉토리로 생성
        '--windowed',  # GUI 모드 (콘솔 창 숨김)
        '--add-data=templates:templates',  # 템플릿 디렉토리 포함
        '--add-data=static:static',  # 정적 파일 디렉토리 포함
        '--hidden-import=plotly',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=scipy',
        '--hidden-import=sklearn',  # scikit-learn 대신 sklearn 사용
        '--clean',  # 빌드 전 캐시 정리
        '--noconfirm',  # 기존 빌드 디렉토리 자동 삭제
    ]
    
    # 운영체제별 설정
    if sys.platform == 'darwin':  # macOS
        icon_path = os.path.join('static', 'icon.icns')
        if os.path.exists(icon_path):
            opts.extend(['--icon', icon_path])
        opts.extend([
            '--target-arch=arm64',  # M1/M2 Mac용 설정
            '--codesign-identity=-',  # 코드사이닝 비활성화
        ])
    elif sys.platform == 'win32':  # Windows
        icon_path = os.path.join('static', 'icon.ico')
        if os.path.exists(icon_path):
            opts.extend(['--icon', icon_path])
        opts.extend([
            '--runtime-hook=windows_runtime_hook.py',
            '--version-file=version_info.txt',
        ])
    
    print(f"Building with options: {opts}")
    run(opts) 