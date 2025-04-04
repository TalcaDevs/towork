document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const filterInput = document.getElementById('filter-input');
    
    if (searchInput && filterInput) {
        const cards = document.querySelectorAll('.card');
        
        function filterCards() {
            const searchTerm = searchInput.value.toLowerCase();
            const filterTerm = filterInput.value.toLowerCase();
            
            cards.forEach(card => {
                const userName = card.querySelector('.user-name').textContent.toLowerCase();
                const educationTitle = card.querySelector('.education-title') ? 
                                      card.querySelector('.education-title').textContent.toLowerCase() : '';
                const userLocation = card.dataset.location ? card.dataset.location.toLowerCase() : '';
                
                const matchesSearch = userName.includes(searchTerm) || educationTitle.includes(searchTerm);
                const matchesFilter = filterTerm === '' || userLocation.includes(filterTerm);
                
                if (matchesSearch && matchesFilter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        searchInput.addEventListener('input', filterCards);
        filterInput.addEventListener('input', filterCards);
    }
});