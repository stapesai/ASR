import os
import subprocess

def get_git_status(repo_path):
    try:
        # Run 'git status' command to check for changes
        result = subprocess.run(['git', 'status'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if the repository has changes
        if "Your branch is ahead" in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        # Handle exceptions, e.g., if the folder is not a Git repository
        return False

def find_git_repos(base_path='.'):
    git_repos = []

    # Walk through all directories and find Git repositories
    for root, dirs, files in os.walk(base_path):
        if '.git' in dirs:
            git_repos.append(root)

    return git_repos

def main():
    base_folder = '.'  # Set the base folder to start the search

    # Find all Git repositories
    git_repos = find_git_repos(base_folder)

    if not git_repos:
        print("No Git repositories found.")
        return

    print("Checking for new commits in Git repositories:")
    for repo in git_repos:
        has_new_commits = get_git_status(repo)
        if has_new_commits:
            print(f"{repo}: has new commits")
            
            # Run 'git pull' command to update the repository
    print('Script Completed')

if __name__ == "__main__":
    main()
