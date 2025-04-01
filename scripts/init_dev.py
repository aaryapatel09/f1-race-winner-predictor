import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DevEnvironmentSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.env_file = self.base_dir / '.env'
        self.env_example = self.base_dir / '.env.example'
        self.venv_dir = self.base_dir / 'venv'
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.logs_dir = self.base_dir / 'logs'

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
                logger.error("Python 3.9 or higher is required")
                return False

            # Check pip
            try:
                subprocess.run(['pip', '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("pip is not installed")
                return False

            # Check git
            try:
                subprocess.run(['git', '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("git is not installed")
                return False

            # Check Docker
            try:
                subprocess.run(['docker', '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("Docker is not installed")
                return False

            # Check Docker Compose
            try:
                subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("Docker Compose is not installed")
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking prerequisites: {str(e)}")
            return False

    def create_directories(self):
        """Create necessary directories"""
        try:
            # Create main directories
            directories = [
                self.data_dir,
                self.models_dir,
                self.logs_dir,
                self.base_dir / 'prometheus' / 'data',
                self.base_dir / 'grafana' / 'data',
                self.base_dir / 'alertmanager' / 'data'
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")

        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            raise

    def setup_virtual_environment(self):
        """Set up Python virtual environment"""
        try:
            if self.venv_dir.exists():
                logger.info("Virtual environment already exists")
                return

            logger.info("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], check=True)

            # Determine the pip path based on the OS
            pip_path = str(self.venv_dir / 'bin' / 'pip') if os.name != 'nt' else str(self.venv_dir / 'Scripts' / 'pip.exe')

            # Upgrade pip
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)

            # Install development dependencies
            subprocess.run([pip_path, 'install', '-r', 'requirements-dev.txt'], check=True)

            logger.info("Virtual environment setup completed")
        except Exception as e:
            logger.error(f"Error setting up virtual environment: {str(e)}")
            raise

    def setup_environment_file(self):
        """Set up environment file"""
        try:
            if self.env_file.exists():
                logger.info("Environment file already exists")
                return

            logger.info("Creating environment file...")
            shutil.copy(self.env_example, self.env_file)
            logger.info("Environment file created. Please update the values in .env")
        except Exception as e:
            logger.error(f"Error setting up environment file: {str(e)}")
            raise

    def setup_git_hooks(self):
        """Set up Git hooks"""
        try:
            hooks_dir = self.base_dir / '.git' / 'hooks'
            if not hooks_dir.exists():
                logger.info("Git hooks directory not found")
                return

            # Create pre-commit hook
            pre_commit_hook = hooks_dir / 'pre-commit'
            with open(pre_commit_hook, 'w') as f:
                f.write('''#!/bin/sh
# Run linting
python -m flake8 .
# Run tests
python -m pytest
''')
            pre_commit_hook.chmod(0o755)

            logger.info("Git hooks setup completed")
        except Exception as e:
            logger.error(f"Error setting up Git hooks: {str(e)}")
            raise

    def setup_monitoring(self):
        """Set up monitoring environment"""
        try:
            logger.info("Setting up monitoring environment...")
            subprocess.run([sys.executable, 'scripts/setup_monitoring.py'], check=True)
            logger.info("Monitoring environment setup completed")
        except Exception as e:
            logger.error(f"Error setting up monitoring: {str(e)}")
            raise

    def setup(self):
        """Set up the complete development environment"""
        try:
            logger.info("Starting development environment setup...")

            if not this.check_prerequisites():
                logger.error("Prerequisites check failed")
                sys.exit(1)

            this.create_directories()
            this.setup_virtual_environment()
            this.setup_environment_file()
            this.setup_git_hooks()
            this.setup_monitoring()

            logger.info("Development environment setup completed successfully")
            logger.info("""
Next steps:
1. Update the values in .env file
2. Activate the virtual environment:
   - On Unix/macOS: source venv/bin/activate
   - On Windows: .\\venv\\Scripts\\activate
3. Run the application:
   - python scripts/manage.py start
            """)
        except Exception as e:
            logger.error(f"Error in development environment setup: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    setup = DevEnvironmentSetup()
    setup.setup() 