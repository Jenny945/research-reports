---
name: preview
description: Preview, deploy, or run a web project in the sandbox. Triggers on "预览", "preview", "看效果", "跑起来", "deploy", "give me a URL", "show me the page", etc.
allowed-tools: Read, Write, Bash
---

Launch a web server inside the sandbox environment and produce an accessible preview URL.

---

## ⛔ ABSOLUTE RULE — NEVER construct a preview URL yourself

> **This is the single most important rule in this skill. Violating it WILL produce a broken link.**

You MUST call the `notify` script to obtain the preview URL. The URL has a **precise, dynamic format** that depends on runtime environment variables you cannot reliably know or assemble.

**FORBIDDEN behaviors (violation = broken preview):**

- ❌ NEVER concatenate, interpolate, or guess any part of the base preview URL (scheme + domain + query params)
- ❌ NEVER read `$X_IDE_SPACE_KEY` or `$X_IDE_PREVIEW_DOMAIN` and build the URL yourself
- ❌ NEVER hardcode or assume any domain pattern (e.g. `e2b6.sandbox.*`, `*.e2b.*`, `e2b6.xxx`)
- ❌ NEVER invent a URL format based on memory or pattern-matching from training data
- ❌ NEVER modify, trim, or "fix" the domain or query parameters that `notify` outputs

**The ONLY correct action:** run `notify <port>`, read its stdout, and use that base URL. You MAY append a file path (e.g. `/demo.html`) to the URL if the user's project requires it, but the **domain and query parameters MUST come from `notify` exactly as printed**.

### Common WRONG URLs (for your awareness — NEVER produce these)

| Wrong URL | What went wrong |
|-----------|----------------|
| `https://webview.e2b6.sandbox.cloudstudio.club/?...` | Domain is fabricated — `e2b6` is NOT a valid subdomain |
| `https://webview.e2b6.sandbox.cloudstudio.club/demo.html?...` | Domain is fabricated — the `e2b6.sandbox` part does not exist |
| `https://webview.sandbox.cloudstudio.club/?...` | Domain is wrong — missing the correct region/cluster subdomain |
| `https://<anything-you-typed-instead-of-notify-output>` | Any base URL not from `notify` output is WRONG |

> The correct domain is **only known at runtime** (e.g. `webview.e2b.bj2.sandbox.cloudstudio.club`) and is produced solely by `notify`. The domain varies by region/cluster — **do not guess it**.

---

## When to activate

- User asks to preview a page or project ("预览", "preview", "看效果", "show me what it looks like")
- User asks to deploy and view ("部署", "deploy", "跑起来", "run it")
- After creating/modifying a web page, user wants to view it ("做好了吗", "let me preview it")
- User asks for an accessible link ("给我链接", "give me a URL")

**Rule**: if the user has a web artifact and expresses any desire to view/access it, activate this skill.

## Steps

### Step 0. Serving strategy

⚠️ **WebSocket is NOT proxied — NEVER use dev servers (`vite dev` / `next dev` / `webpack-dev-server`).**

| Type | Method |
|---|---|
| Static HTML | `python3 -m http.server <port>` |
| Vite / CRA / Vue CLI | `build` → static-serve `dist/` |
| Next.js | `next build && next start` |
| Custom server | Production mode (`node server.js`) |

- Entry must be `index.html` at root `/` (not `app.html` / `hello.html`).
- SPA: prefer **HashRouter** (`/#/path`); if BrowserRouter, add server fallback → `index.html`.

### Step 1. Start the server (with hibernate-safe registration)

Pick an available port (default to **8000**). If occupied, increment (8001, 8002, …).

Follow the strategy from Step 0. Install dependencies, build if needed, then start the server:

- **Bind to `0.0.0.0`**, not `localhost` or `127.0.0.1`.
- **Only kill processes on the specific port** — never use `killall` or `pkill`.
- **Before killing a port**, verify it's not a critical service (e.g. port 22/80/443).
- **Register the service with supervisord** so it auto-restarts after sandbox hibernate/resume.

