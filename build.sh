#!/bin/bash

# Exit on error
set -e

# Ensure correct Python version
if ! command -v python3.9 &> /dev/null; then
    echo "Python 3.9 is required but not found"
    exit 1
fi

# Create and activate virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install/upgrade required packages
pip install --upgrade pip
pip install --upgrade pyinstaller
pip install -r requirements.txt

# Clean previous builds
rm -rf build dist

# Build the application
pyinstaller --clean QuantAnalysis.spec

# Code signing for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Remove quarantine attribute if exists
    xattr -cr dist/QuantAnalysis.app 2>/dev/null || true
    
    # Create app bundle with proper structure
    mkdir -p "dist/QuantAnalysis.app/Contents/"{MacOS,Resources,Frameworks}
    cp -r dist/QuantAnalysis/* "dist/QuantAnalysis.app/Contents/MacOS/"
    
    # Copy icon if exists
    if [ -f "assets/icon.icns" ]; then
        cp "assets/icon.icns" "dist/QuantAnalysis.app/Contents/Resources/"
    fi
    
    # Create Info.plist if not exists
    if [ ! -f "dist/QuantAnalysis.app/Contents/Info.plist" ]; then
        cp "Info.plist" "dist/QuantAnalysis.app/Contents/" 2>/dev/null || true
    fi
    
    # Sign the frameworks and libraries first
    find "dist/QuantAnalysis.app" -name "*.dylib" -or -name "*.so" | while read -r file; do
        codesign --force --sign - --entitlements entitlements.plist --options runtime "$file"
    done
    
    # Sign the main executable
    codesign --force --deep --sign - --entitlements entitlements.plist --options runtime "dist/QuantAnalysis.app"
    
    # Verify signing
    codesign --verify --deep --strict "dist/QuantAnalysis.app"
    
    echo "App bundle created and signed at dist/QuantAnalysis.app"
fi

echo "Build completed!"

# Deactivate virtual environment
deactivate 