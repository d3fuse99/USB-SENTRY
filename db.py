import json
import os
import hashlib
import datetime
import secrets

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHITELIST_FILE = os.path.join(SCRIPT_DIR, "whitelist.json")
SECRET_FILE = os.path.join(SCRIPT_DIR, "secret.key")
HASH_FILE = os.path.join(SCRIPT_DIR, "password.hash")
LOGS_FILE = os.path.join(SCRIPT_DIR, "logs.json")

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
        success = write_whitelist(whitelist)
        if success:
            log_security_event("Device " + serial + " added to Whitelist.")
        return success
    return True

def remove_from_whitelist(serial):
    hashed = hash_serial(serial)
    whitelist = read_whitelist()
    if hashed in whitelist:
        whitelist.remove(hashed)
        success = write_whitelist(whitelist)
        if success:
            log_security_event("Device " + serial + " removed from Whitelist.")
        return success
    return True

def write_whitelist(data):
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

def is_password_configured():
    return os.path.exists(HASH_FILE)

def setup_master_password(password):
    try:
        salt = get_secret()
        combined = password + salt
        hashed = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write(hashed)
        log_security_event("Master Password configured successfully.")
        return True
    except Exception:
        return False

def verify_master_password(password):
    if not is_password_configured():
        return False
    try:
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            stored_hash = f.read().strip()
        salt = get_secret()
        combined = password + salt
        hashed = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        return hashed == stored_hash
    except Exception:
        return False

def init_logs_file():
    if not os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        except Exception:
            pass

def log_security_event(message):
    init_logs_file()
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except Exception:
        logs = []
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append({
        "timestamp": timestamp,
        "message": message
    })
    
    try:
        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs[-50:], f, indent=4)
    except Exception:
        pass

def get_security_logs():
    init_logs_file()
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []