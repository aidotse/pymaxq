# Working with Claude Code

In 2026, a coding agent is part of the toolchain. This project is set up to be developed
with [Claude Code](https://code.claude.com/docs/en/overview), Anthropic's agentic CLI, and
this page captures the high-level practices for using it well here. It's an *overview, not a
manual* — see the [official docs](https://code.claude.com/docs/en/best-practices) for depth.

## Setup

```bash
curl -fsSL https://claude.ai/install.sh | bash   # macOS / Linux / WSL
# or: npm install -g @anthropic-ai/claude-code
```

Launch `claude` from the project root. On the first run in a new repo, generate the project
memory file:

```text
/init
```

`/init` scans the repo and writes a `CLAUDE.md` — a persistent, project-specific guide
(tech stack, `poe` tasks, conventions) loaded into every session so the agent doesn't waste
context rediscovering how to build and test.

## The practices that matter most

Adapted from Anthropic's [best-practices guide](https://code.claude.com/docs/en/best-practices),
in rough priority order:

1. **Give Claude a way to verify its work.** The single highest-leverage habit. Point it at
   this project's gates — `uv run poe test`, `uv run poe lint` — and ask it to run them and act
   on the output. A feedback loop beats one-shot generation every time.
2. **Explore → plan → code.** For anything non-trivial, use **Plan Mode** (`Shift+Tab` cycles
   default → accept-edits → plan) so Claude investigates and proposes a plan you approve *before*
   it edits. Skip it for typos and one-line fixes.
3. **Be specific and give context.** `@`-mention the relevant files, paste the actual error,
   state the constraint. Rich context beats a vague ask.
4. **Configure the environment.** A good `CLAUDE.md`, sensible permission rules, and any MCP
   servers/hooks you need (see below). Setup you do once pays off every session.
5. **Manage the session.** Course-correct *early* with `Esc` instead of letting a wrong approach
   run; `/compact` when context fills; `/clear` between unrelated tasks.

## Maintaining CLAUDE.md

`CLAUDE.md` is an operational manual for *how to build and run* the project — not a map of the
code (Claude indexes files, functions, and tests at runtime).

- **Don't update it** when you add source files, tests, or features — those are discovered
  automatically.
- **Do update it** when your `poe` tasks change, you switch tools, or you set new architectural
  rules for the team.
- **Don't re-run `/init`** to update (it overwrites your customizations). Just ask
  conversationally: *"We changed a poe task — update CLAUDE.md to match."*

## Permissions

By default Claude prompts before running commands that could modify state. Use `/permissions`
to auto-approve high-frequency, safe commands (read-only ones like `git status` already
auto-approve), storing patterns under `permissions.allow` in `.claude/settings.json`:

```json
{ "permissions": { "allow": ["Bash(uv run poe test *)", "Bash(git diff *)"] } }
```

To keep Claude *out* of sensitive or heavy paths, use **deny** rules:

```json
{ "permissions": { "deny": ["Read(./.env)", "Read(./secrets/**)"] } }
```

The `@`-file picker already respects `.gitignore` (the `respectGitignore` setting, on by
default), so build dirs and `.venv` stay out of autocomplete; `claudeMdExcludes` skips chosen
`CLAUDE.md` files. You'll see a `.claudeignore` file suggested in community tips by analogy to
`.gitignore`, but Claude Code does **not** read such a file natively — `permissions.deny` and
`.gitignore` are the documented mechanisms. See
[settings](https://code.claude.com/docs/en/settings) and
[permissions](https://code.claude.com/docs/en/permissions).

## Watch your context window

Check usage with `/context` (the context-window breakdown). A simple traffic-light rule:

- 🟢 **0–60%** — code normally; the model is at peak reasoning.
- 🟡 **60–80%** — `/compact` to summarize the conversation and reclaim space.
- 🔴 **80%+** — `/clear` if the current task is done, to start clean and avoid drift.

## The status-line dashboard

This project ships a ready-made status line at **`.claude/statusline.sh`** — a two-line dashboard:

```text
🟢 Context: 34%  |  🧠 Claude Opus 4.8
🕒 5h: 22% (resets @ 04:30PM)  |  📅 7d: 12% (resets @ Wed 09:00AM)  |  💸 Safe
```

It shows the context-window traffic light + model, and (for Claude.ai Pro/Max plans) your
5-hour and 7-day rate-limit usage, reset times, and a rolling burn-rate estimate. Enable it by
adding a `statusLine` block to `.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash .claude/statusline.sh",
    "padding": 2,
    "refreshInterval": 5
  }
}
```

`refreshInterval` (seconds) controls how often the line re-runs — **this is where you set the
refresh cadence**. Notes: the script needs `jq`; the rate-limit lines populate only for
Claude.ai Pro/Max subscribers (they're omitted on API/Console billing); and context % may read
`0` momentarily right after `/clear` or before the first API response. See
[status line](https://code.claude.com/docs/en/statusline).

## Advanced (optional): token-compression tooling

The PyMaxQ maintainers optionally run a compression pipeline to stretch the context window
further. It is **third-party tooling, not part of Claude Code, and entirely optional** — none of
the practices above depend on it:

- **[RTK](https://github.com/rtk-ai/rtk)** — a `PreToolUse` hook that trims noisy shell output
  (passing tests, boilerplate) before it reaches the model.
- **[Headroom AI](https://pypi.org/project/headroom-ai/)** — an API-layer proxy that compresses
  the outgoing payload.

If you adopt them, you launch Claude wrapped in the proxy (e.g. `uv run headroom wrap claude`).
Treat this as a power-user add-on, not a requirement for working on the project.
