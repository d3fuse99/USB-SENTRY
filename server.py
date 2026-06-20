import http.server
import json
import os
import threading
import time
from scanner import scan_usb_history, check_usbstor_existence, PLATFORM_WINDOWS
from db import is_serial_whitelisted, add_to_whitelist, remove_from_whitelist, init_whitelist
from mitigation import disable_unauthorized_device, is_admin

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def live_monitor_thread():
    init_whitelist()
    known_serials = set()
    
    try:
        initial_devices = scan_usb_history()
        for dev in initial_devices:
            known_serials.add(dev["serial_number"])
    except Exception:
        pass
        
    print("[*] USB-Sentry Active Background Monitor Online.")
    
    while True:
        time.sleep(2)
        try:
            current_devices = scan_usb_history()
            for dev in current_devices:
                serial = dev["serial_number"]
                if serial not in known_serials:
                    known_serials.add(serial)
                    
                    if not is_serial_whitelisted(serial):
                        name = dev["device_name"]
                        is_usbstor = dev.get("is_usbstor", True)
                        
                        print("[ALERT] Unauthorized device connected: " + name + " (" + serial + ")")
                        
                        if PLATFORM_WINDOWS:
                            print("[MITIGATION] Attempting to disable device: " + serial)
                            blocked = disable_unauthorized_device(serial, is_usbstor)
                            if blocked:
                                print("[SUCCESS] Device disabled successfully.")
                            else:
                                print("[FAILURE] Failed to disable device (check admin privileges).")
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