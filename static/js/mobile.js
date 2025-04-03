document.addEventListener('DOMContentLoaded', function() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        document.body.classList.add('mobile-view');
        
        const menuButtons = document.querySelectorAll('.stats-button');
        menuButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                menuButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 500);
            });
        });
        
        const urlParams = new URLSearchParams(window.location.search);
        const currentState = urlParams.get('estado') || 'pendientes';
        
        const activeButton = document.querySelector(`.stats-button[href*="estado=${currentState}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        const cardContainer = document.getElementById('card-container');
        if (cardContainer) {
            window.addEventListener('scroll', function() {
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
                }
            });
        }
        
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', function() {
                this.classList.remove('touch-active');
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
        
        enhanceDetailView();
    }
    
    window.addEventListener('resize', function() {
        const wasDesktop = !document.body.classList.contains('mobile-view');
        const isMobileNow = window.innerWidth <= 768;
        
        if (wasDesktop && isMobileNow) {
            document.body.classList.add('mobile-view');
            enhanceMobileExperience();
        } else if (!wasDesktop && !isMobileNow) {
            document.body.classList.remove('mobile-view');
            revertMobileExperience();
        }
    });
    
    function enhanceDetailView() {
        const detailContainer = document.querySelector('.detail-container');
        if (detailContainer) {
            detailContainer.style.flexDirection = 'column';
            detailContainer.style.height = 'auto';
            
            document.querySelectorAll('.tab-button').forEach(tab => {
                tab.addEventListener('click', function() {
                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple');
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        ripple.remove();
                    }, 500);
                    
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
        document.querySelectorAll('.sidebar-logo, .stats-title, .user-profile, .countdown-container').forEach(el => {
            if (el) el.style.display = 'none';
        });
        
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.height = '56px';
        
        const navbarTitle = document.querySelector('.navbar-title');
        if (navbarTitle) navbarTitle.style.fontSize = '16px';
        
        const navbarSearch = document.querySelector('.navbar-search');
        if (navbarSearch) navbarSearch.style.display = 'none';
        
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer) paginationContainer.style.margin = '15px 0 80px 0';
        
        const urlParams = new URLSearchParams(window.location.search);
        const currentState = urlParams.get('estado') || 'pendientes';
        
        const activeButton = document.querySelector(`.stats-button[href*="estado=${currentState}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        improveTouch();
    }
    
    function revertMobileExperience() {
        document.querySelectorAll('.sidebar-logo, .stats-title, .user-profile, .countdown-container').forEach(el => {
            if (el) el.style.display = '';
        });
        
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.height = '';
        
        const navbarTitle = document.querySelector('.navbar-title');
        if (navbarTitle) navbarTitle.style.fontSize = '';
        
        const navbarSearch = document.querySelector('.navbar-search');
        if (navbarSearch) navbarSearch.style.display = '';
        
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer) paginationContainer.style.margin = '';
    }
    
    function improveTouch() {
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

document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
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
