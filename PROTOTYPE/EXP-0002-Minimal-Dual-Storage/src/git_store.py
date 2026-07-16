"""Git 操作封装 — 通过 subprocess 调用 git CLI。

负责：
- 初始化 bare repo
- 写入 Artifact 内容 → 返回 SHA
- 读取 Artifact 内容
- 验证 SHA 是否可达
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional


class GitStore:
    """最小 Git 存储封装。

    使用独立 bare repo 以避免影响工作仓库。
    """

    def __init__(self, repo_path: Optional[str] = None):
        if repo_path is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            repo_path = self._tmpdir.name
        else:
            self._tmpdir = None
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self._init_repo()

    def _run(self, *args: str) -> str:
        """在 repo 目录运行 git 命令。"""
        result = subprocess.run(
            ["git"] + list(args),
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def _init_repo(self):
        """初始化 Git 仓库。"""
        self._run("init")
        self._run("config", "user.name", "EXP-0002")
        self._run("config", "user.email", "exp-0002@awr.local")

    def write_artifact(self, path: str, content: str) -> str:
        """写入 Artifact 内容到 Git，返回 commit SHA。

        模拟 Artifact.Created 或 Artifact.Updated 的 Git 侧操作。
        """
        file_path = self.repo_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        self._run("add", path)
        self._run("commit", "-m", f"Update {path}")
        return self._run("rev-parse", "HEAD")

    def read_artifact(self, sha: str, path: Optional[str] = None) -> str:
        """读取指定 SHA 时的 Artifact 内容。"""
        if path:
            return self._run("show", f"{sha}:{path}")
        return self._run("show", sha)

    def artifact_exists(self, sha: str) -> bool:
        """检查 SHA 在 Git 中是否可达。"""
        try:
            self._run("cat-file", "-e", sha)
            return True
        except RuntimeError:
            return False

    def get_history(self, path: str) -> list[str]:
        """获取文件的 commit 历史（从新到旧）。"""
        try:
            output = self._run("log", "--format=%H", "--", path)
            return output.split("\n") if output else []
        except RuntimeError:
            return []

    def force_update_artifact(self, path: str, content: str) -> str:
        """强制更新（模拟 force-push）：amend 最近一次含该 path 的 commit。"""
        file_path = self.repo_path / path
        file_path.write_text(content, encoding="utf-8")

        self._run("add", path)
        # 用 --allow-empty 防止无变更时失败
        self._run("commit", "--amend", "-m", f"Force update {path}", "--allow-empty")
        return self._run("rev-parse", "HEAD")

    def cleanup(self):
        if self._tmpdir:
            self._tmpdir.cleanup()
