function showSection(sectionId) {
    const sections = document.querySelectorAll('.detail-content');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
}

function showPopup() {
    document.getElementById('popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function hidePopup() {
    document.getElementById('popup').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function showDeleteConfirmation() {
    document.getElementById('delete-confirmation').style.display = 'block';
    document.body.style.overflow = 'hidden';
}
    
function hideDeleteConfirmation() {
    document.getElementById('delete-confirmation').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    document.querySelector(`.tab-button[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            switchTab(this.getAttribute('data-tab'));
        });
    });
});