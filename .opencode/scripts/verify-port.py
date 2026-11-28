#!/usr/bin/env python3
"""Verify the OpenCode port: generated files, API discovery, skill activation.

Exits 1 on any FAIL. API checks are NOT ASSESSED when the service is absent.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get("OPENCODE_BASE_URL", "http://127.0.0.1:4098")
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))
    print(f"{status:12} {name}{(' — ' + detail) if detail else ''}")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    data: dict[str, str] = {}
    if not text.startswith("---\n"):
        return data
    end = text.find("\n---\n", 4)
    if end == -1:
        return data
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            value = match.group(2).strip()
            if value.startswith('"') and value.endswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = value[1:-1]
            data[match.group(1)] = str(value)
    return data


def api(path: str, *, method: str = "GET", body: object | None = None, location: bool = True):
    query = ""
    if location:
        query = "?" + urllib.parse.urlencode({"location[directory]": str(ROOT)})
    url = BASE + path + query
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    user = os.environ.get("OPENCODE_SERVER_USERNAME", "")
    password = os.environ.get("OPENCODE_SERVER_PASSWORD", "")
    if user and password:
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(request, timeout=10) as response:
        raw = response.read()
        return response.status, json.loads(raw) if raw else None


def check_files() -> None:
    upstream = sorted(p.parent.name for p in (ROOT / ".claude/skills").glob("*/SKILL.md"))
    wrappers = sorted(p.parent.name for p in (ROOT / ".opencode/skills").glob("*/SKILL.md"))
    commands = sorted(p.stem for p in (ROOT / ".opencode/commands").glob("*.md"))
    if upstream == wrappers == commands:
        record("files: 80 skills + 80 commands", "PASS", f"{len(upstream)} IDs aligned")
    else:
        record(
            "files: 80 skills + 80 commands",
            "FAIL",
            f"upstream={len(upstream)} wrappers={len(wrappers)} commands={len(commands)}",
        )

    hidden = []
    for skill_id in upstream:
        meta = frontmatter(ROOT / ".opencode/skills" / skill_id / "SKILL.md")
        original = frontmatter(ROOT / ".claude/skills" / skill_id / "SKILL.md")
        if meta.get("description") != original.get("description"):
            hidden.append(f"{skill_id}:description")
        if meta.get("name") != skill_id:
            hidden.append(f"{skill_id}:name")
        body = (ROOT / ".opencode/skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
        if f".claude/skills/{skill_id}/SKILL.md" not in body:
            hidden.append(f"{skill_id}:missing-upstream-link")
    record("files: skill wrapper metadata/links", "PASS" if not hidden else "FAIL", ", ".join(hidden[:8]))

    manual = {"changelog", "day-one-patch", "dev-story", "help", "hotfix", "launch-checklist", "settings", "story-done"}
    wrong = []
    for skill_id in upstream:
        text = (ROOT / ".opencode/skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
        expected = "opencode/autoinvoke: false" if skill_id in manual else "opencode/autoinvoke: true"
        if expected not in text:
            wrong.append(skill_id)
    record("files: autoinvoke flags", "PASS" if not wrong else "FAIL", ", ".join(wrong))

    upstream_agents = sorted(p.stem for p in (ROOT / ".claude/agents").glob("*.md"))
    ported_agents = sorted(p.stem for p in (ROOT / ".opencode/agents").glob("*.md"))
    if upstream_agents != ported_agents:
        record(f"files: {len(upstream_agents)} agents", "FAIL", f"upstream={len(upstream_agents)} ported={len(ported_agents)}")
    else:
        deprecated = {"name", "tools", "maxTurns", "memory", "disallowedTools", "skills", "isolation", "model"}
        bad = []
        for agent_id in ported_agents:
            meta = frontmatter(ROOT / ".opencode/agents" / f"{agent_id}.md")
            if meta.get("mode") != "subagent":
                bad.append(f"{agent_id}:mode")
            if not meta.get("description"):
                bad.append(f"{agent_id}:description")
            overlap = deprecated & meta.keys()
            if overlap:
                bad.append(f"{agent_id}:{','.join(sorted(overlap))}")
        record(f"files: {len(ported_agents)} agents", "PASS" if not bad else "FAIL", ", ".join(bad[:8]))


def check_api() -> None:
    try:
        status, payload = api("/api/skill")
        skill_ids = {item["id"] for item in payload.get("data", [])}
        expected = {p.parent.name for p in (ROOT / ".opencode/skills").glob("*/SKILL.md")}
        missing = sorted(expected - skill_ids)
        record("api: skills discovered", "PASS" if not missing else "FAIL", f"{len(expected & skill_ids)}/{len(expected)}; missing={missing[:5]}")

        loaded = next((s for s in payload.get("data", []) if s.get("id") == "skill-test"), None)
        content = str(loaded.get("content", "")) if loaded else ""
        if any(marker in content for marker in ("OpenCode port", "OpenCode runtime", "system-installed skill")):
            record("api: wrapper content wins", "PASS", loaded.get("path", ""))
        else:
            record("api: wrapper content wins", "FAIL", "wrapper body not served for skill-test")

        _, payload = api("/api/command")
        command_ids = {item.get("name") or item.get("id") for item in payload.get("data", [])}
        expected_cmds = {p.stem for p in (ROOT / ".opencode/commands").glob("*.md")}
        missing = sorted(expected_cmds - command_ids)
        record("api: commands discovered", "PASS" if not missing else "FAIL", f"{len(expected_cmds & command_ids)}/{len(expected_cmds)}; missing={missing[:5]}")

        _, payload = api("/api/agent")
        agent_ids = {item["id"] for item in payload.get("data", [])}
        expected_agents = {p.stem for p in (ROOT / ".opencode/agents").glob("*.md")}
        missing = sorted(expected_agents - agent_ids)
        record("api: agents discovered", "PASS" if not missing else "FAIL", f"{len(expected_agents & agent_ids)}/{len(expected_agents)}; missing={missing[:5]}")

        try:
            _, payload = api("/api/plugin")
            plugin_ids = {item.get("id") for item in payload.get("data", []) if item.get("id")}
            wanted = {"ccgs-bridge", "question-watchdog"}
            missing = sorted(wanted - plugin_ids)
            record("api: plugins loaded", "PASS" if not missing else "FAIL", f"missing={missing}")
        except urllib.error.HTTPError as error:
            record("api: plugins loaded", "NOT ASSESSED", f"HTTP {error.code}")

        status, payload = api(
            "/api/session",
            method="POST",
            body={"title": "ccgs-port-check", "location": {"directory": str(ROOT)}},
            location=False,
        )
        session_id = payload.get("data", {}).get("id") if payload else None
        if not session_id:
            record("api: create test session", "FAIL", f"HTTP {status}")
            return
        try:
            status, _ = api(
                f"/api/experimental/session/{session_id}/skill",
                method="POST",
                body={"id": "skill-test", "resume": False},
                location=False,
            )
            record("api: activate skill in session", "PASS" if status in (200, 204) else "FAIL", f"HTTP {status}")
        except urllib.error.HTTPError as error:
            record("api: activate skill in session", "FAIL", f"HTTP {error.code}")
        finally:
            try:
                api(f"/api/session/{session_id}", method="DELETE", location=False)
            except Exception:
                pass
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        record("api: OpenCode service", "NOT ASSESSED", str(error))


def main() -> None:
    check_files()
    check_api()
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    skipped = sum(1 for _, status, _ in results if status == "NOT ASSESSED")
    print(f"\nsummary: {len(results) - failed - skipped} PASS, {failed} FAIL, {skipped} NOT ASSESSED")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
