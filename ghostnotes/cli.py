# CLI setup
import argparse
from ghostnotes.hook import install_hook, strip_ghostnotes
from ghostnotes.config import create_config, update_exclude, set_tag, add_lang_support
from ghostnotes.sync import pull, extract_notes

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
    lang_parser.add_argument("--symb", required=True, help="Symbol for commenting in the said language (# for .py, // for .java etc.)")

    # pull
    pull_parser = subparsers.add_parser("pull", help="Git pull with ghostnote-safe stripping and re-applying")

    # status
    status_parser = subparsers.add_parser("status", help="Show all ghost notes in the project")

    args = parser.parse_args()

    if args.command == "init":
        create_config()
        update_exclude()
        install_hook()
        print("GhostNotes is successfully initialized.")
    elif args.command == "set-tag":
        set_tag(args.tag)
    elif args.command == "add-lang":
        add_lang_support(args.ext, args.symb)
    elif args.command == "pull":
        pull()
    elif args.command == "status":
        notes = extract_notes()
        if not notes:
            print("No ghost notes found.")
        else:
            total = sum(len(v) for v in notes.values())
            print(f"Found {total} ghost note(s):\n")
            for file, file_notes in notes.items():
                for n in file_notes:
                    print(f"  {file}:{n['line_number'] + 1}  — {n['note']}")

if __name__ == "__main__":
    main()