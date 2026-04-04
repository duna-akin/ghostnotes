import subprocess
from pathlib import Path
from ghostnotes.config import load_config


def extract_notes():
    config = load_config()
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
        pattern = comment + ' ' + tag

        # extract notes, store code without comment, store comment, and store line num
        file_notes = []
        try:
            with open(file, 'r') as f:
                for i, line in enumerate(f):
                    if pattern in line:
                        stripped = line.split(pattern)[0].rstrip()
                        note_text = line.split(pattern, 1)[1].strip()
                        file_notes.append({
                            'stripped_line': stripped,
                            'note': note_text,
                            'line_number': i,
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


def reapply_notes(notes, config):
    for file, file_notes in notes.items():
        if not Path(file).is_file():
            for n in file_notes:
                print(f"  ORPHANED (file deleted): {file} — {n['note']}")
            continue

        comment = config['languages'][Path(file).suffix]
        tag = config['settings']['tag']
        pattern = comment + ' ' + tag

        with open(file, 'r') as f:
            lines = f.readlines()

        orphaned = []

        for n in file_notes:
            target = n['stripped_line']
            line_num = n['line_number']
            matched = False

            # 1. exact match at same line number
            if line_num < len(lines) and lines[line_num].rstrip() == target:
                lines[line_num] = target + ' ' + pattern + ' ' + n['note'] + '\n'
                matched = True

            # 2. exact match nearby (within 20 lines)
            if not matched:
                start = max(0, line_num - 20)
                end = min(len(lines), line_num + 20)
                for i in range(start, end):
                    if lines[i].rstrip() == target:
                        lines[i] = target + ' ' + pattern + ' ' + n['note'] + '\n'
                        matched = True
                        break

            # 3. exact match anywhere in file
            if not matched:
                for i in range(len(lines)):
                    if lines[i].rstrip() == target:
                        lines[i] = target + ' ' + pattern + ' ' + n['note'] + '\n'
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
    config = load_config()
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
            reapply_notes(notes, config)
            print("GhostNotes: Notes restored. Resolve the pull issue and try again.")
        else:
            print("GhostNotes: Re-applying notes...")
            reapply_notes(notes, config)
            print("GhostNotes: Done.")

    return result.returncode
