// AMTC Lab Management System - Basic Version
// Simple localhost inventory management system

// Global variables
let currentItems = [];
let archivedItems = [];
let currentExtendingItemId = null;
let currentPickupItemId = null;

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏢 AMTC Lab Management System - Basic Version');
    
    // Check if XLSX library is available
    if (typeof XLSX === 'undefined') {
        console.error('❌ XLSX library failed to load from CDN');
        showMessage('Excel import/export functionality is not available. Please check your internet connection and refresh the page.', 'error');
    } else {
        console.log('✅ XLSX library loaded successfully');
    }
    
    loadDataFromStorage();
    updateDashboard();
    updateArchivedDashboard();
    updateStats();
    
    // Set up form submission
    document.getElementById('inventory-form').addEventListener('submit', handleFormSubmit);
    
    // Update time remaining every minute
    setInterval(updateTimeRemaining, 60000);
});



// Tab navigation functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all nav buttons
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked nav button
    event.target.classList.add('active');
    
    // Update data when switching to dashboard or archived
    if (tabName === 'dashboard') {
        updateDashboard();
        updateStats();
    } else if (tabName === 'archived') {
        updateArchivedDashboard();
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Add loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '🔄 Storing Item...';
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(event.target);
        const item = {
            id: Date.now().toString(),
            ownerName: formData.get('ownerName'),
            emailId: formData.get('emailId'),
            ssoId: formData.get('ssoId'),
            objectStored: formData.get('objectStored'),
            uniqueId: formData.get('uniqueId'),
            location: formData.get('location'),
            timePeriod: parseInt(formData.get('timePeriod')),
            dateAdded: new Date().toISOString(),
            expiryDate: new Date(Date.now() + (parseInt(formData.get('timePeriod')) * 24 * 60 * 60 * 1000)).toISOString()
        };
        
        // Check if unique ID already exists
        if (currentItems.find(existingItem => existingItem.uniqueId === item.uniqueId)) {
            showMessage('Oops! An item with this Tag/ID already exists. Please use a different tag number.', 'error');
            submitBtn.classList.remove('loading');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            return;
        }
        
        // Save to database
        const success = await saveItemToDatabase(item);
        
        if (success) {
            // Add to local array
            currentItems.push(item);
            
            // Reset form
            event.target.reset();
            
            // Show success message
            showMessage(`✅ Successfully stored ${item.objectStored} (ID: ${item.uniqueId}) in database`, 'success');
            
            // Update dashboard
            updateDashboard();
            updateStats();
            
            // Send email notification
            sendEmailNotification(item);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        showMessage('❌ Error storing item. Please try again.', 'error');
    } finally {
        // Reset button
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Update dashboard display
function updateDashboard() {
    const tbody = document.getElementById('inventory-tbody');
    const noItemsDiv = document.getElementById('no-items');
    
    if (!tbody) return;
    
    // Sort by expiry date (most urgent first)
    const sortedItems = [...currentItems].sort((a, b) => new Date(a.expiryDate) - new Date(b.expiryDate));
    
    if (sortedItems.length === 0) {
        tbody.innerHTML = '';
        if (noItemsDiv) {
            noItemsDiv.style.display = 'block';
        }
        return;
    }
    
    if (noItemsDiv) {
        noItemsDiv.style.display = 'none';
    }
    
    tbody.innerHTML = sortedItems.map(item => {
        const timeRemaining = calculateTimeRemaining(item.expiryDate);
        const statusClass = getStatusClass(timeRemaining);
        
        return `
            <tr>
                <td>${item.ownerName}</td>
                <td>${item.emailId}</td>
                <td>${item.ssoId}</td>
                <td>${item.objectStored}</td>
                <td>${item.uniqueId}</td>
                <td>${item.location}</td>
                <td>
                    <span class="status-indicator ${statusClass}">
                        ${timeRemaining.display}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-warning" onclick="openExtendModal('${item.id}')">
                            ⏰ Add More Time
                        </button>
                        <button class="btn btn-success" onclick="openPickupModal('${item.id}')">
                            ✅ Mark as Picked Up
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Update archived dashboard
function updateArchivedDashboard() {
    const tbody = document.getElementById('archived-tbody');
    if (!tbody) return;
    
    // Sort by pickup date (most recent first)
    const sortedArchived = [...archivedItems].sort((a, b) => new Date(b.pickupDate) - new Date(a.pickupDate));
    
    if (sortedArchived.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <div class="empty-state">
                        <div class="empty-icon">📋</div>
                        <p>No archived items yet</p>
                        <p class="empty-subtext">Items that are picked up will appear here</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = sortedArchived.map(item => {
        const daysStored = Math.floor((new Date(item.pickupDate) - new Date(item.dateAdded)) / (1000 * 60 * 60 * 24));
        
        return `
            <tr>
                <td>${item.ownerName}</td>
                <td>${item.emailId}</td>
                <td>${item.ssoId}</td>
                <td>${item.objectStored}</td>
                <td>${item.uniqueId}</td>
                <td>${item.location}</td>
                <td>
                    <span class="status-indicator picked-up">
                        ✅ Picked up ${formatDate(item.pickupDate)} (${daysStored}d stored)
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

// Calculate time remaining
function calculateTimeRemaining(expiryDate) {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diff = expiry - now;
    
    if (diff <= 0) {
        return { isExpired: true, text: 'EXPIRED', totalHours: 0, display: '⚠️ EXPIRED' };
    }
    
    const totalHours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(totalHours / 24);
    const hours = totalHours % 24;
    
    if (days > 0) {
        const displayText = `${days}d ${hours}h`;
        return { 
            isExpired: false, 
            text: `${days} day${days !== 1 ? 's' : ''}, ${hours} hour${hours !== 1 ? 's' : ''}`,
            totalHours,
            display: displayText
        };
    } else {
        const displayText = `${hours}h`;
        return { 
            isExpired: false, 
            text: `${hours} hour${hours !== 1 ? 's' : ''}`,
            totalHours,
            display: displayText
        };
    }
}

function getStatusClass(timeRemaining) {
    if (timeRemaining.isExpired) {
        return 'expired';
    } else if (timeRemaining.totalHours <= 24) {
        return 'expiring-soon';
    } else {
        return 'normal';
    }
}

// Update statistics
function updateStats() {
    const totalItems = currentItems.length;
    const expiredItems = currentItems.filter(item => {
        const timeRemaining = calculateTimeRemaining(item.expiryDate);
        return timeRemaining.isExpired;
    }).length;
    const expiringSoonItems = currentItems.filter(item => {
        const timeRemaining = calculateTimeRemaining(item.expiryDate);
        return timeRemaining.totalHours <= 24 && !timeRemaining.isExpired;
    }).length;
    
    const totalEl = document.getElementById('total-items');
    if (totalEl) totalEl.textContent = totalItems;

    // HTML uses different IDs for these stats - guard and set safely
    const expiringSoonEl = document.getElementById('expiring-soon');
    if (expiringSoonEl) expiringSoonEl.textContent = expiringSoonItems;

    const overdueEl = document.getElementById('overdue-items');
    if (overdueEl) overdueEl.textContent = expiredItems;

    // Storage usage/details (optional elements)
    const storageUsageEl = document.getElementById('storage-usage');
    if (storageUsageEl) storageUsageEl.textContent = `${currentItems.length} items`;
    const storageDetailsEl = document.getElementById('storage-details');
    if (storageDetailsEl) storageDetailsEl.textContent = `${currentItems.length} items stored`;

    // Archived count (if present anywhere)
    const archivedCountEl = document.getElementById('archived-count');
    if (archivedCountEl) archivedCountEl.textContent = archivedItems.length;
}

// Update time remaining every minute
function updateTimeRemaining() {
    updateDashboard();
    updateStats();
}

// Extend item storage period
function extendItem(itemId) {
    currentExtendingItemId = itemId;
    const item = currentItems.find(i => i.id === itemId);
    if (!item) return;
    
    document.getElementById('extend-item-name').textContent = item.objectStored;
    document.getElementById('extend-modal').style.display = 'block';
}

// Confirm extension
async function confirmExtension() {
    const additionalDays = parseInt(document.getElementById('extension-days').value);
    if (!additionalDays || additionalDays <= 0) {
        showMessage('Please enter a valid number of days', 'error');
        return;
    }
    
    const item = currentItems.find(i => i.id === currentExtendingItemId);
    if (item) {
        const currentExpiry = new Date(item.expiryDate);
        const newExpiry = new Date(currentExpiry.getTime() + (additionalDays * 24 * 60 * 60 * 1000));
        const newExpiryISO = newExpiry.toISOString();
        
        // Update in database
        const success = await updateItemInDatabase(item.id, { expiryDate: newExpiryISO });
        
        if (success) {
            item.expiryDate = newExpiryISO;
            
            updateDashboard();
            updateStats();
            
            showMessage(`✅ Extended ${item.objectStored} by ${additionalDays} day(s) in database`, 'success');
            
            // Send extension notification email
            sendExtensionNotification(item, additionalDays);
        } else {
            showMessage('❌ Error extending item in database', 'error');
        }
    }
    
    closeExtendModal();
}

// Pickup item
function pickupItem(itemId) {
    currentPickupItemId = itemId;
    const item = currentItems.find(i => i.id === itemId);
    if (!item) return;
    
    document.getElementById('pickup-item-name').textContent = item.objectStored;
    document.getElementById('pickup-modal').style.display = 'block';
}

// Confirm pickup
async function confirmPickup() {
    const itemIndex = currentItems.findIndex(i => i.id === currentPickupItemId);
    if (itemIndex !== -1) {
        const item = currentItems[itemIndex];
        item.pickupDate = new Date().toISOString();
        
        // Archive in database
        const success = await archiveItemInDatabase(item, item.pickupDate);
        
        if (success) {
            // Move to archived items locally
            archivedItems.push(item);
            currentItems.splice(itemIndex, 1);
            
            updateDashboard();
            updateArchivedDashboard();
            updateStats();
            
            showMessage(`✅ ${item.objectStored} marked as picked up and archived in database`, 'success');
            
            // Send pickup confirmation email
            sendPickupNotification(item);
        } else {
            showMessage('❌ Error archiving item in database', 'error');
        }
    }
    
    closePickupModal();
}

// Close modals
function closeExtendModal() {
    document.getElementById('extend-modal').style.display = 'none';
    document.getElementById('extension-days').value = '';
    currentExtendingItemId = null;
}

function closePickupModal() {
    document.getElementById('pickup-modal').style.display = 'none';
    currentPickupItemId = null;
}

// Modal functions for extending time
function openExtendModal(itemId) {
    const item = currentItems.find(i => i.id === itemId);
    if (!item) return;

    currentExtendingItemId = itemId;
    document.getElementById('extend-item-name').textContent = `${item.objectStored} (${item.uniqueId})`;
    document.getElementById('extend-amount').value = '';
    document.getElementById('extend-modal').style.display = 'block';
}

function closeExtendModal() {
    document.getElementById('extend-modal').style.display = 'none';
    currentExtendingItemId = null;
}

function confirmExtension() {
    const amount = parseInt(document.getElementById('extend-amount').value);

    if (!amount || amount <= 0) {
        showMessage('Please enter how much more time you need (must be greater than 0).', 'error');
        return;
    }

    const item = currentItems.find(i => i.id === currentExtendingItemId);
    if (!item) return;

    // Calculate additional time in milliseconds (days only)
    const additionalMs = amount * 24 * 60 * 60 * 1000;

    // Extend the expiry date
    const currentExpiry = new Date(item.expiryDate);
    item.expiryDate = new Date(currentExpiry.getTime() + additionalMs).toISOString();

    // Update time period to reflect the new total (original + extension)
    item.timePeriod = item.timePeriod + amount;

    saveDataToStorage();
    updateDashboard();
    updateStats();
    closeExtendModal();

    showMessage(`Perfect! Storage time extended by ${amount} days. Your item now has ${item.timePeriod} total days!`, 'success');
    
    // Send extension notification
    sendExtensionNotification(item, amount);
}// Modal functions for pickup confirmation
function openPickupModal(itemId) {
    const item = currentItems.find(i => i.id === itemId);
    if (!item) return;
    
    currentPickupItemId = itemId;
    document.getElementById('pickup-item-name').textContent = `${item.objectStored} (${item.uniqueId})`;
    document.getElementById('pickup-modal').style.display = 'block';
}

function closePickupModal() {
    document.getElementById('pickup-modal').style.display = 'none';
    currentPickupItemId = null;
}

function confirmPickup() {
    const item = currentItems.find(i => i.id === currentPickupItemId);
    if (!item) return;
    
    // Add pickup date and move to archived items
    item.pickupDate = new Date().toISOString();
    archivedItems.push(item);
    
    // Remove from current items
    currentItems = currentItems.filter(i => i.id !== currentPickupItemId);
    
    saveDataToStorage();
    updateDashboard();
    updateArchivedDashboard();
    updateStats();
    closePickupModal();
    
    showMessage('Item successfully marked as picked up and moved to history. Thank you!', 'success');
    
    // Send pickup confirmation email
    sendPickupNotification(item);
}

// Calculate storage duration
function calculateStorageDuration(dateAdded, pickedUpDate) {
    const start = new Date(dateAdded);
    const end = new Date(pickedUpDate);
    const diffMs = end - start;
    
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) {
        return `${days} days ${hours}h`;
    } else {
        return `${hours} hours`;
    }
}

// Archived items management functions
function restoreToActive(itemId) {
    const item = archivedItems.find(i => i.id === itemId);
    if (!item) {
        showMessage('❌ Item not found. Please refresh the page and try again.', 'error');
        return;
    }
    
    // Remove pickup date and restore to current items
    delete item.pickedUpDate;
    currentItems.push(item);
    
    // Remove from archived items
    archivedItems = archivedItems.filter(i => i.id !== itemId);
    
    saveDataToStorage();
    updateDashboard();
    updateArchivedDashboard();
    updateStats();
    
    showMessage(`✅ Item "${item.objectStored}" restored to active inventory successfully!`, 'success');
}

function confirmDeleteArchived(itemId) {
    const item = archivedItems.find(i => i.id === itemId);
    if (!item) {
        showMessage('❌ Item not found. Please refresh the page and try again.', 'error');
        return;
    }
    
    // Show confirmation dialog
    const confirmed = confirm(
        `⚠️ Permanently Delete Item?\n\n` +
        `Item: ${item.objectStored}\n` +
        `Tag: ${item.uniqueId}\n` +
        `Owner: ${item.ownerName}\n\n` +
        `This action cannot be undone. Are you sure?`
    );
    
    if (confirmed) {
        // Remove from archived items
        archivedItems = archivedItems.filter(i => i.id !== itemId);
        
        saveDataToStorage();
        updateArchivedDashboard();
        
        showMessage(`🗑️ Item "${item.objectStored}" permanently deleted from records.`, 'success');
    }
}

// Load data from localStorage
// ==================== DATA STORAGE FUNCTIONS ====================

// Load data from SQLite database
async function loadDataFromStorage() {
    try {
        // Load current items
        const itemsResponse = await fetch('/api/items');
        const itemsData = await itemsResponse.json();
        
        if (itemsData.success) {
            currentItems = itemsData.items || [];
            console.log(`✅ Loaded ${currentItems.length} items from database`);
        } else {
            console.error('❌ Error loading items:', itemsData.message);
            currentItems = [];
        }
        
        // Load archived items
        const archivedResponse = await fetch('/api/archived');
        const archivedData = await archivedResponse.json();
        
        if (archivedData.success) {
            archivedItems = archivedData.items || [];
            console.log(`✅ Loaded ${archivedItems.length} archived items from database`);
        } else {
            console.error('❌ Error loading archived items:', archivedData.message);
            archivedItems = [];
        }
        
        // Update UI
        updateDashboard();
        updateArchivedDashboard();
        updateStats();
        
    } catch (error) {
        console.error('❌ Error loading data from database:', error);
        showMessage('⚠️ Could not load data from database. Using local cache.', 'warning');
        // Fallback to localStorage
        loadFromLocalStorage();
    }
}

// Fallback to localStorage if database is unavailable
function loadFromLocalStorage() {
    try {
        const stored = localStorage.getItem('amtc-inventory-data');
        if (stored) {
            const data = JSON.parse(stored);
            currentItems = data.currentItems || [];
            archivedItems = data.archivedItems || [];
        }
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        currentItems = [];
        archivedItems = [];
    }
}

// Save item to database
async function saveItemToDatabase(item) {
    try {
        const response = await fetch('/api/items', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(item)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Item saved to database');
            // Also save to localStorage as backup
            saveToLocalStorageBackup();
            return true;
        } else {
            console.error('❌ Error saving to database:', result.message);
            showMessage(result.message, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Database save error:', error);
        showMessage('⚠️ Could not save to database. Saved locally only.', 'warning');
        saveToLocalStorageBackup();
        return false;
    }
}

// Update item in database
async function updateItemInDatabase(itemId, updates) {
    try {
        const response = await fetch('/api/items/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: itemId, updates: updates })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Item updated in database');
            saveToLocalStorageBackup();
            return true;
        } else {
            console.error('❌ Error updating database:', result.message);
            return false;
        }
    } catch (error) {
        console.error('❌ Database update error:', error);
        return false;
    }
}

// Archive item in database
async function archiveItemInDatabase(item, pickupDate) {
    try {
        const response = await fetch('/api/items/archive', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ item: item, pickupDate: pickupDate })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Item archived in database');
            saveToLocalStorageBackup();
            return true;
        } else {
            console.error('❌ Error archiving in database:', result.message);
            return false;
        }
    } catch (error) {
        console.error('❌ Database archive error:', error);
        return false;
    }
}

// Backup to localStorage
function saveToLocalStorageBackup() {
    try {
        const data = {
            currentItems,
            archivedItems,
            lastUpdated: new Date().toISOString()
        };
        localStorage.setItem('amtc-inventory-data', JSON.stringify(data));
    } catch (error) {
        console.error('Error saving localStorage backup:', error);
    }
}

// Legacy function for compatibility
function saveDataToStorage() {
    saveToLocalStorageBackup();
}

// Update storage usage indicator
function updateStorageUsage() {
    try {
        const currentData = localStorage.getItem('lab-inventory-current') || '[]';
        const archivedData = localStorage.getItem('lab-inventory-archived') || '[]';
        
        // Calculate size in bytes
        const totalBytes = (currentData.length + archivedData.length);
        const totalMB = totalBytes / (1024 * 1024);
        const maxStorageMB = 10; // 10MB typical browser limit
        
        // Calculate percentage used
        const percentageUsed = Math.min((totalMB / maxStorageMB) * 100, 100);
        
        // Update display
        const storageUsageElement = document.getElementById('storage-usage');
        const storageFillElement = document.getElementById('storage-fill');
        const storageDetailsElement = document.getElementById('storage-details');
        
        if (storageUsageElement && storageFillElement && storageDetailsElement) {
            // Format size display
            let displaySize = totalMB < 0.01 ? '<0.01 MB' : `${totalMB.toFixed(2)} MB`;
            
            storageUsageElement.textContent = displaySize;
            storageFillElement.style.width = `${percentageUsed}%`;
            
            // Get the storage usage card element
            const storageCard = document.querySelector('.storage-usage');
            
            // Update bar color based on usage
            storageFillElement.className = 'storage-fill';
            
            // Remove any existing critical class
            if (storageCard) {
                storageCard.classList.remove('critical');
            }
            
            if (percentageUsed > 85) {
                storageFillElement.classList.add('high');
                // Add critical warning styling to the entire card
                if (storageCard) {
                    storageCard.classList.add('critical');
                }
            } else if (percentageUsed > 80) {
                storageFillElement.classList.add('high');
            } else if (percentageUsed > 50) {
                storageFillElement.classList.add('medium');
            }
            
            // Update details with warning message if critical
            const totalItems = JSON.parse(currentData).length + JSON.parse(archivedData).length;
            let detailsText = `${totalItems} items stored (${percentageUsed.toFixed(1)}% of limit)`;
            
            if (percentageUsed > 85) {
                detailsText += ' ⚠️ CRITICAL - Consider exporting data!';
            }
            
            storageDetailsElement.textContent = detailsText;
        }
    } catch (error) {
        console.error('Error updating storage usage:', error);
    }
}

// Show message with auto-hide
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    
    document.body.appendChild(messageEl);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.remove();
        }
    }, 5000);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Excel export functionality