#### 1a. Register the server as a supervisord program

Supervisord is launched by the sandbox init script and is already running when this skill executes. We just need to **add a program** under its control so the service auto-restarts after hibernate/resume.

**Where to write the program conf:**

The supervisord main config (`${IDE_EDITOR_SERVER_DIR}/supervisord-conf/supervisord.conf`) is image-baked and includes program confs from multiple directories via its `[include]` section:

```ini
[include]
files = %(ENV_IDE_EDITOR_SERVER_DIR)s_run/supervisord-conf/*.conf /usr/local/share/supervisor/*.conf
```

We write the program conf to **`/usr/local/share/supervisor/`** because:
- It's the standard supervisord convention directory (cross-distro, cross-tool consistent).
- It sits **outside** the `${IDE_EDITOR_SERVER_DIR}_run/` runtime-overlay tree, which is the most likely candidate for sandbox hibernate/resume cleanup.
- `${IDE_EDITOR_SERVER_DIR}_run/supervisord-conf/` is still in the include list (kept for backward compat / AGS pipeline pre-create) but is no longer our drop site.

```bash
# --- Inputs (replace <port> with the actual port you picked) ---
PORT=<port>   # e.g. 8000, 8001, …

# --- Paths (extracted once, reused below) ---
SUPERVISORD_BIN="${IDE_EDITOR_SERVER_DIR}/bin/supervisord"          # wrapper that dispatches `ctl ...` to supervisorctl
SUPERVISOR_MAIN_CONF="${IDE_EDITOR_SERVER_DIR}/supervisord-conf/supervisord.conf"
SUPERVISOR_CONF_DIR="/usr/local/share/supervisor"                   # drop site for the program conf
PROGRAM_NAME="preview-${PORT}"
PROGRAM_CONF="${SUPERVISOR_CONF_DIR}/${PROGRAM_NAME}.conf"

# Defensive: ensure the target dir exists. /usr/local/share is root:root 755
# by default on Debian/Ubuntu, and the sandbox runs as root, so writes are fine.
mkdir -p "${SUPERVISOR_CONF_DIR}"

cat > "${PROGRAM_CONF}" <<EOF
[program:${PROGRAM_NAME}]
command=<start-command>
directory=<project-dir>
autostart=true
autorestart=true
startsecs=2
startretries=3
stopsignal=INT
stopwaitsecs=10
stdout_logfile=/tmp/${PROGRAM_NAME}.log
stderr_logfile=/tmp/${PROGRAM_NAME}.log
redirect_stderr=true
# Preserve the inherited PATH/NODE_OPTIONS so npx/node/etc. still resolve.
# %(ENV_PATH)s is supervisor's built-in placeholder for the supervisor process' PATH.
environment=PATH="%(ENV_PATH)s",NODE_OPTIONS=""
EOF
```

**Key rules for the `command=` value:**
- Must be a **foreground** process (no `&`, no `nohup`, no `daemon`)
- Must bind to `0.0.0.0:<port>`
- Examples:
  - Static: `python3 -m http.server <port> --bind 0.0.0.0 --directory <project-dir>`
  - Node: `node server.js`
  - Next.js: `npx next start -p <port> -H 0.0.0.0`

#### 1b. Apply the config and start the service

