# file for creating the .ghostnotes configuration
import configparser
import os


def get_patterns(comment, tag, space_mode):
    if space_mode == "nospace":
        return [comment + tag]
    if space_mode == "both":
        return [comment + " " + tag, comment + tag]
    return [comment + " " + tag]


def find_pattern(line, patterns, start=0):
    best_idx = None
    best_pattern = None
    for p in patterns:
        idx = line.find(p, start)
        if idx != -1 and (best_idx is None or idx < best_idx):
            best_idx = idx
            best_pattern = p
    return best_idx, best_pattern


def is_in_string_literal(prefix):
    # Walks prefix character-by-character tracking the active quote char and
    # backslash escapes. Returns True if we end inside an unterminated string.
    # Does not handle triple-quoted or multi-line strings — those are out of
    # scope for a line-by-line scanner.
    open_quote = None
    i = 0
    n = len(prefix)
    while i < n:
        c = prefix[i]
        if open_quote is None:
            if c == '"' or c == "'":
                open_quote = c
        else:
            if c == "\\":
                i += 2
                continue
            if c == open_quote:
                open_quote = None
        i += 1
    return open_quote is not None


def find_pattern_outside_string(line, patterns):
    idx, matched = find_pattern(line, patterns)
    while idx is not None and is_in_string_literal(line[:idx]):
        idx, matched = find_pattern(line, patterns, start=idx + 1)
    return idx, matched


def create_config():
    if not os.path.isdir(".git"):
        print(
            "This project is not initialized with git. GhostNotes only works for directories already initialized with git."
        )
        return

    else:
        # set-up the default config
        config = configparser.ConfigParser()
        config["settings"] = {"tag": "GN:", "space_mode": "space"}
        config["languages"] = {
            ".py": "#",
            ".java": "//",
            ".js": "//",
            ".ts": "//",
            ".c": "//",
            ".cpp": "//",
            ".cs": "//",
            ".go": "//",
            ".rs": "//",
            ".swift": "//",
            ".kt": "//",
            ".rb": "#",
            ".sh": "#",
            ".yaml": "#",
            ".yml": "#",
            ".r": "#",
            ".php": "//",
            ".lua": "--",
            ".sql": "--",
            ".scala": "//",
            ".dart": "//",
            ".zig": "//",
            ".pl": "#",
            ".ex": "#",
            ".hs": "--",
        }

        with open(".ghostnotes", "w") as configfile:
            config.write(configfile)

        print("GhostNotes: Config file is created succesfully")


def update_exclude():
    loc = ".git/info/exclude"

    with open(loc, "r") as file:
        for line in file:
            # already in exclude
            if line.strip() == ".ghostnotes":
                return

    file = open(loc, "a")
    file.write(".ghostnotes\n")
    file.close()


def load_config():
    # Silent by design: this runs on every commit via the pre-commit hook.
    # Callers handle the None return with their own user-facing message.
    if not os.path.isfile(".ghostnotes"):
        return None

    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    return config


# update tag
def set_tag(tag):
    if not os.path.isfile(".ghostnotes"):
        print("This project is not initialized with GhostNotes, cannot set new tag.")
        return

    config = configparser.ConfigParser()
    config.read(".ghostnotes")  # preserve existing settings
    config["settings"]["tag"] = tag
    with open(".ghostnotes", "w") as configfile:
        config.write(configfile)

    print(f"GhostNotes: Config file tag is set to {tag} succesfully")


# add custom language comment support
def add_lang_support(extension, notation):
    if not os.path.isfile(".ghostnotes"):
        print(
            "This project is not initialized with GhostNotes, cannot add new file support."
        )
        return

    config = configparser.ConfigParser()
    config.read(".ghostnotes")
    config["languages"][extension] = notation
    with open(".ghostnotes", "w") as configfile:
        config.write(configfile)

    print(
        f"GhostNotes: Config file language support for {extension} files are added with symbol {notation} successfuly."
    )
