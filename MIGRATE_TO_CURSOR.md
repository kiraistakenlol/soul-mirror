# Migration Guide: From `CLAUDE.md` to Cursor Project Rules

> **Goal:** Turn your single `CLAUDE.md` into a clean, scoped set of **Cursor Project Rules** that the Cursor Agent will reliably use. This playbook is written for an automated assistant (Claude/Cursor Agent) to execute with minimal human input.

**Last updated:** 2025-11-01 05:26:10 UTC

---

## 0) TL;DR (for the impatient automation)
1. Create a `.cursor/` folder at the repo root.
2. Create `.cursor/rules/` and split `CLAUDE.md` into multiple short **.md** rule files (topic- and folder-scoped).
3. (Optional) Keep a tiny legacy `.cursorrules` in the root that just points to `.cursor/rules/` (recommended only as a bridge).
4. Add a root **`.cursorignore`** to keep noise/sensitive files out of indexing and AI-context.
5. Turn on **Codebase Indexing** in Cursor settings; confirm status.
6. Smoke-test the rules from typical work areas (backend, frontend, scripts) and fix any rules the Agent ignores (split, shorten, or lift them earlier).

---

## 1) Why migrate this way (what Cursor expects)

- **Project Rules = persistent instructions**. Cursor prefers multiple, scoped markdown files in `.cursor/rules/` over one giant doc. This improves retrieval and relevance when the Agent decides which rules to include.
- **Indexing ≠ project knowledge**. Indexing helps find code, symbols, and references; rules tell the Agent *how to behave* (architecture choices, patterns, sharp edges). You need **both**.
- **Ignore files** control what the Agent and the index can see. Keep secrets, generated junk, and huge blobs out of context to improve quality and privacy.

> These assumptions match Cursor’s current docs: Project Rules under `.cursor/rules/` (with legacy `.cursorrules` still supported), Codebase Indexing enabled, and `.cursorignore` for access control.


---

## 2) What to create (directory map)

Create the following at the repo root:

```
.cursor/
  rules/
    overview.md
    conventions.md
    architecture.md
    api.md
    data.md
    dev-workflow.md
    deploy.md

apps/
  backend/
    .cursor/
      rules/
        backend.md
  frontend/
    .cursor/
      rules/
        frontend.md
  telegram-bot/
    .cursor/
      rules/
        bot.md
  test-runner/
    .cursor/
      rules/
        tests.md

# Legacy bridge (optional):
.cursorrules  # brief pointer to .cursor/rules/*
```

> **Why this split?** Short, topic-focused files are pulled more reliably than one long essay. Per-folder rules boost relevance when you’re working inside those directories.

---

## 3) How to split `CLAUDE.md` into rule files

> **Automation directive (Claude):** Parse the headings/sections in `CLAUDE.md` and map them into the below target files. If a section doesn’t fit, create a new file under `.cursor/rules/` with a good name (e.g., `observability.md`). Keep **rules short, imperative, and testable**.

### 3.1 Core rule files (repo root)

- **`overview.md`**  
  - Project one‑pager: current state, goals, constraints, priorities.
  - “What exists now / what’s next” (kept *very* fresh).
  - Link to the scoped rule files below.

- **`conventions.md`**  
  - Coding standards, “do/don’t”, naming, logging style, dead code policy, comments policy.
  - Use MUST/SHOULD bullets, minimal prose, with 1–2‑line examples.

- **`architecture.md`**  
  - System components, high‑level data/control flow, key services, background jobs.
  - Contracts between parts (e.g., tools/agents, repositories, adapters).

- **`api.md`**  
  - REST/RPC/GraphQL endpoints; inputs/outputs; auth notes.
  - Tables or short lists grouped by feature area.

- **`data.md`**  
  - DB schema overview, timestamps/triggers, repositories, migrations.
  - Guidance on queries vs. repository methods.

- **`dev-workflow.md`**  
  - Install commands, local run, environment variables layout, hot reload, ports.
  - Notes on tests, linting, formatting, type checks, pre‑commit hooks.

- **`deploy.md`**  
  - Envs (dev/stage/prod), domains, CI/CD, scripts, manual steps, rollback.

