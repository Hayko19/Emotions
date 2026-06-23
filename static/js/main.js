// ===== Bloom & Petal — Main JavaScript =====

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initScrollAnimations();
    initHeroParticles();
    initAlertDismiss();
    initAddToCartAjax();
});

// --- Navbar scroll effect & mobile toggle ---
function initNavbar() {
    const header = document.querySelector('.main-header') || document.getElementById('navbar');
    const navbar = document.getElementById('navbar');
    const toggle = document.getElementById('menuToggle');
    const links = document.getElementById('navLinks');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('open');
            toggle.classList.toggle('active');
        });

        // Close menu on link click
        links.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                links.classList.remove('open');
                toggle.classList.remove('active');
            });
        });
    }
}

// --- Scroll animations (Intersection Observer) ---
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');

    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    elements.forEach(el => observer.observe(el));
}

// --- Floating petal particles in hero ---
function initHeroParticles() {
    const container = document.getElementById('heroParticles');
    if (!container) return;

    const colors = ['#c8956c', '#7a9e7e', '#d4a855', '#c27a7a', '#dbb08e'];

    for (let i = 0; i < 15; i++) {
        const petal = document.createElement('div');
        petal.className = 'petal';
        petal.style.left = Math.random() * 100 + '%';
        petal.style.width = (8 + Math.random() * 12) + 'px';
        petal.style.height = petal.style.width;
        petal.style.background = colors[Math.floor(Math.random() * colors.length)];
        petal.style.animationDuration = (8 + Math.random() * 12) + 's';
        petal.style.animationDelay = (Math.random() * 10) + 's';
        container.appendChild(petal);
    }
}

// --- Auto-dismiss alerts ---
function initAlertDismiss() {
    document.querySelectorAll('[data-auto-dismiss]').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = '0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
}

// --- AJAX add to cart ---
function initAddToCartAjax() {
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Only intercept on non-cart pages for smooth UX
            if (window.location.pathname.includes('/cart')) return;

            e.preventDefault();

            const btn = form.querySelector('button[type="submit"]');
            const originalContent = btn.innerHTML;
            btn.innerHTML = '✓';
            btn.style.background = '#5cb85c';
            btn.style.borderColor = '#5cb85c';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Update badge
                    let badge = document.getElementById('cartBadge');
                    if (!badge) {
                        const cartLink = document.querySelector('.cart-link');
                        if (cartLink) {
                            badge = document.createElement('span');
                            badge.className = 'cart-badge';
                            badge.id = 'cartBadge';
                            cartLink.appendChild(badge);
                        }
                    }
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.style.animation = 'none';
                        badge.offsetHeight; // trigger reflow
                        badge.style.animation = 'badgePop 0.3s ease';
                    }

                    // UBA Tracking
                    if (window.UBA) {
                        const productName = form.closest('.product-card')?.querySelector('.product-title')?.innerText 
                                        || document.querySelector('.product-name')?.innerText 
                                        || 'Товар';
                        const productPrice = form.querySelector('input[name="price"]')?.value || 0;
                        window.UBA.addToCart(form.action.split('/').filter(Boolean).pop(), productName, productPrice);
                    }
                }

                setTimeout(() => {
                    btn.innerHTML = originalContent;
                    btn.style.background = '';
                    btn.style.borderColor = '';
                }, 1200);
            })
            .catch(() => {
                // Fallback: submit form normally
                form.submit();
            });
        });
    });
}
