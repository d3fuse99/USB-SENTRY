import json
import os
import hashlib
import secrets

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHITELIST_FILE = os.path.join(SCRIPT_DIR, "whitelist.json")
SECRET_FILE = os.path.join(SCRIPT_DIR, "secret.key")

def init_secret():
    if not os.path.exists(SECRET_FILE):
        try:
            with open(SECRET_FILE, "w", encoding="utf-8") as f:
                f.write(secrets.token_hex(32))
        except Exception:
            pass

def get_secret():
    init_secret()
    try:
        with open(SECRET_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "defaultsystemsecretkey"

def hash_serial(serial):
    salt = get_secret()
    combined = serial + salt
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

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

def is_serial_whitelisted(serial):
    hashed = hash_serial(serial)
    whitelist = read_whitelist()
    return hashed in whitelist

def add_to_whitelist(serial):
    hashed = hash_serial(serial)
    whitelist = read_whitelist()
    if hashed not in whitelist:
        whitelist.append(hashed)
        return write_whitelist(whitelist)
    return True

def remove_from_whitelist(serial):
    hashed = hash_serial(serial)
    whitelist = read_whitelist()
    if hashed in whitelist:
        whitelist.remove(hashed)
        return write_whitelist(whitelist)
    return True

def write_whitelist(data):
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False