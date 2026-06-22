"""
GitHub Auto-Agent — Cybersecurity + Frontend Edition
Generates daily technical content and saves it to the repo.
Targets Big Tech roles (Google, Amazon, etc.)
"""

import requests
import datetime
import os
import pathlib
import json
import random

API_KEY = os.environ["ANTHROPIC_KEY"]
TODAY = datetime.date.today().isoformat()
DAY_OF_YEAR = datetime.date.today().timetuple().tm_yday

# ─── Topic rotation ───────────────────────────────────────────────────────────
# Alternates between cybersecurity and frontend topics each day
# Cybersecurity topics impress Big Tech security teams
# Frontend topics show breadth for SWE/SDE roles

CYBERSEC_TOPICS = [
    "XSS (Cross-Site Scripting) attack vectors and how to prevent them in modern web apps",
    "Content Security Policy (CSP) headers — what they do and how to configure them",
    "CSRF attacks and SameSite cookie defenses",
    "SQL injection patterns and parameterized query best practices",
    "CORS misconfigurations that lead to security vulnerabilities",
    "JWT security — common mistakes and how to avoid them",
    "OWASP Top 10 — a deep dive on Broken Access Control",
    "How HTTPS and TLS handshakes work under the hood",
    "clickjacking attacks and X-Frame-Options / CSP frame-ancestors defense",
    "Subdomain takeover vulnerabilities — how they happen and how to prevent them",
    "Rate limiting strategies to prevent brute force and DoS attacks",
    "Secure password hashing — bcrypt, argon2, and why MD5 is dangerous",
    "OAuth 2.0 security pitfalls — redirect_uri validation, state parameter",
    "Prototype pollution in JavaScript — what it is and how attackers exploit it",
    "How browser same-origin policy works and when it breaks",
]

FRONTEND_TOPICS = [
    "JavaScript event loop — microtasks vs macrotasks with code examples",
    "React reconciliation algorithm and how the virtual DOM diffing works",
    "CSS specificity rules — how the cascade resolves conflicts",
    "Web performance: critical rendering path and how to optimize it",
    "Accessibility in web apps — ARIA roles, focus management, and screen readers",
    "JavaScript closures — practical patterns and common pitfalls",
    "Browser storage: cookies vs localStorage vs sessionStorage vs IndexedDB",
    "HTTP/2 vs HTTP/3 — what changes for frontend developers",
    "Web Workers — offloading computation from the main thread",
    "Progressive Web Apps (PWA) — service workers, caching strategies",
    "TypeScript generics — practical patterns for type-safe code",
    "CSS Grid vs Flexbox — when to use which with real examples",
    "React hooks deep dive — useCallback, useMemo, and when they actually help",
    "WebSockets vs Server-Sent Events vs Long Polling — trade-offs",
    "How browser caching works — Cache-Control, ETag, and cache busting",
]

# Pick topic: odd days = cybersec, even days = frontend
if DAY_OF_YEAR % 2 == 1:
    category = "cybersecurity"
    topic = CYBERSEC_TOPICS[DAY_OF_YEAR % len(CYBERSEC_TOPICS)]
    folder_name = "cybersec"
    emoji = "🔐"
else:
    category = "frontend"
    topic = FRONTEND_TOPICS[DAY_OF_YEAR % len(FRONTEND_TOPICS)]
    folder_name = "frontend"
    emoji = "🖥️"

# ─── Prompt ───────────────────────────────────────────────────────────────────

PROMPT = f"""Write a short, high-quality "Today I Learned" technical post about:

Topic: {topic}
Category: {category}

Format it as clean markdown with:
1. A clear H2 title (no H1)
2. A 2-3 sentence explanation of what this is and why it matters
3. One concrete real-world scenario or attack/bug example
4. A code snippet (10-20 lines max) demonstrating the concept — use JavaScript, Python, or Bash as appropriate
5. One "Key takeaway" line at the end

Tone: concise, practical, like a senior engineer's notes. No fluff.
Output raw markdown only. No preamble."""

# ─── Call Claude API ──────────────────────────────────────────────────────────

print(f"Generating {category} post: {topic[:50]}...")

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    json={
        "model": "claude-haiku-4-5",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": PROMPT}],
    },
    timeout=30,
)

response.raise_for_status()
content = response.json()["content"][0]["text"]

# ─── Save file ────────────────────────────────────────────────────────────────

folder = pathlib.Path("til") / folder_name
folder.mkdir(parents=True, exist_ok=True)

filename = folder / f"{TODAY}.md"
filename.write_text(f"<!-- category: {category} | generated: {TODAY} -->\n\n{content}\n")

print(f"Written: {filename}")

# ─── Update README index ──────────────────────────────────────────────────────
# Keeps a running log so your repo README always shows recent activity

index_file = pathlib.Path("README.md")

if index_file.exists():
    existing = index_file.read_text()
else:
    existing = "# Daily TIL — Cybersecurity & Frontend\n\nAutomated daily notes on security and web development.\n\n## Recent entries\n\n"

# Insert new entry after "## Recent entries" header
entry_line = f"- **{TODAY}** [{emoji} {category.capitalize()}] `til/{folder_name}/{TODAY}.md` — {topic[:60]}...\n"

if "## Recent entries" in existing:
    parts = existing.split("## Recent entries\n\n")
    # Keep only last 30 entries to avoid bloat
    recent_lines = parts[1].strip().split("\n") if len(parts) > 1 else []
    recent_lines = [entry_line.strip()] + recent_lines[:29]
    index_file.write_text(parts[0] + "## Recent entries\n\n" + "\n".join(recent_lines) + "\n")
else:
    index_file.write_text(existing + entry_line)

print("Updated README.md")
