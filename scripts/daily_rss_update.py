#!/usr/bin/env python3
"""
Complete daily RSS automation pipeline
Runs: git pull -> RSS ingestion -> Claude summaries -> page generation -> Jekyll build -> git push
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('_data/rss/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyRSSPipeline:
    def __init__(self, site_dir=None):
        self.site_dir = Path(site_dir) if site_dir else Path(__file__).parent.parent
        self.data_dir = self.site_dir / '_data' / 'rss'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Change to site directory
        os.chdir(self.site_dir)
        logger.info(f"Working in: {self.site_dir}")
    
    def run_command(self, command, description):
        """Run shell command and handle errors"""
        logger.info(f"Running: {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            if result.stdout.strip():
                logger.info(f"Output: {result.stdout.strip()}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr}")
            return False
    
    def git_pull(self):
        """Pull latest changes from git"""
        logger.info("=== GIT PULL ===")
        return self.run_command("git pull origin master", "Pulling latest changes")
    
    def rss_ingestion(self):
        """Run RSS ingestion script"""
        logger.info("=== RSS INGESTION ===")
        return self.run_command("python3 scripts/rss_ingestion.py", "Ingesting RSS feeds")
    
    def claude_summaries(self):
        """Generate Claude summaries"""
        logger.info("=== CLAUDE SUMMARIES ===")
        
        # Check for API key
        if not os.environ.get('CLAUDE_API_KEY'):
            logger.error("CLAUDE_API_KEY environment variable not set")
            logger.info("Creating fallback summaries...")
            
            # Create minimal summaries as fallback
            fallback = {
                'daily': 'Daily summary generation requires Claude API key configuration.',
                'weekly': 'Weekly summary generation requires Claude API key configuration.',
                'generated_at': datetime.now().isoformat()
            }
            
            with open(self.data_dir / 'summaries.json', 'w') as f:
                json.dump(fallback, f, indent=2)
            
            return True
        
        return self.run_command("python3 scripts/claude_summariser.py", "Generating Claude summaries")
    
    def generate_rss_page(self):
        """Generate RSS feeds page"""
        logger.info("=== GENERATE RSS PAGE ===")
        return self.run_command("python3 scripts/generate_rss_page.py", "Generating RSS feeds page")
    
    def jekyll_build(self):
        """Build Jekyll site"""
        logger.info("=== JEKYLL BUILD ===")
        # Set Ruby path and build Jekyll
        ruby_env = 'export PATH="/opt/homebrew/opt/ruby/bin:/Users/nico/.gem/ruby/3.4.0/bin:$PATH" && '
        return self.run_command(f"{ruby_env}bundle exec jekyll build", "Building Jekyll site")
    
    def git_commit_push(self):
        """Commit and push changes"""
        logger.info("=== GIT COMMIT & PUSH ===")
        
        # Add all changes
        if not self.run_command("git add .", "Adding changes to git"):
            return False
        
        # Check if there are changes to commit
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if not result.stdout.strip():
            logger.info("No changes to commit")
            return True
        
        # Commit changes
        commit_msg = f"Daily RSS update - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        if not self.run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
            return False
        
        # Push to origin
        return self.run_command("git push origin master", "Pushing to GitHub")
    
    def log_completion_stats(self):
        """Log completion statistics"""
        try:
            with open(self.data_dir / 'stats.json', 'r') as f:
                stats = json.load(f)
            
            logger.info("=== COMPLETION STATS ===")
            logger.info(f"Total articles processed: {stats.get('total_articles', 0)}")
            logger.info(f"Today's articles: {stats.get('today_count', 0)}")
            logger.info(f"This week's articles: {stats.get('week_count', 0)}")
            logger.info(f"Feeds processed: {stats.get('feeds_processed', 0)}")
            logger.info(f"Site updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
        except Exception as e:
            logger.error(f"Could not read completion stats: {e}")
    
    def run_pipeline(self):
        """Run the complete pipeline"""
        logger.info("Starting daily RSS automation pipeline")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        steps = [
            ("Git Pull", self.git_pull),
            ("RSS Ingestion", self.rss_ingestion), 
            ("Claude Summaries", self.claude_summaries),
            ("Generate RSS Page", self.generate_rss_page),
            ("Jekyll Build", self.jekyll_build),
            ("Git Commit & Push", self.git_commit_push)
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            logger.info(f"\n--- Starting: {step_name} ---")
            if not step_func():
                logger.error(f"FAILED: {step_name}")
                failed_steps.append(step_name)
                
                # Decide whether to continue or abort
                if step_name in ["Git Pull", "RSS Ingestion"]:
                    logger.error("Critical step failed - aborting pipeline")
                    break
                else:
                    logger.warning("Non-critical step failed - continuing pipeline")
            else:
                logger.info(f"SUCCESS: {step_name}")
        
        # Log completion
        if failed_steps:
            logger.error(f"Pipeline completed with failures: {', '.join(failed_steps)}")
            self.log_completion_stats()
            return False
        else:
            logger.info("Pipeline completed successfully!")
            self.log_completion_stats()
            return True

def main():
    """Main entry point"""
    # Check for site directory argument
    site_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    pipeline = DailyRSSPipeline(site_dir)
    
    try:
        success = pipeline.run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.error("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()