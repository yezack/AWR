import os
import shutil
import tempfile
from pathlib import Path

from git import Repo, GitCommandError


class GitIntegration:
    def __init__(self, repo_path: str = None):
        if repo_path is None:
            self.repo_path = tempfile.mkdtemp()
            self._init_repo()
        else:
            self.repo_path = repo_path
            if not os.path.exists(os.path.join(repo_path, ".git")):
                self._init_repo()
        self.repo = Repo(self.repo_path)

    def _init_repo(self):
        os.makedirs(self.repo_path, exist_ok=True)
        repo = Repo.init(self.repo_path)
        with open(os.path.join(self.repo_path, "README.md"), "w") as f:
            f.write("# AWR Test Repo\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

    def create_commit(self, artifact_id: str, content: str, message: str) -> str:
        file_path = os.path.join(self.repo_path, artifact_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        self.repo.index.add([artifact_id])
        commit = self.repo.index.commit(message)
        return commit.hexsha

    def update_commit(self, artifact_id: str, content: str, message: str) -> str:
        file_path = os.path.join(self.repo_path, artifact_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        self.repo.index.add([artifact_id])
        commit = self.repo.index.commit(message)
        return commit.hexsha

    def get_commit(self, sha: str):
        try:
            return self.repo.commit(sha)
        except Exception:
            return None

    def verify_sha_exists(self, sha: str) -> bool:
        try:
            self.repo.commit(sha)
            return True
        except Exception:
            return False

    def force_push(self, artifact_id: str, new_content: str) -> str:
        file_path = os.path.join(self.repo_path, artifact_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(new_content)
        self.repo.index.add([artifact_id])
        commit = self.repo.index.commit("Force push commit")
        return commit.hexsha

    def get_file_sha(self, artifact_id: str) -> str:
        try:
            blob = self.repo.head.commit.tree[artifact_id]
            return blob.hexsha
        except KeyError:
            return None

    def get_latest_sha(self) -> str:
        return self.repo.head.commit.hexsha

    def cleanup(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)