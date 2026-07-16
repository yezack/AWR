import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.dual_store import DualStore


class TestDualStore:
    def setup_method(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.git_path = os.path.join(self.tmpdir.name, "repo")
        self.store = DualStore(db_path=":memory:", git_path=self.git_path)

    def teardown_method(self):
        self.store.close()
        self.tmpdir.cleanup()

    # ── 创建流程 ──

    def test_create_artifact_writes_both_stores(self):
        """Artifact 创建：Event Store 有事件 + Git 有 commit。"""
        sha = self.store.create_artifact(
            path="docs/design.md",
            content="# Design Doc\n\nInitial version.",
            art_id="art-1",
            art_type="design",
            actor="part-reasonix-001",
        )

        # Git 侧：commit 存在
        assert self.store.git.artifact_exists(sha)

        # Event Store 侧：事件存在
        events = self.store.events.get_events_by_type("Artifact.Created")
        assert len(events) == 1
        assert events[0].payload["id"] == "art-1"
        assert events[0].payload["initial_sha"] == sha

    # ── 更新流程 ──

    def test_update_artifact_preserves_sha_chain(self):
        """Artifact 更新：Event 携带 old_sha→new_sha。"""
        sha1 = self.store.create_artifact(
            path="src/main.py",
            content="print('v1')",
            art_id="art-2",
            art_type="code",
            actor="part-reasonix-001",
        )

        sha2 = self.store.update_artifact(
            art_id="art-2",
            path="src/main.py",
            content="print('v2')",
            actor="part-reasonix-001",
        )

        # sha2 不同于 sha1
        assert sha2 != sha1

        # Event Store 有两条事件
        created = self.store.events.get_events_by_type("Artifact.Created")
        updated = self.store.events.get_events_by_type("Artifact.Updated")
        assert len(created) == 1
        assert len(updated) == 1

        # updated 事件携带 old_sha→new_sha
        assert updated[0].payload["old_sha"] == sha1
        assert updated[0].payload["new_sha"] == sha2

    # ── Review 绑定 ──

    def test_review_binds_to_artifact_sha(self):
        """Review 绑定 Artifact@sha。"""
        sha = self.store.create_artifact(
            path="api/spec.yaml",
            content="openapi: 3.0",
            art_id="art-3",
            art_type="api_spec",
            actor="part-reasonix-001",
        )

        self.store.submit_review(
            rev_id="rev-1",
            target_type="Artifact",
            target_id="art-3",
            target_version=f"art-3@{sha}",
            author="part-human-001",
            verdict="approve",
            content="Looks good.",
        )

        reviews = self.store.events.get_events_by_type("Review.Submitted")
        assert len(reviews) == 1
        assert reviews[0].payload["target_version"] == f"art-3@{sha}"

    def test_review_stays_valid_after_artifact_update(self):
        """Artifact 更新后旧 Review 仍然有效（指向旧 sha，不悬空）。"""
        sha1 = self.store.create_artifact(
            path="docs/rfc.md",
            content="# RFC v1",
            art_id="art-4",
            art_type="design",
            actor="part-reasonix-001",
        )

        self.store.submit_review(
            rev_id="rev-1",
            target_type="Artifact",
            target_id="art-4",
            target_version=f"art-4@{sha1}",
            author="part-human-001",
            verdict="approve",
        )

        # 更新 Artifact
        sha2 = self.store.update_artifact(
            art_id="art-4",
            path="docs/rfc.md",
            content="# RFC v2",
            actor="part-reasonix-001",
        )

        # 旧 Review 仍指向旧 sha，sha1 仍在 Git 中可达
        reviews = self.store.events.get_events_by_type("Review.Submitted")
        assert reviews[0].payload["target_version"] == f"art-4@{sha1}"
        assert self.store.git.artifact_exists(sha1)  # 旧版本仍存在
        assert self.store.git.artifact_exists(sha2)  # 新版本也存在

    # ── force-push 后引用不悬空 ──

    def test_review_reference_survives_force_push(self):
        """force-push 后旧 Review 指向旧 sha，不悬空（标记为 stale 但不崩溃）。"""
        sha1 = self.store.create_artifact(
            path="src/config.py",
            content="DEBUG = True",
            art_id="art-5",
            art_type="code",
            actor="part-reasonix-001",
        )

        self.store.submit_review(
            rev_id="rev-1",
            target_type="Artifact",
            target_id="art-5",
            target_version=f"art-5@{sha1}",
            author="part-human-001",
            verdict="approve",
        )

        # 模拟 force-push：amend 重写历史
        sha2 = self.store.git.force_update_artifact(
            "src/config.py",
            "DEBUG = False",
        )

        # sha1 可能不再可达（amend 后），但系统不应崩溃
        # 检查一致性：Review 引用的 sha1 标记为 MISSING (stale)
        result = self.store.check_consistency()

        # 直接检查 Review 引用
        reviews = self.store.events.get_events_by_type("Review.Submitted")
        assert reviews[0].payload["target_version"] == f"art-5@{sha1}"

        # sha2 可达
        assert self.store.git.artifact_exists(sha2)

    # ── 对象图重建 ──

    def test_rebuild_object_graph(self):
        """从 Event Store 完整事件流重建对象图。"""
        sha1 = self.store.create_artifact(
            path="README.md",
            content="# Project",
            art_id="art-a",
            art_type="document",
            actor="part-reasonix-001",
        )
        sha2 = self.store.update_artifact(
            art_id="art-a",
            path="README.md",
            content="# Project v2",
            actor="part-reasonix-001",
        )
        self.store.submit_review(
            rev_id="rev-a",
            target_type="Artifact",
            target_id="art-a",
            target_version=f"art-a@{sha1}",
            author="part-human-001",
            verdict="approve",
        )

        graph = self.store.rebuild_object_graph()

        assert "art-a" in graph["artifacts"]
        assert graph["artifacts"]["art-a"]["current_sha"] == sha2
        assert graph["artifacts"]["art-a"]["previous_sha"] == sha1
        assert graph["artifacts"]["art-a"]["type"] == "document"

        assert "rev-a" in graph["reviews"]
        assert graph["reviews"]["rev-a"]["target_version"] == f"art-a@{sha1}"
        assert graph["reviews"]["rev-a"]["verdict"] == "approve"

    # ── 一致性检查 ──

    def test_consistency_check_all_pass(self):
        """正常操作后一致性检查全部通过。"""
        sha = self.store.create_artifact(
            path="notes.md",
            content="# Notes",
            art_id="art-c",
            art_type="document",
            actor="part-reasonix-001",
        )
        self.store.submit_review(
            rev_id="rev-c",
            target_type="Artifact",
            target_id="art-c",
            target_version=f"art-c@{sha}",
            author="part-human-001",
            verdict="comment",
        )

        result = self.store.check_consistency()
        assert result["passed"] is True
        for check in result["checks"]:
            assert check["status"] == "ok", f"Check failed: {check['detail']}"

    # ── 顺序保证 ──

    def test_event_order_is_preserved(self):
        """Event Store 中的事件保持写入顺序。"""
        self.store.create_artifact("a.txt", "a", "art-1", "code", "actor")
        self.store.create_artifact("b.txt", "b", "art-2", "code", "actor")

        events = self.store.events.get_all_events()
        assert len(events) == 2
        assert events[0].payload["id"] == "art-1"
        assert events[1].payload["id"] == "art-2"


class TestDualStoreGitHistory:
    """Git 历史追踪测试。"""

    def setup_method(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.git_path = os.path.join(self.tmpdir.name, "repo")
        self.store = DualStore(db_path=":memory:", git_path=self.git_path)

    def teardown_method(self):
        self.store.close()
        self.tmpdir.cleanup()

    def test_git_history_tracks_artifact_versions(self):
        """Git history 记录了 Artifact 的版本演进。"""
        sha1 = self.store.create_artifact(
            "file.txt", "v1", "art-x", "code", "actor"
        )
        sha2 = self.store.update_artifact(
            "art-x", "file.txt", "v2", "actor"
        )

        history = self.store.git.get_history("file.txt")
        assert len(history) >= 2  # 至少两个 commit
        # history[0] 是最新 commit
        assert history[0] == sha2

    def test_artifact_content_readable_by_sha(self):
        """不同 SHA 读取不同版本的内容。"""
        sha1 = self.store.create_artifact(
            "doc.md", "# v1 content", "art-y", "design", "actor"
        )
        sha2 = self.store.update_artifact(
            "art-y", "doc.md", "# v2 content", "actor"
        )

        v1_content = self.store.git.read_artifact(sha1, "doc.md")
        v2_content = self.store.git.read_artifact(sha2, "doc.md")

        assert "v1 content" in v1_content
        assert "v2 content" in v2_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
