---
description: Git workflow, commit messages, and branching strategy
applyTo: "**/*"
---

# Git Instructions

- Always use English for commit messages.
- Never include "Generated with Claude" (or similar) in commits.

## Branching and Flow

- Main branch is `develop`.
- Never commit directly to `develop`; always use a feature branch.
- Branch naming: `<type>/ds-<short-description>`.

Examples:

```
feature/ds-coupon-sharing
hotfix/ds-gopay-timeout
release/1.0.0
```

Start work:

```bash
git checkout develop
git fetch --verbose
git pull origin develop
git checkout -b feature/ds-new-feature
```

## Commit Messages

Format:

```
<type>: <description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`.

Rules:

- Max 50 characters on the first line.
- Lowercase, no period, imperative mood.

Examples:

```
feat: add coupon preview modal
fix: handle gopay callback timeout
docs: update AGENTS.md links
```

## Before Committing

- Review changes: `git status`, `git diff`.
- Run checks: `npm run lint` and `npm run build`.

## Good Practices

- Keep commits atomic (one logical change).
- Commit frequently after each completed step.
- If you need to fix a commit message before push:

```bash
git commit --amend -m "fix: correct commit message"
```

## Undo (Use Carefully)

```bash
git reset HEAD <file>      # Unstage
git checkout -- <file>     # Discard local changes
git reset --soft HEAD~1    # Undo last commit, keep changes
```
