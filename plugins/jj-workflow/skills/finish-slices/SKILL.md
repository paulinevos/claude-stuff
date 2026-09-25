---
name: finish-slices
description: Verify and publish completed Jujutsu slices, then after each PR merges forget its workspace, remove its centralised directory, and clean up its bookmark.
---

# finish-slices

Run from the default workspace. For every slice, verify its revisions are
described, conflict-free, and all reachable from its bookmark:

```sh
jj log -r '<base>..<slice>' --no-graph --reversed -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
jj log -r '(<base>..<slice>) & (conflicts() | description(exact:""))'
jj log -r '(<slice>:: ~ <slice>) ~ working_copies() ~ ::(bookmarks() ~ <slice>)'
```

If needed, fetch and rebase the slice onto `trunk()` (or its child onto its
parent), then verify again. Fix an unadvanced bookmark only when its worker has
finished and the repair is mechanical.

Show the per-slice revision lists and parent-first push order; wait for explicit
approval before `jj git push --bookmark <slice>`. Stack child PRs on their
parent. When a parent merges, rebase and push its child, then retarget it to
`main`.

Keep a workspace while its PR may need changes. Once that PR merges:

```sh
jj git fetch
jj bookmark delete <slice>       # or `jj bookmark forget` if the forge removed it
jj workspace forget <slice>
rm -rf "${HOME}/.jj-workspaces/<repo>/<slice>"
jj workspace list
```

Forget by name from the default workspace, never from the workspace being
forgotten. `jj forget` removes only jj's record; always remove the directory.
An empty `@` is abandoned automatically; reconcile or abandon a non-empty
anonymous head before cleanup.
