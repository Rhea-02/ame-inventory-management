// Global variables
let currentItems = [];
let archivedItems = [];
let currentExtendingItemId = null;
let currentPickupItemId = null;

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
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
function handleFormSubmit(event) {
    event.preventDefault();
    
    // Add loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '🔄 Storing Item...';
    submitBtn.disabled = true;
    
    // Simulate processing time for better UX
    setTimeout(() => {
        const formData = new FormData(event.target);
        const item = {
            id: Date.now().toString(), // Simple ID generation
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
            
            // Reset button
            submitBtn.classList.remove('loading');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            return;
        }
        
        // Add item to current items
        currentItems.push(item);
        saveDataToStorage();
        
        // Reset form
        event.target.reset();
        
        // Show success message
        showMessage('Great! Your item has been registered for storage successfully!', 'success');
        
        // Switch to dashboard
        showTab('dashboard');
        document.querySelector('.nav-btn[onclick="showTab(\'dashboard\')"]').classList.add('active');
        document.querySelector('.nav-btn[onclick="showTab(\'add-item\')"]').classList.remove('active');
        
        // Reset button
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }, 800); // Small delay for better UX
}

// Update dashboard display
function updateDashboard() {
    const tbody = document.getElementById('inventory-tbody');
    const noItemsDiv = document.getElementById('no-items');
    
    if (currentItems.length === 0) {
        tbody.innerHTML = '';
        noItemsDiv.style.display = 'block';
        return;
    }
    
    noItemsDiv.style.display = 'none';
    
    tbody.innerHTML = currentItems.map(item => {
        const timeRemaining = getTimeRemaining(item.expiryDate);
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
                            ✅ I Picked This Up
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
    const noArchivedDiv = document.getElementById('no-archived');
    
    if (archivedItems.length === 0) {
        tbody.innerHTML = '';
        noArchivedDiv.style.display = 'block';
        return;
    }
    
    noArchivedDiv.style.display = 'none';
    
    tbody.innerHTML = archivedItems.map(item => {
        const storageDuration = calculateStorageDuration(item.dateAdded, item.pickedUpDate);
        
        return `
            <tr>
                <td>${item.ownerName}</td>
                <td>${item.emailId}</td>
                <td>${item.ssoId}</td>
                <td>${item.objectStored}</td>
                <td>${item.uniqueId}</td>
                <td>${item.location}</td>
                <td>${storageDuration}</td>
                <td>${new Date(item.pickedUpDate).toLocaleDateString()}</td>
            </tr>
        `;
    }).join('');
}

// Calculate time remaining
function getTimeRemaining(expiryDate) {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diffMs = expiry - now;
    
    if (diffMs <= 0) {
        return {
            days: 0,
            hours: 0,
            display: 'Time Expired',
            status: 'overdue'
        };
    }
    
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    let display;
    let status;
    
    if (days > 2) {
        display = `${days} days left`;
        status = 'normal';
    } else if (days > 0) {
        display = `${days} days ${hours}h left`;
        status = 'expiring';
    } else {
        display = `${hours} hours left`;
        status = 'expiring';
    }
    
    return { days, hours, display, status };
}

// Get status class for styling
function getStatusClass(timeRemaining) {
    switch (timeRemaining.status) {
        case 'overdue':
            return 'status-overdue';
        case 'expiring':
            return 'status-expiring';
        default:
            return 'status-normal';
    }
}

// Update statistics
function updateStats() {
    const totalItems = currentItems.length;
    const expiringSoon = currentItems.filter(item => {
        const timeRemaining = getTimeRemaining(item.expiryDate);
        return timeRemaining.days <= 2 && timeRemaining.days >= 0;
    }).length;
    const overdueItems = currentItems.filter(item => {
        const timeRemaining = getTimeRemaining(item.expiryDate);
        return timeRemaining.status === 'overdue';
    }).length;
    
    document.getElementById('total-items').textContent = totalItems;
    document.getElementById('expiring-soon').textContent = expiringSoon;
    document.getElementById('overdue-items').textContent = overdueItems;
}

// Update time remaining every minute
function updateTimeRemaining() {
    updateDashboard();
    updateStats();
}

// Modal functions for extending time
function openExtendModal(itemId) {
    const item = currentItems.find(i => i.id === itemId);
    if (!item) return;
    
    currentExtendingItemId = itemId;
    document.getElementById('extend-item-name').textContent = `${item.objectStored} (${item.uniqueId})`;
    document.getElementById('extend-amount').value = '';
    document.getElementById('extend-unit').value = 'days';
    document.getElementById('extend-modal').style.display = 'block';
}

function closeExtendModal() {
    document.getElementById('extend-modal').style.display = 'none';
    currentExtendingItemId = null;
}

function confirmExtension() {
    const amount = parseInt(document.getElementById('extend-amount').value);
    const unit = document.getElementById('extend-unit').value;
    
    if (!amount || amount <= 0) {
        showMessage('Please enter how much more time you need (must be greater than 0).', 'error');
        return;
    }
    
    const item = currentItems.find(i => i.id === currentExtendingItemId);
    if (!item) return;
    
    // Calculate additional time in milliseconds
    const additionalMs = unit === 'days' ? 
        amount * 24 * 60 * 60 * 1000 : 
        amount * 60 * 60 * 1000;
    
    // Extend the expiry date
    const currentExpiry = new Date(item.expiryDate);
    item.expiryDate = new Date(currentExpiry.getTime() + additionalMs).toISOString();
    
    // Update original time period for record keeping
    const originalDays = Math.floor((new Date(item.expiryDate) - new Date(item.dateAdded)) / (1000 * 60 * 60 * 24));
    item.timePeriod = originalDays;
    
    saveDataToStorage();
    updateDashboard();
    updateStats();
    closeExtendModal();
    
    showMessage(`Perfect! Storage time extended by ${amount} ${unit}. Your item now has more time!`, 'success');
}

// Modal functions for pickup confirmation
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
    item.pickedUpDate = new Date().toISOString();
    archivedItems.push(item);
    
    // Remove from current items
    currentItems = currentItems.filter(i => i.id !== currentPickupItemId);
    
    saveDataToStorage();
    updateDashboard();
    updateStats();
    closePickupModal();
    
    showMessage('Item successfully marked as picked up and moved to history. Thank you!', 'success');
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

// Local storage functions
function saveDataToStorage() {
    localStorage.setItem('lab-inventory-current', JSON.stringify(currentItems));
    localStorage.setItem('lab-inventory-archived', JSON.stringify(archivedItems));
}

function loadDataFromStorage() {
    const currentData = localStorage.getItem('lab-inventory-current');
    const archivedData = localStorage.getItem('lab-inventory-archived');
    
    if (currentData) {
        currentItems = JSON.parse(currentData);
    }
    
    if (archivedData) {
        archivedItems = JSON.parse(archivedData);
    }
}

// Show success/error messages
function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
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
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
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
            showMessage('Sorry, there was a problem reading your file. Please check the file format and try again.', 'error');
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