function exportToExcel() {
    if (currentItems.length === 0) {
        showMessage('No items to download. Add some items first!', 'error');
        return;
    }
    
    try {
        // Prepare data for Excel
        const exportData = currentItems.map(item => {
            const timeRemaining = getTimeRemaining(item.expiryDate);
            return {
                'Owner Name': item.ownerName,
                'Email ID': item.emailId,
                'SSO ID': item.ssoId,
                'Object Stored': item.objectStored,
                'Unique ID': item.uniqueId,
                'Location': item.location,
                'Time Period (Days)': item.timePeriod,
                'Date Added': new Date(item.dateAdded).toLocaleDateString(),
                'Expiry Date': new Date(item.expiryDate).toLocaleDateString(),
                'Time Remaining': timeRemaining.display
            };
        });
        
        // Create workbook and worksheet
        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Current Inventory');
        
        // Generate filename with current date
        const filename = `AME_Lab_Inventory_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Save file
        XLSX.writeFile(wb, filename);
        
        showMessage('Report downloaded successfully! Check your Downloads folder.', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showMessage('Sorry, there was a problem downloading the report. Please try again.', 'error');
    }
}

function exportArchivedToExcel() {
    if (archivedItems.length === 0) {
        showMessage('No pickup history to download yet.', 'error');
        return;
    }
    
    try {
        // Prepare data for Excel
        const exportData = archivedItems.map(item => {
            const storageDuration = calculateStorageDuration(item.dateAdded, item.pickedUpDate);
            return {
                'Owner Name': item.ownerName,
                'Email ID': item.emailId,
                'SSO ID': item.ssoId,
                'Object Stored': item.objectStored,
                'Unique ID': item.uniqueId,
                'Location': item.location,
                'Original Time Period (Days)': item.timePeriod,
                'Date Added': new Date(item.dateAdded).toLocaleDateString(),
                'Picked Up Date': new Date(item.pickedUpDate).toLocaleDateString(),
                'Storage Duration': storageDuration
            };
        });
        
        // Create workbook and worksheet
        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Archived Items');
        
        // Generate filename with current date
        const filename = `AME_Lab_Archived_Items_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Save file
        XLSX.writeFile(wb, filename);
        
        showMessage('Pickup history downloaded successfully! Check your Downloads folder.', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showMessage('Sorry, there was a problem downloading the history. Please try again.', 'error');
    }
}

// Excel import functionality
function importFromExcel(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check if XLSX library is loaded
    if (typeof XLSX === 'undefined') {
        showMessage('Excel processing library not loaded. Please refresh the page and try again.', 'error');
        console.error('XLSX library is not available');
        return;
    }
    
    // Check file type
    const fileExtension = file.name.toLowerCase().split('.').pop();
    if (!['xlsx', 'xls'].includes(fileExtension)) {
        showMessage('Please upload only Excel files (.xlsx or .xls)', 'error');
        return;
    }
    
    console.log(`Processing file: ${file.name} (${file.size} bytes)`);
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            console.log('File read successfully, parsing Excel data...');
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            
            // Get the first worksheet
            const worksheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[worksheetName];
            
            // Convert to JSON
            const jsonData = XLSX.utils.sheet_to_json(worksheet);
            
            if (jsonData.length === 0) {
                showMessage('The uploaded file appears to be empty. Please check your file.', 'error');
                return;
            }
            
            let importedCount = 0;
            let skippedCount = 0;
            
            jsonData.forEach(row => {
                // Map Excel columns to our data structure
                const item = {
                    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
                    ownerName: row['Owner Name'] || '',
                    emailId: row['Email ID'] || '',
                    ssoId: row['SSO ID'] || '',
                    objectStored: row['Object Stored'] || '',
                    uniqueId: row['Unique ID'] || '',
                    location: row['Location'] || '',
                    timePeriod: parseInt(row['Time Period (Days)']) || 1,
                    dateAdded: new Date().toISOString(),
                    expiryDate: new Date(Date.now() + ((parseInt(row['Time Period (Days)']) || 1) * 24 * 60 * 60 * 1000)).toISOString()
                };
                
                // Validate required fields
                if (item.ownerName && item.emailId && item.ssoId && item.objectStored && item.uniqueId && item.location) {
                    // Check if unique ID already exists
                    if (!currentItems.find(existingItem => existingItem.uniqueId === item.uniqueId)) {
                        currentItems.push(item);
                        importedCount++;
                    } else {
                        skippedCount++;
                    }
                } else {
                    skippedCount++;
                }
            });
            
            saveDataToStorage();
            updateDashboard();
            updateStats();
            
            let message = `Successfully added ${importedCount} items to storage.`;
            if (skippedCount > 0) {
                message += ` ${skippedCount} items were skipped (missing information or duplicate tags).`;
            }
            
            showMessage(message, importedCount > 0 ? 'success' : 'error');
        } catch (error) {
            console.error('Import error:', error);
            let errorMessage = 'Sorry, there was a problem reading your file. ';
            
            if (error.message && error.message.includes('Unsupported file')) {
                errorMessage += 'The file format is not supported. Please ensure you\'re uploading a valid Excel file (.xlsx or .xls).';
            } else if (error.message && error.message.includes('Invalid')) {
                errorMessage += 'The file appears to be corrupted or invalid. Please try exporting your data to a new Excel file.';
            } else {
                errorMessage += 'Please check the file format and try again. Make sure it\'s a valid Excel file with data.';
            }
            
            showMessage(errorMessage, 'error');
            console.error('Detailed error:', error.message, error.stack);
        }
    };
    
    reader.readAsArrayBuffer(file);
    
    // Reset file input
    event.target.value = '';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const extendModal = document.getElementById('extend-modal');
    const pickupModal = document.getElementById('pickup-modal');
    
    if (event.target === extendModal) {
        closeExtendModal();
    }
    if (event.target === pickupModal) {
        closePickupModal();
    }
};

