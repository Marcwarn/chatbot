/**
 * PERSONA LANDING PAGE - JAVASCRIPT
 * Professional interactive elements and form handling
 */

(function() {
    'use strict';

    // ============================================
    // DOM READY
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        initializeNavigation();
        initializeSmoothScroll();
        initializePricingButtons();
        initializeTrialForm();
        initializeAnimations();
        initializeAnalytics();
    });

    // ============================================
    // NAVIGATION
    // ============================================
    function initializeNavigation() {
        const nav = document.querySelector('.nav');
        if (!nav) return;

        // Add shadow on scroll
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                nav.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
            } else {
                nav.style.boxShadow = 'none';
            }
        });

        // Mobile menu toggle (if needed in future)
        const mobileMenuButton = document.querySelector('.mobile-menu-button');
        if (mobileMenuButton) {
            mobileMenuButton.addEventListener('click', toggleMobileMenu);
        }
    }

    function toggleMobileMenu() {
        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            navLinks.classList.toggle('active');
        }
    }

    // ============================================
    // SMOOTH SCROLL
    // ============================================
    function initializeSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');

                // Skip empty anchors
                if (href === '#') {
                    e.preventDefault();
                    return;
                }

                const target = document.querySelector(href);

                if (target) {
                    e.preventDefault();
                    const navHeight = document.querySelector('.nav')?.offsetHeight || 0;
                    const targetPosition = target.offsetTop - navHeight - 20;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    // Track navigation click
                    trackEvent('Navigation', 'Click', href);
                }
            });
        });
    }

    // ============================================
    // PRICING BUTTONS
    // ============================================
    function initializePricingButtons() {
        const purchaseButtons = document.querySelectorAll('.btn-purchase');

        purchaseButtons.forEach(button => {
            button.addEventListener('click', function() {
                const packageType = this.getAttribute('data-package');
                handlePurchaseClick(packageType);
            });
        });
    }

    function handlePurchaseClick(packageType) {
        // Track the purchase intent
        trackEvent('Purchase', 'Click', packageType);

        // Show modal or redirect based on package
        switch(packageType) {
            case 'big-five':
                window.location.href = '/big-five-demo.html';
                break;
            case 'disc':
                window.location.href = '/disc-assessment.html';
                break;
            case 'complete':
                // Show selection modal or redirect to index
                showPackageSelectionModal();
                break;
            default:
                console.warn('Unknown package type:', packageType);
        }
    }

    function showPackageSelectionModal() {
        // For now, redirect to index page
        // In future, this could show a modal to choose which test to take first
        const choice = confirm('Vill du börja med Big Five-testet? (Tryck OK för Big Five, Avbryt för DISC)');

        if (choice) {
            window.location.href = '/big-five-demo.html';
        } else {
            window.location.href = '/disc-assessment.html';
        }
    }

    // ============================================
    // FREE TRIAL FORM
    // ============================================
    function initializeTrialForm() {
        const trialForm = document.getElementById('trialForm');
        if (!trialForm) return;

        trialForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleTrialSubmission();
        });
    }

    function handleTrialSubmission() {
        const inviteCodeInput = document.getElementById('invite-code');
        const inviteCode = inviteCodeInput?.value.trim();

        if (!inviteCode) {
            showNotification('Vänligen ange en giltig inbjudningskod', 'error');
            return;
        }

        // Validate invite code format (example: alphanumeric, 8-16 characters)
        if (!isValidInviteCode(inviteCode)) {
            showNotification('Ogiltig inbjudningskod. Kontrollera och försök igen.', 'error');
            return;
        }

        // Track trial activation attempt
        trackEvent('Trial', 'Submit', inviteCode);

        // Show loading state
        const submitButton = document.querySelector('.trial-form button');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span>Verifierar...</span>';

        // Simulate API call (in production, this would validate against backend)
        setTimeout(() => {
            // For demo purposes, accept any valid format code
            // In production, verify against database
            if (inviteCode.toLowerCase().startsWith('free')) {
                showNotification('Inbjudningskod aktiverad! Omdirigerar...', 'success');

                setTimeout(() => {
                    // Store the invite code in session storage
                    sessionStorage.setItem('inviteCode', inviteCode);
                    // Redirect to assessment selection
                    window.location.href = '/index.html';
                }, 1500);
            } else {
                showNotification('Inbjudningskoden är inte giltig eller har redan använts.', 'error');
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        }, 1000);
    }

    function isValidInviteCode(code) {
        // Basic validation: alphanumeric, 6-20 characters
        const regex = /^[a-zA-Z0-9]{6,20}$/;
        return regex.test(code);
    }

    // ============================================
    // NOTIFICATIONS
    // ============================================
    function showNotification(message, type = 'info') {
        // Remove any existing notifications
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i data-lucide="${getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            background: getNotificationColor(type),
            color: 'white',
            borderRadius: '12px',
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
            zIndex: '10000',
            animation: 'slideInRight 0.3s ease-out',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            maxWidth: '400px'
        });

        // Add to DOM
        document.body.appendChild(notification);

        // Initialize Lucide icons for notification
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    function getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || icons.info;
    }

    function getNotificationColor(type) {
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6'
        };
        return colors[type] || colors.info;
    }

    // ============================================
    // SCROLL ANIMATIONS
    // ============================================
    function initializeAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements that should animate in
        const animatedElements = document.querySelectorAll('.benefit, .step, .pricing-card, .security-item');
        animatedElements.forEach(el => observer.observe(el));
    }

    // ============================================
    // ANALYTICS
    // ============================================
    function initializeAnalytics() {
        // Track page view
        trackPageView();

        // Track scroll depth
        trackScrollDepth();

        // Track time on page
        trackTimeOnPage();
    }

    function trackPageView() {
        trackEvent('Page', 'View', window.location.pathname);
    }

    function trackScrollDepth() {
        let maxScroll = 0;
        const milestones = [25, 50, 75, 100];
        const trackedMilestones = new Set();

        window.addEventListener('scroll', function() {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrolled = (window.scrollY / scrollHeight) * 100;

            if (scrolled > maxScroll) {
                maxScroll = scrolled;

                milestones.forEach(milestone => {
                    if (scrolled >= milestone && !trackedMilestones.has(milestone)) {
                        trackedMilestones.add(milestone);
                        trackEvent('Scroll', 'Depth', `${milestone}%`);
                    }
                });
            }
        });
    }

    function trackTimeOnPage() {
        const startTime = Date.now();

        window.addEventListener('beforeunload', function() {
            const timeSpent = Math.round((Date.now() - startTime) / 1000);
            trackEvent('Engagement', 'TimeOnPage', `${timeSpent}s`);
        });
    }

    function trackEvent(category, action, label) {
        // Console log for development
        console.log('Analytics:', { category, action, label });

        // In production, integrate with Google Analytics, Plausible, or custom analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label
            });
        }

        // Custom analytics endpoint (if available)
        if (window.analytics) {
            window.analytics.track(action, {
                category: category,
                label: label
            });
        }
    }

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ============================================
    // CSS ANIMATIONS (add to document)
    // ============================================
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .notification-content i {
            width: 24px;
            height: 24px;
        }
    `;
    document.head.appendChild(style);

    // ============================================
    // EXPOSE PUBLIC API
    // ============================================
    window.PersonaLanding = {
        trackEvent: trackEvent,
        showNotification: showNotification
    };

})();
