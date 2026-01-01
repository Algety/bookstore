document.addEventListener('DOMContentLoaded', function() {
    // Add a small delay to ensure DOM is fully loaded
    setTimeout(function() {
        console.log('Custom changelist script loaded');
        
        // Only add save button if we have list_editable fields (changelist form exists)
        const changelistForm = document.getElementById('changelist-form');
        if (!changelistForm) {
            console.log('No changelist form found - no editable fields on this page');
            return;
        }
        
        console.log('Changelist form found:', changelistForm);
        
        // Find the actions row - try multiple selectors
        let actionsRow = document.querySelector('div.actions');
        if (!actionsRow) {
            actionsRow = document.querySelector('.actions');
        }
        
        if (!actionsRow) {
            console.log('No actions row found');
            return;
        }
        
        console.log('Actions row found:', actionsRow);
        
        // Check if button already exists to avoid duplicates
        if (document.querySelector('.top-save-button')) {
            console.log('Save button already exists');
            return;
        }
        
        // Create and add the top save button
        const saveButton = document.createElement('input');
        saveButton.type = 'submit';
        saveButton.name = '_save';
        saveButton.value = 'Save';
        saveButton.className = 'top-save-button default';
        saveButton.form = 'changelist-form';
        
        // Add the button to the actions row
        actionsRow.appendChild(saveButton);
        console.log('Save button added successfully:', saveButton);
        
        // Also make the table scrollable
        const resultsTable = document.querySelector('.results');
        if (resultsTable) {
            resultsTable.style.maxHeight = '600px';
            resultsTable.style.overflowY = 'auto';
            console.log('Table made scrollable');
        }
    }, 500); // Increased delay
});