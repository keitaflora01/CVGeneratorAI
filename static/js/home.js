   function animateCounters() {
        const counters = document.querySelectorAll('.purecounter');
        
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                    entry.target.classList.add('animated');
                    
                    const target = parseFloat(entry.target.getAttribute('data-purecounter-end'));
                    const duration = parseFloat(entry.target.getAttribute('data-purecounter-duration')) * 1000;
                    const increment = target / (duration / 16);
                    let current = 0;
                    
                    const updateCounter = () => {
                        if (current < target) {
                            current += increment;
                            if (target > 1000) {
                                entry.target.textContent = Math.floor(current).toLocaleString();
                            } else {
                                entry.target.textContent = Math.floor(current);
                            }
                            requestAnimationFrame(updateCounter);
                        } else {
                            if (target > 1000) {
                                entry.target.textContent = target.toLocaleString();
                            } else {
                                entry.target.textContent = target;
                            }
                        }
                    };
                    updateCounter();
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    // FAQ Toggle functionality
    function initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');
        
        faqItems.forEach(item => {
            const header = item.querySelector('h3');
            header.addEventListener('click', () => {
                // Close all other items
                faqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('faq-active');
                    }
                });
                
                // Toggle current item
                item.classList.toggle('faq-active');
            });
        });
    }

    // Enhanced Animation Observer
    function initAnimations() {
        const elements = document.querySelectorAll('[data-aos]');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        elements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            
            const delay = element.getAttribute('data-aos-delay');
            if (delay) {
                element.style.transitionDelay = delay + 'ms';
            }
            
            observer.observe(element);
        });
    }

    // Smooth scrolling for navigation links
    function initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Initialize everything on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Wait for theme manager to be initialized from footer
        setTimeout(() => {
            animateCounters();
            initFAQ();
            initAnimations();
            initSmoothScrolling();

            // Page loading animation
            document.body.style.opacity = '0';
            setTimeout(() => {
                document.body.style.transition = 'opacity 0.5s ease';
                document.body.style.opacity = '1';
            }, 100);
        }, 100);
    });

    // Keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal:not(.hidden)');
            modals.forEach(modal => modal.classList.add('hidden'));
        }
    });

    // Performance optimization: Debounce scroll events
    let ticking = false;
    function updateOnScroll() {
        ticking = false;
    }

    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateOnScroll);
            ticking = true;
        }
    });