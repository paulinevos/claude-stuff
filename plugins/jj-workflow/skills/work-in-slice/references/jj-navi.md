# Managing workspaces with jj-navi

[`jj-navi`](https://github.com/eersnington/jj-navi) manages jj workspace
lifecycle: naming, deterministic paths, switching, inventory, and cleanup. It
is **optional**. Every skill in this plugin works with plain `jj`; `navi` only
removes bookkeeping. Verified against jj-navi 0.2.3 and jj 0.43.

Binaries: `navi` and `nv` (identical). Requires jj >= 0.39.

## Detecting and installing

```sh
navi --version
```

If that fails, `jj-navi` is not installed. Offer it, do not install it: a
global package is the user's call.

```sh
npm install -g jj-navi      # or: cargo install jj-navi
navi config shell install --shell zsh && source ~/.zshrc   # optional, bash/zsh
```

Shell integration only lets `navi switch` change an interactive shell's
directory. An agent cannot change its own shell's cwd, so skip it; without it
`switch` simply prints the resolved path on stdout, which is what you want —
capture it and `cd` in your own command.

## Point it at this plugin's workspace layout

`navi` plans paths from a repo-scoped template, default `../{repo}.{workspace}`,
which puts workspaces next to the checkout rather than under the centralised
root this plugin requires. Absolute templates are allowed, so set it once per
repo, before creating the first workspace, and `navi` will match the
convention in `conventions.md`:

```sh
mkdir -p "$(jj root)/.jj/repo/navi"
cat > "$(jj root)/.jj/repo/navi/config.toml" <<EOF
workspace_template = "${HOME}/.jj-workspaces/{repo}/{workspace}"
EOF
```

Only `{repo}` and `{workspace}` are substituted; any other brace placeholder is
rejected, and nothing expands `~` or `$HOME` — write the path out in full (the
heredoc above is unquoted, so the shell expands `${HOME}` as it writes). Config
and metadata live in shared jj storage, at `.jj/repo/navi/config.toml` and
`.jj/repo/navi/workspaces.toml`, so every workspace sees the same settings.

## What is safe for whom

`navi` is workspace-level tooling, so the ownership rule in `conventions.md`
decides who may run what.

| Command | Who | Notes |
| --- | --- | --- |
| `navi doctor [-j]` | anyone | Read-only health of repo, workspace, and shell. |
| `navi switch <ws>` | anyone | Resolves and prints a path; does not touch other workspaces' commits. |
| `navi switch -c <ws> -r <revset>` | orchestrator | Creates the workspace and switches to it. |
| `navi list [-j]` | orchestrator | **Snapshots every healthy workspace**, see below. |
| `navi remove <ws> [-y]` | orchestrator | Forgets the workspace *and* deletes its directory. |
| `navi merge -f <ws>` | nobody, in this workflow | Duplicates revisions; see below. |

Shorthands: `navi cd` = `switch`, `navi ls` = `list`, `navi rm` = `remove`.
`switch ^` goes to the primary workspace, `switch -` to the previous one, and
`switch @` to the current one.

### `navi list` snapshots other workspaces

To fix the stale cross-workspace view that plain `jj log` gives, `list` runs
`jj util snapshot` inside every workspace whose path it can resolve, then
renders path health, diff stats, commit info, and age. That write is exactly
what `conventions.md` forbids an orchestrator from doing by hand: it captures
another worker's half-written files into their `@`.

It is still the right command for a workspace inventory — just know it is not
read-only, and prefer it when workers are idle (between hand-offs, during
cleanup). While workers are mid-change, inspect with revsets from your own
workspace instead:

```sh
jj log -r '<slice>@' --ignore-working-copy
jj log -r 'trunk()..<slice>' --ignore-working-copy
```

`navi list --json` exposes structured `freshness`, `diff`, and `age` fields and
reports missing, stale, and not-current workspaces rather than hiding them; add
`--compact` for one-line JSON. Use `--json` whenever you parse the output.

### `navi merge` does not fit stacked slices

`merge -f <source> [-i <target>]` duplicates the source workspace's revisions
(`jj duplicate`), rebases the copy onto the target, and starts a new working
copy on top. The duplicates get **new change IDs**, so the original revisions
and their bookmark stay behind: the slice is now in two places, the source
bookmark still points at the old copies, and a later rebase of the real slice
conflicts with the duplicate.

This plugin stacks slices by rebasing instead, which preserves change IDs and
lets bookmarks follow:

```sh
jj git fetch && jj rebase -b <slice> -o <base>
```

Use `navi merge` only for a throwaway workspace whose work you want copied
somewhere else and whose bookmark you do not intend to push.

## Equivalents

Everything `navi` does has a plain-jj form; neither column is preferred, and a
repo with no `navi` installed loses nothing.

| Task | With `navi` | With plain `jj` |
| --- | --- | --- |
| Create a workspace | `navi switch -c <slice> -r 'trunk()'` | `mkdir -p "${HOME}/.jj-workspaces/<repo>" && jj workspace add --name <slice> -r 'trunk()' --sparse-patterns full "${HOME}/.jj-workspaces/<repo>/<slice>"` |
| Find a workspace path | `navi switch <slice>` (prints it) | `jj workspace root --name <slice>` |
| Inventory | `navi list --json` | `jj workspace list` + `jj log -r '<slice>@' --ignore-working-copy` |
| Remove a finished slice | `navi remove <slice> --yes` | `jj workspace forget <slice> && rm -rf "${HOME}/.jj-workspaces/<repo>/<slice>"` |
| Health check | `navi doctor` | `jj status`, `jj workspace list` |

Two gaps to know when you create workspaces through `navi`:

- `navi` does not pass `--sparse-patterns`, so a new workspace **inherits the
  current workspace's sparse patterns**. In a repo with sparse patterns set,
  create workspaces with `jj workspace add --sparse-patterns full` instead, or
  the worker will be missing files.
- `navi remove` refuses to remove the workspace you are currently in, and
  prompts before deleting the directory; `--yes` skips the prompt. Run it from
  the default workspace, as `finish-slices` requires.
