document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.navbar-nav');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const value = parseInt(target.getAttribute('data-target') || target.textContent.replace(/[^0-9]/g, ''));
                    if (value > 0) {
                        let current = 0;
                        const increment = Math.ceil(value / 60);
                        const timer = setInterval(() => {
                            current += increment;
                            if (current >= value) {
                                current = value;
                                clearInterval(timer);
                            }
                            target.textContent = current + (target.textContent.includes('+') ? '+' : '%');
                        }, 30);
                    }
                    observer.unobserve(target);
                }
            });
        }, { threshold: 0.5 });
        statNumbers.forEach(stat => observer.observe(stat));
    }
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const navHeight = document.querySelector('.navbar').offsetHeight;
                window.scrollTo({ top: target.getBoundingClientRect().top + window.pageYOffset - navHeight, behavior: 'smooth' });
                if (navMenu && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    hamburger.classList.remove('active');
                }
            }
        });
    });
    document.querySelectorAll('.solution-card, .industry-item, .stat-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        observer.observe(el);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            try {
                const response = await fetch('/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.ok) {
                    alert('Message sent successfully!');
                    this.reset();
                } else {
                    alert('Error: ' + (result.error || 'Something went wrong.'));
                }
            } catch (error) {
                alert('Network error. Please try again.');
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});