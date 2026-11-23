# Trim Docs — Example

A real before/after from trimming an `asana-tasks` skill reading section.

## Before (36 words, two violations)

```markdown
## Reading tasks

Always read all three before planning or implementing. Agents and humans skim
from the top; a decision buried at the end will be missed. The key content is
in `notes`, `comments`, and `subtasks` — read them all.
```

**Violations:**
- "Agents and humans skim from the top; a decision buried at the end will be missed" — rationale, not a rule (KISS)
- Rule stated twice: first sentence + last sentence (DRY)

## After (10 words)

```markdown
## Reading tasks

Always read `notes`, `comments`, and `subtasks` before planning or implementing.
```

**Result:** 36 words → 10 words. No actionable rule dropped.
