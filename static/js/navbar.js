document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-filter-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {
                const nameElement = card.querySelector('.user-name');
                const educationElement = card.querySelector('.education-title');
                
                const name = nameElement ? nameElement.textContent.toLowerCase() : '';
                const education = educationElement ? educationElement.textContent.toLowerCase() : '';
                
                if (name.includes(searchTerm) || education.includes(searchTerm)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
            
            const cardContainer = document.getElementById('card-container');
            const emptyState = document.querySelector('.empty-state') || 
                               (function() {
                                   const div = document.createElement('div');
                                   div.className = 'empty-state';
                                   div.innerHTML = '<p>No se encontraron resultados para tu búsqueda</p>';
                                   return div;
                               })();
            
            const visibleCards = Array.from(cards).filter(card => card.style.display !== 'none');
            
            if (visibleCards.length === 0 && searchTerm) {
                if (!document.querySelector('.empty-state')) {
                    cardContainer.appendChild(emptyState);
                }
            } else if (document.querySelector('.empty-state')) {
                document.querySelector('.empty-state').remove();
            }
        });
    }
});