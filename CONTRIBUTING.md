# 🤝 Contributing to PsycheCare

Thank you for contributing to **PsycheCare** — a mental health support platform! This guide covers everything you need to get started, submit quality PRs, and earn GSSoC points.

---

## 📋 Table of Contents
1. [Project Setup](#-project-setup)
2. [Branch Naming](#-branch-naming-convention)
3. [Commit Messages](#-commit-message-format)
4. [Submitting a PR](#-submitting-a-pull-request)
5. [GSSoC Label System](#-gssoc-label-system)
6. [Code Style Guide](#-code-style-guide)
7. [Getting Help](#-getting-help)

---

## 🛠️ Project Setup

### Prerequisites
- Git
- A modern browser (Chrome / Firefox / Edge)
- Python 3.8+ (for chatbot backend)
- PHP 7.4+ (for login/contact forms)

### Local Setup
```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/PYSCHECARE-main.git
cd PYSCHECARE-main

# 2. Add the upstream remote
git remote add upstream https://github.com/Niteshagarwal01/PYSCHECARE-main.git

# 3. Open index.html directly in your browser for frontend work
# OR serve with a local server:
npx serve .

# 4. For the chatbot backend (Python):
pip install -r requirements.txt
python app.py
```

### Keeping Your Fork Updated
```bash
git fetch upstream
git checkout main
git rebase upstream/main
git push origin main
```

---

## 🌿 Branch Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Bug fix | `fix/issue-<N>-short-description` | `fix/issue-12-xss-chatbot` |
| New feature | `feat/<short-description>` | `feat/password-toggle` |
| Documentation | `docs/<short-description>` | `docs/update-readme` |
| DevOps / CI | `devops/<short-description>` | `devops/upgrade-codeql-v3` |
| Refactor | `refactor/<short-description>` | `refactor/clean-app-js` |

> ✅ Always branch off from `main`. Never commit directly to `main`.

---

## 💬 Commit Message Format

Follow the **Conventional Commits** standard:

```
type(scope): short description

Optional longer body explaining the WHY.
```

### Types
| Type | When to Use |
|------|------------|
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `docs` | Documentation only changes |
| `refactor` | Code cleanup with no behaviour change |
| `style` | CSS / formatting changes |
| `test` | Adding or fixing tests |
| `devops` | CI/CD workflow changes |
| `perf` | Performance improvements |
| `security` | Security fixes |

### Examples
```bash
feat(chatbot): add rate limiting to /chat endpoint
fix(login): prevent error message via URL query param
docs(readme): add local setup instructions
devops(codeql): upgrade from v2 to v3 actions
security(contact): add input length validation to process_contact.php
```

---

## 🚀 Submitting a Pull Request

1. **Create an issue first** — every PR should fix or implement a tracked issue
2. **Branch off main** — `git checkout -b fix/issue-42-description`
3. **Make your changes** — keep PRs small and focused (one issue per PR)
4. **Test thoroughly** — check browser, mobile view, and console errors
5. **Push your branch** — `git push origin your-branch-name`
6. **Open the PR** — the PR template will auto-fill with the required sections
7. **Fill in the template** — especially the `Closes #` field and type of change

> ⚠️ PRs without a linked issue or without the PR template filled in may be closed without review.

---

## 🏷️ GSSoC Label System

Every merged PR earns points based on its labels. Labels are applied by **maintainers only**.

### Label Categories

#### Difficulty — Required, Pick ONE
| Label | Points |
|-------|--------|
| `level:beginner` | 20 pts |
| `level:intermediate` | 35 pts |
| `level:advanced` | 55 pts |
| `level:critical` | 80 pts |

#### Quality — Optional Multiplier (applied on difficulty points)
| Label | Multiplier |
|-------|-----------|
| `quality:clean` | ×1.0 |
| `quality:exceptional` | ×1.5 |

#### Type — Optional, Stackable
| Label | Points |
|-------|--------|
| `type:security` | +20 pts |
| `type:devops` | +15 pts |
| `type:performance` | +15 pts |
| `type:accessibility` | +15 pts |
| `type:bug` | +10 pts |
| `type:feature` | +10 pts |
| `type:testing` | +10 pts |
| `type:refactor` | +10 pts |
| `type:design` | +10 pts |
| `type:docs` | +5 pts |

### Score Formula
```
Score = 50 (base) + (difficulty × quality) + type_bonus
```

### Example
`level:advanced` + `quality:exceptional` + `type:bug` + `type:security`
= 50 + (55 × 1.5) + 10 + 20
= 50 + 82.5 + 30 = **162.5 pts**

> 🤖 The GSSoC Score Bot automatically posts a score breakdown on every PR when labels change.

---

## 🎨 Code Style Guide

### HTML
- Use semantic elements (`<header>`, `<main>`, `<section>`, `<footer>`)
- Always include `alt` text on images
- Keep inline styles minimal — use CSS classes instead
- Validate at [validator.w3.org](https://validator.w3.org)

### CSS
- Use CSS variables defined in `style.css` (e.g. `var(--primary-color)`)
- Mobile-first: add `@media (min-width: ...)` for larger screens
- Avoid `!important` unless absolutely necessary

### JavaScript
- Always add null checks before using `querySelector` results
- Use `const` and `let`, never `var`
- Add comments for non-obvious logic
- No `console.log` statements in final PR (use `console.warn`/`console.error`)

### Python
- Follow PEP 8 style
- Add docstrings to all functions
- Handle exceptions explicitly — no bare `except:` clauses
- Validate and sanitize all user inputs before processing

### PHP
- Sanitize all `$_POST` / `$_GET` inputs with `htmlspecialchars()`
- Always validate input length
- Never store passwords in plain text

---

## 🙋 Getting Help

- 💬 **Questions?** Open a [GitHub Discussion](https://github.com/Niteshagarwal01/PYSCHECARE-main/discussions)
- 🐛 **Found a bug?** [Open a Bug Report](https://github.com/Niteshagarwal01/PYSCHECARE-main/issues/new?template=bug_report.md)
- ✨ **Have an idea?** [Open a Feature Request](https://github.com/Niteshagarwal01/PYSCHECARE-main/issues/new?template=feature_request.md)
- 🔒 **Security issue?** Use [GitHub Security Advisories](https://github.com/Niteshagarwal01/PYSCHECARE-main/security/advisories/new) — **do not open a public issue**

---

*Thank you for making PsycheCare better for people seeking mental health support. 💜*
