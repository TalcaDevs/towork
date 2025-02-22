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
