import os
import sys

def _append_path_if_exists(path):
    if os.path.exists(path):
        sys.path.append(path)

# Add potential Python framework paths
_append_path_if_exists('/System/Library/Frameworks/Python.framework/Versions/Current/lib/python3.9/site-packages')
_append_path_if_exists(os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages'))

# Set environment variables for macOS
os.environ['DYLD_LIBRARY_PATH'] = os.path.dirname(sys.executable)
os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem') 