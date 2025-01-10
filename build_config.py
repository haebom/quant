import sys
import os
import platform
from PyInstaller.__main__ import run

if __name__ == '__main__':
    sys.setrecursionlimit(sys.getrecursionlimit() * 5)
    
    # 운영체제별 경로 구분자 설정
    separator = ';' if sys.platform == 'win32' else ':'
    
    # 기본 디렉토리 생성
    for dir_name in ['static', 'templates']:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    
    # 기본 옵션 설정
    opts = [
        'app.py',
        '--name=QuantAnalysis',
        '--onefile',  # 단일 실행 파일로 빌드
        '--windowed',
        '--clean',
        '--noconfirm',
        
        # 데이터 파일 추가
        f'--add-data=templates{separator}templates',
        f'--add-data=static{separator}static',
        
        # 필수 패키지 import
        '--hidden-import=flask',
        '--hidden-import=werkzeug',
        '--hidden-import=jinja2',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=scipy',
        '--hidden-import=sklearn',
        '--hidden-import=ta',
        '--hidden-import=plotly',
        '--hidden-import=python_binance',
        '--hidden-import=websocket',
        '--hidden-import=requests',
        '--hidden-import=certifi',
        
        # 전체 패키지 수집
        '--collect-all=flask',
        '--collect-all=werkzeug',
        '--collect-all=pandas',
        '--collect-all=numpy',
        '--collect-all=ta',
        '--collect-all=plotly',
        '--collect-all=python_binance',
        
        # 디버그 옵션
        '--debug=imports',
        '--debug=bootloader',
    ]
    
    # macOS 특정 설정
    if sys.platform == 'darwin':
        icon_path = os.path.join('static', 'icon.icns')
        if os.path.exists(icon_path):
            opts.extend(['--icon', icon_path])
        
        is_arm = platform.machine() == 'arm64'
        opts.extend([
            f'--target-arch={"arm64" if is_arm else "x86_64"}',
            '--osx-bundle-identifier=com.haebom.quantanalysis',
            '--codesign-identity=-',  # 자체 서명 사용
            '--runtime-hook=macos_runtime_hook.py',
            '--exclude-module=tkinter',
            '--exclude-module=_tkinter',
            '--exclude-module=Tkinter',
            '--exclude-module=tcl',
            '--exclude-module=tk',
        ])
        
        # macOS 특정 환경 변수 설정
        os.environ['DYLD_LIBRARY_PATH'] = ''
        os.environ['DYLD_FRAMEWORK_PATH'] = ''
    
    # Windows 특정 설정
    elif sys.platform == 'win32':
        icon_path = os.path.join('static', 'icon.ico')
        if os.path.exists(icon_path):
            opts.extend(['--icon', icon_path])
        opts.extend([
            '--runtime-hook=windows_runtime_hook.py',
            '--version-file=version_info.txt',
        ])
    
    print(f"Building with options: {opts}")
    run(opts) 