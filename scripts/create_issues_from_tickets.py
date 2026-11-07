#!/usr/bin/env python3
"""Issues as code: create GitHub issues (and optionally Project cards) from issues/<slug>.md.

Idempotent and create-only: every issue carries a hidden marker `<!-- issue-key: <slug> -->`.
A file whose marker already exists in the repo is skipped, never updated or duplicated.
The file name is the key, so don't rename a file after its issue has been created.

Requires: python 3.9+, PyYAML, and the GitHub CLI (`gh`).
Env:
  GH_TOKEN       token used to create issues (needs issues: write)
  PROJECT_TOKEN  optional token used for Projects v2 (GITHUB_TOKEN cannot access them)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", re.DOTALL)
MARKER_RE = re.compile(r"<!--\s*issue-key:\s*([a-z0-9-]+)\s*-->")
BASE_LABEL = "issues-as-code"


class IssueFile:
    def __init__(self, key: str, path: Path, title: str, labels: list[str], body: str):
        self.key = key
        self.path = path
        self.title = title
        self.labels = labels
        self.body = body


def gh(args: list[str], *, token: str | None = None, stdin: str | None = None) -> str:
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    result = subprocess.run(
        ["gh", *args], input=stdin, capture_output=True, text=True, env=env, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout


def load_issue_files(issues_dir: Path) -> tuple[list[IssueFile], list[str]]:
    files: list[IssueFile] = []
    errors: list[str] = []

    for path in sorted(issues_dir.glob("*.md")):
        if path.name.startswith("_") or path.name.lower() == "readme.md":
            continue  # templates and docs
        key = path.stem
        if not SLUG_RE.match(key):
            errors.append(f"{path}: file name must be lowercase-kebab-case, like 'add-ci-pipeline.md'")
            continue
        parsed = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
        if not parsed:
            errors.append(f"{path}: missing YAML front matter (--- ... ---)")
            continue
        try:
            meta = yaml.safe_load(parsed[1]) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid front matter: {exc}")
            continue

        title = str(meta.get("title", "")).strip()
        labels = meta.get("labels", [])
        if not title:
            errors.append(f"{path}: front matter needs a 'title'")
            continue
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            errors.append(f"{path}: 'labels' must be a list of strings")
            continue
        body = parsed[2].strip()
        if "- [ ]" not in body:
            print(f"warning: {path} has no '- [ ]' task list", file=sys.stderr)
        files.append(IssueFile(key, path, title, labels, body))

    return files, errors


def existing_issues(repo: str) -> dict[str, dict]:
    """Map issue key -> issue, found via the hidden marker (open and closed issues)."""
    out = gh(["api", "--paginate", f"repos/{repo}/issues?state=all&per_page=100"])
    # --paginate prints one JSON array per page
    decoder, pos, found = json.JSONDecoder(), 0, {}
    while True:
        while pos < len(out) and out[pos].isspace():
            pos += 1
        if pos >= len(out):
            break
        page, pos = decoder.raw_decode(out, pos)
        for issue in page:
            if "pull_request" in issue:
                continue
            m = MARKER_RE.search(issue.get("body") or "")
            if m:
                found[m[1]] = issue
    return found


def ensure_labels(repo: str, wanted: set[str]) -> None:
    out = gh(["label", "list", "--repo", repo, "--limit", "500", "--json", "name"])
    have = {x["name"].lower() for x in json.loads(out)}
    for name in sorted(wanted):
        if name.lower() not in have:
            gh(["label", "create", name, "--repo", repo])
            print(f"  created label '{name}'")


def render_body(issue: IssueFile, repo: str, branch: str) -> str:
    rel = issue.path.as_posix()
    return (
        f"{issue.body}\n\n---\n"
        f"_Created from [`{rel}`](https://github.com/{repo}/blob/{branch}/{rel})_\n"
        f"<!-- issue-key: {issue.key} -->\n"
    )


class Project:
    """Minimal Projects v2 client: add an issue, set Status only if it is empty."""

    def __init__(self, url: str, status: str, token: str):
        m = re.match(r"https://github\.com/(orgs|users)/([^/]+)/projects/(\d+)", url)
        if not m:
            raise ValueError("project url must be https://github.com/orgs/<org>/projects/<n> (or /users/)")
        kind, owner, number = m[1], m[2], int(m[3])
        self.token = token
        root = "organization" if kind == "orgs" else "user"
        data = self.query(
            f"""query($o:String!,$n:Int!){{{root}(login:$o){{projectV2(number:$n){{
                id field(name:"Status"){{... on ProjectV2SingleSelectField{{id options{{id name}}}}}}}}}}}}""",
            o=owner, n=number,
        )
        project = data[root]["projectV2"]
        self.id = project["id"]
        field = project["field"]
        options = {o["name"].lower(): o["id"] for o in field["options"]}
        if status.lower() not in options:
            raise ValueError(f"Status option '{status}' not found; project has: {', '.join(o['name'] for o in field['options'])}")
        self.status_field = field["id"]
        self.status_option = options[status.lower()]

    def query(self, q: str, **variables) -> dict:
        args = ["api", "graphql", "-f", f"query={q}"]
        for k, v in variables.items():
            args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
        return json.loads(gh(args, token=self.token))["data"]

    def ensure_card(self, issue_node_id: str) -> str:
        item = self.query(
            "mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id "
            'fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}',
            p=self.id, c=issue_node_id,
        )["addProjectV2ItemById"]["item"]
        if item["fieldValueByName"] is None:  # never overwrite a card someone already moved
            self.query(
                "mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,"
                "fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}}}",
                p=self.id, i=item["id"], f=self.status_field, o=self.status_option,
            )
            return "added to board"
        return "already on board"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issues-dir", default="issues")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/repo")
    ap.add_argument("--branch", default="main", help="branch used for source links")
    ap.add_argument("--project-url", default=os.environ.get("PROJECT_URL", ""))
    ap.add_argument("--status", default="Backlog", help="Status column for new cards")
    ap.add_argument("--validate-only", action="store_true", help="lint issue files, no GitHub calls")
    ap.add_argument("--dry-run", action="store_true", help="show what would be created, change nothing")
    args = ap.parse_args()

    issues_dir = Path(args.issues_dir)
    if not issues_dir.is_dir():
        print(f"error: {issues_dir} not found", file=sys.stderr)
        return 1
    files, errors = load_issue_files(issues_dir)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"{len(files)} valid issue file(s) found")
    if args.validate_only:
        return 0
    if not args.repo:
        print("error: --repo or GITHUB_REPOSITORY required", file=sys.stderr)
        return 1

    project_token = os.environ.get("PROJECT_TOKEN")
    project = None
    if args.project_url and project_token and not args.dry_run:
        project = Project(args.project_url, args.status, project_token)
    elif args.project_url:
        print("note: Project step skipped (dry run or PROJECT_TOKEN not set)")

    existing = existing_issues(args.repo)
    todo = [f for f in files if f.key not in existing]
    print(f"{len(files) - len(todo)} already have an issue, {len(todo)} to create")

    if not args.dry_run:
        ensure_labels(args.repo, {BASE_LABEL, *(l for f in todo for l in f.labels)})

    failures = 0
    for f in files:
        issue = existing.get(f.key)
        try:
            if issue is None:
                if args.dry_run:
                    print(f"  [dry-run] would create '{f.key}': {f.title}  labels={[BASE_LABEL, *f.labels]}")
                    continue
                payload = json.dumps(
                    {"title": f.title, "body": render_body(f, args.repo, args.branch),
                     "labels": [BASE_LABEL, *f.labels]}
                )
                issue = json.loads(gh(["api", f"repos/{args.repo}/issues", "--input", "-"], stdin=payload))
                print(f"  created '{f.key}' -> #{issue['number']} {issue['html_url']}")
            else:
                print(f"  skip '{f.key}': issue #{issue['number']} exists")
            if project and issue["state"] == "open":
                print(f"    '{f.key}': {project.ensure_card(issue['node_id'])}")
        except Exception as exc:  # keep going so one bad file doesn't block the rest
            failures += 1
            print(f"error: '{f.key}': {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
