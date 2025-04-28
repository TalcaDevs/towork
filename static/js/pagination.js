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
    
    function checkPaginationVisibility() {
        const paginationContainer = document.querySelector('.pagination-container');
        if (!paginationContainer) return;
        
        const rect = paginationContainer.getBoundingClientRect();
        const isVisible = (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (!isVisible) {
            const cardContainer = document.getElementById('card-container');
            if (cardContainer) {
                cardContainer.style.paddingBottom = '70px';
            }
            
            const components = document.querySelector('.components');
            if (components) {
                components.style.paddingBottom = '80px';
            }
            
            paginationContainer.style.marginBottom = '70px';
        }
    }
    
    checkPaginationVisibility();
    
    window.addEventListener('resize', checkPaginationVisibility);
});