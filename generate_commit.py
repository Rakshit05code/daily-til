"""
GitHub Pro Agent v2 — Random daily commits
Uses FREE APIs: Gemini (AI), wttr.in (weather), quotable.io (quotes),
chucknorris.io (fun), numbersapi.com (facts), github API (trending)
Random 2-6 commits per day at randomized times.
"""

import requests, datetime, os, pathlib, random, hashlib, json

GEMINI_KEY = os.environ.get("GEMINI_KEY", "")
TODAY      = datetime.date.today().isoformat()
SEED       = int(hashlib.md5(TODAY.encode()).hexdigest(), 16)
rng        = random.Random(SEED)

DAY_OF_YEAR = datetime.date.today().timetuple().tm_yday
NOW_HOUR    = datetime.datetime.utcnow().hour

# How many commits today? Seeded by date so all 5 crons know the same number
DAILY_COUNT = rng.randint(2, 6)

# Which slot is this? (0-indexed based on hour)
SLOTS = [3, 5, 7, 11, 14]
try:
    slot_index = SLOTS.index(NOW_HOUR)
except ValueError:
    slot_index = 0

# Skip if this slot is beyond today's commit count
if slot_index >= DAILY_COUNT:
    print(f"Slot {slot_index} skipped — today only {DAILY_COUNT} commits scheduled.")
    pathlib.Path(".skip_commit").write_text("skip")
    exit(0)

# ── Content banks ─────────────────────────────────────────────────────────────

CYBERSEC = [
    "XSS attack vectors and DOM-based prevention",
    "Content Security Policy deep dive",
    "CSRF and SameSite cookie defense",
    "SQL injection and parameterized queries",
    "CORS misconfigurations",
    "JWT security pitfalls",
    "OWASP Broken Access Control",
    "TLS handshake and certificate pinning",
    "Clickjacking and X-Frame-Options",
    "Subdomain takeover vulnerabilities",
    "Rate limiting vs brute force",
    "bcrypt vs argon2 password hashing",
    "OAuth 2.0 security pitfalls",
    "Prototype pollution in JavaScript",
    "Same-origin policy explained",
    "HTTP security headers checklist",
    "Directory traversal attacks",
    "XXE injection",
    "SSRF vulnerabilities",
    "IDOR (Insecure Direct Object Reference)",
    "Session fixation attacks",
    "Open redirect vulnerabilities",
    "Broken cryptography patterns",
    "Security misconfigurations in cloud",
    "Insecure deserialization",
]

FRONTEND = [
    "JavaScript event loop deep dive",
    "React reconciliation algorithm",
    "CSS specificity and the cascade",
    "Critical rendering path optimization",
    "Web accessibility ARIA patterns",
    "JavaScript closures",
    "Browser storage comparison",
    "HTTP/2 vs HTTP/3 for devs",
    "Web Workers off-main-thread",
    "PWA service workers",
    "TypeScript generics",
    "CSS Grid vs Flexbox",
    "React useCallback and useMemo",
    "WebSockets vs SSE",
    "Browser caching strategies",
    "Tree shaking and bundle size",
    "React Context vs Redux",
    "Core Web Vitals — LCP FID CLS",
    "Lazy loading and code splitting",
    "CSS custom properties",
    "Intersection Observer API",
    "Web Components and Shadow DOM",
    "JavaScript memory leaks",
    "Canvas vs WebGL",
    "IndexedDB for offline apps",
]

PROJECTS = [
    ("port-scanner",     "python",     "TCP port scanner using raw sockets"),
    ("xss-detector",     "javascript", "DOM-based XSS pattern detector"),
    ("jwt-debugger",     "python",     "CLI tool to decode and validate JWTs"),
    ("csp-analyzer",     "javascript", "Grades Content Security Policy headers"),
    ("hash-cracker",     "python",     "Dictionary attack on MD5/SHA1 (educational)"),
    ("cors-tester",      "javascript", "Tests CORS config of any API"),
    ("rate-limiter",     "python",     "Token bucket rate limiter"),
    ("secure-headers",   "javascript", "Express.js security headers middleware"),
    ("sql-sanitizer",    "python",     "Safe vs unsafe SQL query patterns"),
    ("subdomain-enum",   "python",     "Passive subdomain enumeration via DNS"),
    ("password-audit",   "python",     "Check passwords against HaveIBeenPwned API"),
    ("cookie-scanner",   "javascript", "Audits cookies for secure/httponly flags"),
    ("http-fuzzer",      "python",     "Simple HTTP parameter fuzzer"),
    ("tls-checker",      "python",     "Checks TLS cert expiry and cipher suites"),
    ("cve-watcher",      "python",     "Polls NVD API for new CVEs by keyword"),
]

ALGORITHMS = [
    ("binary search",        "python"),
    ("merge sort",           "python"),
    ("dijkstra shortest path","python"),
    ("lru cache",            "python"),
    ("trie data structure",  "python"),
    ("sliding window",       "python"),
    ("two pointers",         "python"),
    ("dynamic programming",  "python"),
    ("graph BFS DFS",        "python"),
    ("union find",           "python"),
]

