# Assignment 2: Growing Your CI Pipeline

GitHub Actions - a guided, step-by-step assignment.

**The situation:** In Assignment 1 you built a pipeline with one job that ran
on one machine. It worked. But the team has grown and that pipeline is now too
simple. It only tests one version of Node, everything runs one after another in
a single long list, and the deploy step needs a secret key that must never
appear in the code. Your job in this assignment is to grow that pipeline into a
real one: several jobs, several versions of Node, information passed from one
job to the next, secrets handled safely, and your own reusable action.

## How to use this assignment

This is a guided assignment. That means every piece of code you need is already
written for you in this document. You are not expected to invent YAML from
scratch. What you ARE expected to do is:

- Type or paste each block exactly as it is shown.
- Push it to GitHub and watch what happens in the Actions tab.
- Write down the answers to the questions in your own words.

Some steps are designed to fail on purpose. When a step says "this will fail",
that is not a mistake in the document. Breaking something and then fixing it is
the fastest way to understand what a setting actually does. Do not skip those
steps, and do not jump straight to the fix.

Throughout the document you will see these markers:

- **Goal:** what you are trying to achieve.
- **Do this:** the exact actions to take.
- **What should happen:** how to tell whether it worked.
- **Write this down:** a question for your answer sheet
  ([Appendix A](#appendix-a-answer-sheet)).
- **Why this matters:** the lesson in plain English.

> **Important note about your account:** GitHub gives you unlimited free
> workflow minutes on PUBLIC repositories, but only a limited number of free
> minutes per month on PRIVATE ones. Windows machines also use up minutes twice
> as fast as Linux ones. This assignment uses Windows in one place, so please do
> this work in a PUBLIC repository to avoid running out of minutes. There is
> nothing secret in it.

## Part 1: Prepare the project

You can reuse the repository from Assignment 1, or make a new public repository
called `ci-pipeline-assignment-2`. Either is fine.

### Step 1.1: Update package.json

Open `package.json` and replace the whole file with this. The only change from
Assignment 1 is a new `lint` script. Like the `test` script, it does not really
check anything, it just prints a message and exits successfully. That is enough
for our purposes.

File: `package.json`

```json
{
  "name": "ci-pipeline-assignment",
  "version": "1.0.0",
  "scripts": {
    "lint": "echo 'Linting... no problems found!' && exit 0",
    "test": "echo 'All tests passed successfully!' && exit 0"
  }
}
```

### Step 1.2: Create a lock file

Run this command on your own computer, inside the project folder:

```bash
npm install
```

This creates a file called `package-lock.json`. A lock file records the exact
version of every dependency. Later in this assignment we will use a command
called `npm ci`, and a caching feature, and both of them refuse to work without
a lock file. So commit it:

```bash
git add package.json package-lock.json
git commit -m "Add lint script and lock file"
git push
```

**Why this matters:** `npm install` reads `package.json` and figures out
versions as it goes. `npm ci` reads `package-lock.json` and installs exactly
what is written there, nothing more and nothing less. On a CI server you almost
always want `npm ci`, because it is faster and because it gives the same result
every single time.

## Part 2: Warm-up A - a job that waits for a job that does not exist

**Goal:** find out when GitHub checks your workflow file, and where it tells you
about a mistake.

### Step 2.1: Create the broken file

Create a file at `.github/workflows/warmup-a.yml` and paste this exactly:

File: `.github/workflows/warmup-a.yml`

```yaml
name: Warm-Up A (Broken needs)

on:
  push:
    branches: [main]

jobs:
  first-job:
    runs-on: ubuntu-latest
    steps:
      - name: Say hello
        run: echo "Hello from the first job"

  second-job:
    needs: first-jobb
    runs-on: ubuntu-latest
    steps:
      - name: Say goodbye
        run: echo "Goodbye from the second job"
```

Look carefully at the line `needs: first-jobb`. The job above it is called
`first-job` with one "b". We have written "bb". `needs:` is how you tell GitHub
"do not start this job until that other job has finished successfully". We are
pointing it at a job name that does not exist.

### Step 2.2: Push it

```bash
git add .github/workflows/warmup-a.yml
git commit -m "Warm-up A: broken needs"
git push
```

### Step 2.3: Look at what happened

**What should happen:** open the Actions tab in your repository. You will see an
entry, but it is not a normal failed run. There are no jobs in it and no logs to
open, only an error message about the workflow file being invalid.

**Write this down (Questions A1 to A4):**

1. Did either job run? How can you tell?
2. Copy the exact error message GitHub shows.
3. In Assignment 1 you used a fake runner called `windows-1999` and the job
   failed. Was that failure reported in the same way as this one, or
   differently? Describe the difference in one or two sentences.
4. Based on those two experiences, does GitHub read and check your whole
   workflow file before starting any job, or does it discover problems as it
   goes?

### Step 2.4: Fix it

Change `needs: first-jobb` to `needs: first-job`, then commit and push again.

```bash
git add .github/workflows/warmup-a.yml
git commit -m "Warm-up A: fix the job name"
git push
```

**What should happen:** now the run appears properly. Click into it and you will
see a small diagram with two boxes joined by a line. The second box does not
start until the first one finishes. Take a screenshot of that diagram, you will
submit it.

**Why this matters:** A workflow file has two kinds of problems. The first kind
is a problem with the file itself, such as a name that does not exist or wrong
indentation. GitHub catches these before anything runs, and nothing happens at
all. The second kind is a problem inside a step, such as a command that fails.
Those only show up once the job is running, and you read them in the logs.
Knowing which kind you are looking at saves a lot of time.

## Part 3: Warm-up B - can a secret stay secret?

**Goal:** learn what GitHub Secrets actually protect you from, and what they do
not.

### Step 3.1: Create a fake secret

In your repository on GitHub, go to
**Settings > Secrets and variables > Actions > New repository secret**.

Name it `FAKE_API_KEY` and set the value to:

```text
hunter2-abcdef
```

This is not a real key. Never put a real key in a practice repository.

### Step 3.2: Create the workflow

Create `.github/workflows/warmup-b.yml`:

File: `.github/workflows/warmup-b.yml`

```yaml
name: Warm-Up B (Secrets)

on:
  push:
    branches: [main]

jobs:
  secret-test:
    runs-on: ubuntu-latest
    steps:
      - name: Print the secret directly
        run: echo "The key is ${{ secrets.FAKE_API_KEY }}"

      - name: Print the secret backwards
        run: echo "${{ secrets.FAKE_API_KEY }}" | rev

      - name: Print the secret in base64
        run: echo "${{ secrets.FAKE_API_KEY }}" | base64
```

The second step uses `rev`, a Linux command that reverses text. The third uses
`base64`, which scrambles text into a different alphabet. Neither is
encryption. Anyone can undo both in a second.

### Step 3.3: Push and read the logs

```bash
git add .github/workflows/warmup-b.yml
git commit -m "Warm-up B: secrets test"
git push
```

Open the run in the Actions tab and expand all three steps.

**Write this down (Questions B1 to B4):**

1. What appeared in the log for each of the three steps? Copy all three lines.
2. The first one was hidden. The other two were not. Explain in your own words
   why GitHub could hide the first but not the others.
3. Is hiding secrets in logs a real security protection, or just a helpful
   convenience that stops accidents?
4. You add a third-party action written by a stranger to a workflow that has
   access to your secrets. Based on what you just saw, what could that action
   do? Write two or three sentences.

### Step 3.4: Clean up

Delete `warmup-b.yml` and push. Keep the secret itself, we will use it again in
[Task 5](#task-5-run-the-workflow-by-hand-with-options).

**Why this matters:** GitHub replaces a secret with asterisks when it sees the
exact text in the log. That is pattern matching, not protection. The moment the
value is changed even slightly, the hiding stops working. The real rule is: once
a workflow can read a secret, every single thing running in that workflow can
read it too. So be careful which actions you trust, and give each workflow only
the secrets it truly needs.

## Part 4: Building the real pipeline

From here on you are building one file: `.github/workflows/ci.yml`. Create it
now, empty. You will add to it task by task, pushing after each task so you can
see each change working on its own.

Here is the plan, so you know where you are going:

| Task | What you will add | New idea |
| --- | --- | --- |
| 1 | Split the work into three jobs | `needs:`, separate machines |
| 2 | Test on 3 Node versions, 2 systems | `strategy: matrix` |
| 3 | Move files and values between jobs | `outputs`, `download-artifact` |
| 4 | Print a readable report | `$GITHUB_STEP_SUMMARY` |
| 5 | Run the workflow by hand with options | `workflow_dispatch` inputs |
| 6 | Make your own action | Composite actions |
| 7 | Control when and how long it runs | `concurrency`, `timeout` |
| 8 | Publish a release from a tag | Token permissions |

### Task 1: Split one job into three

**Goal:** understand that each job runs on its own separate machine.

**Do this:** put this in `.github/workflows/ci.yml` and push it.

File: `.github/workflows/ci.yml`

```yaml
name: CI Advanced

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Run the linter
        run: npm run lint

      - name: Leave a note on this machine
        run: echo "the lint job was here" > /tmp/note.txt

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Look for the note the lint job left
        run: cat /tmp/note.txt
```

**What should happen:** the `lint` job passes. The `test` job then fails on the
last step with a message saying the file does not exist. This failure is on
purpose.

**Write this down (Question C1):** the `lint` job created `/tmp/note.txt` and it
clearly succeeded. So why could the `test` job not find that file?

**Now fix it:** delete the two steps about the note (the one that writes it and
the one that reads it). Replace the `test` job's last step with this, then push
again:

```yaml
      - name: Run the tests
        run: npm test
```

**Why this matters:** A job is not a section of one long script. Each job gets a
brand new, completely empty virtual machine. Nothing survives from one job to
the next, not files, not installed programs, not variables. `needs:` only
controls the ORDER, it does not share anything. If you want to move something
between jobs, you have to send it deliberately, which is exactly what Task 3
teaches.

### Task 2: Test on many versions at once

**Goal:** run the same job many times with different settings, using a matrix.

Real projects have to work on more than one version of Node and more than one
operating system. Instead of copying the job six times, you describe the
options once and GitHub builds the combinations for you.

**Do this:** replace your whole `test` job with this version, then push.

```yaml
  test:
    needs: lint
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: ['18', '20', '22']
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run the tests and save the output
        run: npm test > test-output.txt

      - name: Upload the test output
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-output.txt
```

**What should happen:** 2 systems multiplied by 3 Node versions gives you 6
copies of the job, all running at the same time. One of them finishes its
upload first. The other five then fail with an error about an artifact with
that name already existing. This failure is also on purpose.

**Write this down (Questions C2 and C3):**

1. How many copies of the `test` job appeared, and what are their names in the
   Actions tab?
2. Why did the upload step fail for five of the six, even though the step
   itself is correct?

**Now fix it:** an artifact name has to be unique inside one run. Give each copy
its own name by using the matrix values in the name. Change the upload step to:

```yaml
      - name: Upload the test output
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-node${{ matrix.node }}
          path: test-output.txt
```

Push again. Now all six pass and you get six separate artifacts at the bottom
of the run page.

#### A small extra experiment

Add this line under `strategy:` (at the same indentation as `matrix:`):

```yaml
      fail-fast: false
```

**Write this down (Question C4):** read the GitHub documentation for
`fail-fast` and explain in one sentence what changes when one of the six copies
fails. Which setting would you want while hunting a bug, and which would you
want to save minutes?

**Why this matters:** A matrix is a loop. You write the job once and list the
values you want to vary. GitHub creates one real job per combination and runs
them in parallel, so six jobs take about as long as one. Also notice that
`setup-node` with `cache: 'npm'` has quietly replaced the `actions/cache` step
you wrote by hand in Assignment 1. It does the same caching for you and gets the
key right automatically. When a maintained action wraps a job you were doing
manually, use it.

### Task 3: Move files and values between jobs

**Goal:** collect the artifacts from all six test jobs into one place, and pass
a plain text value from one job to another.

There are two different things to move, and they use two different mechanisms.
Files travel as **artifacts**: one job uploads, another downloads. Small values
such as a version number or an ID travel as **job outputs**.

#### Part A: pass a value out of the lint job

Add an `outputs` section to the `lint` job, and a step that produces the value.
Your `lint` job becomes:

```yaml
  lint:
    runs-on: ubuntu-latest
    outputs:
      build_id: ${{ steps.make_id.outputs.build_id }}
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Run the linter
        run: npm run lint

      - name: Create a build ID
        id: make_id
        run: echo "build_id=build-${GITHUB_RUN_NUMBER}" >> "$GITHUB_OUTPUT"
```

Read that last step carefully, because it is the part students usually find
strange. `$GITHUB_OUTPUT` is a special file on the runner. Anything you write
into it in the form `name=value` becomes an output of that step. The
`id: make_id` line gives the step a name so other lines can refer to it. The
`outputs:` block at the top of the job then lifts that step output up to become
an output of the whole job, which other jobs are allowed to read.

#### Part B: add a job that collects everything

Add this third job at the bottom of the file:

```yaml
  report:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - name: Download every artifact from this run
        uses: actions/download-artifact@v4
        with:
          path: all-results

      - name: Show what we collected
        run: |
          echo "Build ID from the lint job: ${{ needs.lint.outputs.build_id }}"
          ls -R all-results
```

**Notice:** `needs: [lint, test]` lists two jobs. The `test` job already waits
for `lint`, so you might think listing `test` alone is enough. It is not. You
can only read `needs.lint.outputs` if `lint` is in this job's own `needs` list.

**Write this down (Questions C5 and C6):**

1. Open the "Show what we collected" step. Paste the folder structure that
   `ls -R` printed. Why are there six folders?
2. Try removing `lint` from the `needs` list so it reads `needs: [test]`, and
   push. What does the build ID line print now? Put it back afterwards.

**Why this matters:** Artifacts are for files. Outputs are for short text
values. Both exist because jobs cannot see each other's machines. A good
pipeline usually ends with a collecting job like this one, that gathers the
results of everything that ran in parallel.

### Task 4: Write a report people will actually read

**Goal:** put a summary on the run page itself, so nobody has to dig through
logs.

Every job can write Markdown into a special file called `$GITHUB_STEP_SUMMARY`.
Whatever you write there is displayed as a formatted panel at the top of the
run page.

**Do this:** replace the "Show what we collected" step in the `report` job with
this.

```yaml
      - name: Write the report
        run: |
          S="$GITHUB_STEP_SUMMARY"
          echo "## CI Report" >> "$S"
          echo "" >> "$S"
          echo "- Build ID: ${{ needs.lint.outputs.build_id }}" >> "$S"
          echo "- Commit: ${{ github.sha }}" >> "$S"
          echo "- Started by: ${{ github.actor }}" >> "$S"
          echo "- Branch: ${{ github.ref_name }}" >> "$S"
          echo "" >> "$S"
          echo "### Artifacts collected" >> "$S"
          ls all-results | sed 's/^/- /' >> "$S"
```

The very first line saves that long file name into a short variable called `S`
so every line below it stays readable. That is ordinary shell, nothing to do
with GitHub. The `>>` means "add this to the end of the file".

**What should happen:** push, then open the run. Above the list of jobs you will
now see a formatted panel with a heading and a bullet list.

**Write this down (Question C7):** `github.sha`, `github.actor` and
`github.ref_name` are values GitHub gives you for free. Find three more useful
ones in the documentation page called "Contexts" and write down what each
contains.

**Why this matters:** Logs are for debugging. Summaries are for communicating.
A pipeline that tells a human what happened in five lines is far more useful
than one that makes them open nine collapsed steps to find out.

### Task 5: Run the workflow by hand, with options

**Goal:** add a Run workflow button with a dropdown and a checkbox, and use the
secret safely.

So far your workflow only runs when you push. `workflow_dispatch` adds a button
in the Actions tab so you can start it yourself, and it lets you ask the person
for input first.

**Do this, part 1:** add `workflow_dispatch` to the `on:` section at the top of
the file.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      target:
        description: 'Where should we deploy?'
        required: true
        type: choice
        options:
          - staging
          - production
        default: staging
      dry_run:
        description: 'Only pretend to deploy?'
        required: false
        type: boolean
        default: true
```

**Do this, part 2:** add a fourth job at the bottom of the file.

```yaml
  deploy:
    needs: report
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Show what I was asked to do
        run: |
          echo "Target: ${{ inputs.target }}"
          echo "Dry run: ${{ inputs.dry_run }}"

      - name: Pretend to deploy
        if: ${{ inputs.dry_run }}
        run: echo "DRY RUN - nothing was really deployed."

      - name: Really deploy
        if: ${{ !inputs.dry_run }}
        env:
          API_KEY: ${{ secrets.FAKE_API_KEY }}
        run: |
          echo "Deploying to ${{ inputs.target }} ..."
          echo "The key I was given is ${#API_KEY} characters long."
```

Push this. Then go to the Actions tab, click **CI Advanced** in the left
sidebar, and you will see a **Run workflow** button on the right with your
dropdown and checkbox.

**Do this, part 3:** run it three times and compare.

1. Push a normal commit. Look at the `deploy` job.
2. Press **Run workflow** with dry run TICKED, target `staging`.
3. Press **Run workflow** with dry run UNTICKED, target `production`.

**Write this down (Questions C8 to C10):**

1. In run 1, what happened to the `deploy` job? What word does GitHub use for a
   job that was not run because of an `if:` condition?
2. In runs 2 and 3, which of the two steps ran each time, and which was
   skipped?
3. The last step never prints the key, only its length. Look at how `env:` is
   used there and explain why passing a secret into `env:` is tidier than
   writing it directly inside the command.

**Why this matters:** `if:` can be used on a whole job or on a single step, and
it is how one workflow serves several purposes. The same file now handles
automatic checks on every push and a manual, human-triggered deploy, without
duplicating anything.

### Task 6: Build your own action

**Goal:** notice repetition and remove it by packaging steps into a reusable
action of your own.

Look at your file. The `lint` job and the `test` job both set up Node and
install dependencies. Right now that is only two places, but on a real project
it would be ten. A **composite action** lets you bundle a group of steps under
one name and then call that name wherever you need it.

#### Step 6.1: Create the action, with a deliberate mistake

Create a new file at `.github/actions/setup-project/action.yml`. Note that this
is `.github/actions/`, not `.github/workflows/`. The folder name you choose
becomes the name you call it by, and the file must be called `action.yml`.

File: `.github/actions/setup-project/action.yml`

```yaml
name: 'Setup Project'
description: 'Sets up Node and installs dependencies'

inputs:
  node-version:
    description: 'Which version of Node to install'
    required: false
    default: '20'

runs:
  using: 'composite'
  steps:
    - name: Set up Node
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci
```

Now use it. In the `test` job, delete the "Set up Node" and "Install
dependencies" steps and put this single step in their place (keep the checkout
step above it):

```yaml
      - name: Set up the project
        uses: ./.github/actions/setup-project
        with:
          node-version: ${{ matrix.node }}
```

Push it.

**What should happen:** it fails immediately with a message complaining that a
required property is missing, pointing at your `run` step. This failure is on
purpose.

**Write this down (Question C11):** copy the exact error message.

#### Step 6.2: Fix it

Inside a normal workflow, a `run:` step uses a default shell. Inside a
composite action, there is no default and you must say which shell you want.
Add one line:

```yaml
    - name: Install dependencies
      run: npm ci
      shell: bash
```

Push again. It should now work.

#### Step 6.3: One more experiment

In the `test` job, temporarily move your "Set up the project" step above the
checkout step, and push.

**What should happen:** it fails, saying it cannot find the action.

**Write this down (Question C12):** why can GitHub not find an action that is
clearly sitting in your own repository? Hint: think about what the runner's
hard drive contains before the checkout step runs.

Put the step back in the right order, then apply the same change to the `lint`
job so it also uses your action.

**Why this matters:** There are two ways to reuse steps. A **composite action**,
which you just built, is a reusable group of STEPS that runs inside someone
else's job. A **reusable workflow** is a whole file of JOBS that another
workflow can call. Use a composite action for repeated setup like this one. Use
a reusable workflow when several repositories need the same complete pipeline.

### Task 7: Control when it runs and how long it may take

**Goal:** stop wasting minutes on runs you no longer care about.

#### Step 7.1: Cancel old runs automatically

Add this block at the top level of the file, after the `on:` section and before
`jobs:`. It must start at the very left margin, with no indentation.

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

**Test it:** make a small change, push, and then within about twenty seconds
make another small change and push again.

**What should happen:** the first run turns grey and says it was cancelled. Only
the newest one continues.

#### Step 7.2: Ignore changes that do not matter

Add a `paths-ignore` to the push trigger:

```yaml
on:
  push:
    branches: [main]
    paths-ignore:
      - '**.md'
```

**Test it:** create or edit a `README.md` file, change nothing else, and push.

**What should happen:** no run starts at all.

#### Step 7.3: Put a time limit on a job

Add this line to the `lint` job, at the same indentation as `runs-on:`:

```yaml
    timeout-minutes: 2
```

Then temporarily add this step to the `lint` job and push:

```yaml
      - name: Take far too long
        run: sleep 300
```

**What should happen:** after two minutes GitHub stops the job itself and marks
it as cancelled or timed out. Remove that `sleep` step afterwards and push
again.

**Write this down (Questions C13 and C14):**

1. Why is `cancel-in-progress: true` usually a good idea for pull request
   checks, but a dangerous idea for a job that deploys to production?
2. A job hangs forever waiting for something that will never arrive. Without a
   timeout, how long would GitHub let it run, and why does that matter on a
   private repository?

**Why this matters:** Minutes are a real resource, and on a free private
repository you have a limited number each month. These three settings cost you
three minutes to write and save hours of wasted runs.

### Task 8: Publish a release when you push a tag

**Goal:** learn that the token your workflow uses has permissions, and that the
default is deliberately minimal.

Every run is automatically given a temporary token called `GITHUB_TOKEN`. In
Assignment 1 you added `permissions: issues: write` so your workflow could
create an issue. This task shows you what happens when that permission is
missing.

#### Step 8.1: Make sure the default is read-only

In your repository go to
**Settings > Actions > General > Workflow permissions**.

Select **Read repository contents and packages permissions** and save. Some
older repositories default to read and write, which would hide the lesson.

#### Step 8.2: Create the release workflow

Create `.github/workflows/release.yml`:

File: `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Make a file to attach
        run: echo "Release built by GitHub Actions" > release-notes.txt

      - name: Create the release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create "$GITHUB_REF_NAME" release-notes.txt \
            --title "$GITHUB_REF_NAME" \
            --notes "Created automatically."
```

`gh` is GitHub's own command line tool. It is already installed on every Ubuntu
runner, so you do not need to install anything. `$GITHUB_REF_NAME` will contain
the tag name.

#### Step 8.3: Push a tag

```bash
git add .github/workflows/release.yml
git commit -m "Add release workflow"
git push

git tag v1.0.0
git push origin v1.0.0
```

**What should happen:** the workflow starts, and the last step fails with an
HTTP 403 error. This failure is on purpose.

**Write this down (Question C15):** copy the error message. Which permission
does it say is missing?

#### Step 8.4: Fix it

Add a `permissions` block to the job, at the same indentation as `runs-on:`:

```yaml
    permissions:
      contents: write
```

Push the fix, then push a new tag (you cannot reuse the old one):

```bash
git tag v1.0.1
git push origin v1.0.1
```

**What should happen:** the run succeeds, and a new release appears on the
right-hand side of your repository home page with the file attached.

**Why this matters:** This is called **least privilege**: give a job exactly
the permissions it needs and nothing more. If an action you trusted turns out
to be malicious, the damage it can do is limited to what you granted. A
workflow that only reads code cannot delete your branches, and a workflow that
can create issues cannot publish releases.

## Part 5: The finished file

When all eight tasks are done, your `ci.yml` should look like this. Use it to
check your work, but please do not simply paste it in at the start. The errors
are the lesson.

File: `.github/workflows/ci.yml` (final)

```yaml
name: CI Advanced

on:
  push:
    branches: [main]
    paths-ignore:
      - '**.md'
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      target:
        description: 'Where should we deploy?'
        required: true
        type: choice
        options:
          - staging
          - production
        default: staging
      dry_run:
        description: 'Only pretend to deploy?'
        required: false
        type: boolean
        default: true

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    outputs:
      build_id: ${{ steps.make_id.outputs.build_id }}
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Set up the project
        uses: ./.github/actions/setup-project
        with:
          node-version: '20'

      - name: Run the linter
        run: npm run lint

      - name: Create a build ID
        id: make_id
        run: echo "build_id=build-${GITHUB_RUN_NUMBER}" >> "$GITHUB_OUTPUT"

  test:
    needs: lint
    runs-on: ${{ matrix.os }}
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: ['18', '20', '22']
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Set up the project
        uses: ./.github/actions/setup-project
        with:
          node-version: ${{ matrix.node }}

      - name: Run the tests and save the output
        run: npm test > test-output.txt

      - name: Upload the test output
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-node${{ matrix.node }}
          path: test-output.txt

  report:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - name: Download every artifact from this run
        uses: actions/download-artifact@v4
        with:
          path: all-results

      - name: Write the report
        run: |
          S="$GITHUB_STEP_SUMMARY"
          echo "## CI Report" >> "$S"
          echo "" >> "$S"
          echo "- Build ID: ${{ needs.lint.outputs.build_id }}" >> "$S"
          echo "- Commit: ${{ github.sha }}" >> "$S"
          echo "- Started by: ${{ github.actor }}" >> "$S"
          echo "- Branch: ${{ github.ref_name }}" >> "$S"
          echo "" >> "$S"
          echo "### Artifacts collected" >> "$S"
          ls all-results | sed 's/^/- /' >> "$S"

  deploy:
    needs: report
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Show what I was asked to do
        run: |
          echo "Target: ${{ inputs.target }}"
          echo "Dry run: ${{ inputs.dry_run }}"

      - name: Pretend to deploy
        if: ${{ inputs.dry_run }}
        run: echo "DRY RUN - nothing was really deployed."

      - name: Really deploy
        if: ${{ !inputs.dry_run }}
        env:
          API_KEY: ${{ secrets.FAKE_API_KEY }}
        run: |
          echo "Deploying to ${{ inputs.target }} ..."
          echo "The key I was given is ${#API_KEY} characters long."
```

## Part 6: Check your work before submitting

Tick every line. If one of them does not match, go back to that task.

- [ ] Warm-up A failed with an invalid workflow message, and the fixed version
      shows two connected boxes in the job diagram.
- [ ] Warm-up B showed the secret hidden once and visible twice.
- [ ] The `test` job appears six times in the Actions tab with different names.
- [ ] Six separate artifacts are listed at the bottom of a successful run.
- [ ] The run page shows a formatted CI Report panel containing a build ID.
- [ ] The Run workflow button appears with a dropdown and a checkbox.
- [ ] With dry run ticked, the "Really deploy" step is skipped. With it
      unticked, "Pretend to deploy" is skipped.
- [ ] `.github/actions/setup-project/action.yml` exists and is used by both the
      `lint` and `test` jobs.
- [ ] Pushing twice quickly cancels the first run.
- [ ] A README-only push starts no run at all.
- [ ] A release exists for tag `v1.0.1` with a file attached.
- [ ] Your workflow permissions setting is read-only, and `release.yml` asks for
      `contents: write` for itself.

## Part 7: What to submit

1. A link to your public repository.
2. Your completed answer sheet ([Appendix A](#appendix-a-answer-sheet)), in your
   own words.
3. Three screenshots: the job diagram showing `lint`, `test`, `report` and
   `deploy`; the CI Report panel on a run page; the published release page.

Your commit history is part of the submission. Your instructor will look for
commits showing the broken `needs`, the fix, the artifact name clash, the fix,
the missing shell, the fix, the 403 error, and the fix. Those commits are the
proof that you ran into each problem yourself rather than copying the finished
file from Part 5.

## Appendix A: Answer sheet

Answer in your own words. Two or three sentences each is plenty. Do not copy
and paste from the documentation.

### Warm-up A

- **A1.** Did either job run, and how can you tell?
- **A2.** The exact error message.
- **A3.** How was this failure reported differently from the fake runner in
  Assignment 1?
- **A4.** Does GitHub check the whole file before starting, or discover problems
  as it goes?

### Warm-up B

- **B1.** The three log lines.
- **B2.** Why could the first be hidden but not the other two?
- **B3.** Is secret masking real protection or a convenience?
- **B4.** What could an untrusted third-party action do in a workflow that has
  your secrets?

### Main tasks

- **C1.** Why could the test job not find the file the lint job created?
- **C2.** How many copies of the test job ran, and what were they called?
- **C3.** Why did five of the six uploads fail?
- **C4.** What does `fail-fast` change, and when would you want each setting?
- **C5.** The folder structure the report job printed, and why there are six
  folders.
- **C6.** What the build ID printed when `lint` was removed from the `needs`
  list.
- **C7.** Three more context values you found, and what each contains.
- **C8.** What happened to the deploy job on a normal push, and what GitHub
  calls that state.
- **C9.** Which deploy step ran in each of the two manual runs.
- **C10.** Why passing a secret through `env:` is tidier than writing it inline.
- **C11.** The exact error message from the composite action without a shell.
- **C12.** Why GitHub could not find your own action when the step ran before
  checkout.
- **C13.** Why `cancel-in-progress` is good for PR checks but risky for deploys.
- **C14.** What happens to a hanging job with no timeout, and why that matters
  on a private repo.
- **C15.** The 403 error message, and the permission it named.

## Appendix B: Words you should now be able to explain

- **Job**: A unit of work that gets its own fresh, empty machine.
- `needs:`: Controls the order of jobs. It shares no files, only timing.
- **Matrix**: A loop that creates one job per combination of the values you list.
- **Artifact**: A file saved from a run so you, or another job, can download it.
- **Job output**: A short text value one job passes to another.
- **Step summary**: A Markdown panel displayed on the run page for humans to
  read.
- `workflow_dispatch`: A trigger that adds a Run workflow button,
  optionally with inputs.
- **Composite action**: Your own reusable group of steps, stored in your repository.
- **Reusable workflow**: A whole workflow file that another workflow can call.
- **Concurrency group**: A rule saying only one run of this kind may be
  active at a time.
- `GITHUB_TOKEN`: A temporary token given to each run, with
  permissions you control.
- **Least privilege**: Granting only the permissions actually needed, and
  nothing more.
