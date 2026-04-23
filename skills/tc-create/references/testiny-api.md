# Testiny API Reference

## Auth
- Base URL: `https://app.testiny.io/api/v1`
- Header: `X-Api-Key: <YOUR_TESTINY_API_KEY>`
- `owner_user_id`: `<YOUR_USER_ID>`

## Projects
Configure your project IDs as needed. Example:

| Project | id |
|---|---|
| Web | 1 |
| Back | 2 |
| Admin | 3 |

## Folder IDs
Folder IDs are project-specific. Query via `GET /testcase-folder?project_id=N` to discover your folder IDs.

Example structure for Web (project_id=1):

| Folder | id |
|---|---|
| Billing | 1 |
| UI | 2 |
| Auth | 13 |
| Generation | 14 |

For Back and Admin: if no subfolders, omit `testcase_folder_id`.

## Create TC — POST /testcase

Required fields:
```json
{
  "project_id": 1,
  "title": "...",
  "testcase_folder_id": 14,
  "priority": 1,
  "status": "DRAFT",
  "template": "STEPS",
  "automation": "NOT_AUTOMATED",
  "testcase_type": "REGRESSION",
  "owner_user_id": "<YOUR_USER_ID>",
  "content_text": "<slate_json_string>"
}
```

Optional:
- `"precondition_text": "..."` — plain text preconditions

Valid enum values:
- `status`: ACTIVE, DRAFT, GUESS
- `testcase_type`: REGRESSION, FUNCTIONAL, SMOKE, PERFORMANCE, SECURITY, ACCEPTANCE
- `automation`: AUTOMATED, NOT_AUTOMATED
- `priority`: 1 (high), 2 (medium), 3 (low)

## Update TC — PUT /testcase/{id}

Requires `_etag` (optimistic locking). Always fetch current etag first:
```bash
curl -s "https://app.testiny.io/api/v1/testcase/{id}" \
  -H "X-Api-Key: <YOUR_TESTINY_API_KEY>" | python3 -c "import sys,json; t=json.load(sys.stdin); print(t['_etag'])"
```

## Fetch all TCs for a project

```bash
curl -s "https://app.testiny.io/api/v1/testcase?project_id=1&limit=500" \
  -H "X-Api-Key: <YOUR_TESTINY_API_KEY>" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data.get('data', []):
    print(f\"TC-{t['id']} | {t['title']}\")
"
```

## Slate.js Step Format (CRITICAL)

`content_text` must be a JSON string in this exact format:

```python
def make_steps(steps: list[str]) -> str:
    rows = [{"t": "tr", "rid": rid(), "children": [
        {"t": "td", "children": [{"t": "p", "children": [{"text": s}]}]},
        {"t": "td", "children": [{"t": "p", "children": [{"text": ""}]}]}
    ]} for s in steps]
    return json.dumps(
        {"t": "slate", "v": 1, "c": [{"t": "t", "columns": 2, "children": rows}]},
        ensure_ascii=False
    )
```

Rules:
- Each step = one `tr` row with 2 columns (step text + empty expected result)
- `rid` must be random 6 letters (regenerated each call)
- `content_text` is the JSON-serialized string, NOT a dict
