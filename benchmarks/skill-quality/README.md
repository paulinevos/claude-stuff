# Skill-quality benchmark

This benchmark checks whether an agent can still produce the important outcomes
from the skills after they are compressed. It runs nine natural developer
requests—one per skill—against exact Jujutsu revisions in isolated, read-only
temporary directories. Each response is checked against broad outcome patterns;
the cases do not name the target skill.

Run it with:

```sh
ruby scripts/benchmark-skill-quality.rb <revision> <output.json>
```

The retained reports compare the pre-compaction baseline (`ulvtkopm`) with the
current benchmarked revision (`tzlsrnwp`): 7/9 and 9/9 passing cases,
respectively. The baseline misses explicit publish confirmation and one
rebase-continuation outcome; the current revision passes every case.

This is a single-run, model-based behavioural check, not a statistically powered
quality claim. Re-run each revision multiple times before using it as a release
gate; use the stored responses to inspect any score change rather than treating
the regex score alone as a verdict.

## Runners

`BENCHMARK_RUNNER` selects the runtime: `codex` (the default) or `claude`.
`BENCHMARK_MODEL` pins the model for the `claude` runner, defaulting to
`sonnet`.

The two are not comparable. `results/pr-reviewer.json` records twelve cases on
the `claude` runner: the three `pr-reviewer` cases pass, and four cases that
pass under codex in `results/current.json` fail here. Reading those four shows
the plans are still right — one omits the literal skill name it is told to
hand off to, another describes confirming a push without using the word. They
are scoring differences between runtimes, not regressions. Compare a revision
only against another run on the same runner and model.

The `claude` runner denies every tool and inlines the skill text into the
prompt. A case is meant to measure what the skill text leads an agent to say;
an agent left free to read and shell out answers from the operator's own
machine instead, which both invalidates the score and leaves files behind.
