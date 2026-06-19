import http.server
import json
import os
from scanner import scan_usb_history, check_usbstor_existence, PLATFORM_WINDOWS
from db import read_whitelist, write_whitelist, init_whitelist

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
            whitelist = read_whitelist()
            for dev in devices:
                dev["is_whitelisted"] = dev["serial_number"] in whitelist
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
            whitelist = read_whitelist()
            if add:
                if serial not in whitelist:
                    whitelist.append(serial)
            else:
                if serial in whitelist:
                    whitelist.remove(serial)
            if write_whitelist(whitelist):
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
    server_address = ('127.0.0.1', 9090)
    httpd = http.server.HTTPServer(server_address, USBSentryHandler)
    print("Server active on http://127.0.0.1:9090")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    run_server()