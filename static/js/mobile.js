// mobile.js - Comportamiento específico para dispositivos móviles
document.addEventListener('DOMContentLoaded', function() {
    // Detecta si es un dispositivo móvil basado en el ancho de pantalla
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Agrega clase para identificar que estamos en mobile
        document.body.classList.add('mobile-view');
        
        // Maneja el cambio entre las diferentes vistas (pendientes, aprobados, rechazados)
        const menuButtons = document.querySelectorAll('.stats-button');
        menuButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                menuButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Efecto visual al hacer clic
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 500);
            });
        });
        
        // Detecta qué botón debe estar activo según la URL actual
        const urlParams = new URLSearchParams(window.location.search);
        const currentState = urlParams.get('estado') || 'pendientes';
        
        const activeButton = document.querySelector(`.stats-button[href*="estado=${currentState}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Gestiona el scroll infinito en dispositivos móviles (opcional)
        const cardContainer = document.getElementById('card-container');
        if (cardContainer) {
            // Esta función cargaría más tarjetas al llegar al final del scroll
            // Requiere implementación adicional en el backend para funcionar correctamente
            window.addEventListener('scroll', function() {
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
                    // Cuando el usuario esté cerca del final, se podría cargar más contenido
                    // console.log('Cargando más tarjetas...');
                }
            });
        }
        
        // Mejora la experiencia táctil en las tarjetas
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            // Agrega efecto de presión
            card.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', function() {
                this.classList.remove('touch-active');
                // Pequeño retraso para que se vea el efecto visual
                setTimeout(() => {
                    const detailLink = this.querySelector('.detail-link');
                    if (detailLink) {
                        detailLink.click();
                    }
                }, 100);
            });
            
            card.addEventListener('touchmove', function() {
                this.classList.remove('touch-active');
            });
        });
        
        // Mejora la experiencia en la vista de detalle para móviles
        enhanceDetailView();
    }
    
    // Gestiona el cambio de orientación del dispositivo
    window.addEventListener('resize', function() {
        const wasDesktop = !document.body.classList.contains('mobile-view');
        const isMobileNow = window.innerWidth <= 768;
        
        // Si cambia de escritorio a móvil o viceversa, aplicamos los cambios necesarios
        if (wasDesktop && isMobileNow) {
            document.body.classList.add('mobile-view');
            // Ajustar elementos dinámicamente
            enhanceMobileExperience();
        } else if (!wasDesktop && !isMobileNow) {
            document.body.classList.remove('mobile-view');
            // Revertir ajustes móviles
            revertMobileExperience();
        }
    });
    
    function enhanceDetailView() {
        // Si estamos en la vista de detalle
        const detailContainer = document.querySelector('.detail-container');
        if (detailContainer) {
            // Ajustamos para versión móvil
            detailContainer.style.flexDirection = 'column';
            detailContainer.style.height = 'auto';
            
            // Mejoramos navegación entre tabs
            document.querySelectorAll('.tab-button').forEach(tab => {
                tab.addEventListener('click', function() {
                    // Añade efecto de ripple al hacer clic
                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple');
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 500);
                    
                    // Scroll al contenido del tab
                    const tabId = this.getAttribute('data-tab');
                    const tabContent = document.getElementById(tabId);
                    if (tabContent) {
                        setTimeout(() => {
                            const tabsHeight = document.querySelector('.detail-tabs').offsetHeight;
                            const offsetTop = tabContent.offsetTop;
                            window.scrollTo({
                                top: offsetTop - tabsHeight - 20,
                                behavior: 'smooth'
                            });
                        }, 100);
                    }
                });
            });
        }
    }
    
    function enhanceMobileExperience() {
        // Aplicamos mejoras para móvil sin recargar la página
        console.log('Aplicando mejoras para experiencia móvil');
        
        // Ocultamos elementos que no necesitamos en móvil
        document.querySelectorAll('.sidebar-logo, .stats-title, .user-profile, .countdown-container').forEach(el => {
            if (el) el.style.display = 'none';
        });
        
        // Ajustamos la barra de navegación
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.height = '56px';
        
        // Ajustamos el tamaño del título
        const navbarTitle = document.querySelector('.navbar-title');
        if (navbarTitle) navbarTitle.style.fontSize = '16px';
        
        // Ocultamos la búsqueda en móvil
        const navbarSearch = document.querySelector('.navbar-search');
        if (navbarSearch) navbarSearch.style.display = 'none';
        
        // Reorganizamos la paginación
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer) paginationContainer.style.margin = '15px 0 80px 0';
        
        // Seleccionamos el botón activo del menú
        const urlParams = new URLSearchParams(window.location.search);
        const currentState = urlParams.get('estado') || 'pendientes';
        
        const activeButton = document.querySelector(`.stats-button[href*="estado=${currentState}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Mejoramos la experiencia táctil
        improveTouch();
    }
    
    function revertMobileExperience() {
        // Reversión de los cambios hechos para móvil
        console.log('Reversión de mejoras móviles para escritorio');
        
        // Restauramos elementos ocultos
        document.querySelectorAll('.sidebar-logo, .stats-title, .user-profile, .countdown-container').forEach(el => {
            if (el) el.style.display = '';
        });
        
        // Restauramos la barra de navegación
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.height = '';
        
        // Restauramos el tamaño del título
        const navbarTitle = document.querySelector('.navbar-title');
        if (navbarTitle) navbarTitle.style.fontSize = '';
        
        // Mostramos la búsqueda nuevamente
        const navbarSearch = document.querySelector('.navbar-search');
        if (navbarSearch) navbarSearch.style.display = '';
        
        // Restauramos la paginación
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer) paginationContainer.style.margin = '';
    }
    
    function improveTouch() {
        // Mejora la experiencia táctil en dispositivos móviles
        
        // Agrega efecto de ripple a botones
        document.querySelectorAll('button, .stats-button, .tab-button, .card').forEach(el => {
            if (!el.classList.contains('touch-enhanced')) {
                el.classList.add('touch-enhanced');
                
                el.addEventListener('touchstart', function(e) {
                    this.classList.add('touch-active');
                });
                
                el.addEventListener('touchend', function(e) {
                    this.classList.remove('touch-active');
                });
                
                el.addEventListener('touchmove', function(e) {
                    this.classList.remove('touch-active');
                });
            }
        });
    }
});

// Estilos adicionales para la experiencia móvil
document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
        // Agregar estilos dinámicos que sean difíciles de poner en el CSS
        const style = document.createElement('style');
        style.textContent = `
            .touch-active {
                transform: scale(0.97) !important;
                opacity: 0.9;
                transition: transform 0.1s ease, opacity 0.1s ease;
            }
            
            .ripple {
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                width: 100px;
                height: 100px;
                transform: scale(0);
                animation: ripple 0.5s linear;
                pointer-events: none;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            
            .stats-button.active {
                color: var(--color-primary);
            }
            
            .stats-button.active .stats-icon {
                transform: translateY(-5px);
            }
            
            .stats-button.pending.active .stats-icon {
                color: #ff8049;
            }
            
            .stats-button.approved.active .stats-icon {
                color: #378b74;
            }
            
            .stats-button.rejected.active .stats-icon {
                color: #dc3545;
            }
        `;
        document.head.appendChild(style);
    }
});