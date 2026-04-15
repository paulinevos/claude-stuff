# Version Control Skills

## Overview
This skill describes best practices for version control using Git. Use this skill when making changes in your codebase. These skills embody an "atomic commit" workflow and involve amending existing commits. When applying these skills, always take into account commits that are new on the active branch relative to its base branch. We don't want to amend commits that are already part of public branches like "main" or "develop". 

## Skills

### rebase
**Trigger:** When a branch is outdated from its base branch.
**Description:** Compare commits on the current and base branches using `git log`, and take note of commits that look duplicated on either branch. Then run an interactive rebase onto the base branch using `git rebase -i`. The swap file for interactive commits will be opened. Remove lines for any commits that look like duplicates. 
**Usage:** `/rebase [base-branch]`

### resolve-merge-conflict
**Trigger:** When a merge conflict arises
**Description:** Attempt to consolidate the conflicting changes. Always show the proposed resolution and ask for confirmation. If the user wants to keep their own changes instead, run `git add [file-path] --theirs`. Conversely, run `git add [file-path] --ours` when they want to keep the incoming changes. After resolving all conflicts, continue whatever was running (i.e. `git rebase --continue` or `git cherry-pick --continue`)
**Usage:** `/resolve [file-path]`

### stash
**Trigger:** When a user attempts to perform an operation that requires no unstaged changes
**Description**: Use `git stash` when there are unstaged changes before performing an operation like rebase. After the operation is concluded, use `git stash pop` to return the unstaged changes.
**Usage:** `/stash`

### edit-commit
**Trigger:** Before starting changes that belong to an existing commit.
When planning to start on some changes, try to guess if an unstaged change logically belongs in an existing commit. If so, Run `git rebase -i HEAD~[number-of-commits]` and change the prefix of the relevant commit to `e`, then save the file. This will check out the relevant commit. Make the changes, then run `git rebase --continue`. You may change the commit message that comes up if relevant, then save the file. The change has now been amended to the commit.
**Usage:** `/edit `

### fixup
**Trigger:** When changes are made pertaining to existing commits
**Description:** When working on a set of changes, try to guess if an unstaged change logically belongs in an existing commit. If so, stage any changes that belong to that commit using `git add -p [file-name]`. Then run `git commit --fixup [commit-id]`.

Sometimes, different hunks in a single file should be added to multiple different commits, for instance in this example:

### Example
Commit 1: changes a method signature in Foo.php
Commit 2: adds a method in Foo.php

Unstaged changes in Foo.php: 
- fixed typo in the changed signature (belongs in commit 1)
- added error handling in the new method (belongs in commit 2)

When all unstaged changes have been recorded in fixup commits, ask the user if that seems right. If so, perform in interactive rebase with `git rebase -i HEAD~[number-of-commits] --autosqash` to squash the fixup commits in their respective commits.
**Usage:** `/fixup`

### undo-op
**Trigger:** When the user requests to undo an operation like merge, rebase, reset, amend.
**Description:** Use `git reflog` to guess the operation described by the user. Then use `git checkout HEAD~{%d}` to the next operation on the list (before the described operation). Ask the user if this is the expected outcome. If so, `git checkout [current-branch]` and `git reset --hard HEAD{%d}` to reset the state of the branch to the expected state.
**Usage:** `/undo [current-branch, description]`

## Conventions

### Atomic commits
Atomic commits are commits that are organized by purpose. Atomic commits have three features:

- Single, irreducible unit. Every commit pertains to one coherent set of changes, as small as possible without breaking anything.
- Everything works. Don't break the build or test suite on any commit.
- Clear and concise. The commit changes one thing, and its purpose is clear from commit message and description.

The opposite of an atomic commit is a "checkpoint commit": a commit that is created in a linear fashion, committing as you go like a save point in a video game. This is not what we want to achieve. This means that when making new changes that pertain to an existing commit, those changes should be added to that commit instead of being placed in a new commit. It also means that changes that serve different purposes do not go in a single commit.

### Commit message conventions
- Separate subject from body with a blank line
- Do not end the subject line with a period
- Capitalize the subject line and each paragraph
- Use the imperative mood in the subject line
- Wrap lines at 72 characters
- Use the subject line to describe what has changed
- Use the description to describe why the changes were needed
- Don't go into detail technical implementation -- that will be apparent from the diff.
