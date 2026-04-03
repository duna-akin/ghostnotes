# CLI setup
import argparse
from hook import install_hook, strip_ghostnotes
from config import create_config, update_exclude, set_tag, add_lang_support

def main():
    parser = argparse.ArgumentParser(description="GhostNotes")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize GhostNotes")

    # set tag
    tag_parser = subparsers.add_parser("set-tag", help="Set the tag for GhostNotes to ignore, Default tag is 'GN:'. ")
    tag_parser.add_argument("--tag", required=True, help="New tag")

    # add lang
    lang_parser = subparsers.add_parser("add-lang", help="Add a new language support, Check .ghostnotes for the default languages supported")
    lang_parser.add_argument("--ext", required=True, help="File extension (.py, .js, .sql etc.)")
    lang_parser.add_argument("--not", required=True, help="Notation for commenting in the said language (# for .py, // for .java etc.)")

    args = parser.parse_args()

    if args.command == "init":
        create_config()
        update_exclude()
        install_hook()
        print("GhostNotes is successfully initialized.")
    elif args.command == "set-tag":
        pass # will call once the appropriate func is implemented
    elif args.command == "add-lang":
        pass
