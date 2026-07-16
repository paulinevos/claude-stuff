# Git conventions

Shared context for the git-workflow skills. Read it when organizing commits or
wording a commit message. Keywords (MUST, MUST NOT, SHOULD) are normative.

## Atomic commits

- Commits MUST be organized by purpose, not chronology.
- Each commit MUST be a single, irreducible unit — one coherent change, as small
  as possible without breaking on its own.
- Each commit MUST build and pass tests on its own, so history stays bisectable.
- A commit's purpose MUST be clear from its message alone.
- You MUST NOT create "checkpoint" commits ("wip", "more fixes"). When a change
  belongs in an existing commit, fold it in (use `maintain-atomic-commits`)
  rather than stacking a follow-up; when one change serves two purposes, split
  it into two.

## Commit messages

- The subject MUST be separated from the body by a blank line.
- The subject MUST be capitalized, MUST use the imperative mood ("Add", "Fix",
  not "Added"/"Fixes"), and MUST NOT end with a period.
- The body MUST wrap at 72 characters.
- The subject MUST say *what* changed; the body SHOULD say *why* — the
  motivation, constraint, or rejected alternative.
- The body SHOULD NOT narrate implementation; the diff shows that.

## Only rewrite local history

- You MUST NOT rewrite (amend, rebase, squash) a commit reachable from a shared
  branch like `main` or `develop` — others may have built on it, and rewriting
  forces everyone to reconcile diverging history.
- Before rewriting, determine which commits are local with
  `git log --oneline <base>..HEAD`. Those MAY be rewritten; everything below the
  base MUST be treated as frozen.

## Clear the working tree by stashing

- A rewrite needs a clean tree. You SHOULD `git stash` (`-u` to include untracked
  files) any uncommitted work, run the operation, then `git stash pop`.
- You MUST NOT commit half-finished work to move it aside — that creates the
  checkpoint commits above. If `pop` conflicts, the stash is retained until
  resolved, so nothing is lost.

## Prefer rebase over merge to stay current

- To bring a branch up to date, you SHOULD rebase onto the base
  (`git rebase [base]`, or `git rebase --onto [newbase] [oldbase]` for a
  different base) rather than merging the base in — a merge leaves a non-linear
  graph, whereas rebasing keeps history linear and each commit atomic.
- You need not hunt for duplicates: git omits any commit whose changes already
  exist on the base (matched by patch content). If a replay conflicts, see
  `resolve-merge-conflict`.
- Reserve merges for integrating a finished branch, not for staying current.
