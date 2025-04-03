#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

def create_directories():
    """Create required directories if they don't exist."""
    directories = [
        'models',
        'data',
        'logs',
        'src/ml',
        'src/web',
        'tests'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_virtual_environment():
    """Create and activate virtual environment if it doesn't exist."""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        venv.create('venv', with_pip=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment exists")

def install_dependencies():
    """Install required packages."""
    requirements = [
        'streamlit==1.12.0',
        'pandas',
        'numpy',
        'scikit-learn',
        'plotly',
        'altair<5.0.0',
        'joblib'
    ]
    
    pip_cmd = [sys.executable, '-m', 'pip', 'install']
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.run(pip_cmd + [package], check=True)
        print(f"✓ Installed {package}")
    
    # Install the package in development mode
    print("Installing package in development mode...")
    subprocess.run(pip_cmd + ['-e', '.'], check=True)
    print("✓ Package installed in development mode")

def main():
    print("🧪 Setting up F1 Predictor...")
    
    # Create directories
    print("\n🔍 Creating directories...")
    create_directories()
    
    # Setup virtual environment
    print("\n🔍 Setting up virtual environment...")
    setup_virtual_environment()
    
    # Install dependencies
    print("\n🔍 Installing dependencies...")
    install_dependencies()
    
    print("\n✨ Setup complete! You can now run the application with:")
    print("streamlit run src/web/app.py")

if __name__ == "__main__":
    main() 