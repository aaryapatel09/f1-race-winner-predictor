import os
import sys
import subprocess
import logging
import argparse
from typing import List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApplicationManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.env_file = self.base_dir / '.env'
        self.docker_compose_file = self.base_dir / 'docker-compose.yml'

    def check_environment(self) -> bool:
        """Check if the environment is properly set up"""
        try:
            # Check if .env file exists
            if not self.env_file.exists():
                logger.error("Environment file (.env) not found")
                return False

            # Check if docker-compose.yml exists
            if not self.docker_compose_file.exists():
                logger.error("Docker Compose file not found")
                return False

            # Check if Docker is running
            try:
                subprocess.run(['docker', 'info'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("Docker is not running")
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking environment: {str(e)}")
            return False

    def start(self, services: Optional[List[str]] = None):
        """Start the application services"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Starting application services...")
            cmd = ['docker-compose', 'up', '-d']
            if services:
                cmd.extend(services)

            subprocess.run(cmd, check=True, cwd=self.base_dir)
            logger.info("Application services started successfully")
        except Exception as e:
            logger.error(f"Error starting services: {str(e)}")
            sys.exit(1)

    def stop(self, services: Optional[List[str]] = None):
        """Stop the application services"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Stopping application services...")
            cmd = ['docker-compose', 'down']
            if services:
                cmd.extend(services)

            subprocess.run(cmd, check=True, cwd=self.base_dir)
            logger.info("Application services stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping services: {str(e)}")
            sys.exit(1)

    def restart(self, services: Optional[List[str]] = None):
        """Restart the application services"""
        try:
            self.stop(services)
            self.start(services)
        except Exception as e:
            logger.error(f"Error restarting services: {str(e)}")
            sys.exit(1)

    def logs(self, services: Optional[List[str]] = None, follow: bool = False):
        """View application logs"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Fetching application logs...")
            cmd = ['docker-compose', 'logs']
            if follow:
                cmd.append('-f')
            if services:
                cmd.extend(services)

            subprocess.run(cmd, check=True, cwd=self.base_dir)
        except Exception as e:
            logger.error(f"Error fetching logs: {str(e)}")
            sys.exit(1)

    def status(self):
        """Check the status of application services"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Checking application status...")
            subprocess.run(['docker-compose', 'ps'], check=True, cwd=self.base_dir)
        except Exception as e:
            logger.error(f"Error checking status: {str(e)}")
            sys.exit(1)

    def build(self, services: Optional[List[str]] = None):
        """Build application services"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Building application services...")
            cmd = ['docker-compose', 'build']
            if services:
                cmd.extend(services)

            subprocess.run(cmd, check=True, cwd=self.base_dir)
            logger.info("Application services built successfully")
        except Exception as e:
            logger.error(f"Error building services: {str(e)}")
            sys.exit(1)

    def clean(self):
        """Clean up application resources"""
        try:
            if not self.check_environment():
                sys.exit(1)

            logger.info("Cleaning up application resources...")
            subprocess.run(['docker-compose', 'down', '-v'], check=True, cwd=self.base_dir)
            subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
            logger.info("Application resources cleaned successfully")
        except Exception as e:
            logger.error(f"Error cleaning resources: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Manage the F1 Predictor application')
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'logs', 'status', 'build', 'clean'],
                      help='Command to execute')
    parser.add_argument('--services', nargs='+', help='Specific services to manage')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow log output')

    args = parser.parse_args()

    manager = ApplicationManager()

    if args.command == 'start':
        manager.start(args.services)
    elif args.command == 'stop':
        manager.stop(args.services)
    elif args.command == 'restart':
        manager.restart(args.services)
    elif args.command == 'logs':
        manager.logs(args.services, args.follow)
    elif args.command == 'status':
        manager.status()
    elif args.command == 'build':
        manager.build(args.services)
    elif args.command == 'clean':
        manager.clean()

if __name__ == "__main__":
    main() 