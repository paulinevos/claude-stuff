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
