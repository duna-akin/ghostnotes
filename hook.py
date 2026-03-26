import os
import stat

# for adding this script to pre-commit
def install_hook():
    path = '.git/hooks/pre-commit'

    # if a pre-commit hook file already exists:
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                # already in exclude
                if line.strip() == 'python3 hook.py':
                    return
            
        with open(path, 'a') as file:
            file.write('\npython3 hook.py')
    else:
        with open(path, 'w') as file:
            file.write('#!/bin/bash\n')
            file.write('python3 hook.py')

    # make the file executable
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

# main logic function for stripping the committed files of the keyworded comments
def strip_ghostnotes():
    pass

if __name__ == "__main__":
    strip_ghostnotes()