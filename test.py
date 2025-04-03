#!/usr/bin/env python3
import os
import sys
import subprocess
import importlib.util
import pkg_resources

def check_python_version():
    version = sys.version_info
    return version.major >= 3 and version.minor >= 7

def check_virtual_env():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def check_directories():
    required_dirs = ['data', 'models', 'logs']
    return all(os.path.exists(dir) for dir in required_dirs)

def check_dependencies():
    required_packages = ['pandas', 'numpy', 'scikit-learn', 'flask', 'streamlit']
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.require(package)
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            missing_packages.append(package)
    
    return missing_packages

def check_app_import():
    try:
        spec = importlib.util.spec_from_file_location("app", "src/web/app.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
    except Exception as e:
        print(f"❌ App import failed: {str(e)}")
    return False

def main():
    print("🧪 Starting F1 Predictor Tests\n")
    
    print("🔍 Testing setup...")
    setup_ok = True
    
    if check_python_version():
        print("✓ Python version:", sys.version.split()[0])
    else:
        print("❌ Python version too old")
        setup_ok = False
    
    if check_virtual_env():
        print("✓ Virtual environment exists")
    else:
        print("❌ No virtual environment found")
        setup_ok = False
    
    if check_directories():
        print("✓ data folder exists")
        print("✓ models folder exists")
        print("✓ logs folder exists")
    else:
        print("❌ Missing required directories")
        setup_ok = False
    
    print("\n🔍 Testing dependencies...")
    missing_packages = check_dependencies()
    if missing_packages:
        print("❌ Missing packages:", ", ".join(missing_packages))
    else:
        print("✓ All dependencies installed")
    
    print("\n🔍 Testing application...")
    if check_app_import():
        print("✓ App imports successfully")
    else:
        print("❌ App import failed")
    
    print("\n📊 Test Results:")
    print(f"Setup: {'✓' if setup_ok else '❌'}")
    print(f"Dependencies: {'✓' if not missing_packages else '❌'}")
    print(f"Application: {'✓' if check_app_import() else '❌'}")
    
    if not setup_ok or missing_packages or not check_app_import():
        print("\n❌ Some tests failed. Please run: python run.py to fix setup")
    else:
        print("\n✨ All tests passed! You can run the app with: streamlit run src/web/app.py")

if __name__ == "__main__":
    main() 