TOOLS = [
    ("nmap",       "network scanning"),
    ("burp suite", "web app security testing"),
    ("wireshark",  "packet analysis"),
    ("metasploit", "penetration testing framework"),
    ("sqlmap",     "automated SQL injection"),
    ("nikto",      "web server scanner"),
    ("hydra",      "password brute forcing"),
    ("aircrack-ng","wifi security testing"),
    ("john the ripper", "password cracking"),
    ("shodan",     "IoT and exposed service search"),
]

# ── Pick content based on slot ────────────────────────────────────────────────

COMMIT_TYPES = ["til", "snippet", "security", "project", "algorithm", "cheatsheet", "tooling", "data"]
# Shuffle types per day so each day has a different combination
day_types = rng.sample(COMMIT_TYPES, min(DAILY_COUNT, len(COMMIT_TYPES)))
commit_type = day_types[slot_index % len(day_types)]

# Pick topic seeded per slot so each slot gets a unique topic
slot_rng = random.Random(SEED + slot_index)
cybersec_topic = slot_rng.choice(CYBERSEC)
frontend_topic = slot_rng.choice(FRONTEND)
project        = slot_rng.choice(PROJECTS)
algorithm      = slot_rng.choice(ALGORITHMS)
tool           = slot_rng.choice(TOOLS)
topic_category = "cybersecurity" if slot_index % 2 == 0 else "frontend"
main_topic     = cybersec_topic if topic_category == "cybersecurity" else frontend_topic

# ── Free API data fetchers ─────────────────────────────────────────────────────

def fetch_fact():
    try:
        r = requests.get(f"http://numbersapi.com/{DAY_OF_YEAR}/day", timeout=5)
        return r.text.strip() if r.ok else ""
    except:
        return ""

def fetch_quote():
    try:
        r = requests.get("https://api.quotable.io/random?tags=technology|science", timeout=5)
        if r.ok:
            d = r.json()
            return f'"{d["content"]}" — {d["author"]}'
    except:
        pass
    return ""

def fetch_trending_repos():
    try:
        r = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": "security+stars:>100+pushed:>2024-01-01", "sort": "stars", "per_page": 3},
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=8
        )
        if r.ok:
            items = r.json().get("items", [])
            return [(i["full_name"], i["description"] or "", i["stargazers_count"]) for i in items]
    except:
        pass
    return []

# ── Build prompt per type ─────────────────────────────────────────────────────

extra_fact = fetch_fact()

def get_prompt_and_path():
    if commit_type == "til":
        prompt = f"""Write a concise "Today I Learned" markdown post for a developer targeting Big Tech security/frontend roles.
Topic: {main_topic}
Category: {topic_category}
Structure:
## TIL: [topic title]
[2-3 sentences why it matters]
### The problem
[real bug or attack scenario]
### The fix
```[language]
[10-15 line code example]
```
**Key takeaway:** [one sharp sentence]
Output raw markdown only."""
        return prompt, f"til/{topic_category}/{TODAY}-{slot_index}.md", f"docs: TIL — {main_topic[:55]}"

    elif commit_type == "snippet":
        lang = "python" if slot_rng.random() > 0.5 else "javascript"
        prompt = f"""Write a useful, reusable security-focused code snippet.
Topic: {main_topic}
Language: {lang}
Structure:
## {main_topic[:50]}
[1 line description]
```{lang}
[20-30 lines clean well-commented production-ready code]
```
**Usage:** [one line example]
Output raw markdown only."""
        return prompt, f"snippets/{lang}/{TODAY}-{slot_index}.md", f"feat: {lang} snippet — {main_topic[:45]}"

    elif commit_type == "security":
        prompt = f"""Write a detailed security research note.
Topic: {cybersec_topic}
Structure:
## Security: {cybersec_topic[:50]}
### What is it?
[2-3 sentences]
### Attack scenario
[step by step attack]
### Vulnerable code
```javascript
[8-12 lines]
```
### Secure code
```javascript
[8-12 lines]
```
### Prevention checklist
- [3-4 bullets]
Output raw markdown only."""
        return prompt, f"security-notes/{TODAY}-{slot_index}.md", f"security: {cybersec_topic[:50]}"

    elif commit_type == "project":
        pname, plang, pdesc = project
        prompt = f"""Write a README + starter code for a security tool.
Project: {pname}
Language: {plang}
Description: {pdesc}
Include:
## {pname}
[2-line description, 3-4 feature bullets, usage example]
## Code
```{plang}
[35-45 lines functional starter code with comments]
```
Output raw markdown only."""
        return prompt, f"projects/{pname}/README.md", f"feat: {pname} — {pdesc[:40]}"

    elif commit_type == "algorithm":
        algo, lang = algorithm
        prompt = f"""Write a clean implementation of {algo} in {lang} for interview prep.
Structure:
## {algo.title()}
[2 sentences — what it is and time/space complexity]
```{lang}
[25-35 lines clean implementation with comments]
```
### Example
[show input → output]
**Interview tip:** [one sentence]
Output raw markdown only."""
        return prompt, f"dsa/{algo.replace(' ','-')}/{TODAY}.md", f"feat: DSA — {algo}"

    elif commit_type == "cheatsheet":
        prompt = f"""Create a cheatsheet for Big Tech interviews.
Topic: {main_topic}
Structure:
## Cheatsheet: {main_topic[:50]}
### Quick reference
| Concept | What it means |
|---------|--------------|
[5-6 rows]
### Key patterns
```[language]
[15-20 lines covering 2-3 patterns]
```
### Interview tips
- [3 bullets]
Output raw markdown only."""
        return prompt, f"cheatsheets/{topic_category}/{TODAY}-{slot_index}.md", f"docs: cheatsheet — {main_topic[:48]}"

    elif commit_type == "tooling":
        tname, tdesc = tool
        prompt = f"""Write a practical guide for {tname} ({tdesc}) aimed at security beginners.
Structure:
## {tname.title()} — quick reference
[2 sentences what it does]
### Install
```bash
[install commands]
```
### Most useful commands
```bash
[8-12 commands with comments]
```
### Real use case
[2-3 sentence example scenario]
**When to use it:** [one sentence]
Output raw markdown only."""
        return prompt, f"tooling/{tname.replace(' ','-')}/{TODAY}.md", f"docs: {tname} guide"

    elif commit_type == "data":
        repos = fetch_trending_repos()
        repo_text = "\n".join([f"- {n}: {d} ({s} stars)" for n,d,s in repos]) if repos else "No data fetched."
        quote = fetch_quote()
        prompt = f"""Write a markdown log entry for a security-focused developer.
Date: {TODAY}
Fact of the day: {extra_fact}
Trending security repos on GitHub:
{repo_text}
Structure:
## Dev log — {TODAY}
### Today's focus
[2-3 sentences on {main_topic}]
### Trending in security
[bullet for each repo, 1-line insight]
### Quote
{quote}
### Tomorrow's plan
[2-3 concrete things to study/build]
Output raw markdown only."""
        return prompt, f"devlog/{TODAY}.md", f"log: daily dev log {TODAY}"

    return "", f"misc/{TODAY}-{slot_index}.md", "chore: update"

