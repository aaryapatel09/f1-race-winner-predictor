#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def test_setup():
    """Test if the basic setup works."""
    print("🔍 Testing setup...")
    
    # Check Python version
    print("✓ Python version:", sys.version.split()[0])
    
    # Check virtual environment
    venv_path = Path("venv")
    if venv_path.exists():
        print("✓ Virtual environment exists")
    else:
        print("❌ Virtual environment missing")
        return False
    
    # Check required folders
    folders = ["data", "models", "logs"]
    for folder in folders:
        if os.path.exists(folder):
            print(f"✓ {folder} folder exists")
        else:
            print(f"❌ {folder} folder missing")
            return False
    
    return True

def test_dependencies():
    """Test if all required packages are installed."""
    print("\n🔍 Testing dependencies...")
    try:
        import pandas
        import numpy
        import sklearn
        import streamlit
        import plotly
        print("✓ All basic packages installed")
        
        # Test cloud packages if .env exists
        if os.path.exists(".env"):
            import boto3
            import google.cloud
            import prometheus_client
            print("✓ Cloud packages installed")
        
        return True
    except ImportError as e:
        print(f"❌ Missing package: {str(e)}")
        return False

def test_app():
    """Test if the app can start."""
    print("\n🔍 Testing application...")
    try:
        # Try to import the app
        from src.web import app
        print("✓ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting F1 Predictor Tests\n")
    
    setup_ok = test_setup()
    deps_ok = test_dependencies()
    app_ok = test_app()
    
    print("\n📊 Test Results:")
    print(f"Setup: {'✓' if setup_ok else '❌'}")
    print(f"Dependencies: {'✓' if deps_ok else '❌'}")
    print(f"Application: {'✓' if app_ok else '❌'}")
    
    if setup_ok and deps_ok and app_ok:
        print("\n✨ All tests passed! You can run the app with: python run.py")
    else:
        print("\n❌ Some tests failed. Please run: python run.py to fix setup")

if __name__ == "__main__":
    main() 