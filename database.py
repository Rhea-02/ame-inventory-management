"""
SQLite Database Manager for AMTC Lab Inventory System
Handles all database operations for permanent data storage
"""

import sqlite3
import json
from datetime import datetime
import os

# Database file path
DB_FILE = 'inventory.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            ownerName TEXT NOT NULL,
            emailId TEXT NOT NULL,
            ssoId TEXT NOT NULL,
            objectStored TEXT NOT NULL,
            uniqueId TEXT UNIQUE NOT NULL,
            location TEXT NOT NULL,
            timePeriod INTEGER NOT NULL,
            dateAdded TEXT NOT NULL,
            expiryDate TEXT NOT NULL
        )
    ''')
    
    # Create archived items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived (
            id TEXT PRIMARY KEY,
            ownerName TEXT NOT NULL,
            emailId TEXT NOT NULL,
            ssoId TEXT NOT NULL,
            objectStored TEXT NOT NULL,
            uniqueId TEXT NOT NULL,
            location TEXT NOT NULL,
            timePeriod INTEGER NOT NULL,
            dateAdded TEXT NOT NULL,
            expiryDate TEXT NOT NULL,
            pickupDate TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def add_item(item):
    """Add a new item to the inventory"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inventory 
            (id, ownerName, emailId, ssoId, objectStored, uniqueId, location, timePeriod, dateAdded, expiryDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['id'],
            item['ownerName'],
            item['emailId'],
            item['ssoId'],
            item['objectStored'],
            item['uniqueId'],
            item['location'],
            item['timePeriod'],
            item['dateAdded'],
            item['expiryDate']
        ))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Item added successfully'}
    except sqlite3.IntegrityError as e:
        return {'success': False, 'message': f'Item with this ID already exists: {str(e)}'}
    except Exception as e:
        return {'success': False, 'message': f'Error adding item: {str(e)}'}

def get_all_items():
    """Get all items from inventory"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM inventory')
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'ownerName': row[1],
                'emailId': row[2],
                'ssoId': row[3],
                'objectStored': row[4],
                'uniqueId': row[5],
                'location': row[6],
                'timePeriod': row[7],
                'dateAdded': row[8],
                'expiryDate': row[9]
            })
        
        conn.close()
        return {'success': True, 'items': items}
    except Exception as e:
        return {'success': False, 'message': f'Error fetching items: {str(e)}', 'items': []}

def get_all_archived():
    """Get all archived items"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM archived')
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'ownerName': row[1],
                'emailId': row[2],
                'ssoId': row[3],
                'objectStored': row[4],
                'uniqueId': row[5],
                'location': row[6],
                'timePeriod': row[7],
                'dateAdded': row[8],
                'expiryDate': row[9],
                'pickupDate': row[10]
            })
        
        conn.close()
        return {'success': True, 'items': items}
    except Exception as e:
        return {'success': False, 'message': f'Error fetching archived items: {str(e)}', 'items': []}

def update_item(item_id, updates):
    """Update an existing item"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Build update query dynamically
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [item_id]
        
        cursor.execute(f'UPDATE inventory SET {set_clause} WHERE id = ?', values)
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Item updated successfully'}
    except Exception as e:
        return {'success': False, 'message': f'Error updating item: {str(e)}'}

def delete_item(item_id):
    """Delete an item from inventory"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Item deleted successfully'}
    except Exception as e:
        return {'success': False, 'message': f'Error deleting item: {str(e)}'}

def archive_item(item, pickup_date):
    """Move item from inventory to archived"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Add to archived
        cursor.execute('''
            INSERT INTO archived 
            (id, ownerName, emailId, ssoId, objectStored, uniqueId, location, timePeriod, dateAdded, expiryDate, pickupDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['id'],
            item['ownerName'],
            item['emailId'],
            item['ssoId'],
            item['objectStored'],
            item['uniqueId'],
            item['location'],
            item['timePeriod'],
            item['dateAdded'],
            item['expiryDate'],
            pickup_date
        ))
        
        # Remove from inventory
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item['id'],))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Item archived successfully'}
    except Exception as e:
        return {'success': False, 'message': f'Error archiving item: {str(e)}'}

def import_items(items):
    """Import multiple items at once"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        success_count = 0
        errors = []
        
        for item in items:
            try:
                cursor.execute('''
                    INSERT INTO inventory 
                    (id, ownerName, emailId, ssoId, objectStored, uniqueId, location, timePeriod, dateAdded, expiryDate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['id'],
                    item['ownerName'],
                    item['emailId'],
                    item['ssoId'],
                    item['objectStored'],
                    item['uniqueId'],
                    item['location'],
                    item['timePeriod'],
                    item['dateAdded'],
                    item['expiryDate']
                ))
                success_count += 1
            except sqlite3.IntegrityError:
                errors.append(f"Duplicate ID: {item['uniqueId']}")
        
        conn.commit()
        conn.close()
        
        return {
            'success': True, 
            'message': f'Imported {success_count} items', 
            'count': success_count,
            'errors': errors
        }
    except Exception as e:
        return {'success': False, 'message': f'Error importing items: {str(e)}'}

# Initialize database on import
if not os.path.exists(DB_FILE):
    init_database()
