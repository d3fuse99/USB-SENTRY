import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHITELIST_FILE = os.path.join(SCRIPT_DIR, "whitelist.json")

def init_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        except Exception:
            pass

def read_whitelist():
    init_whitelist()
    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def write_whitelist(data):
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False