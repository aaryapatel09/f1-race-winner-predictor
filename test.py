#!/usr/bin/env python3
import os
import sys
import importlib
import subprocess

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print("✓ Python version: {}.{}.{}".format(version.major, version.minor, version.micro))
        return True
    else:
        print("❌ Python version: {}.{}.{} (3.9+ required)".format(version.major, version.minor, version.micro))
        return False

def check_virtual_env():
    """Check if running in virtual environment."""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print("✓ Virtual environment exists")
    else:
        print("❌ Not running in virtual environment")
    return in_venv

def check_directories():
    """Check if required directories exist."""
    required_dirs = ['models', 'data', 'logs', 'src/ml', 'src/web', 'tests']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    if not missing_dirs:
        print("✓ Required directories exist")
        return True
    else:
        print("❌ Missing required directories:", ", ".join(missing_dirs))
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'sklearn',
        'plotly',
        'altair',
        'joblib'
    ]
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ Missing package: {package}")
    return len(missing_packages) == 0

def check_app_import():
    """Check if the app can be imported."""
    try:
        from src.web.app import main
        print("✓ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {str(e)}")
        return False

def main():
    print("🧪 Starting F1 Predictor Tests\n")
    
    # Test setup
    print("🔍 Testing setup...")
    setup_ok = check_python_version() and check_virtual_env() and check_directories()
    
    # Test dependencies
    print("\n🔍 Testing dependencies...")
    deps_ok = check_dependencies()
    
    # Test application
    print("\n🔍 Testing application...")
    app_ok = check_app_import()
    
    # Print summary
    print("\n📊 Test Results:")
    print(f"Setup: {'✓' if setup_ok else '❌'}")
    print(f"Dependencies: {'✓' if deps_ok else '❌'}")
    print(f"Application: {'✓' if app_ok else '❌'}")
    
    if not (setup_ok and deps_ok and app_ok):
        print("\n❌ Some tests failed. Please run: python run.py to fix setup")
        sys.exit(1)
    else:
        print("\n✨ All tests passed! You can run the application with:")
        print("streamlit run src/web/app.py")

if __name__ == "__main__":
    main() 