/* ===================================================
   MAIN.JS — Global JavaScript for Luxury Curtains
   =================================================== */

document.addEventListener('DOMContentLoaded', function () {

    /* ---------- Navbar Scroll Effect ---------- */
    const navbar = document.querySelector('.navbar-luxury');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll(); // initial check
    }

    /* ---------- Scroll Reveal Animation ---------- */
    const revealElements = document.querySelectorAll('.reveal');
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        revealElements.forEach((el, index) => {
            el.style.transitionDelay = `${index * 0.08}s`;
            revealObserver.observe(el);
        });
    }

    /* ---------- Toast Auto-Dismiss ---------- */
    const toasts = document.querySelectorAll('.toast-luxury');
    toasts.forEach((toast, index) => {
        setTimeout(() => {
            toast.style.transition = 'all 0.4s ease-out';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(60px)';
            setTimeout(() => toast.remove(), 400);
        }, 4000 + (index * 500));
    });

    /* ---------- Mobile Navbar Close on Link Click ---------- */
    const navLinks = document.querySelectorAll('.navbar-luxury .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) bsCollapse.hide();
            }
        });
    });

    /* ---------- Smooth Scroll for Anchor Links ---------- */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /* ---------- Active Nav Link Highlight ---------- */
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-luxury .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        }
    });

});
