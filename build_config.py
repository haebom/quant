import sys
import os
import platform
from PyInstaller.__main__ import run

if __name__ == '__main__':
    sys.setrecursionlimit(sys.getrecursionlimit() * 5)
    
    # 운영체제별 경로 구분자 설정
    separator = ';' if sys.platform == 'win32' else ':'
    
    # static 디렉토리가 없으면 생성
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 기본 옵션 설정
    opts = [
        'app.py',  # 메인 스크립트
        '--name=QuantAnalysis',  # 실행 파일 이름
        '--onedir',  # 단일 디렉토리로 생성
        '--windowed',  # GUI 모드 (콘솔 창 숨김)
        f'--add-data=templates{separator}templates',  # 템플릿 디렉토리 포함
        f'--add-data=static{separator}static',  # 정적 파일 디렉토리 포함
        # Core Dependencies
        '--hidden-import=flask',
        '--hidden-import=werkzeug',
        '--hidden-import=markupsafe',
        '--collect-all=flask',
        '--collect-all=werkzeug',
        # Data Processing & Analysis
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=scipy',
        '--hidden-import=sklearn',
        '--collect-all=pandas',
        '--collect-all=numpy',
        # Technical Analysis
        '--hidden-import=ta',
        '--collect-all=ta',
        # Visualization
        '--hidden-import=plotly',
        '--collect-all=plotly',
        # Utilities
        '--hidden-import=python_binance',
        '--hidden-import=websocket',
        '--hidden-import=requests',
        '--hidden-import=dotenv',
        '--collect-all=python_binance',
        # Build options
        '--clean',  # 빌드 전 캐시 정리
        '--noconfirm',  # 기존 빌드 디렉토리 자동 삭제
    ]
    
    # 운영체제별 설정
    if sys.platform == 'darwin':  # macOS
        icon_path = os.path.join('static', 'icon.icns')
        if os.path.exists(icon_path):
            opts.extend(['--icon', icon_path])
            
        # Check if running on Apple Silicon
        is_arm = platform.machine() == 'arm64'
        
        opts.extend([
            f'--target-arch={"arm64" if is_arm else "x86_64"}',  # 현재 아키텍처에 맞게 설정
            '--codesign-identity=',  # 자동 코드사이닝
            '--osx-bundle-identifier=com.haebom.quantanalysis',
            '--debug=imports',
            '--exclude-module=tkinter',  # 불필요한 모듈 제외
            '--exclude-module=_tkinter',
            '--exclude-module=Tkinter',
            '--exclude-module=tcl',
            '--exclude-module=tk',
        ])
        
        # Add runtime hooks for SSL/Socket only if needed
        if is_arm:
            opts.extend([
                '--runtime-hook=macos_runtime_hook.py',
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