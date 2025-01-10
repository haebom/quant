import os
import sys
import site

def _append_path_if_exists(path):
    if os.path.exists(path):
        sys.path.append(path)

# Add MEIPASS to Python path
if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
    
    # Add site-packages from MEIPASS
    site_packages = os.path.join(sys._MEIPASS, 'lib', 'python3.9', 'site-packages')
    if os.path.exists(site_packages):
        site.addsitedir(site_packages)

# Add potential Python framework paths
_append_path_if_exists('/System/Library/Frameworks/Python.framework/Versions/Current/lib/python3.9/site-packages')
_append_path_if_exists(os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages'))

# Set environment variables for macOS
os.environ['DYLD_LIBRARY_PATH'] = os.path.dirname(sys.executable)
os.environ['DYLD_FRAMEWORK_PATH'] = os.path.join(sys._MEIPASS, 'Frameworks')
os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem') 