import os
import tempfile
import configparser

from ghostnotes.config import create_config
from ghostnotes.sync import extract_notes, strip_working_tree, reapply_notes


# --- Helper ---
def make_project():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".git", "info"))
    with open(os.path.join(tmp, ".git", "info", "exclude"), "w") as f:
        f.write("")
    return tmp

def test_extract_notes_finds_ghost_note():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("x = 1\n")
        f.write("y = 2

    notes = extract_notes()

    assert "example.py" in notes
    assert len(notes["example.py"]) == 1
    assert notes["example.py"][0]["note"] == "remember this"

    os.chdir(original_dir)


def test_extract_notes_gets_line_number():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("x = 1\n")       # line 0
        f.write("y = 2\n")       # line 1
        f.write("z = 3

    notes = extract_notes()

    assert notes["example.py"][0]["line_number"] == 2

    os.chdir(original_dir)


def test_extract_notes_gets_stripped_line():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("x = 1

    notes = extract_notes()

    assert notes["example.py"][0]["stripped_line"] == "x = 1"

    os.chdir(original_dir)


def test_extract_notes_ignores_unsupported_files():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("notes.txt", "w") as f:
        f.write("hello

    notes = extract_notes()

    assert "notes.txt" not in notes

    os.chdir(original_dir)


def test_extract_notes_skips_hidden_dirs():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open(os.path.join(".git", "test.py"), "w") as f:
        f.write("x = 1

    notes = extract_notes()

    assert len(notes) == 0

    os.chdir(original_dir)


def test_extract_notes_finds_multiple_notes():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("x = 1
        f.write("y = 2\n")
        f.write("z = 3

    notes = extract_notes()

    assert len(notes["example.py"]) == 2

    os.chdir(original_dir)


def test_strip_working_tree_removes_notes():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("x = 1
        f.write("y = 2\n")

    notes = extract_notes()
    strip_working_tree(notes)

    with open("example.py", "r") as f:
        content = f.read()

    assert "GN:" not in content
    assert "x = 1\n" in content
    assert "y = 2\n" in content

    os.chdir(original_dir)


def test_strip_working_tree_keeps_other_lines():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("# a normal comment\n")
        f.write("x = 1
        f.write("y = 2  # regular comment\n")

    notes = extract_notes()
    strip_working_tree(notes)

    with open("example.py", "r") as f:
        content = f.read()

    assert "# a normal comment" in content
    assert "# regular comment" in content
    assert "GN:" not in content

    os.chdir(original_dir)


def test_reapply_notes_restores_notes():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    config = configparser.ConfigParser()
    config.read(".ghostnotes")

    with open("example.py", "w") as f:
        f.write("x = 1
        f.write("y = 2\n")

    notes = extract_notes()
    strip_working_tree(notes)
    reapply_notes(notes, config)

    with open("example.py", "r") as f:
        content = f.read()

    # the note should be back
    assert "
    assert "x = 1" in content

    os.chdir(original_dir)


def test_reapply_notes_handles_shifted_lines():
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    config = configparser.ConfigParser()
    config.read(".ghostnotes")

    with open("example.py", "w") as f:
        f.write("x = 1

    notes = extract_notes()
    strip_working_tree(notes)

    with open("example.py", "r") as f:
        lines = f.readlines()
    lines.insert(0, "# new line from pull\n")
    with open("example.py", "w") as f:
        f.writelines(lines)

    reapply_notes(notes, config)

    with open("example.py", "r") as f:
        content = f.read()

    assert "

    os.chdir(original_dir)


def test_reapply_notes_reports_orphaned(capsys):
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    config = configparser.ConfigParser()
    config.read(".ghostnotes")

    with open("example.py", "w") as f:
        f.write("x = 1

    notes = extract_notes()

    with open("example.py", "w") as f:
        f.write("totally_different = True\n")

    reapply_notes(notes, config)

    captured = capsys.readouterr()
    assert "ORPHANED" in captured.out

    os.chdir(original_dir)


def test_reapply_notes_reports_deleted_file(capsys):
    """Does reapply_notes() print ORPHANED when the file was deleted?"""
    tmp = make_project()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    config = configparser.ConfigParser()
    config.read(".ghostnotes")

    with open("example.py", "w") as f:
        f.write("x = 1

    notes = extract_notes()

    # delete the file entirely
    os.remove("example.py")

    reapply_notes(notes, config)

    captured = capsys.readouterr()
    assert "ORPHANED" in captured.out
    assert "file deleted" in captured.out

    os.chdir(original_dir)