### 3.2 Per‑folder scoped rules (example apps/ layout)

- **`apps/backend/.cursor/rules/backend.md`**  
  - Server/agent tooling, request lifecycles, error handling, logging, repos, env.
  - Any “never do X” landmines that are backend-only.

- **`apps/frontend/.cursor/rules/frontend.md`**  
  - Pages/layout, UI state, routing, components, query/mutation patterns.
  - Any refresh intervals/keyboard shortcuts, preferred UI libs.

- **`apps/telegram-bot/.cursor/rules/bot.md`**  
  - Bot commands, message flow, transcription/translation notes, token handling.

- **`apps/test-runner/.cursor/rules/tests.md`**  
  - Test scenarios, evaluator expectations, ports, fixtures, data seeding.

> **Tip:** If a per-folder file grows beyond ~150–250 lines, split it by topic (`api-rules.md`, `observability.md`, etc.).


---

## 4) Rule file template (copy‑paste)

> **Automation directive (Claude):** When transforming each section of `CLAUDE.md`, normalize into the following template. Prefer bullets with MUST/SHOULD and concrete examples.

```md
# <Scope Title>

## When you’re editing files in <path>...
- MUST: <short rule>
- SHOULD: <short rule>
- MUST NOT: <short rule>

## Patterns
- Use <lib/pattern> for <problem> (Reason: <1 line>).
- Prefer <X> over <Y> in <folder>.

## Interfaces / Contracts
- <Module/Tool>: accepts <shape>, returns <shape>, errors <cases>.
- All calls MUST <constraint>.

## Gotchas
- Never <pitfall> (breaks <thing>).
- Avoid <edge case> in <folder>.

## Examples (1–2 lines each)
- ✅ Do: <tiny good example>
- ❌ Don’t: <tiny bad example>
```

**Formatting rules**
- Use **short bullets**, not essays. If a rule needs context, add a single ‑line reason.
- Prefer specifics (“Use zod for input validation under `/api/*`”) over vague language.
- Link out to longer docs in your repo, but keep the rule self‑sufficient.


---

## 5) Add a `.cursorignore` (privacy, speed, signal)

Create a root `.cursorignore` to keep sensitive or noisy files out of indexing and AI context.

```gitignore
# secrets
.env
.env.*
*.pem
*.key

# build artifacts
dist/
build/
.out/
.next/
coverage/
reports/

# large/media
*.mp4
*.mov
*.zip
*.tar
*.gz

# data dumps
dump.sql
*.sqlite
*.db

# generated docs / caches
node_modules/
*.cache/
*.log
```

> **Notes**
> - Keep this **stricter** than `.gitignore` if needed. You can still allow specific files back in with negation patterns (e.g., `!.env.example`).  
> - If a file must be available to the Agent but not committed, *copy* non‑secret snippets into a rule file or a safe placeholder (`.env.example`).


---

## 6) Migrate the old file(s)

