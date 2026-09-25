# Skill-context benchmark

Run `ruby scripts/benchmark-skills.rb` from the repository root. It measures
the text loaded from every `SKILL.md`: line count, word count, and bytes. The
baseline is the state before the skill compaction revision; compare future runs
against it to make increases in agent context explicit.
