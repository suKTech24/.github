#!/usr/bin/env python3
"""Create GitHub issues (and optionally Project cards) from tickets/<ID>-<slug>/README.md.

Idempotent and create-only: every issue carries a hidden marker `<!-- ticket-id: <ID> -->`.
A ticket whose marker already exists in the repo is skipped, never updated or duplicated.

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

FOLDER_RE = re.compile(r"^(?P<id>\d+)-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", re.DOTALL)
MARKER_RE = re.compile(r"<!--\s*ticket-id:\s*(\d+)\s*-->")
BASE_LABEL = "ticket"


class Ticket:
    def __init__(self, tid: int, path: Path, title: str, labels: list[str], body: str):
        self.id = tid
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


def load_tickets(tickets_dir: Path) -> tuple[list[Ticket], list[str]]:
    tickets: list[Ticket] = []
    errors: list[str] = []
    seen: dict[int, Path] = {}

    for folder in sorted(p for p in tickets_dir.iterdir() if p.is_dir()):
        if folder.name.startswith("_"):
            continue  # templates and other non-ticket folders
        match = FOLDER_RE.match(folder.name)
        if not match:
            errors.append(f"{folder}: folder name must look like '100-short-slug'")
            continue
        tid = int(match["id"])
        if tid in seen:
            errors.append(f"{folder}: ticket id {tid} already used by {seen[tid]}")
            continue
        seen[tid] = folder

        readme = folder / "README.md"
        if not readme.is_file():
            errors.append(f"{folder}: missing README.md")
            continue
        parsed = FRONT_MATTER_RE.match(readme.read_text(encoding="utf-8"))
        if not parsed:
            errors.append(f"{readme}: missing YAML front matter (--- ... ---)")
            continue
        try:
            meta = yaml.safe_load(parsed[1]) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{readme}: invalid front matter: {exc}")
            continue

        title = str(meta.get("title", "")).strip()
        labels = meta.get("labels", [])
        if not title:
            errors.append(f"{readme}: front matter needs a 'title'")
            continue
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            errors.append(f"{readme}: 'labels' must be a list of strings")
            continue
        body = parsed[2].strip()
        if "- [ ]" not in body:
            print(f"warning: {readme} has no '- [ ]' task list", file=sys.stderr)
        tickets.append(Ticket(tid, folder, title, labels, body))

    return tickets, errors


def existing_ticket_issues(repo: str) -> dict[int, dict]:
    """Map ticket id -> issue, found via the hidden marker (open and closed issues)."""
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
                found[int(m[1])] = issue
    return found


def next_ticket_id(tickets_dir: Path, repo: str | None, start: int = 100) -> int:
    """Highest id seen in folders and issue markers, plus one. Issues are included so
    the id of a deleted ticket folder is never handed out again."""
    ids = [int(m["id"]) for p in tickets_dir.iterdir() if p.is_dir() and (m := FOLDER_RE.match(p.name))]
    if repo:
        try:
            ids += list(existing_ticket_issues(repo))
        except (RuntimeError, FileNotFoundError) as exc:
            print(f"warning: could not read issues ({exc}); using local folders only", file=sys.stderr)
    return max(ids, default=start - 1) + 1


def ensure_labels(repo: str, wanted: set[str]) -> None:
    out = gh(["label", "list", "--repo", repo, "--limit", "500", "--json", "name"])
    have = {x["name"].lower() for x in json.loads(out)}
    for name in sorted(wanted):
        if name.lower() not in have:
            gh(["label", "create", name, "--repo", repo])
            print(f"  created label '{name}'")


def render_body(ticket: Ticket, repo: str, branch: str) -> str:
    rel = (ticket.path / "README.md").as_posix()
    return (
        f"{ticket.body}\n\n---\n"
        f"_Ticket T-{ticket.id} · source: [`{rel}`](https://github.com/{repo}/blob/{branch}/{rel})_\n"
        f"<!-- ticket-id: {ticket.id} -->\n"
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
    ap.add_argument("--tickets-dir", default="tickets")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/repo")
    ap.add_argument("--branch", default="main", help="branch used for source links")
    ap.add_argument("--project-url", default=os.environ.get("PROJECT_URL", ""))
    ap.add_argument("--status", default="Backlog", help="Status column for new cards")
    ap.add_argument("--next-id", action="store_true", help="print the next unused ticket id and exit")
    ap.add_argument("--validate-only", action="store_true", help="lint tickets, no GitHub calls")
    ap.add_argument("--dry-run", action="store_true", help="show what would be created, change nothing")
    args = ap.parse_args()

    tickets_dir = Path(args.tickets_dir)
    if not tickets_dir.is_dir():
        print(f"error: {tickets_dir} not found", file=sys.stderr)
        return 1
    if args.next_id:
        print(next_ticket_id(tickets_dir, args.repo))
        return 0
    tickets, errors = load_tickets(tickets_dir)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"{len(tickets)} valid ticket(s) found")
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

    existing = existing_ticket_issues(args.repo)
    todo = [t for t in tickets if t.id not in existing]
    print(f"{len(existing)} already have an issue, {len(todo)} to create")

    if not args.dry_run:
        ensure_labels(args.repo, {BASE_LABEL, *(l for t in todo for l in t.labels)})

    failures = 0
    for t in tickets:
        issue = existing.get(t.id)
        try:
            if issue is None:
                if args.dry_run:
                    print(f"  [dry-run] would create T-{t.id}: {t.title}  labels={[BASE_LABEL, *t.labels]}")
                    continue
                payload = json.dumps(
                    {"title": f"[T-{t.id}] {t.title}", "body": render_body(t, args.repo, args.branch),
                     "labels": [BASE_LABEL, *t.labels]}
                )
                issue = json.loads(gh(["api", f"repos/{args.repo}/issues", "--input", "-"], stdin=payload))
                print(f"  created T-{t.id} -> #{issue['number']} {issue['html_url']}")
            else:
                print(f"  skip T-{t.id}: issue #{issue['number']} exists")
            if project and issue["state"] == "open":
                print(f"    T-{t.id}: {project.ensure_card(issue['node_id'])}")
        except Exception as exc:  # keep going so one bad ticket doesn't block the rest
            failures += 1
            print(f"error: T-{t.id}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
