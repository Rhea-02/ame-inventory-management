#!/usr/bin/env python3
"""
Enhanced Python HTTP Server with REST API for AMTC Lab Management System
Provides both static file serving and data access endpoints for the automated email system
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LabManagementAPIHandler(http.server.SimpleHTTPRequestHandler):
    """Enhanced HTTP request handler with API endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - both API and static files"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # API endpoints
        if parsed_path.path.startswith('/api/'):
            self.handle_api_request(parsed_path)
        else:
            # Serve static files (existing functionality)
            super().do_GET()
    
    def handle_api_request(self, parsed_path):
        """Handle API requests"""
        try:
            if parsed_path.path == '/api/inventory/current':
                self.get_current_inventory()
            elif parsed_path.path == '/api/inventory/archived':
                self.get_archived_inventory()
            elif parsed_path.path == '/api/inventory/all':
                self.get_all_inventory()
            elif parsed_path.path == '/api/inventory/notifications':
                self.get_notification_data()
            elif parsed_path.path == '/api/health':
                self.health_check()
            else:
                self.send_error_response(404, "API endpoint not found")
        except Exception as e:
            logger.error(f"API error: {e}")
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def get_current_inventory(self):
        """Get current inventory items from localStorage simulation or fallback"""
        try:
            data = self.read_inventory_data()
            current_items = data.get('currentItems', [])
            
            response_data = {
                'status': 'success',
                'count': len(current_items),
                'items': current_items,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response_data)
            logger.info(f"Served current inventory: {len(current_items)} items")
            
        except Exception as e:
            logger.error(f"Error getting current inventory: {e}")
            self.send_error_response(500, f"Failed to retrieve current inventory: {str(e)}")
    
    def get_archived_inventory(self):
        """Get archived inventory items"""
        try:
            data = self.read_inventory_data()
            archived_items = data.get('archivedItems', [])
            
            response_data = {
                'status': 'success',
                'count': len(archived_items),
                'items': archived_items,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response_data)
            logger.info(f"Served archived inventory: {len(archived_items)} items")
            
        except Exception as e:
            logger.error(f"Error getting archived inventory: {e}")
            self.send_error_response(500, f"Failed to retrieve archived inventory: {str(e)}")
    
    def get_all_inventory(self):
        """Get both current and archived inventory items"""
        try:
            data = self.read_inventory_data()
            current_items = data.get('currentItems', [])
            archived_items = data.get('archivedItems', [])
            
            response_data = {
                'status': 'success',
                'current': {
                    'count': len(current_items),
                    'items': current_items
                },
                'archived': {
                    'count': len(archived_items),
                    'items': archived_items
                },
                'total_items': len(current_items) + len(archived_items),
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response_data)
            logger.info(f"Served all inventory: {len(current_items)} current, {len(archived_items)} archived")
            
        except Exception as e:
            logger.error(f"Error getting all inventory: {e}")
            self.send_error_response(500, f"Failed to retrieve inventory: {str(e)}")
    
    def get_notification_data(self):
        """Get data formatted for email notifications with status analysis"""
        try:
            data = self.read_inventory_data()
            current_items = data.get('currentItems', [])
            
            # Analyze items for notification status
            notification_data = {
                'items_due_soon': [],
                'items_overdue': [],
                'items_normal': [],
                'notification_summary': {
                    'total_items': len(current_items),
                    'due_soon_count': 0,
                    'overdue_count': 0,
                    'normal_count': 0
                },
                'timestamp': datetime.now().isoformat()
            }
            
            now = datetime.now()
            
            for item in current_items:
                try:
                    expiry_date = datetime.fromisoformat(item['expiryDate'].replace('Z', '+00:00'))
                    days_until_expiry = (expiry_date - now).days
                    
                    # Calculate notification status
                    item_with_status = item.copy()
                    item_with_status['days_until_expiry'] = days_until_expiry
                    item_with_status['notification_status'] = self.get_notification_status(days_until_expiry)
                    
                    # Categorize items
                    if days_until_expiry < 0:
                        notification_data['items_overdue'].append(item_with_status)
                        notification_data['notification_summary']['overdue_count'] += 1
                    elif days_until_expiry <= 2:
                        notification_data['items_due_soon'].append(item_with_status)
                        notification_data['notification_summary']['due_soon_count'] += 1
                    else:
                        notification_data['items_normal'].append(item_with_status)
                        notification_data['notification_summary']['normal_count'] += 1
                        
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing item {item.get('uniqueId', 'unknown')}: {e}")
                    continue
            
            response_data = {
                'status': 'success',
                'data': notification_data
            }
            
            self.send_json_response(response_data)
            logger.info(f"Served notification data: {notification_data['notification_summary']['overdue_count']} overdue, {notification_data['notification_summary']['due_soon_count']} due soon")
            
        except Exception as e:
            logger.error(f"Error getting notification data: {e}")
            self.send_error_response(500, f"Failed to retrieve notification data: {str(e)}")
    
    def get_notification_status(self, days_until_expiry):
        """Determine notification status based on days until expiry"""
        if days_until_expiry < 0:
            return 'overdue'
        elif days_until_expiry <= 2:
            return 'due_soon'
        else:
            return 'normal'
    
    def health_check(self):
        """Health check endpoint"""
        try:
            data = self.read_inventory_data()
            current_count = len(data.get('currentItems', []))
            archived_count = len(data.get('archivedItems', []))
            
            health_data = {
                'status': 'healthy',
                'service': 'AMTC Lab Management System API',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'data_status': {
                    'current_items': current_count,
                    'archived_items': archived_count,
                    'total_items': current_count + archived_count
                },
                'uptime': 'Available'
            }
            
            self.send_json_response(health_data)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.send_error_response(500, f"Health check failed: {str(e)}")
    
    def read_inventory_data(self):
        """Read inventory data from fallback JSON files or return empty structure"""
        data = {
            'currentItems': [],
            'archivedItems': []
        }
        
        # Try to read from fallback JSON files
        try:
            current_file = 'inventory_data.json'
            if os.path.exists(current_file):
                with open(current_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    data['currentItems'] = file_data.get('currentItems', [])
                    data['archivedItems'] = file_data.get('archivedItems', [])
                    logger.debug(f"Loaded data from {current_file}")
            else:
                logger.warning(f"No data file found at {current_file}")
                
        except Exception as e:
            logger.error(f"Error reading inventory data: {e}")
        
        return data
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {
            'status': 'error',
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(error_data, status_code)

def run_server(port=8084):
    """Run the enhanced HTTP server with API endpoints"""
    try:
        # Change to the directory containing the web files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        with socketserver.TCPServer(("", port), LabManagementAPIHandler) as httpd:
            print(f"🔬 AMTC Lab Management System with API")
            print(f"📊 Server running at: http://localhost:{port}")
            print(f"🌐 Web App: http://localhost:{port}")
            print(f"📡 API Base: http://localhost:{port}/api/")
            print("📋 Available API Endpoints:")
            print(f"   • GET /api/inventory/current     - Current inventory items")
            print(f"   • GET /api/inventory/archived    - Archived inventory items")
            print(f"   • GET /api/inventory/all         - All inventory data")
            print(f"   • GET /api/inventory/notifications - Notification data")
            print(f"   • GET /api/health                - System health check")
            print("\n🛑 Press Ctrl+C to stop the server")
            
            logger.info(f"AMTC Lab Management API Server started on port {port}")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        logger.info("Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            print(f"❌ Port {port} is already in use. Please:")
            print("   1. Close any other running servers")
            print("   2. Try a different port number")
            print("   3. Or restart your computer")
        else:
            print(f"❌ Error starting server: {e}")
        logger.error(f"Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected server error: {e}")

if __name__ == "__main__":
    # Get port from command line argument or use default
    port = 8084
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8084.")
    
    run_server(port)