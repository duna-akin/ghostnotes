"""Project-hygiene guard: make sure ghostnotes/ never contains an active
default marker in its own source. This is the test that would have caught
the dogfooding bug where hook.py's own explanatory comment was being
stripped from every commit."""
from pathlib import Path

from ghostnotes.config import find_pattern_outside_string, get_patterns


def test_no_active_gn_markers_in_own_source():
    project_root = Path(__file__).resolve().parent.parent
    source_dir = project_root / "ghostnotes"
    patterns = get_patterns("#", "GN:", "space")

    offenders = []
    for path in source_dir.rglob("*.py"):
        text = path.read_text()
        for line_no, line in enumerate(text.splitlines(), 1):
            idx, _ = find_pattern_outside_string(line, patterns)
            if idx is not None:
                offenders.append(f"{path.relative_to(project_root)}:{line_no}: {line.strip()}")

    assert not offenders, (
        "Source files contain active GN markers outside string literals; "
        "the pre-commit hook will strip them on every commit:\n  "
        + "\n  ".join(offenders)
    )
