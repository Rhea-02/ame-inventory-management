# AMTC Lab Management System - Complete Automation Guide

## 🎯 Overview
Your AMTC Lab Management System now features a **fully automated email notification system** that requires **zero manual intervention**. The system monitors your inventory 24/7 and automatically sends email alerts based on your Time Period settings.

## 🔧 System Components

### 1. Web Application (`index.html`)
- **Purpose**: Main inventory management interface
- **Features**: Add/manage items, view dashboard, export data
- **Access**: http://localhost:8084
- **Storage**: Browser localStorage (10MB capacity with usage monitoring)

### 2. Enhanced API Server (`api_server.py`)
- **Purpose**: Provides REST API endpoints for data access
- **Features**: Real-time data access, CORS support, comprehensive logging
- **Endpoints**: 
  - `/api/inventory/current` - Current inventory items
  - `/api/inventory/archived` - Archived items  
  - `/api/inventory/all` - Complete inventory data
  - `/api/inventory/notifications` - Notification analysis
  - `/api/health` - System health check

### 3. Automated Email System (`automated_email_system.py`)
- **Purpose**: Fully automated email notifications
- **Features**: Smart scheduling, notification history, multiple data sources
- **Schedule**: 2 days before due → on due date → daily after overdue
- **Intelligence**: Prevents duplicate notifications, tracks history

## 📧 Email Notification Logic

### When Emails Are Sent:
1. **2 days before expiry**: "Your item expires soon" warning
2. **On expiry date**: "Your item expires today" alert  
3. **Every day after expiry**: "Your item is overdue" reminders

### Smart Features:
- ✅ **No Duplicates**: Won't send the same notification twice
- ✅ **Intelligent Scheduling**: Calculates exact notification dates
- ✅ **Multiple Data Sources**: API → localStorage → JSON fallback
- ✅ **Comprehensive Logging**: Track all notification activity

## 🚀 Quick Start Guide

### Step 1: Initial Setup
```cmd
# Run as Administrator
setup-automated-emails.bat
```
This creates:
- Daily email task (9:00 AM)
- API server startup task
- All necessary scripts

### Step 2: Configure Email Settings
Edit `email_config.json`:
```json
{
  "smtp_server": "smtp.office365.com",
  "smtp_port": 587,
  "sender_email": "your-email@domain.com",
  "sender_password": "your-app-password",
  "lab_name": "AMTC Lab"
}
```

### Step 3: Start the API Server
```cmd
start-api-server.bat
```

### Step 4: Test Everything
```cmd
# Test API endpoints
test-api.bat

# Test email notifications (dry run)
test-notifications.bat
```

## 🛠️ Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `start-server.bat` | Basic web server | Simple web app access |
| `start-api-server.bat` | Enhanced server with API | Full system functionality |
| `setup-automated-emails.bat` | Complete system setup | Initial installation |
| `test-api.bat` | Test API endpoints | Verify API connectivity |
| `test-notifications.bat` | Test emails (dry run) | Email system testing |
| `run-manual-notifications.bat` | Send emails now | Manual email sending |

## 🔄 Data Flow Architecture

```
Web App (localhost:8084)
    ↓ (saves to)
Browser localStorage
    ↓ (accessed by)
API Server (api_server.py)
    ↓ (provides data to)
Email System (automated_email_system.py)
    ↓ (sends notifications via)
Office 365 SMTP
    ↓ (delivers to)
Users' Email Inboxes
```

### Data Access Priority:
1. **API Endpoint** (preferred) - Real-time data
2. **localStorage** (fallback) - Direct browser access
3. **JSON Export** (backup) - Manual export file
4. **Web Server** (last resort) - Alternative access

## ⏰ Automation Schedule

### Windows Task Scheduler Tasks:
1. **"AMTC Lab Email Notifications"**
   - **Runs**: Daily at 9:00 AM
   - **Action**: Check inventory and send emails
   - **Level**: System (highest privileges)

2. **"AMTC Lab API Server"**
   - **Runs**: On system startup
   - **Action**: Start API server in background
   - **Level**: System (persistent service)

## 🔍 Monitoring & Troubleshooting

### Log Files:
- `automated_email_notifications.log` - Email system activity
- `api_server.log` - API server requests and responses
- `notification_history.json` - Email tracking database

### Health Checks:
```cmd
# Check API server status
curl http://localhost:8084/api/health

# Verify email system (dry run)
python automated_email_system.py --dry-run

# Test specific endpoint
python test_api.py
```

### Common Issues:

#### API Server Not Running:
```cmd
# Manual start
start-api-server.bat

# Check if port is in use
netstat -an | findstr :8084
```

#### Email Authentication Fails:
1. Verify email credentials in `email_config.json`
2. Use app-specific password for Office 365
3. Check firewall/antivirus blocking SMTP

#### No Data Found:
1. Ensure web app is being used (adds data to localStorage)
2. Check if API server can access data
3. Verify JSON export file exists as fallback

## 🎛️ Advanced Configuration

### Custom Email Schedule:
Edit Task Scheduler task "AMTC Lab Email Notifications":
- Change time: Task Properties → Triggers → Edit
- Change frequency: Daily/Weekly/Monthly options

### API Server Port:
```cmd
# Use different port
python api_server.py 8085
```

### Email Templates:
Modify email content in `email_config.json` → "notification_templates"

## 🔒 Security Considerations

### Email Credentials:
- Use app-specific passwords, not account passwords
- Store credentials securely in `email_config.json`
- Limit file permissions to prevent unauthorized access

### Network Security:
- API server runs on localhost only (not external access)
- CORS headers allow local web app access
- No sensitive data exposed in API responses

## 📞 Support & Maintenance

### Regular Maintenance:
- Monitor log files for errors
- Update email credentials if changed
- Archive old notification history periodically

### System Updates:
- Python updates: Verify script compatibility
- Windows updates: Check Task Scheduler tasks still work
- Browser updates: Verify localStorage access

### Getting Help:
1. Check log files for specific error messages
2. Run test scripts to isolate issues
3. Verify all components are running correctly

---

## 🎉 Success! Your AMTC Lab is Now Fully Automated

With this setup, your lab management system:
- ✅ **Monitors inventory 24/7**
- ✅ **Sends intelligent email alerts**
- ✅ **Requires zero manual intervention**  
- ✅ **Provides real-time API access**
- ✅ **Tracks notification history**
- ✅ **Handles multiple data sources**

The system will continue working automatically, sending email notifications exactly when needed based on your Time Period settings. Users will receive timely reminders about their stored items without any action required from lab administrators.

**Important**: The system starts automatically with Windows and runs continuously in the background. You only need to configure it once!