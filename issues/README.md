# Issues as code

Each Markdown file in this folder becomes one GitHub issue when it is merged
to the default branch. Write a whole backlog as files, review it in a pull
request, and let the workflow create the issues for you.

## Add issues

1. Copy [`_template.md`](_template.md) to a new file named after the work, in
   lowercase-kebab-case: `add-ci-pipeline.md`.
2. Fill in the `title`, `labels`, and body. Add as many files as you like.
3. Open a pull request. CI validates the files.
4. Merge. The workflow creates one issue per new file and, if configured, adds
   it to the Project board.

Preview locally (needs `gh` and PyYAML):

```bash
python scripts/create_issues.py --repo <owner>/<repo> --dry-run
```

## Rules

- **The file name is the issue's key.** Don't rename a file after its issue
  exists, or a duplicate issue is created.
- **Creation is one-way.** After the issue exists, edit and discuss it on
  GitHub. Changes to the file are ignored. You can delete the file once its
  issue has been created.
- Files starting with `_` and this `README.md` are ignored.
- GitHub assigns the issue number (`#42`). Use that number in branches, commits,
  and `Closes #42`.
