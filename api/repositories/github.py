from github import Github
from github.GithubException import GithubException

class GitHubClient:
    def __init__(self, token: str):
        # 使用个人访问令牌初始化 GitHub 客户端
        self.github = Github(token)

    def list_repo(self):
       pass

    def get_repo(self, repo_name: str):
        """
        获取指定的 GitHub 仓库
        :param repo_name: 仓库的全名，格式为 '用户名/仓库名'
        :return: GitHub 仓库对象
        """
        try:
            resp = self.github.get_repo(repo_name)
        except GithubException as e:
            print(f"Error fetching repository {repo_name}: {e}")
            return None

    def get_pull_requests(self, repo_name: str, state='open'):
        """
        获取指定仓库的 Pull Requests
        :param repo_name: 仓库全名
        :param state: PR 的状态 ('open' 或 'closed')
        :return: PR 列表
        """
        repo = self.get_repo(repo_name)
        if repo:
            try:
                pull_requests = repo.get_pulls(state=state)
                return pull_requests
            except GithubException as e:
                print(f"Error fetching pull requests: {e}")
                return []

    def create_issue_comment(self, repo_name: str, pr_number: int, comment: str):
        """
        在指定的 PR 上发表评论
        :param repo_name: 仓库全名
        :param pr_number: PR 的编号
        :param comment: 要发表评论的内容
        :return: 评论对象
        """
        repo = self.get_repo(repo_name)
        if repo:
            try:
                pr = repo.get_pull(pr_number)
                pr.create_issue_comment(comment)
                return f"Comment added to PR #{pr_number}"
            except GithubException as e:
                print(f"Error adding comment to PR {pr_number}: {e}")
                return None

    def get_commit_info(self, repo_name: str, sha: str):
        """
        获取指定提交的详细信息
        :param repo_name: 仓库全名
        :param sha: 提交的 SHA 哈希值
        :return: 提交信息
        """
        repo = self.get_repo(repo_name)
        if repo:
            try:
                commit = repo.get_commit(sha)
                return commit
            except GithubException as e:
                print(f"Error fetching commit info: {e}")
                return None

