import http.server
import json
import os
import threading
import time
from scanner import scan_usb_history, check_usbstor_existence, PLATFORM_WINDOWS
from db import (
    is_serial_whitelisted, add_to_whitelist, remove_from_whitelist, init_whitelist,
    is_password_configured, setup_master_password, verify_master_password,
    log_security_event, get_security_logs
)
from mitigation import disable_unauthorized_device, is_admin

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNLOCK_EXPIRE_TIME = 0.0

def is_unlocked():
    global UNLOCK_EXPIRE_TIME
    return time.time() < UNLOCK_EXPIRE_TIME

def get_unlock_seconds_left():
    global UNLOCK_EXPIRE_TIME
    left = UNLOCK_EXPIRE_TIME - time.time()
    return int(max(0, left))

def live_monitor_thread():
    init_whitelist()
    known_serials = set()
    was_unlocked = False
    
    try:
        initial_devices = scan_usb_history()
        for dev in initial_devices:
            known_serials.add(dev["serial_number"])
    except Exception:
        pass
        
    print("[*] USB-Sentry Active Background Monitor Online.")
    log_security_event("Active Background Monitor started.")
    
    while True:
        time.sleep(2)
        try:
            unlocked_state = is_unlocked()
            if was_unlocked and not unlocked_state:
                log_security_event("Unlock session expired. Ports are armed.")
            was_unlocked = unlocked_state

            current_devices = scan_usb_history()
            for dev in current_devices:
                serial = dev["serial_number"]
                if serial not in known_serials:
                    known_serials.add(serial)
                    
                    if not is_serial_whitelisted(serial):
                        name = dev["device_name"]
                        is_usbstor = dev.get("is_usbstor", True)
                        
                        log_security_event("Unauthorized device insertion detected: " + name + " (" + serial + ")")
                        print("[ALERT] Unauthorized device connected: " + name + " (" + serial + ")")
                        
                        if unlocked_state:
                            log_security_event("Skipped mitigation for " + serial + " (Active unlock session)")
                            print("[BYPASS] Skipped mitigation. System is unlocked.")
                        elif PLATFORM_WINDOWS:
                            log_security_event("Executing PnP disable command on: " + serial)
                            print("[MITIGATION] Attempting to disable device: " + serial)
                            blocked = disable_unauthorized_device(serial, is_usbstor)
                            if blocked:
                                log_security_event("Mitigation success. Device " + serial + " disabled.")
                                print("[SUCCESS] Device disabled successfully.")
                            else:
                                log_security_event("Mitigation failed. Device " + serial + " remains active.")
                                print("[FAILURE] Failed to disable device.")
        except Exception as e:
            print("Error in background monitor: " + str(e))

class USBSentryHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print("LOG: " + (format % args))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif self.path == '/style.css':
            self.serve_file('style.css', 'text/css')
        elif self.path == '/app.js':
            self.serve_file('app.js', 'text/javascript')
        elif self.path == '/api/usb-history':
            self.handle_get_history()
        elif self.path == '/api/logs':
            self.handle_get_logs()
        elif self.path == '/api/auth/status':
            self.handle_auth_status()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Endpoint Not Found")

    def do_POST(self):
        if self.path == '/api/whitelist/add':
            self.handle_whitelist_action(add=True)
        elif self.path == '/api/whitelist/remove':
            self.handle_whitelist_action(add=False)
        elif self.path == '/api/auth/setup':
            self.handle_auth_setup()
        elif self.path == '/api/auth/unlock':
            self.handle_auth_unlock()
        elif self.path == '/api/auth/lock':
            self.handle_auth_lock()
        else:
            self.send_error_response(404, "Endpoint Not Found")

    def serve_file(self, filename, content_type):
        filepath = os.path.join(SCRIPT_DIR, filename)
        if not os.path.exists(filepath):
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"File not found")
            return
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Error reading file")

    def handle_get_history(self):
        try:
            devices = scan_usb_history()
            for dev in devices:
                dev["is_whitelisted"] = is_serial_whitelisted(dev["serial_number"])
            response_data = json.dumps(devices).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            
            status_str = "Windows (Registry)"
            if not PLATFORM_WINDOWS:
                status_str = "Simulation Mode"
            elif not check_usbstor_existence():
                status_str = "Simulation (No USBSTOR Key)"
                
            self.send_header('X-Platform', status_str)
            self.end_headers()
            self.wfile.write(response_data)
        except Exception:
            self.send_error_response(500, "Internal registry parse error")

    def handle_get_logs(self):
        try:
            logs = get_security_logs()
            response_data = json.dumps(logs).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data)
        except Exception:
            self.send_error_response(500, "Internal database error")

    def handle_auth_status(self):
        try:
            unlocked = is_unlocked()
            seconds_left = get_unlock_seconds_left()
            configured = is_password_configured()
            data = {
                "is_configured": configured,
                "is_unlocked": unlocked,
                "seconds_left": seconds_left
            }
            response_data = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data)
        except Exception:
            self.send_error_response(500, "Auth status parsing error")

    def handle_auth_setup(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            password = payload.get("password")
            
            if is_password_configured():
                self.send_error_response(400, "Password already configured")
                return
            
            if not password or len(password) < 4:
                self.send_error_response(400, "Password too short")
                return
            
            success = setup_master_password(password)
            if success:
                response_data = json.dumps({"status": "success"}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(response_data))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
            else:
                self.send_error_response(500, "Database setup error")
        except Exception:
            self.send_error_response(400, "Malformed setup data")

    def handle_auth_unlock(self):
        global UNLOCK_EXPIRE_TIME
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            password = payload.get("password")
            duration = int(payload.get("duration", 120))
            
            if not verify_master_password(password):
                self.send_error_response(401, "Invalid Master Password")
                return
            
            UNLOCK_EXPIRE_TIME = time.time() + duration
            log_security_event("System temporarily unlocked for " + str(duration) + " seconds.")
            
            response_data = json.dumps({"status": "success", "seconds_left": duration}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data)
        except Exception:
            self.send_error_response(400, "Malformed unlock payload")

    def handle_auth_lock(self):
        global UNLOCK_EXPIRE_TIME
        try:
            UNLOCK_EXPIRE_TIME = 0.0
            log_security_event("System locked manually by Administrator.")
            response_data = json.dumps({"status": "success"}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data)
        except Exception:
            self.send_error_response(500, "Error locking system")

    def handle_whitelist_action(self, add=True):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            serial = payload.get("serial_number")
            if not serial:
                self.send_error_response(400, "Missing serial")
                return
            
            if add:
                success = add_to_whitelist(serial)
            else:
                success = remove_from_whitelist(serial)
            
            if success:
                response_data = json.dumps({"status": "success"}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(response_data))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response_data)
            else:
                self.send_error_response(500, "Database write failure")
        except Exception:
            self.send_error_response(400, "Malformed payload")

    def send_error_response(self, status, message):
        response_bytes = json.dumps({"error": message}).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_bytes))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

def run_server():
    init_whitelist()
    
    monitor_t = threading.Thread(target=live_monitor_thread, daemon=True)
    monitor_t.start()
    
    server_address = ('127.0.0.1', 9090)
    httpd = http.server.HTTPServer(server_address, USBSentryHandler)
    
    admin_status = "Admin elevated" if is_admin() else "Standard privileges (Mitigation disabled)"
    print("Server active on http://127.0.0.1:9090 (" + admin_status + ")")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    run_server()