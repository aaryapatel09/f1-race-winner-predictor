import os
import subprocess
import random
import time
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import openai

logger = logging.getLogger(__name__)

class GitAutomation:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.commit_history = []
        self.bug_patterns = [
            "fixed a bug where",
            "fixed an issue with",
            "fixed the problem with",
            "fixed the error in",
            "fixed the bug in"
        ]
        self.commit_types = [
            "feature",
            "bugfix",
            "refactor",
            "optimization",
            "cleanup"
        ]

    def generate_commit_message(self, changes: List[str]) -> str:
        """Generate an informal commit message based on changes"""
        try:
            if self.openai_api_key:
                # Use OpenAI to generate a message
                prompt = f"""
                Summarize these code changes in an informal, chaotic way as if a distracted programmer wrote them:
                {json.dumps(changes)}
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a distracted programmer writing commit messages."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Fallback to simple message generation
                change_type = random.choice(self.commit_types)
                if random.random() < 0.3:  # 30% chance of a bug fix
                    return f"fixed a bug where {random.choice(changes)}"
                return f"{change_type}: {random.choice(changes)}"
                
        except Exception as e:
            logger.error(f"Error generating commit message: {str(e)}")
            return f"uhhh did something with {random.choice(changes)}"

    def simulate_bug_fix(self, file_path: str) -> List[str]:
        """Simulate a bug fix by making and reverting changes"""
        try:
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Make a random change
            lines = content.split('\n')
            if len(lines) > 1:
                # Introduce a bug
                bug_line = random.randint(0, len(lines) - 1)
                original_line = lines[bug_line]
                lines[bug_line] = f"# BUG: {original_line}"
                
                # Write the bug
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                # Commit the bug
                self.commit_changes([file_path], "uhhh why is this not working")
                
                # Fix the bug
                lines[bug_line] = original_line
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                return [f"Fixed bug in {file_path}"]
            
        except Exception as e:
            logger.error(f"Error simulating bug fix: {str(e)}")
        return []

    def commit_changes(self, files: List[str], message: str = None):
        """Commit changes with the given message"""
        try:
            # Stage changes
            subprocess.run(['git', 'add'] + files, check=True)
            
            # Generate message if not provided
            if not message:
                message = self.generate_commit_message(files)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], check=True)
            
            # Record commit
            self.commit_history.append({
                'timestamp': datetime.now(),
                'files': files,
                'message': message
            })
            
            logger.info(f"Committed changes: {message}")
            
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")

    def randomize_commit_timing(self, files: List[str]):
        """Commit changes with random timing"""
        try:
            # Random delay between 1 hour and 3 days
            delay = random.uniform(3600, 259200)
            time.sleep(delay)
            
            # Random time of day (avoiding very late/early hours)
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            
            # Set commit time
            commit_time = datetime.now().replace(hour=hour, minute=minute)
            os.environ['GIT_AUTHOR_DATE'] = commit_time.isoformat()
            os.environ['GIT_COMMITTER_DATE'] = commit_time.isoformat()
            
            # Commit changes
            self.commit_changes(files)
            
        except Exception as e:
            logger.error(f"Error randomizing commit timing: {str(e)}")

    def simulate_development_cycle(self, files: List[str]):
        """Simulate a realistic development cycle"""
        try:
            # Initial commit
            self.commit_changes(files, "i j finished this i think")
            
            # Simulate some bug fixes
            if random.random() < 0.7:  # 70% chance of bugs
                bug_files = random.sample(files, min(2, len(files)))
                for file in bug_files:
                    self.simulate_bug_fix(file)
            
            # Final polish
            self.commit_changes(files, "maybe fixed idk")
            
        except Exception as e:
            logger.error(f"Error simulating development cycle: {str(e)}")

    def save_commit_history(self):
        """Save commit history to a file"""
        try:
            with open('commit_history.json', 'w') as f:
                json.dump(
                    [{
                        'timestamp': commit['timestamp'].isoformat(),
                        'files': commit['files'],
                        'message': commit['message']
                    } for commit in self.commit_history],
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving commit history: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize Git automation
    git_auto = GitAutomation()
    
    # Get list of changed files
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    changed_files = [line[3:] for line in result.stdout.split('\n') if line]
    
    if changed_files:
        # Simulate development cycle
        git_auto.simulate_development_cycle(changed_files)
        git_auto.save_commit_history()
    else:
        logger.info("No changes to commit") 