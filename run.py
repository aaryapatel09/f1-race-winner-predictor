#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
import webbrowser
from pathlib import Path

def check_python():
    """Check if Python is installed and show helpful message if not."""
    try:
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is needed.")
            print("📥 Download Python from: https://python.org")
            input("Press Enter to exit...")
            sys.exit(1)
    except Exception:
        print("❌ Python is not installed!")
        print("📥 Download Python from: https://python.org")
        input("Press Enter to exit...")
        sys.exit(1)

def setup_app():
    """Set up the application environment."""
    try:
        # Create virtual environment
        venv_path = Path("venv")
        if not venv_path.exists():
            print("🔄 Setting up the app...")
            venv.create("venv", with_pip=True)
        
        # Install packages
        print("📦 Installing required packages...")
        pip_cmd = str(venv_path / "bin" / "pip") if os.name != "nt" else str(venv_path / "Scripts" / "pip.exe")
        subprocess.run([pip_cmd, "install", "-e", "."], check=True)
        
        # Create folders
        print("📁 Creating necessary folders...")
        os.makedirs("data", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        return venv_path
    except Exception as e:
        print(f"\n❌ Error setting up the app: {str(e)}")
        print("💡 Make sure you have an internet connection")
        input("Press Enter to exit...")
        sys.exit(1)

def setup_cloud():
    """Set up cloud environment if needed."""
    try:
        if os.path.exists(".env"):
            print("☁️  Cloud configuration found")
            return True
        else:
            print("\n☁️  Cloud Setup Available")
            print("Would you like to set up cloud deployment? (y/n)")
            if input().lower() == 'y':
                print("\n🌐 Setting up cloud environment...")
                subprocess.run([sys.executable, "scripts/setup_cloud.py"], check=True)
                return True
            return False
    except Exception as e:
        print(f"\n❌ Error setting up cloud: {str(e)}")
        print("💡 You can still use the app locally")
        return False

def run_app(venv_path, cloud_enabled=False):
    """Run the F1 Predictor application."""
    try:
        print("\n🚀 Starting F1 Predictor...")
        print("🌐 The app will open in your web browser")
        if cloud_enabled:
            print("☁️  Cloud features enabled")
        print("💡 Press Ctrl+C to close the app\n")
        
        # Start the application
        python_cmd = str(venv_path / "bin" / "python") if os.name != "nt" else str(venv_path / "Scripts" / "python.exe")
        
        # Start monitoring if cloud is enabled
        if cloud_enabled:
            subprocess.Popen([python_cmd, "scripts/setup_monitoring.py"])
        
        # Start the main application
        subprocess.run([python_cmd, "-m", "streamlit", "run", "src/web/app.py"])
        
        # Open the web interface
        webbrowser.open("http://localhost:8501")
    except KeyboardInterrupt:
        print("\n👋 Thanks for using F1 Predictor!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running the app: {str(e)}")
        print("💡 Try running the app again")
        input("Press Enter to exit...")
        sys.exit(1)

def main():
    """Main function to run the application."""
    print("🏎️ Welcome to F1 Race Winner Predictor!")
    print("This will set up and run the app for you.\n")
    
    check_python()
    venv_path = setup_app()
    cloud_enabled = setup_cloud()
    run_app(venv_path, cloud_enabled)

if __name__ == "__main__":
    main() 