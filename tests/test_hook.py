import os
import stat
import tempfile
import subprocess
from ghostnotes.hook import install_hook, strip_ghostnotes
from ghostnotes.config import create_config


# --- Helpers ---
def make_fake_git_dir():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".git", "hooks"))
    os.makedirs(os.path.join(tmp, ".git", "info"))
    with open(os.path.join(tmp, ".git", "info", "exclude"), "w") as f:
        f.write("")
    return tmp
def make_real_git_repo():
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "init", tmp], capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, capture_output=True)
    return tmp

def test_install_hook_creates_file():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    install_hook()

    assert os.path.isfile(".git/hooks/pre-commit")

    os.chdir(original_dir)


def test_install_hook_has_shebang():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    install_hook()

    with open(".git/hooks/pre-commit", "r") as f:
        first_line = f.readline().strip()
    assert first_line == "#!/bin/bash"

    os.chdir(original_dir)


def test_install_hook_has_command():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    install_hook()

    with open(".git/hooks/pre-commit", "r") as f:
        contents = f.read()
    assert "python3 -m ghostnotes.hook" in contents

    os.chdir(original_dir)


def test_install_hook_is_executable():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    install_hook()

    file_stat = os.stat(".git/hooks/pre-commit")
    assert file_stat.st_mode & stat.S_IEXEC

    os.chdir(original_dir)


def test_install_hook_appends_to_existing(): # crucial to not mess up user's previous hooks and workflows
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    # create an existing pre-commit hook with some other command
    with open(".git/hooks/pre-commit", "w") as f:
        f.write("#!/bin/bash\necho 'existing hook'\n")

    install_hook()

    with open(".git/hooks/pre-commit", "r") as f:
        contents = f.read()

    # both the old content and the new command should be there
    assert "existing hook" in contents
    assert "python3 -m ghostnotes.hook" in contents

    os.chdir(original_dir)


def test_install_hook_no_duplicate():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    install_hook()
    install_hook()

    with open(".git/hooks/pre-commit", "r") as f:
        contents = f.read()

    count = contents.count("python3 -m ghostnotes.hook")
    assert count == 1

    os.chdir(original_dir)


# these tests use a real git repo because strip_ghostnotes()
# runs actual git commands (git diff, git show, git hash-object, etc.)

def test_strip_removes_ghost_note_from_index(): # crucial
    tmp = make_real_git_repo()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    # create a python file with a ghost note comment
    with open("example.py", "w") as f:
        f.write("x = 1\n")
        f.write("y = 2
        f.write("z = 3\n")

    # stage the file (add it to the git index)
    subprocess.run(["git", "add", "example.py"], capture_output=True)

    strip_ghostnotes()

    # read what's now in the git index (staged version) after stripping
    result = subprocess.run(
        ["git", "show", ":example.py"],
        capture_output=True, text=True
    )
    staged_content = result.stdout

    assert "GN:" not in staged_content
    assert "y = 2" in staged_content
    assert "x = 1" in staged_content
    assert "z = 3" in staged_content

    os.chdir(original_dir)


def test_strip_leaves_non_tagged_comments(): # crucial
    tmp = make_real_git_repo()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("example.py", "w") as f:
        f.write("# this is a normal comment\n")
        f.write("x = 1
        f.write("y = 2  # regular inline comment\n")

    subprocess.run(["git", "add", "example.py"], capture_output=True)

    strip_ghostnotes()

    result = subprocess.run(
        ["git", "show", ":example.py"],
        capture_output=True, text=True
    )
    staged_content = result.stdout

    assert "# this is a normal comment" in staged_content
    assert "# regular inline comment" in staged_content
    assert "GN:" not in staged_content

    os.chdir(original_dir)


def test_strip_ignores_unsupported_files():
    tmp = make_real_git_repo()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("notes.txt", "w") as f:
        f.write("some text

    subprocess.run(["git", "add", "notes.txt"], capture_output=True)

    strip_ghostnotes()

    result = subprocess.run(
        ["git", "show", ":notes.txt"],
        capture_output=True, text=True
    )

    assert "

    os.chdir(original_dir)


def test_strip_works_with_js_files():
    tmp = make_real_git_repo()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    with open("app.js", "w") as f:
        f.write("const x = 1;\n")
        f.write("const y = 2; // GN: remember to refactor\n")

    subprocess.run(["git", "add", "app.js"], capture_output=True)

    strip_ghostnotes()

    result = subprocess.run(
        ["git", "show", ":app.js"],
        capture_output=True, text=True
    )
    staged_content = result.stdout

    assert "GN:" not in staged_content
    assert "const y = 2;" in staged_content

    os.chdir(original_dir)
