#!/bin/bash

# Clean previous builds
rm -rf build dist

# Build the application
pyinstaller QuantAnalysis.spec

# Code signing for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Create app bundle
    mkdir -p "dist/QuantAnalysis.app/Contents/MacOS"
    cp -r dist/QuantAnalysis/* "dist/QuantAnalysis.app/Contents/MacOS/"
    
    # Sign the app bundle with entitlements
    codesign --force --deep --sign - --entitlements entitlements.plist --options runtime "dist/QuantAnalysis.app"
    
    # Verify signing
    codesign --verify --deep --strict "dist/QuantAnalysis.app"
fi

echo "Build completed!" 