document.addEventListener('DOMContentLoaded', function() {
    // Add a small delay to ensure DOM is fully loaded
    setTimeout(function() {
        console.log('Looking for changelist form...');
        
        // Only add save button if we have list_editable fields (changelist form exists)
        const changelistForm = document.getElementById('changelist-form');
        if (!changelistForm) {
            console.log('No changelist form found - no editable fields on this page');
            return;
        }
        
        console.log('Changelist form found, looking for actions row...');
        
        // Find the actions row
        const actionsRow = document.querySelector('.actions');
        if (!actionsRow) {
            console.log('No actions row found');
            return;
        }
        
        console.log('Actions row found, creating save button...');
        
        // Check if button already exists to avoid duplicates
        if (document.querySelector('.top-save-button')) {
            console.log('Save button already exists');
            return;
        }
        
        // Create and add the top save button
        const saveButton = document.createElement('button');
        saveButton.type = 'submit';
        saveButton.name = '_save';
        saveButton.form = 'changelist-form';
        saveButton.className = 'top-save-button';
        saveButton.textContent = 'Save';
        
        // Add the button to the actions row
        actionsRow.appendChild(saveButton);
        console.log('Save button added successfully');
    }, 100);
});