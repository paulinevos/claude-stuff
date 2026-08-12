# Git fallback: the same flow with worktrees

Use this when `jj root` fails, or when git submodules matter to the work (jj
does not materialise submodules in a workspace). The shape is identical: one
worktree and one branch per slice, granular commits, rebase to stay current,
remove the worktree when done.

## Orchestrator

```sh
git fetch origin
repo=$(basename "$(git rev-parse --show-toplevel)")
mkdir -p "../$repo.worktrees"
git worktree add -b <slice> "../$repo.worktrees/<slice>" origin/main        # independent slice
git worktree add -b <child> "../$repo.worktrees/<child>" <parent-slice>     # dependent slice
git -C "../$repo.worktrees/<slice>" submodule update --init --recursive     # when submodules matter
git worktree list
```

Never run mutating git commands inside another worker's worktree. Inspect with
`git log <slice>` or `git diff origin/main...<slice>` from your own checkout.

## Worker

Work only inside the assigned worktree. One atomic commit per logical step;
`git commit --fixup <commit>` for a fix to an earlier step, then
`git rebase -i --autosquash origin/main` (or `<parent-slice>` for a dependent
slice) before hand-off. Stay current with `git fetch origin && git rebase
origin/main`; for a dependent slice `git rebase <parent-slice>`, or
`git rebase --onto <parent-slice> <old-parent-tip>` if the parent was rewritten.
Resolve conflicts, `git add`, `git rebase --continue`. Hand off with a clean
tree (`git status`) and a pushed-nothing branch.

## Finish

```sh
git log --oneline origin/main..<slice>              # review per slice, then confirm with the user
git push -u origin <slice>                          # first push
git push --force-with-lease origin <slice>          # after a rebase
git worktree remove "../$repo.worktrees/<slice>"    # add --force only if the tree is dirty on purpose
git worktree prune
git branch -d <slice>                               # after the PR merged
```

Stacked slices: open the child PR against the parent branch; when the parent
merges, `git rebase origin/main` the child, force-push with lease, and retarget
the PR to `main`.
