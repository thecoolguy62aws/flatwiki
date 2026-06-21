import sys
import os
import json
from argon2 import PasswordHasher

ph = PasswordHasher()

def main():
    if len(sys.argv) == 1:
        from flatwiki.core import run_server
        run_server()
    
    elif len(sys.argv) > 2:
        print("Error: Too many arguments")
        exit(1)
        
    else:
        match sys.argv[1]:
            case "create-user":
                username = input("username:")
                password = input("password:")
                hash = ph.hash(password)
                
                CURRENT_DIR = os.getcwd()
                CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")

                if not os.path.exists(CONFIG_PATH):
                    print(f"Error: Could not find 'config.json' in {CURRENT_DIR}")
                    sys.exit(1)
                
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    try:
                        CONFIG = json.load(f)
                    except:
                        print("Error: Invalid JSON content in config.json")
                        exit(1)
                
                if "admins" not in CONFIG:
                    CONFIG["admins"] = {}

                CONFIG["admins"][username] = hash
                
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    CONFIG = json.dump(CONFIG, f, indent=4)
                    
                exit(0)
                
            case "config":
                CONFIG = {}
                CONFIG["wiki_title"] = input("Wiki Title (the name of your wiki displayed on the website):")
                CONFIG["port"] = input("Port (usually 80 for production or 8080 for testing):")
                CONFIG["pages_directory"] = input("Pages Directory (directory to store pages in relative to current working directory; usually 'pages'):")
                confirm = input("Please confirm. THIS ACTION WILL OVERWRITE ANY FILE IN THE CURRENT DIRECTORY NAMED 'config.json'! Type 'overwrite' to continue with this DESTRUCTIVE action:")
                if confirm != "overwrite":
                    print("Safely cancelled.")
                    exit(0)
                CURRENT_DIR = os.getcwd()
                CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(CONFIG, f, indent=4)
                
                print("Success! Your config file has been built, now use the command 'flatwiki create-user' to add your first admin to this config file.")
                exit(0)
            
            case _:
                print("Error: Unknown argument")
                exit(1)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())