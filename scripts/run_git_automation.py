import os
import sys
import time
import random
from datetime import datetime, timedelta
import logging
from git_automation import GitAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize Git automation
        git_auto = GitAutomation()
        
        # Get list of changed files
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        changed_files = [line[3:] for line in result.stdout.split('\n') if line]
        
        if not changed_files:
            logger.info("No changes to commit")
            return
        
        # Random delay between 1 hour and 3 days
        delay = random.uniform(3600, 259200)
        logger.info(f"Waiting {delay/3600:.1f} hours before committing...")
        time.sleep(delay)
        
        # Random time of day (avoiding very late/early hours)
        hour = random.randint(9, 21)
        minute = random.randint(0, 59)
        
        # Set commit time
        commit_time = datetime.now().replace(hour=hour, minute=minute)
        os.environ['GIT_AUTHOR_DATE'] = commit_time.isoformat()
        os.environ['GIT_COMMITTER_DATE'] = commit_time.isoformat()
        
        # Commit changes
        git_auto.commit_changes(changed_files)
        
        # Simulate bug fixes if needed
        if random.random() < 0.7:  # 70% chance of bugs
            bug_files = random.sample(changed_files, min(2, len(changed_files)))
            for file in bug_files:
                # Random delay between bug fixes
                time.sleep(random.uniform(1800, 7200))  # 30 minutes to 2 hours
                git_auto.simulate_bug_fix(file)
        
        # Save commit history
        git_auto.save_commit_history()
        
        logger.info("Git automation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in Git automation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 