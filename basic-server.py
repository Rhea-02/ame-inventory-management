#!/usr/bin/env python3
"""
AMTC Lab Management System - Basic Server
Simplified localhost server with email notifications and SQLite database
"""

import http.server
import socketserver
import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import threading
import database  # Import our database module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicLabServer(http.server.SimpleHTTPRequestHandler):
    """Basic server for AMTC Lab Management System"""
    
    def do_POST(self):
        """Handle POST requests for email notifications and database operations"""
        if self.path == '/send-notification':
            self.handle_email_notification()
        elif self.path == '/api/items':
            self.handle_add_item()
        elif self.path == '/api/items/update':
            self.handle_update_item()
        elif self.path == '/api/items/delete':
            self.handle_delete_item()
        elif self.path == '/api/items/archive':
            self.handle_archive_item()
        elif self.path == '/api/items/import':
            self.handle_import_items()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - serve static files and API calls"""
        if self.path == '/api/items':
            self.handle_get_items()
        elif self.path == '/api/archived':
            self.handle_get_archived()
        else:
            # Serve static files from the current directory
            return super().do_GET()
    
    # ==================== DATABASE API HANDLERS ====================
    
    def handle_get_items(self):
        """Get all inventory items from database"""
        try:
            result = database.get_all_items()
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error getting items: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_get_archived(self):
        """Get all archived items from database"""
        try:
            result = database.get_all_archived()
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error getting archived items: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_add_item(self):
        """Add a new item to database"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            item = json.loads(post_data.decode('utf-8'))
            
            result = database.add_item(item)
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error adding item: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_update_item(self):
        """Update an existing item in database"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            item_id = data.get('id')
            updates = data.get('updates')
            
            result = database.update_item(item_id, updates)
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_delete_item(self):
        """Delete an item from database"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            item_id = data.get('id')
            result = database.delete_item(item_id)
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_archive_item(self):
        """Archive an item (move from inventory to archived)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            item = data.get('item')
            pickup_date = data.get('pickupDate')
            
            result = database.archive_item(item, pickup_date)
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error archiving item: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_import_items(self):
        """Import multiple items at once"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            items = data.get('items', [])
            result = database.import_items(items)
            self.send_json_response(result)
        except Exception as e:
            logger.error(f"Error importing items: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    # ==================== EMAIL NOTIFICATION HANDLER ====================
    
    def handle_email_notification(self):
        """Handle email notification requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({'error': 'No data provided'}, 400)
                return
            
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            notification_type = data.get('type')
            item = data.get('item')
            
            if not notification_type or not item:
                self.send_json_response({'error': 'Missing notification type or item data'}, 400)
                return
            
            # Send email notification in background
            threading.Thread(
                target=self.send_email_notification,
                args=(notification_type, item, data.get('additionalDays')),
                daemon=True
            ).start()
            
            self.send_json_response({'success': True, 'message': 'Notification queued'})
            
        except json.JSONDecodeError:
            self.send_json_response({'error': 'Invalid JSON data'}, 400)
        except Exception as e:
            logger.error(f"Error handling notification: {e}")
            self.send_json_response({'error': 'Server error'}, 500)
    
    def send_email_notification(self, notification_type, item, additional_days=None):
        """Send email notification"""
        try:
            # Email configuration (customize these settings)
            smtp_server = "smtp.gmail.com"  # Change to your SMTP server
            smtp_port = 587
            sender_email = "your-email@gmail.com"  # Change to your email
            sender_password = "your-app-password"  # Use app password for Gmail
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = item['emailId']
            
            if notification_type == 'storage':
                subject = f"🔬 AMTC Lab - Item Stored: {item['objectStored']}"
                body = f"""
Hello {item['ownerName']},

Your item has been successfully stored in the AMTC Lab Management System.

📦 STORAGE DETAILS:
• Item: {item['objectStored']}
• Tag ID: {item['uniqueId']}
• Location: {item['location']}
• Storage Period: {item['timePeriod']} days
• Expiry Date: {datetime.fromisoformat(item['expiryDate'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}

⚠️ IMPORTANT REMINDERS:
• Please collect your item before the expiry date
• You will receive reminder emails as the expiry approaches
• Contact the lab if you need to extend the storage period

Thank you for using the AMTC Lab Management System!

Best regards,
AMTC Lab Team
"""
            
            elif notification_type == 'extension':
                subject = f"⏰ AMTC Lab - Storage Extended: {item['objectStored']}"
                body = f"""
Hello {item['ownerName']},

The storage period for your item has been successfully extended.

📦 EXTENSION DETAILS:
• Item: {item['objectStored']}
• Tag ID: {item['uniqueId']}
• Extended by: {additional_days} days
• New Expiry Date: {datetime.fromisoformat(item['expiryDate'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}

Your item is now safe for the extended period. Please collect it before the new expiry date.

Thank you for using the AMTC Lab Management System!

Best regards,
AMTC Lab Team
"""
            
            elif notification_type == 'pickup':
                subject = f"✅ AMTC Lab - Item Picked Up: {item['objectStored']}"
                body = f"""
Hello {item['ownerName']},

This email confirms that your item has been successfully picked up from the AMTC Lab.

📦 PICKUP DETAILS:
• Item: {item['objectStored']}
• Tag ID: {item['uniqueId']}
• Original Location: {item['location']}
• Pickup Date: {datetime.fromisoformat(item['pickupDate'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}

Thank you for using the AMTC Lab Management System!

Best regards,
AMTC Lab Team
"""
            
            else:
                logger.warning(f"Unknown notification type: {notification_type}")
                return
            
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email (disable for local testing)
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                text = msg.as_string()
                server.sendmail(sender_email, item['emailId'], text)
                server.quit()
                
                logger.info(f"Email sent successfully to {item['emailId']} for {notification_type}")
                
            except Exception as email_error:
                # Email failed, but don't break the application
                logger.warning(f"Email sending failed: {email_error}")
                logger.info("Email notifications are disabled for local development")
        
        except Exception as e:
            logger.error(f"Error in email notification: {e}")
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    """Start the basic lab management server"""
    port = 8000
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create server
    with socketserver.TCPServer(("", port), BasicLabServer) as httpd:
        print("=" * 60)
        print("🔬 AMTC Lab Management System - Basic Server")
        print("=" * 60)
        print(f"📡 Server running on: http://localhost:{port}")
        print(f"🌐 Access the lab system: http://localhost:{port}")
        print("📧 Email notifications: Enabled (configure SMTP settings)")
        print("💾 Data storage: localStorage (browser-based)")
        print("🔧 Mode: Basic localhost functionality")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            print("Thank you for using AMTC Lab Management System!")

if __name__ == "__main__":
    run_server()