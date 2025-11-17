# AMTC Lab Management System - GitHub Pages Deployment

> **Note:** This is a static version deployed on GitHub Pages. Email notification features are disabled as GitHub Pages only supports static files.

## 🌐 Live Demo
[View Live Application](https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/)

## Features
- ✅ Add and manage lab inventory items
- ✅ Track storage time with countdown
- ✅ Mark items as picked up
- ✅ Export/Import Excel data
- ✅ View archived items
- ⚠️ Email notifications (requires local server setup)

## Local Development

### Prerequisites
- Python 3.7+
- Modern web browser

### Running Locally with Email Support
1. Clone the repository
2. Run `start-system.bat` (Windows) or `python basic-server.py`
3. Open http://localhost:8000

### GitHub Pages (Static Only)
Simply push to main branch - automatic deployment via GitHub Actions.

## Project Structure
```
├── index.html          # Main application
├── css/
│   └── style.css      # Styling
├── js/
│   └── app.js         # Application logic
├── basic-server.py    # Local Python server (for email features)
└── .github/
    └── workflows/
        └── deploy.yml # Auto-deployment workflow
```

## Configuration

### For GitHub Pages Deployment
1. Go to repository Settings → Pages
2. Source: GitHub Actions
3. Push to main branch - automatic deployment

### For Email Notifications (Local Only)
Edit `email_config.json` with your SMTP settings.

## License
MIT License
