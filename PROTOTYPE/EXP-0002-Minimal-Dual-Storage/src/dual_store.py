"""双存储一致性层 — 集成 EventStore + GitStore。

按照 RFC-0002 §4 定义：
- Event Store 是对象状态的唯一真相源
- Git 只存储 Artifact 内容
- 所有状态变更必须通过 Event
- 对象间引用使用内容寻址
"""

import sys
import os

from .event_store import EventStore
from .git_store import GitStore
from typing import Dict, Any, List


class DualStore:
    """Event Store + Git Store 的一致性封装。

    所有 Artifact 操作都先写 Git、拿到 SHA，再写 Event Store。
    """

    def __init__(self, db_path: str = ":memory:", git_path: str = None):
        self.events = EventStore(db_path)
        self.git = GitStore(git_path)

    # ── Artifact 操作 ──

    def create_artifact(self, path: str, content: str, art_id: str,
                        art_type: str, actor: str) -> str:
        """创建 Artifact：先写 Git，再写 Event。

        Returns: commit SHA
        """
        sha = self.git.write_artifact(path, content)

        self.events.write_event("Artifact.Created", actor, {
            "id": art_id,
            "type": art_type,
            "path": path,
            "initial_sha": sha,
        })

        return sha

    def update_artifact(self, art_id: str, path: str, content: str, actor: str) -> str:
        """更新 Artifact：先写 Git（拿 new_sha），再写 Event（带 old_sha→new_sha）。

        注意：需要从 Event Store 获取 current_sha 作为 old_sha。
        """
        # 从 Event Store 获取当前状态
        state = self.events.materialize_object(art_id)
        old_sha = state.get("current_sha", state.get("initial_sha", "unknown"))

        new_sha = self.git.write_artifact(path, content)

        self.events.write_event("Artifact.Updated", actor, {
            "id": art_id,
            "path": path,
            "old_sha": old_sha,
            "new_sha": new_sha,
        })

        return new_sha

    # ── Review 操作（内容寻址绑定） ──

    def submit_review(self, rev_id: str, target_type: str, target_id: str,
                      target_version: str, author: str, verdict: str,
                      content: str = "") -> None:
        """提交 Review，绑定 target_version（如 art-1@abc123）。"""
        self.events.write_event("Review.Submitted", author, {
            "id": rev_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_version": target_version,
            "verdict": verdict,
            "content": content,
        })

    # ── 对象图重建 ──

    def rebuild_object_graph(self) -> Dict[str, Any]:
        """从 Event Store 的完整事件流重建对象图状态。

        Returns:
            {
                "artifacts": {art_id: {path, current_sha, type, ...}},
                "reviews": {rev_id: {target_id, target_version, verdict, ...}},
            }
        """
        graph = {"artifacts": {}, "reviews": {}}
        for event in self.events.get_all_events():
            p = event.payload
            if event.event_type == "Artifact.Created":
                graph["artifacts"][p["id"]] = {
                    "type": p.get("type"),
                    "path": p.get("path"),
                    "current_sha": p.get("initial_sha"),
                    "created_by": event.actor,
                }
            elif event.event_type == "Artifact.Updated":
                if p["id"] in graph["artifacts"]:
                    graph["artifacts"][p["id"]]["current_sha"] = p["new_sha"]
                    graph["artifacts"][p["id"]]["previous_sha"] = p["old_sha"]
            elif event.event_type == "Review.Submitted":
                graph["reviews"][p["id"]] = {
                    "target_type": p["target_type"],
                    "target_id": p["target_id"],
                    "target_version": p["target_version"],
                    "verdict": p["verdict"],
                    "author": event.actor,
                }

        return graph

    # ── 一致性检查 ──

    def check_consistency(self) -> Dict[str, Any]:
        """运行一致性检查清单（RFC-0002 §4.3）。

        Returns:
            {
                "passed": bool,
                "checks": [{"rule": str, "status": "ok"|"fail", "detail": str}],
            }
        """
        checks = []
        all_ok = True

        # Rule 1: Artifact.Created/Updated 发出前 Git commit 已存在
        for event in self.events.get_all_events():
            if event.event_type == "Artifact.Created":
                sha = event.payload.get("initial_sha", "")
                exists = self.git.artifact_exists(sha)
                if not exists:
                    all_ok = False
                checks.append({
                    "rule": "Artifact.Created.commit_exists",
                    "status": "ok" if exists else "fail",
                    "detail": f"Artifact {event.payload['id']} @{sha} — {'reachable' if exists else 'MISSING'}",
                })
            elif event.event_type == "Artifact.Updated":
                new_sha = event.payload.get("new_sha", "")
                exists = self.git.artifact_exists(new_sha)
                if not exists:
                    all_ok = False
                checks.append({
                    "rule": "Artifact.Updated.commit_exists",
                    "status": "ok" if exists else "fail",
                    "detail": f"Artifact {event.payload['id']} @{new_sha} — {'reachable' if exists else 'MISSING'}",
                })

        # Rule 2: Review.version 引用的 @sha 在 Git 中可达
        for event in self.events.get_all_events():
            if event.event_type == "Review.Submitted":
                tv = event.payload.get("target_version", "")
                if "@" in tv:
                    sha = tv.split("@", 1)[1]
                    exists = self.git.artifact_exists(sha)
                    if not exists:
                        all_ok = False
                    checks.append({
                        "rule": "Review.target_version.reachable",
                        "status": "ok" if exists else "fail",
                        "detail": f"Review {event.payload['id']} → {tv} — {'reachable' if exists else 'MISSING (stale)'}",
                    })

        return {"passed": all_ok, "checks": checks}

    # ── 生命周期 ──

    def close(self):
        self.events.close()
        self.git.cleanup()
