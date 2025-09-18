# AME Lab Inventory Management System

A comprehensive web-based inventory management tool for tracking temporary storage items in the AME Lab shop floor.

## Features

### Core Functionality
- **Add Items**: Record new items with owner details, object description, location, and time period
- **Dashboard View**: Real-time overview of all stored items with status indicators
- **Time Extension**: Easily extend storage periods by days or hours
- **Pickup Management**: Mark items as picked up and archive them
- **Excel Integration**: Export and import data to/from Excel files
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Item Tracking Attributes
- Owner Name
- Email ID
- SSO ID
- Object Being Stored
- Unique ID (must be unique across all items)
- Location
- Time Period (in days)
- Automatic expiry date calculation
- Time remaining display with status indicators

### Status Indicators
- **Normal** (Green): More than 2 days remaining
- **Expiring Soon** (Yellow): 2 days or less remaining
- **Overdue** (Red): Time period has expired

### Dashboard Features
- Statistics overview (Total Items, Expiring Soon, Overdue)
- Real-time countdown updates
- Action buttons for each item (Extend/Mark as Picked Up)
- Search and sort functionality
- Export current inventory to Excel

### Archived Items
- Complete history of picked-up items
- Storage duration tracking
- Export archived data to Excel
- Permanent record keeping

## How to Use

### 1. Adding New Items
1. Click on the "Add Item" tab
2. Fill in all required fields:
   - Owner Name
   - Email ID
   - SSO ID
   - Object Being Stored
   - Unique ID (must be unique)
   - Location
   - Time Period (in days)
3. Click "Add Item to Inventory"

### 2. Managing Items
1. Go to the "Dashboard" tab to view all current items
2. Each item shows:
   - Owner information
   - Object details
   - Time remaining with color-coded status
   - Action buttons

### 3. Extending Time Period
1. Click the "Extend" button next to any item
2. Enter additional time (days or hours)
3. Click "Extend" to confirm
4. The new expiry date will be calculated automatically

### 4. Marking Items as Picked Up
1. Click "Mark as Picked Up" button next to the item
2. Confirm the action in the popup
3. Item will be moved to "Archived Items" tab
4. Original storage duration will be recorded

### 5. Excel Integration
- **Export Current Inventory**: Click "Export to Excel" on the Dashboard tab
- **Export Archived Items**: Click "Export Archived to Excel" on the Archived tab
- **Import from Excel**: Click "Import from Excel" and select a properly formatted Excel file

#### Excel File Format for Import
The Excel file should have the following columns:
- Owner Name
- Email ID
- SSO ID
- Object Stored
- Unique ID
- Location
- Time Period (Days)

## Technical Details

### Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Storage**: Browser Local Storage
- **Excel Integration**: SheetJS (xlsx) library
- **Styling**: Custom CSS with responsive design

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

### Data Persistence
- All data is stored locally in the browser's localStorage
- Data persists between browser sessions
- Export to Excel for backup and external storage

### File Structure
```
lab-inventory-management/
├── index.html          # Main application file
├── css/
│   └── style.css      # Styling and responsive design
├── js/
│   └── app.js         # Application logic and functionality
└── README.md          # This documentation
```

## Installation & Setup

1. Download all files to a local directory
2. Open `index.html` in a modern web browser
3. No additional installation or server setup required
4. For best performance, serve from a local web server (optional)

## Usage Tips

### Best Practices
1. Always use unique IDs for items to avoid conflicts
2. Regular exports to Excel for data backup
3. Check dashboard regularly for expiring items
4. Use descriptive object names for easy identification

### Time Management
- Time remaining updates automatically every minute
- Status colors help prioritize attention:
  - Red (Overdue): Immediate attention required
  - Yellow (Expiring): Plan for pickup or extension
  - Green (Normal): No immediate action needed

### Data Management
- Export data regularly for backup
- Use Excel exports for reporting to management
- Archived items provide complete audit trail

## Troubleshooting

### Common Issues
1. **Duplicate Unique ID Error**: Each item must have a unique identifier
2. **Import Failed**: Check Excel file format and column names
3. **Data Lost**: Data is stored locally; clearing browser data will remove items

### Browser Requirements
- JavaScript must be enabled
- Local Storage must be available
- Modern browser (IE11+ or equivalent)

## Future Enhancements
- User authentication and multi-user support
- Advanced search and filtering
- Email notifications for expiring items
- Integration with external databases
- Mobile app version
- Barcode scanning support

## Support
For issues or questions, contact the AME Lab administration or IT support.

---

**Version**: 1.0  
**Last Updated**: September 2025  
**Author**: AME Lab IT Team