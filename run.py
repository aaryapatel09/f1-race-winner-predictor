#!/usr/bin/env python3
import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version.split()[0]}")
        print("Download from: https://www.python.org/downloads/")
        input("Press Enter to exit...")
        sys.exit(1)

def create_virtual_env():
    if not os.path.exists("venv"):
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment exists")

def install_dependencies():
    print("📦 Installing dependencies...")
    pip_cmd = "venv/bin/pip" if os.name != "nt" else "venv\\Scripts\\pip"
    subprocess.run([pip_cmd, "install", "-e", "."], check=True)
    print("✓ Dependencies installed")

def create_directories():
    print("📁 Creating directories...")
    for dir_name in ["data", "models", "logs"]:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ {dir_name} directory created")

def run_app():
    print("🚀 Starting F1 Predictor...")
    streamlit_cmd = "venv/bin/streamlit" if os.name != "nt" else "venv\\Scripts\\streamlit"
    subprocess.Popen([streamlit_cmd, "run", "src/web/app.py"])
    print("🌐 Opening web interface...")
    webbrowser.open("http://localhost:8501")
    print("✨ F1 Predictor is running!")
    print("Press Ctrl+C to stop")

def main():
    try:
        check_python_version()
        create_virtual_env()
        install_dependencies()
        create_directories()
        run_app()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main() 