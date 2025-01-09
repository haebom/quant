import os
import sys

def _append_run_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller로 생성된 실행 파일인 경우
        base_dir = os.path.dirname(sys.executable)
        
        # 필요한 디렉토리들을 PATH에 추가
        os.environ['PATH'] = os.pathsep.join([
            base_dir,
            os.path.join(base_dir, 'templates'),
            os.path.join(base_dir, 'static'),
            os.environ.get('PATH', '')
        ])
        
        # 작업 디렉토리 설정
        if not os.path.exists('backtest_results'):
            os.makedirs('backtest_results')
        if not os.path.exists('reports'):
            os.makedirs('reports')

_append_run_path() 