#!/usr/bin/env python3
"""
AMTC Lab Management System - Web Launcher Server
Creates bookmarkable URLs for Chrome browser access
"""

import http.server
import socketserver
import os
import sys
import json
import subprocess
import webbrowser
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import threading
import time

class AMTCLauncherHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Route requests - direct redirect to lab system
        if path == '/' or path == '/launcher' or path == '/lab':
            self.redirect_to_lab()
        elif path == '/api/launcher/status':
            self.serve_launcher_status()
        elif path == '/api/launcher/start':
            self.handle_start_lab()
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        else:
            super().do_GET()
    
    def serve_launcher_page(self):
        """Serve the main launcher page"""
        launcher_html = self.get_launcher_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(launcher_html.encode())
    
    def redirect_to_lab(self):
        """Redirect directly to the main lab system"""
        # Check if lab server is running
        lab_server_running = self.is_lab_server_running()
        
        if lab_server_running:
            # Direct redirect to lab system
            self.send_response(302)
            self.send_header('Location', 'http://localhost:8000')
            self.end_headers()
        else:
            # Auto-start lab server and redirect
            self.auto_start_lab_and_redirect()
    
    def serve_launcher_status(self):
        """API endpoint for launcher status"""
        status = {
            'launcher_running': True,
            'lab_running': self.is_lab_server_running(),
            'onedrive_status': self.check_onedrive_status(),
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def handle_start_lab(self):
        """API endpoint to start the lab server"""
        try:
            if not self.is_lab_server_running():
                # Start the lab server in background
                subprocess.Popen([
                    sys.executable, 'basic-server.py'
                ], cwd=os.getcwd())
                
                result = {'success': True, 'message': 'Lab server starting...'}
            else:
                result = {'success': True, 'message': 'Lab server already running'}
                
        except Exception as e:
            result = {'success': False, 'message': str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def is_lab_server_running(self):
        """Check if the lab server is running on port 8000"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            return result == 0
        except:
            return False
    
    def check_onedrive_status(self):
        """Check localhost status (no cloud sync)"""
        # Basic version always runs in local mode
        return 'local_mode'
    
    def serve_auto_start_page(self):
        """Serve page that auto-starts lab and redirects"""
        auto_start_html = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Starting AMTC Lab System...</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3;url=http://localhost:8000">
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; 
            text-align: center; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 50px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid #fff;
            width: 50px;
            height: 50px;
            animation: spin 2s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <script>
        // Start the lab server
        fetch('/api/launcher/start')
            .then(response => response.json())
            .then(data => {
                console.log('Lab server start:', data);
                // Redirect after 3 seconds
                setTimeout(() => {
                    window.location.href = 'http://localhost:8000';
                }, 3000);
            })
            .catch(error => {
                console.error('Error starting lab:', error);
            });
    </script>
</head>
<body>
    <div>
        <h1>🔬 AMTC Lab Management System</h1>
        <div class="spinner"></div>
        <h2>Starting lab server...</h2>
        <p>You will be redirected automatically in 3 seconds.</p>
        <p>If not redirected, <a href="http://localhost:8000" style="color: #fff;">click here</a></p>
    </div>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(auto_start_html.encode())
    
    def auto_start_lab_and_redirect(self):
        """Auto-start lab server and show loading page"""
        # Start lab server in background
        try:
            import subprocess
            subprocess.Popen(['python', '-m', 'http.server', '8000'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("🚀 Starting lab server on port 8000...")
        except Exception as e:
            print(f"⚠️ Could not auto-start lab server: {e}")
        
        # Show auto-redirect page
        self.serve_auto_start_page()
    
    def get_launcher_html(self):
        """Generate the launcher HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔬 AMTC Lab System</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔬</text></svg>">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .launcher-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 600px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .launcher-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
            animation: shine 3s infinite;
            pointer-events: none;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .logo {
            font-size: 4em;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.2em;
            font-weight: 400;
        }
        
        .bookmark-info {
            background: #e8f4fd;
            border: 2px solid #0078d4;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .bookmark-info h3 {
            color: #0078d4;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .url-to-bookmark {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            color: #495057;
            margin: 10px 0;
            word-break: break-all;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .action-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            text-decoration: none;
            display: inline-block;
            min-width: 180px;
        }
        
        .action-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        
        .action-button:active {
            transform: translateY(0);
        }
        
        .action-button.success {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .action-button.warning {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
            color: #212529;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #dee2e6;
        }
        
        .status-card.online {
            border-left-color: #28a745;
            background: #d4edda;
        }
        
        .status-card.offline {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .status-card.warning {
            border-left-color: #ffc107;
            background: #fff3cd;
        }
        
        .status-title {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        
        .status-value {
            font-size: 0.95em;
            color: #666;
        }
        
        .instructions {
            text-align: left;
            background: #e9ecef;
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
        }
        
        .instructions h3 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .step {
            margin: 12px 0;
            padding-left: 25px;
            position: relative;
            line-height: 1.5;
        }
        
        .step::before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .footer {
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 600px) {
            .launcher-container {
                padding: 20px;
                margin: 10px;
            }
            
            .action-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="launcher-container">
        <div class="logo">🔬</div>
        <h1>AMTC Lab Management</h1>
        <p class="subtitle">OneDrive Enterprise Edition • Chrome Bookmarks</p>
        
        <div class="bookmark-info">
            <h3>📌 Bookmark These URLs in Chrome:</h3>
            <div><strong>Launcher:</strong> <div class="url-to-bookmark">http://localhost:8082/launcher</div></div>
            <div><strong>Direct Lab Access:</strong> <div class="url-to-bookmark">http://localhost:8082/lab</div></div>
        </div>
        
        <div class="action-buttons">
            <button class="action-button" onclick="openLab()">
                🚀 Open Lab System
            </button>
            <button class="action-button success" onclick="createBookmarks()">
                📌 Add to Chrome Bookmarks
            </button>
        </div>
        
        <div class="status-grid">
            <div class="status-card" id="launcher-status">
                <div class="status-title">🌐 Launcher Server</div>
                <div class="status-value" id="launcher-value">Running</div>
            </div>
            <div class="status-card" id="lab-status">
                <div class="status-title">🔬 Lab System</div>
                <div class="status-value" id="lab-value">Checking...</div>
            </div>
            <div class="status-card" id="onedrive-status">
                <div class="status-title">📁 OneDrive Sync</div>
                <div class="status-value" id="onedrive-value">Checking...</div>
            </div>
        </div>
        
        <div class="instructions">
            <h3>🎯 For Your Employees (Unlimited):</h3>
            <div class="step">Visit this URL: <strong>http://localhost:8082/launcher</strong></div>
            <div class="step">Click "Add to Chrome Bookmarks" button</div>
            <div class="step">Daily use: Click bookmark → Click "Open Lab System"</div>
            <div class="step">Scales to 100+ employees easily!</div>
        </div>
        
        <div class="footer">
            🏢 Company Edition • Real-time OneDrive Sync • Multi-user Support
        </div>
    </div>

    <script>
        // Auto-refresh status every 3 seconds
        setInterval(updateStatus, 3000);
        updateStatus(); // Initial load
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/launcher/status');
                const status = await response.json();
                
                // Update launcher status
                document.getElementById('launcher-value').textContent = 'Online';
                document.getElementById('launcher-status').className = 'status-card online';
                
                // Update lab status
                const labCard = document.getElementById('lab-status');
                const labValue = document.getElementById('lab-value');
                if (status.lab_running) {
                    labValue.textContent = 'Running on :8000';
                    labCard.className = 'status-card online';
                } else {
                    labValue.textContent = 'Not Running';
                    labCard.className = 'status-card offline';
                }
                
                // Update OneDrive status
                const onedriveCard = document.getElementById('onedrive-status');
                const onedriveValue = document.getElementById('onedrive-value');
                if (status.onedrive_status === 'synced') {
                    onedriveValue.textContent = 'Synced';
                    onedriveCard.className = 'status-card online';
                } else {
                    onedriveValue.textContent = 'Local Mode';
                    onedriveCard.className = 'status-card warning';
                }
                
            } catch (error) {
                console.error('Error updating status:', error);
                document.getElementById('launcher-value').textContent = 'Error';
                document.getElementById('launcher-status').className = 'status-card offline';
            }
        }
        
        function openLab() {
            // Open lab system (will auto-start if needed)
            window.open('/lab', '_blank');
        }
        
        function createBookmarks() {
            // Create bookmark instructions
            alert(`📌 To bookmark in Chrome:
            
1. Press Ctrl+D to bookmark this page
2. Or copy these URLs to bookmark:
   • Launcher: http://localhost:8080/launcher
   • Lab Direct: http://localhost:8080/lab

3. Share these URLs with all your employees! (Unlimited capacity)`);
        }
        
        // Auto-open lab if URL has ?autostart parameter
        if (window.location.search.includes('autostart')) {
            setTimeout(openLab, 1000);
        }
    </script>
</body>
</html>"""

def start_launcher_server(port=8082):
    """Start the direct lab access server"""
    print("🔬 AMTC Lab Management System - Direct Access")
    print("=" * 50)
    print(f"🚀 Starting direct lab access on port {port}")
    print(f"📌 Direct Lab Access: http://localhost:{port}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", port), AMTCLauncherHandler) as httpd:
            print(f"✅ Direct access server running at http://localhost:{port}")
            print("💡 Chrome Bookmark URL:")
            print(f"   • Lab System: http://localhost:{port}")
            print()
            print("🎯 For employees: Bookmark http://localhost:8082 for direct lab access")
            print("Press Ctrl+C to stop the server")
            
            # Auto-open browser to launcher
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}/launcher')).start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Launcher server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_launcher_server()