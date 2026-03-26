import os
import stat

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
    pass

if __name__ == "__main__":
    strip_ghostnotes()