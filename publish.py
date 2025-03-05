#!/usr/bin/env python3

# publish.py
# Automatically execute blog update script and push to Git repository
# Can be scheduled via cron for periodic execution

import os
import sys
import subprocess
import datetime

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

def main():
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
        sys.exit(1)
    
    # Add all changes to Git
    print("Adding changes to git...")
    if not run_command(["git", "add", "."], 
                      "Failed to add changes to git. Aborting."):
        sys.exit(1)
    
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
            sys.exit(1)
    
    # Push changes to remote repository
    print("Pushing changes to remote repository...")
    if not run_command(["git", "push"], 
                      "Failed to push changes. Aborting."):
        sys.exit(1)
    
    print(f"Blog update completed successfully at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 