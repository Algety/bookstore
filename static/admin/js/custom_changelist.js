document.addEventListener('DOMContentLoaded', function() {
    // Only add save button if we have list_editable fields (changelist form exists)
    const changelistForm = document.getElementById('changelist-form');
    if (!changelistForm) return;
    
    // Find the actions row
    const actionsRow = document.querySelector('.actions');
    if (!actionsRow) return;
    
    // Create and add the top save button
    const saveButton = document.createElement('button');
    saveButton.type = 'submit';
    saveButton.name = '_save';
    saveButton.form = 'changelist-form';
    saveButton.className = 'top-save-button';
    saveButton.textContent = 'Save';
    
    // Add the button to the actions row
    actionsRow.appendChild(saveButton);
});