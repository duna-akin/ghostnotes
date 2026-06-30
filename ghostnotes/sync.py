import subprocess
from pathlib import Path
from ghostnotes.config import load_config, get_patterns, find_pattern_outside_string


def extract_notes():
    config = load_config()
    if config is None:
        return {}
    notes = {}

    for file in Path('.').rglob('*'):
        # skip hidden directories (.git, .venv, etc.)
        if any(part.startswith('.') for part in file.parts):
            continue

        if not file.is_file():
            continue

        ext = file.suffix
        if ext not in config['languages']:
            continue

        comment = config['languages'][ext]
        tag = config['settings']['tag']
        space_mode = config['settings'].get('space_mode', 'space')
        patterns = get_patterns(comment, tag, space_mode)

        file_notes = []
        try:
            with open(file, 'r') as f:
                for i, line in enumerate(f):
                    idx, matched = find_pattern_outside_string(line, patterns)
                    if idx is not None:
                        prefix = line[:idx]
                        stripped = prefix.rstrip()
                        # whitespace between the stripped code and the pattern
                        pre_pattern_ws = prefix[len(stripped):]
                        # whitespace between the pattern and the note text
                        after_pattern = line[idx + len(matched):]
                        post_pattern_ws = after_pattern[: len(after_pattern) - len(after_pattern.lstrip())]
                        note_text = after_pattern.strip()
                        file_notes.append({
                            'stripped_line': stripped,
                            'note': note_text,
                            'line_number': i,
                            'pattern': matched,
                            'pre_pattern_ws': pre_pattern_ws,
                            'post_pattern_ws': post_pattern_ws,
                        })
        except UnicodeDecodeError:
            continue

        if file_notes:
            notes[str(file)] = file_notes

    return notes

def strip_working_tree(notes):
    for file, file_notes in notes.items():
        patterns = {n['line_number'] for n in file_notes}

        with open(file, 'r') as f:
            lines = f.readlines()

        for line_num in patterns:
            note_entry = next(n for n in file_notes if n['line_number'] == line_num)
            lines[line_num] = note_entry['stripped_line'] + '\n'

        with open(file, 'w') as f:
            f.writelines(lines)


def reapply_notes(notes):
    for file, file_notes in notes.items():
        if not Path(file).is_file():
            for n in file_notes:
                print(f"  ORPHANED (file deleted): {file} — {n['note']}")
            continue

        with open(file, 'r') as f:
            lines = f.readlines()

        orphaned = []

        for n in file_notes:
            target = n['stripped_line']
            line_num = n['line_number']
            pattern = n['pattern']
            pre_ws = n.get('pre_pattern_ws', ' ')
            post_ws = n.get('post_pattern_ws', ' ')
            restored = target + pre_ws + pattern + post_ws + n['note'] + '\n'
            matched = False

            # 1. exact match at same line number
            if line_num < len(lines) and lines[line_num].rstrip() == target:
                lines[line_num] = restored
                matched = True

            # 2. exact match nearby (within 20 lines)
            if not matched:
                start = max(0, line_num - 20)
                end = min(len(lines), line_num + 20)
                for i in range(start, end):
                    if lines[i].rstrip() == target:
                        lines[i] = restored
                        matched = True
                        break

            # 3. exact match anywhere in file
            if not matched:
                for i in range(len(lines)):
                    if lines[i].rstrip() == target:
                        lines[i] = restored
                        matched = True
                        break

            # 4. orphaned
            if not matched:
                orphaned.append(n)

        with open(file, 'w') as f:
            f.writelines(lines)

        for n in orphaned:
            print(f"  ORPHANED: {file}:{n['line_number']} — {n['note']}")


def pull():
    notes = extract_notes()

    if notes:
        print(f"GhostNotes: Saved {sum(len(v) for v in notes.values())} note(s), stripping before pull...")
        strip_working_tree(notes)

    result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if notes:
        if result.returncode != 0:
            print("GhostNotes: Pull failed, restoring notes to working tree...")
            reapply_notes(notes)
            print("GhostNotes: Notes restored. Resolve the pull issue and try again.")
        else:
            print("GhostNotes: Re-applying notes...")
            reapply_notes(notes)
            print("GhostNotes: Done.")

    return result.returncode
