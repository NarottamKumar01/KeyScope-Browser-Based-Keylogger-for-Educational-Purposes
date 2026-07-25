import http.server
import socketserver
import webbrowser
import threading
import socket
import sys
import os
import json
import urllib.parse
from win32_keylogger import Win32Keylogger
from detector_engine import KeyloggerDetector

# Default port
PORT = 8000

# Global singletons
keylogger = Win32Keylogger()
detector = KeyloggerDetector()

# Try to find a free port starting from 8000
def find_free_port(start_port):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except socket.error:
                port += 1
    return start_port

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence console log spam for cleaner output
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path == '/api/logger/start':
            method = query.get('method', ['hook'])[0]
            try:
                keylogger.start(method)
                self.send_json_response({"status": "success", "message": f"Started {method} keylogger."})
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, 500)

        elif path == '/api/logger/stop':
            keylogger.stop()
            self.send_json_response({"status": "success", "message": "Stopped keylogger."})

        elif path == '/api/logger/events':
            events = keylogger.get_logs()
            self.send_json_response({"events": events})

        elif path == '/api/logger/status':
            self.send_json_response({
                "is_running": keylogger.is_running,
                "method": keylogger.method
            })

        elif path == '/api/detector/scan':
            try:
                report = detector.scan_system()
                self.send_json_response(report)
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)}, 500)

        else:
            # Standard static file serving
            super().do_GET()

    def send_json_response(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception:
            pass

def run_server(port):
    # Serve files from the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Enable address re-use
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(('localhost', port), CustomHTTPRequestHandler) as httpd:
        print(f"Serving Keyboard Event Demonstration and Security Suite at http://localhost:{port}")
        print("Press Ctrl+C in the terminal to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            # Clean up keylogger if running
            keylogger.stop()
            sys.exit(0)

def main():
    port = find_free_port(PORT)
    url = f"http://localhost:{port}"
    
    # Start server in a separate thread so we can launch browser concurrently
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Give the server a small moment to start, then open the web browser
    print(f"Launching web browser at {url}...")
    webbrowser.open(url)
    
    # Keep the main thread alive to listen to exit signal
    try:
        while True:
            server_thread.join(timeout=1.0)
            if not server_thread.is_alive():
                break
    except KeyboardInterrupt:
        print("\nExiting application...")
        keylogger.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()

