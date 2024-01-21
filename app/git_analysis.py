import os
import pandas as pd
from datetime import datetime
from collections import defaultdict
from git import Repo


def analyze_git_repo(repo_path, recent_days=30):
    """
    Analyze a Git repository and collect data on file commit age and change frequency.

    Args:
        repo_path (str): Path to the Git repository.
        recent_days (int, optional): Number of recent days to consider for change frequency. Default is 30 days.

    Returns:
        tuple: Two dictionaries containing file commit age and change frequency data.
    """
    file_commit_age = defaultdict(int)
    file_change_frequency = defaultdict(int)

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.relpath(file_path, repo_path)

            last_commit_date = get_last_commit_date(file_path)
            commit_count = get_commit_count(file_path, recent_days)

            file_commit_age[file_name] = commit_age_in_days(last_commit_date)
            file_change_frequency[file_name] = commit_count

    return file_commit_age, file_change_frequency

def get_last_commit_date(file_path):
    """
    Get the last commit date of a file in a Git repository.

    Args:
        file_path (str): Path to the file.

    Returns:
        datetime: Last commit date of the file.
    """
    try:
        repo = Repo(file_path, search_parent_directories=True)
        commit = repo.blame("HEAD", file_path).get_current_commit()
        commit_date = datetime.fromtimestamp(commit.committed_date)

        return commit_date
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_commit_count(file_path, recent_days):
    """
    Get the commit count of a file in a specified recent period.

    Args:
        file_path (str): Path to the file.
        recent_days (int): Number of recent days to consider.

    Returns:
        int: Commit count of the file in the recent period.
    """
    try:
        repo = Repo(file_path, search_parent_directories=True)
        since_date = datetime.now() - timedelta(days=recent_days)
        
        # Count commits within the specified recent_days
        commit_count = sum(1 for commit in repo.iter_commits('HEAD', paths=file_path, since=since_date))

        return commit_count
    except Exception as e:
        print(f"Error: {e}")
        return 0  # Return 0 in case of an error or no commits



def commit_age_in_days(commit_date):
    """
    Calculate the age of a commit in days.

    Args:
        commit_date (datetime): Date of the commit.

    Returns:
        int: Age of the commit in days.
    """
    if commit_date:
        current_date = datetime.now()
        age_in_days = (current_date - commit_date).days
        return age_in_days
    else:
        return 0  # Return 0 if commit_date is None or invalid
