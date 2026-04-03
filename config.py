# file for creating the .ghostnotes configuration
import configparser
import os

def create_config():
    if not os.path.isdir('.git'):
        print("This project is not initialized with git. GhostNotes only works for directories already initialized with git.")
        return

    else:
        # set-up the default config
        config = configparser.ConfigParser()
        config['settings'] = {'tag': 'GN:'}
        config['languages'] = {'.py': '#', '.java': '//', '.js': '//', '.ts': '//'}

        with open('.ghostnotes', 'w') as configfile:
            config.write(configfile)

        print("GhostNotes: Config file is created succesfully")

def update_exclude():
    loc = ".git/info/exclude"
    
    with open(loc, 'r') as file:
        for line in file:
            # already in exclude
            if line.strip() == '.ghostnotes':
                return
            
    file = open(loc, "a")
    file.write('.ghostnotes\n')
    file.close()
        
def load_config():
    # check if config exists
    if not os.path.isfile('.ghostnotes'):
        print("This project is not initialized with GhostNotes.")
        return
    
    else:
        # set-up the default config
        config = configparser.ConfigParser()
        config.read('.ghostnotes')
        print("GhostNotes: Config file is read succesfully")

        return config

# update tag 
def set_tag(tag):
    if not os.path.isfile('.ghostnotes'):
        print("This project is not initialized with GhostNotes, cannot set new tag.")
        return
    
    config = configparser.ConfigParser()
    config.read('.ghostnotes')          # preserve existing settings
    config['settings']['tag'] = tag
    with open('.ghostnotes', 'w') as configfile:
        config.write(configfile)
        
    print(f"GhostNotes: Config file tag is set to {tag} succesfully")

# add custom language comment support
def add_lang_support(extension, notation):
    pass