1. **Backup**: Commit the current `CLAUDE.md` (and optionally tag a `pre-cursor-rules` commit).
2. **Create** `.cursor/rules/` and per‑folder rule directories as above.
3. **Transform**: Split content from `CLAUDE.md` into the new files using the template.
4. **(Optional) Bridge**: Create a tiny root `.cursorrules` that only says:
   ```md
   This repository uses **Cursor Project Rules**. See `.cursor/rules/*` and `apps/*/.cursor/rules/*`.
   ```
5. **Remove** any duplicated long prose; keep rules short. Move background text to `overview.md` or existing docs (README/Wiki).


---

## 7) Turn on and verify Codebase Indexing

1. Open the repo in **Cursor**.
2. Go to **Settings → Indexing & Docs** and ensure **Codebase Indexing** is enabled.
3. Wait for indexing to finish (large repos may take longer). Confirm the status bar or settings indicator shows completion.
4. (Optional) If you added `.cursorignore`, reindex if needed.

**Sanity check:** Ask the Agent to locate a symbol or file **by name** and summarize it. If it can’t find it, check your `.cursorignore` or indexing status.


---

## 8) QA: prompts to validate the rules work

Run these checks **inside the relevant folder** with the corresponding rule file present.

- **Global sanity**  
  “Summarize our project rules. What should you always do in this repo? What should you never do?”

- **Backend**  
  “Add a new `/api/example` endpoint using our patterns. Follow logging and error rules.”

- **Frontend**  
  “Refactor the `Header` component to use our UI rules. Keep shortcuts and refresh intervals.”

- **Data**  
  “Create a migration for `<table>` with timestamps and update the repository methods accordingly.”

- **Deployment**  
  “Prepare a release build for staging, then outline the exact steps to deploy using our scripts.”

If the Agent violates a rule, **move that rule earlier** in the relevant file or **split it** into its own file with a clearer name. Short, obvious rules are prioritized.


---

## 9) Team handoff and maintenance

- **Keep `overview.md` fresh**; it’s your “current truth” for the Agent.
- When a rule changes, **update the smallest relevant file** and commit.
- If rules grow, split them by topic; avoid files > ~250 lines.
- Add a 5‑line **README** section for humans: “This repo uses Cursor Project Rules; start here: `.cursor/rules/overview.md`.”


---

## 10) Troubleshooting

- **Agent ignores rules** → Split long files, rename to be more direct, move critical rules to the top. Confirm you are in the folder that has scoped rules (per‑folder `.cursor/rules/`).  
- **Missing/old context** → Verify indexing status; re-open the repo; check `.cursorignore`.  
- **Leaking secrets** → Tighten `.cursorignore`; mirror only safe examples in rules; never include real tokens in rule files.  
- **Slow or noisy results** → Expand `.cursorignore` (artifacts, logs, large assets).  
- **Single‑file nostalgia** → Keep a tiny `.cursorrules` that only points to the new rules; don’t duplicate content.

---

## 11) Done checklist (automation can assert these)

- [ ] `.cursor/rules/` exists with core files (`overview.md`, `conventions.md`, `architecture.md`, `api.md`, `data.md`, `dev-workflow.md`, `deploy.md`).
- [ ] Per‑folder `.cursor/rules/` exist in key app directories (backend, frontend, bot, tests).
- [ ] `CLAUDE.md` content is fully transformed into the new files.
- [ ] `.cursorrules` exists (optional) and only points to the new structure.
- [ ] `.cursorignore` exists with secrets/junk excluded.
- [ ] Indexing enabled and completed; spot‑checks pass.
- [ ] QA prompts run without critical rule violations.
- [ ] README mentions `.cursor/rules/` entry point.

---

## Appendix A — Examples you can paste into files

**Minimal `overview.md`**

```md
# Project Overview (One‑Pager)

## Current State
- <1–5 bullets that describe exactly what works today>

## Near‑Term Priorities
- <ordered bullets of the next things to build>

## Entry Points
- Backend rules: apps/backend/.cursor/rules/backend.md
- Frontend rules: apps/frontend/.cursor/rules/frontend.md
- Data rules: .cursor/rules/data.md
```

**Minimal `conventions.md`**

```md
# Conventions

## Always
- MUST: Use structured, expressive logs with context.
- MUST: Remove dead code as you touch a file.
- SHOULD: Keep functions small and pure when possible.

## Never
- MUST NOT: Commit secrets or real credentials.
- MUST NOT: Add tech we don’t already use without a rule update.
```

**Minimal `backend.md`**

```md
# Backend Rules

## When editing /apps/backend/
- MUST: Validate inputs with our chosen library in /api/*.
- MUST: Centralize DB access via repositories.
- MUST NOT: Bypass error middleware; use standardized error helpers.

## Gotchas
- Never run a second hot‑reload server locally; use the existing dev script.
```

---

## Appendix B — Safe patterns for secrets & environment

- Keep real `.env` out of AI context with `.cursorignore`.  
- Provide **`.env.example`** with placeholders used in docs/rules.  
- If the Agent needs a value to generate code, stub it out in code or the example file; replace manually later.

---

## Appendix C — Rollback plan

- Revert to the `pre-cursor-rules` tag (or the commit before the migration).
- Remove `.cursor/` and `.cursorrules` if desired.
- Restore the original `CLAUDE.md`.
- Re-run indexing if you changed ignore files.

---

**End of guide.**
