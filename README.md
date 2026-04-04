# GhostNotes
**Version:** 0.2.0 | **Last Updated:** April 4, 2026

A Git tool that strips tagged comments before committing.

---

## What it does
GhostNotes lets you leave personal notes in your code using a tag (default: `GN:`). Before every commit, it automatically strips them out so they never reach your repository.
```python
x = some_function() # GN: this breaks when input is negative, fix later
```
This comment line gets stripped before the commit so it looks like:
```python
x = some_function()
```

Your local file stays untouched.

---

## Commands

| Command | Description |
|---|---|
| `ghostnotes init` | Initialize GhostNotes in the current project |
| `ghostnotes set-tag --tag <tag>` | Change the default comment tag |
| `ghostnotes add-lang --ext <.ext> --symb <symbol>` | Add support for a new language |
| `ghostnotes pull` | Git pull that safely strips and re-applies your ghostnotes |