// Handle keyboard events for modals
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeExtendModal();
        closePickupModal();
    }
});

// Email notification functions
async function sendEmailNotification(item) {
    try {
        const response = await fetch('http://localhost:8000/send-notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'storage',
                item: item
            })
        });
        
        if (response.ok) {
            console.log('📧 Storage notification sent successfully');
        } else {
            console.log('📧 Email notification failed, but item was stored successfully');
        }
    } catch (error) {
        console.log('📧 Email service unavailable, but item was stored successfully');
    }
}

async function sendExtensionNotification(item, additionalDays) {
    try {
        const response = await fetch('http://localhost:8000/send-notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'extension',
                item: item,
                additionalDays: additionalDays
            })
        });
        
        if (response.ok) {
            console.log('📧 Extension notification sent successfully');
        }
    } catch (error) {
        console.log('📧 Email service unavailable for extension notification');
    }
}

async function sendPickupNotification(item) {
    try {
        const response = await fetch('http://localhost:8000/send-notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'pickup',
                item: item
            })
        });
        
        if (response.ok) {
            console.log('� Pickup notification sent successfully');
        }
    } catch (error) {
        console.log('📧 Email service unavailable for pickup notification');
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const extendModal = document.getElementById('extend-modal');
    const pickupModal = document.getElementById('pickup-modal');
    
    if (event.target === extendModal) {
        closeExtendModal();
    }
    if (event.target === pickupModal) {
        closePickupModal();
    }
};