# ── Call Gemini ───────────────────────────────────────────────────────────────

prompt, file_path, commit_msg = get_prompt_and_path()
print(f"[{commit_type}] slot {slot_index}/{DAILY_COUNT-1} — {main_topic[:50]}")

if GEMINI_KEY:
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.75},
        },
        timeout=30,
    )
    print(f"API status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        raise Exception(f"Gemini error {response.status_code}")
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
else:
    content = f"## {main_topic}\n\nPlaceholder — add GEMINI_KEY secret to enable AI generation.\n"

for fence in ["```markdown\n", "```\n"]:
    if content.startswith(fence):
        content = content[len(fence):]
        break
if content.endswith("\n```"):
    content = content[:-4]
if content.endswith("```"):
    content = content[:-3]
content = content.strip()

# ── Save ──────────────────────────────────────────────────────────────────────

out = pathlib.Path(file_path)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(f"<!-- type:{commit_type} slot:{slot_index} date:{TODAY} -->\n\n{content}\n")
print(f"Written: {out}")

pathlib.Path(".commit_msg").write_text(commit_msg)

# ── Update README ─────────────────────────────────────────────────────────────

EMOJI = {"til":"📚","snippet":"💡","security":"🔐","project":"🛠️","algorithm":"🧮","cheatsheet":"📋","tooling":"🔧","data":"📓"}
emoji = EMOJI.get(commit_type, "📝")

index = pathlib.Path("README.md")
base = """# Rakshit's Dev & Security Journal

> Daily notes, snippets, security research, and project starters — cybersecurity + frontend engineering.

![GitHub commit activity](https://img.shields.io/github/commit-activity/w/YOUR_USERNAME/daily-til?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/daily-til?style=flat-square)

## Structure
| Folder | Content |
|--------|---------|
| `til/` | Today I Learned |
| `snippets/` | Reusable code |
| `security-notes/` | Security research |
| `projects/` | Mini tools |
| `dsa/` | Algorithms & data structures |
| `cheatsheets/` | Interview prep |
| `tooling/` | Security tool guides |
| `devlog/` | Daily dev logs |

## Recent activity

"""

existing = index.read_text() if index.exists() else base
entry = f"- `{TODAY}` {emoji} **{commit_type}** — {main_topic[:65]}"
marker = "## Recent activity\n\n"
if marker in existing:
    parts = existing.split(marker)
    lines = [l for l in parts[1].strip().split("\n") if l.strip()]
    lines = [entry] + lines[:59]
    index.write_text(parts[0] + marker + "\n".join(lines) + "\n")
else:
    index.write_text(existing + entry + "\n")

print("Done.")
