---
name: tc-create
description: >-
  Creates test cases in Testiny following project naming conventions, priority
  rules, and Slate.js step format. Data must come from a real source (analytics
  events, code, logs). Never invent steps or property values.
  Trigger: "create a test case", "write a TC", "add a test case".
version: 0.1.0
---

# TC Create

Create test cases in Testiny following established conventions.
All data must come from a real source (analytics platform, code, monitoring). Never invent steps or property values.

## Workflow

**Step 1 — Clarify if not provided:**
- Which project: Web (id=1), Back (id=2), or Admin (id=3)?
- Which folder? (see references/testiny-api.md for folder IDs)
- What is the data source (analytics event, code handler, log)?

**Step 2 — Choose title pattern** (pick one based on TC type):

| Type | Pattern | Example |
|---|---|---|
| Analytics event + property | `EventName: property=value` | `Task Created: type=videogen` |
| Negative / edge case | `condition → consequence` | `credits=0 → Task Created не стреляет` |
| UI behavior / backend logic | `Object: short description` | `Promote Trusted: requires confirmation` |

Rules:
- Never repeat the folder name in the title
- No fluff words ("Successful", "Correct", "happy path" as prefix)
- Analytics data (event names, properties, values) in English with `property=value` notation

**Step 3 — Set priority** based on analytics event volume or criticality:

| Priority | Volume /30d | API value |
|---|---|---|
| HIGH | >50 000 or critical path | 1 |
| MEDIUM | 5 000–50 000 or important edge case | 2 |
| LOW | <5 000 or rare scenario | 3 |

**Step 4 — Set status:**
- `DRAFT` — only when fully confident: every step and every value is verified from a real source, nothing assumed
- `GUESS` — any doubt for any reason: UI steps not seen in code, property values not queried, behavior assumed

When in doubt — always GUESS. Better to revisit later than to mark DRAFT incorrectly.

**Step 5 — Write steps.** Each step is one action or one assertion. Format:
- Action steps: imperative ("Open the task", "Click Retry")
- Assertion steps: "Verify: X = Y" or "Check analytics for event X"
- Never invent UI element names not seen in code

**Step 6 — Create via API.** See `references/testiny-api.md` for auth, Slate.js format, and folder IDs.

## Quick API Call

```python
import urllib.request, json, random, string

API = "https://app.testiny.io/api/v1"
KEY = "<YOUR_TESTINY_API_KEY>"
HEADERS = {"X-Api-Key": KEY, "Content-Type": "application/json"}

def rid():
    return "".join(random.choices(string.ascii_letters, k=6))

def make_steps(steps):
    rows = [{"t": "tr", "rid": rid(), "children": [
        {"t": "td", "children": [{"t": "p", "children": [{"text": s}]}]},
        {"t": "td", "children": [{"t": "p", "children": [{"text": ""}]}]}
    ]} for s in steps]
    return json.dumps({"t": "slate", "v": 1, "c": [{"t": "t", "columns": 2, "children": rows}]}, ensure_ascii=False)

body = {
    "project_id": PROJECT_ID,       # 1=Web, 2=Back, 3=Admin
    "title": TITLE,
    "testcase_folder_id": FOLDER_ID,
    "priority": PRIORITY,           # 1=HIGH, 2=MED, 3=LOW
    "status": "DRAFT",              # or "GUESS"
    "template": "STEPS",
    "automation": "NOT_AUTOMATED",
    "testcase_type": "REGRESSION",
    "owner_user_id": "<YOUR_USER_ID>",
    "content_text": make_steps(STEPS),
}
data = json.dumps(body).encode()
req = urllib.request.Request(f"{API}/testcase", data=data, headers=HEADERS, method="POST")
with urllib.request.urlopen(req) as resp:
    result = json.load(resp)
    print(f"TC-{result['id']} created")
```

## Additional Resources

- **`references/testiny-api.md`** — folder IDs per project, PUT/etag update flow, bulk folder mapping, field reference
