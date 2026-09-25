# Current: after skill compaction

Measured with `ruby scripts/benchmark-skills.rb` after the compaction and
workspace-permission revisions.

| Skill | Lines | Words | Bytes |
| --- | ---: | ---: | ---: |
| `plugins/git-workflow/skills/bisect-debug/SKILL.md` | 21 | 138 | 878 |
| `plugins/git-workflow/skills/maintain-atomic-commits/SKILL.md` | 21 | 190 | 1239 |
| `plugins/git-workflow/skills/resolve-merge-conflict/SKILL.md` | 17 | 120 | 837 |
| `plugins/git-workflow/skills/undo-op/SKILL.md` | 19 | 136 | 852 |
| `plugins/jj-workflow/skills/finish-slices/SKILL.md` | 39 | 239 | 1594 |
| `plugins/jj-workflow/skills/parallel-slices/SKILL.md` | 45 | 320 | 2438 |
| `plugins/jj-workflow/skills/sync-workspace/SKILL.md` | 20 | 199 | 1289 |
| `plugins/jj-workflow/skills/work-in-slice/SKILL.md` | 44 | 302 | 1956 |
| `plugins/php-style/skills/php-object-calisthenics/SKILL.md` | 67 | 506 | 3496 |
| **Total** | **293** | **2150** | **14579** |

Compared with the baseline: 545 fewer lines (65.0%), 4,441 fewer words
(67.4%), and 27,116 fewer bytes (65.0%).
