document.addEventListener('DOMContentLoaded', function() {
    function updatePaginationLinks() {
        const searchParams = new URLSearchParams(window.location.search);
        const searchValue = document.getElementById('search-filter-input')?.value || '';
        const filterValue = document.getElementById('filter-input')?.value || '';
        
        const estado = searchParams.get('estado') || 'pendientes';
        
        document.querySelectorAll('.pagination a').forEach(link => {
            const linkParams = new URLSearchParams(link.search);
            linkParams.set('estado', estado);
            
            if (searchValue) {
                linkParams.set('search', searchValue);
            }
            
            if (filterValue) {
                linkParams.set('filter', filterValue);
            }
            
            link.search = linkParams.toString();
        });
    }
    
    updatePaginationLinks();
    
    document.getElementById('search-filter-input')?.addEventListener('input', function() {
        clearTimeout(this.timer);
        this.timer = setTimeout(updatePaginationLinks, 300);
    });
    
    document.getElementById('filter-input')?.addEventListener('input', function() {
        clearTimeout(this.timer);
        this.timer = setTimeout(updatePaginationLinks, 300);
    });
    
    const activePage = document.querySelector('.pagination .active');
    if (activePage) {
        activePage.classList.add('highlighted');
        setTimeout(() => {
            activePage.classList.remove('highlighted');
        }, 1000);
    }
});