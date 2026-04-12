import os
import tempfile
import configparser

from ghostnotes.config import (
    create_config,
    load_config,
    set_tag,
    add_lang_support,
    update_exclude,
)


# --- Helper ---
# set up a fake project folder so we don't touch real files.
def make_fake_git_dir():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".git", "info"))
    with open(os.path.join(tmp, ".git", "info", "exclude"), "w") as f:
        f.write("")
    return tmp


def test_create_config_makes_file():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    # check: the file should now exist
    assert os.path.isfile(".ghostnotes")

    # go back and remove temp dir
    os.chdir(original_dir)


def test_create_config_has_default_tag():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    # read the file and check the tag value
    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    assert config["settings"]["tag"] == "GN:"

    os.chdir(original_dir)


def test_create_config_has_default_languages():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    assert config["languages"][".py"] == "#"
    assert config["languages"][".java"] == "//"
    assert config["languages"][".js"] == "//"
    assert config["languages"][".ts"] == "//"

    os.chdir(original_dir)


def test_create_config_refuses_without_git():
    tmp = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()

    # .ghostnotes should not exist because there's no git
    assert not os.path.isfile(".ghostnotes")

    os.chdir(original_dir)

def test_load_config_returns_config():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config() 
    config = load_config() 
    assert config is not None
    assert config["settings"]["tag"] == "GN:"

    os.chdir(original_dir)


def test_load_config_returns_none_without_file():
    tmp = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(tmp)

    result = load_config()

    assert result is None

    os.chdir(original_dir)

def test_set_tag_changes_tag():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    set_tag("TODO:")

    # read the file again and check the tag changed
    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    assert config["settings"]["tag"] == "TODO:"

    os.chdir(original_dir)


def test_set_tag_keeps_languages():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    set_tag("NOTE:")

    config = configparser.ConfigParser()
    config.read(".ghostnotes")

    assert ".py" in config["languages"]
    assert ".js" in config["languages"]

    os.chdir(original_dir)


def test_set_tag_refuses_without_config():
    tmp = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(tmp)

    set_tag("NEW:")

    # .ghostnotes should still not exist
    assert not os.path.isfile(".ghostnotes")

    os.chdir(original_dir)


def test_add_lang_support_adds_language():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    add_lang_support(".rb", "#")

    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    assert config["languages"][".rb"] == "#"

    os.chdir(original_dir)


def test_add_lang_support_keeps_existing():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    create_config()
    add_lang_support(".go", "//")

    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    assert config["languages"][".py"] == "#"
    assert config["languages"][".go"] == "//"

    os.chdir(original_dir)


def test_add_lang_support_refuses_without_config():
    tmp = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(tmp)

    add_lang_support(".rb", "#")

    assert not os.path.isfile(".ghostnotes")

    os.chdir(original_dir)

def test_update_exclude_adds_entry():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    update_exclude()

    with open(".git/info/exclude", "r") as f:
        contents = f.read()
    assert ".ghostnotes" in contents

    os.chdir(original_dir)


def test_update_exclude_no_duplicates():
    tmp = make_fake_git_dir()
    original_dir = os.getcwd()
    os.chdir(tmp)

    update_exclude()
    update_exclude()

    with open(".git/info/exclude", "r") as f:
        lines = f.readlines()

    count = sum(1 for line in lines if line.strip() == ".ghostnotes")
    assert count == 1

    os.chdir(original_dir)