```bash
# Kill any leftover process on the port (only this port — never pkill/killall)
lsof -ti:${PORT} | xargs -r kill -9 2>/dev/null || true

# Pick up the new program conf and (re)start it. This sequence is idempotent:
#   reread  — discover newly added .conf files
#   update  — restart programs whose config changed
#   start   — start newly added programs (no-op if already RUNNING; safe to re-run)
${SUPERVISORD_BIN} ctl -c ${SUPERVISOR_MAIN_CONF} reread
${SUPERVISORD_BIN} ctl -c ${SUPERVISOR_MAIN_CONF} update
${SUPERVISORD_BIN} ctl -c ${SUPERVISOR_MAIN_CONF} start ${PROGRAM_NAME}

# Wait up to 10s for it to reach RUNNING (startsecs=2 plus headroom).
for _ in $(seq 1 10); do
  STATE=$(${SUPERVISORD_BIN} ctl -c ${SUPERVISOR_MAIN_CONF} status ${PROGRAM_NAME} 2>/dev/null | awk '{print $2}')
  [ "${STATE}" = "RUNNING" ] && break
  sleep 1
done
```

#### 1c. Verify the service is actually serving

Two checks are required — supervisor saying `RUNNING` only means the process didn't immediately exit, **not** that the port is accepting traffic.

```bash
# 1. Supervisor state
${SUPERVISORD_BIN} ctl -c ${SUPERVISOR_MAIN_CONF} status ${PROGRAM_NAME}
# Expect:  preview-<port>                    RUNNING   pid 1234, uptime 0:00:05

# 2. Port is accepting HTTP (not just bound)
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:${PORT}/" \
  || echo "WARN: port ${PORT} not responding — see /tmp/${PROGRAM_NAME}.log"
```

| State | Meaning | What to do |
|---|---|---|
| `RUNNING` + `HTTP 2xx/3xx` | Service healthy | Proceed to Step 2 |
| `RUNNING` but `curl` fails | Process up, port not listening (or wrong bind) | Check `command=` binds `0.0.0.0`, not `127.0.0.1` |
| `STARTING` (still after 10s) | `startsecs` not yet elapsed | Wait 2-3s more, or inspect `/tmp/${PROGRAM_NAME}.log` |
| `BACKOFF` | Crashed `startretries` times | Read `/tmp/${PROGRAM_NAME}.log`, fix command, re-run from 1a |
| `FATAL` | Supervisor gave up | Same as BACKOFF — log has the last error |
| `EXITED` (status 0) | Foreground command returned | Most likely your `command=` daemonized itself; remove `&`/`nohup`/`disown` |

If the supervisor itself is unreachable (e.g. `${SUPERVISOR_BIN}` missing or `status` errors with "no such file"), skip to the Fallback below.

#### Fallback (only when supervisord is genuinely unavailable)

How to confirm supervisord is actually unavailable (not just the wrong path):

```bash
# 1. Is the binary there?
ls -la "${IDE_EDITOR_SERVER_DIR}/bin/supervisord" 2>/dev/null
# 2. Can we talk to it?
${IDE_EDITOR_SERVER_DIR}/bin/supervisord ctl -c ${IDE_EDITOR_SERVER_DIR}/supervisord-conf/supervisord.conf status
```

If both fail, fall back to `nohup`:

```bash
lsof -ti:${PORT} | xargs -r kill -9 2>/dev/null || true
nohup <start-command> > /tmp/${PROGRAM_NAME}.log 2>&1 &
sleep 3
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:${PORT}/"
```

⚠️ **Note**: The `nohup` fallback does NOT survive hibernate — the preview will go down on resume and the user will see a broken link. **Document this in the chat reply** so the user knows to ask again after a resume. Only use the fallback when supervisord is truly unavailable.

### Step 2. Call `notify` to get the preview URL (REQUIRED — NO EXCEPTIONS)

> ⚠️ **REMINDER: You MUST NOT build the URL yourself. Only `notify` produces valid URLs.**

**Immediately after the server starts**, call `notify` for each port:

```bash
<this-skill-directory>/notify <port>
```

`notify` will:
1. Verify the port is listening (fails if not)
2. Build the correct preview URL using runtime environment variables
3. Signal the client to open a browser tab
4. **Output the URL on stdout** — this is your ONLY source of truth for the preview URL

**If `notify` fails** (port not listening), check `server.log` for errors, fix the issue, restart the server, and **call `notify` again**. Retry up to 3 times.

