---
applyTo: "**/*.json"
---

# JSON Instructions

**Applies to:** all JSON files.

## Formatting

- 2-space indentation
- no trailing commas
- double quotes for all keys and string values
- single newline at EOF

## Validation

Validate JSON syntax after edits:

```bash
python3 -m json.tool <file>.json > /dev/null
```

## Change Discipline

- Keep key ordering stable when possible.
- Avoid unrelated reformatting in large JSON files.
