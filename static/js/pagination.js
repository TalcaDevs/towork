// Este script debe añadirse al final de la página o en un archivo separado
document.addEventListener('DOMContentLoaded', function() {
    // Función para preservar los parámetros de búsqueda y filtrado al cambiar de página
    function updatePaginationLinks() {
        const searchParams = new URLSearchParams(window.location.search);
        const searchValue = document.getElementById('search-filter-input')?.value || '';
        const filterValue = document.getElementById('filter-input')?.value || '';
        
        // Obtener estado actual
        const estado = searchParams.get('estado') || 'pendientes';
        
        // Actualizar todos los enlaces de paginación
        document.querySelectorAll('.pagination a').forEach(link => {
            const linkParams = new URLSearchParams(link.search);
            linkParams.set('estado', estado);
            
            // Agregar parámetros de búsqueda y filtro si tienen valor
            if (searchValue) {
                linkParams.set('search', searchValue);
            }
            
            if (filterValue) {
                linkParams.set('filter', filterValue);
            }
            
            // Actualizar la URL del enlace
            link.search = linkParams.toString();
        });
    }
    
    // Inicializar la función al cargar la página
    updatePaginationLinks();
    
    // Volver a aplicar cuando cambian los valores de búsqueda o filtrado
    document.getElementById('search-filter-input')?.addEventListener('input', function() {
        // Esperar un poco para no actualizar constantemente
        clearTimeout(this.timer);
        this.timer = setTimeout(updatePaginationLinks, 300);
    });
    
    document.getElementById('filter-input')?.addEventListener('input', function() {
        clearTimeout(this.timer);
        this.timer = setTimeout(updatePaginationLinks, 300);
    });
    
    // Efecto visual para la paginación activa
    const activePage = document.querySelector('.pagination .active');
    if (activePage) {
        activePage.classList.add('highlighted');
        setTimeout(() => {
            activePage.classList.remove('highlighted');
        }, 1000);
    }
});