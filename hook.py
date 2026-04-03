import os
import stat
import subprocess
from pathlib import Path 
from config import load_config

# for adding this script to pre-commit
def install_hook():
    path = '.git/hooks/pre-commit'
    script_path = os.path.abspath(__file__)
    command = f'python3 "{script_path}"' 

    # if a pre-commit hook file already exists:
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                if line.strip() == command:
                    return
            
        with open(path, 'a') as file:
            file.write(f'\n{command}\n')
    else:
        with open(path, 'w') as file:
            file.write(f'#!/bin/bash\n{command}\n')

    # make the file executable
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

# main logic function for stripping the committed files of the keyworded comments
def strip_ghostnotes():
    """
    Read Config
    Get the list of staged files — how do you ask git which files are staged? Think about what terminal command you'd run manually.
    Filter to only supported extensions
    For each supported file, strip lines matching the tag.
    Re-stage the files with git add
    """
    # read config
    configuration = load_config()

    # get the list of staged file:
    res = subprocess.run(['git', 'diff', '--name-only', '--cached'], capture_output=True, text=True)
    staged_files = res.stdout.splitlines()
    supported_staged_files = list()

    # filter staged_files to only supported file types
    for f in staged_files:
        if Path(f).suffix in configuration['languages']:
            supported_staged_files.append(f)

    # strip lines matching the tag
    # TODO: split has a subtle issue even for exact matching. What if the tag appears inside a string literal in the code, like: message = "use GN: prefix for notes"

    for file in supported_staged_files:
        # check the commenting style for the file type from configuration['languages'] as well as the tag from configuration['settings'] to build the exact sequence of chars we are looking for
        comment = configuration['languages'][Path(file).suffix]
        tag = configuration['settings']['tag']
        pattern = comment + ' ' + tag

        # read the staged version from the git index, not the working tree
        staged_content = subprocess.run(
            ['git', 'show', f':{file}'],
            capture_output=True, text=True
        ).stdout

        new_lines = list()
        for line in staged_content.splitlines(keepends=True):
            # strip
            if pattern in line:
                line = line.split(pattern)[0].rstrip() + '\n'
            new_lines.append(line)

        stripped_content = ''.join(new_lines)

        # write the stripped content back into the git index only
        hash_result = subprocess.run(
            ['git', 'hash-object', '-w', '--stdin'],
            input=stripped_content, capture_output=True, text=True
        )
        blob_hash = hash_result.stdout.strip()

        # get the file's mode from the index
        ls_result = subprocess.run(
            ['git', 'ls-files', '--stage', file],
            capture_output=True, text=True
        )
        mode = ls_result.stdout.split()[0]

        # update the index entry with the new blob
        subprocess.run(
            ['git', 'update-index', '--cacheinfo', f'{mode},{blob_hash},{file}']
        )

if __name__ == "__main__":
    strip_ghostnotes()