**NEVER skip this step. NEVER build the URL yourself. NEVER use `echo $X_IDE_SPACE_KEY` or `curl` to construct a URL — `notify` does all of this.**

### Step 3. Reply with the EXACT URL from `notify` output

> ⚠️ **The domain and query parameters MUST come directly from `notify`'s output. Do NOT modify, reformat, or replace them.**

`notify` outputs a JSON line like:
```
[Preview] {"port":"8000","url":"https://webview.e2b.bj2.sandbox.cloudstudio.club/?x-cs-sandbox-id=abc123&x-cs-sandbox-port=8000"}
```

Extract the `url` value from that JSON. This is your **base URL**.

- You MAY append a file path if the project needs it (e.g. add `/demo.html` to the URL path, before the `?`)
- You MUST NOT change the domain, scheme, or query parameters

Example (appending a path):
```
Base from notify: https://webview.e2b.bj2.sandbox.cloudstudio.club/?x-cs-sandbox-id=abc123&x-cs-sandbox-port=8000
With file path:   https://webview.e2b.bj2.sandbox.cloudstudio.club/demo.html?x-cs-sandbox-id=abc123&x-cs-sandbox-port=8000
```

Reply in **the same language the user used**. Examples:

If user spoke English:
```
[Click to preview](<URL>)

If the link above does not work, copy and paste this URL into your browser:
<URL>
```

If user spoke Chinese:
```
[点击预览](<URL>)

如果上方链接无法打开，请复制下方地址到浏览器访问：
<URL>
```

Always match the user's language — do NOT default to English.

**Final check before replying:**
- ✅ The domain in your URL is **identical** to what `notify` printed (e.g. `webview.e2b.bj2.sandbox.cloudstudio.club`)
- ✅ The query parameters (`x-cs-sandbox-id`, `x-cs-sandbox-port`) are unchanged from `notify` output
- ✅ You did NOT fabricate or guess any part of the domain (no `e2b6`, no made-up subdomains)
- ❌ If you cannot find `notify`'s output, **re-run `notify`** — do NOT guess the URL

---

## Bad Cases (common mistakes to avoid)

| # | Mistake | Why it breaks |
|---|---------|---------------|
| 1 | Forgot to call `notify`, fabricated URL | Domain is wrong → 404 or SSL error |
| 2 | Used `localhost:8000` in reply | Only reachable inside sandbox, not by user |
| 3 | URL path placed after `?` query params | Path treated as query string → file not found |
| 4 | Appended non-existent file path | 404 error (e.g. `/app.html` when only `index.html` exists) |
| 5 | Double slash in path (`//index.html`) | Path resolution error |
| 6 | Used `vite dev` / `next dev` for preview | HMR WebSocket fails → `$RefreshReg$` error or blank page |
| 7 | Used BrowserRouter without fallback | Webview query params break path matching → blank page |
| 8 | Entry file named `hello.html` / `app.html` | User expects root `/` access, not `/hello.html` |

---

## Self-Check (before replying with URL)

```bash
# Verify file exists and server responds
ls <project-dir>/<entry-file>
curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/<entry-file>
```

| # | Check | Pass criteria |
|---|-------|---------------|
| 1 | Domain from `notify` output | Character-by-character match |
| 2 | Query params unchanged | `x-cs-sandbox-id` and `x-cs-sandbox-port` identical |
| 3 | File path before `?` | Format: `https://domain/path.html?params` |
| 4 | File actually exists | `ls` confirms presence |
| 5 | Server returns 200 | `curl` confirms accessible |
| 6 | No fabricated domain | You did NOT type/recall any part of domain |
| 7 | Response body non-empty | `curl -s http://localhost:<port>/ \| wc -c` > 100 |
| 8 | No dev server running | Process is static serve / production, NOT `vite` / `next dev` |

⛔ Do NOT reply with URL until all checks pass.
