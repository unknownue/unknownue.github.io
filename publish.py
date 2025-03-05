#!/usr/bin/env python3

# publish.py
# Automatically execute blog update script and push to Git repository
# Can be scheduled via cron for periodic execution or run in schedule mode

import os
import sys
import subprocess
import datetime
import time
import argparse
import signal

def run_command(command, error_message=None):
    """
    Run a shell command and handle errors
    
    Args:
        command: The command to run as a list of strings
        error_message: Custom error message to display on failure
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"Error: {error_message}")
        print(f"Command failed: {' '.join(command)}")
        print(f"Exit code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def publish_blog():
    """
    Execute the blog publishing process
    
    Returns:
        0 if successful, non-zero otherwise
    """
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Output timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting blog update at {current_time}")
    
    # Execute Python script to generate index files
    print("Generating index files...")
    if not run_command(["python3", "scripts/generate_index_files.py"], 
                      "Failed to generate index files. Aborting."):
        return 1
    
    # Add all changes to Git
    print("Adding changes to git...")
    if not run_command(["git", "add", "."], 
                      "Failed to add changes to git. Aborting."):
        return 1
    
    # Commit changes with current date as commit message
    commit_message = f"Blog auto update: {current_time}"
    print(f"Committing changes with message: {commit_message}")
    if not run_command(["git", "commit", "-m", commit_message], 
                      "Failed to commit changes. Aborting."):
        # If nothing to commit, this is not an error
        if "nothing to commit" in subprocess.run(["git", "status"], 
                                               capture_output=True, 
                                               text=True).stdout:
            print("No changes to commit. Continuing...")
        else:
            return 1
    
    # Push changes to remote repository
    print("Pushing changes to remote repository...")
    if not run_command(["git", "push"], 
                      "Failed to push changes. Aborting."):
        return 1
    
    print(f"Blog update completed successfully at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

def schedule_mode(interval_hours):
    """
    Run the publish operation periodically at specified interval
    
    Args:
        interval_hours: Interval in hours between executions
    """
    print(f"Starting scheduled mode. Will publish every {interval_hours} hours.")
    print("Press Ctrl+C to exit.")
    
    # Setup signal handler for graceful exit
    def signal_handler(sig, frame):
        print("\nExiting scheduled mode.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        # Run the publish operation
        publish_blog()
        
        # Calculate next run time
        next_run = datetime.datetime.now() + datetime.timedelta(hours=interval_hours)
        print(f"Next update scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sleep until next run
        time.sleep(interval_hours * 3600)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Blog publishing automation script")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--once", action="store_true", help="Run the publish operation once and exit")
    group.add_argument("--schedule", type=float, metavar="HOURS", 
                      help="Run in schedule mode, publishing every HOURS hours")
    args = parser.parse_args()
    
    # Handle different execution modes
    if args.schedule:
        if args.schedule <= 0:
            print("Error: Schedule interval must be greater than 0")
            return 1
        schedule_mode(args.schedule)
    else:
        # Default is to run once (same as --once)
        return publish_blog()

if __name__ == "__main__":
    sys.exit(main()) 