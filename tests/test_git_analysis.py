import unittest
import os
from datetime import datetime, timedelta
from collections import defaultdict
from git import Repo
from app.git_analysis import analyze_git_repo, get_last_commit_date, get_commit_count, commit_age_in_days

class GitAnalysisTestCase(unittest.TestCase):

    def setUp(self):
        # Create a temporary Git repository with sample data for testing
        self.test_repo_path = '/tmp/test_repo'
        self.create_test_repo()
    
    def tearDown(self):
        # Clean up the temporary Git repository
        self.delete_test_repo()

    def create_test_repo(self):
        # Create a temporary Git repository with sample data
        os.mkdir(self.test_repo_path)
        os.chdir(self.test_repo_path)
        self.repo = Repo.init(self.test_repo_path)

        # Create a sample file and make commits
        with open('sample_file.txt', 'w') as f:
            f.write('Sample content')

        self.repo.index.add(['sample_file.txt'])
        self.repo.index.commit('Initial commit')

    def delete_test_repo(self):
        # Delete the temporary Git repository
        os.chdir('..')
        os.system(f'rm -rf {self.test_repo_path}')

    def test_analyze_git_repo(self):
        # Test the analyze_git_repo function
        file_commit_age, file_change_frequency = analyze_git_repo(self.test_repo_path)

        # Assert that the result contains the expected keys (sample_file.txt)
        self.assertIn('sample_file.txt', file_commit_age)
        self.assertIn('sample_file.txt', file_change_frequency)

        # Assert that the commit age is non-negative
        self.assertGreaterEqual(file_commit_age['sample_file.txt'], 0)

        # Assert that the change frequency is at least 1 (initial commit)
        self.assertGreaterEqual(file_change_frequency['sample_file.txt'], 1)

    def test_get_last_commit_date(self):
        # Test the get_last_commit_date function
        file_path = os.path.join(self.test_repo_path, 'sample_file.txt')
        last_commit_date = get_last_commit_date(file_path)

        # Assert that last_commit_date is a datetime object
        self.assertIsInstance(last_commit_date, datetime)

    def test_get_commit_count(self):
        # Test the get_commit_count function
        file_path = os.path.join(self.test_repo_path, 'sample_file.txt')
        recent_days = 30
        commit_count = get_commit_count(file_path, recent_days)

        # Assert that commit_count is an integer
        self.assertIsInstance(commit_count, int)

        # Assert that commit_count is at least 1 (initial commit)
        self.assertGreaterEqual(commit_count, 1)

    def test_commit_age_in_days(self):
        # Test the commit_age_in_days function
        commit_date = datetime.now() - timedelta(days=10)  # 10 days ago
        age_in_days = commit_age_in_days(commit_date)

        # Assert that age_in_days is a non-negative integer
        self.assertIsInstance(age_in_days, int)
        self.assertGreaterEqual(age_in_days, 0)

if __name__ == '__main__':
    unittest.main()
