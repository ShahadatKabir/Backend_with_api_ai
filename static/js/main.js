// Main JavaScript file for FastAPI Pro Dashboard

// ===== GLOBAL STATE =====
const state = {
    darkMode: localStorage.getItem('darkMode') === 'true' || 
              (window.matchMedia('(prefers-color-scheme: dark)').matches && 
               localStorage.getItem('darkMode') === null),
    apiBaseUrl: '/',
    csrfToken: null
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initMobileMenu();
    initUserDropdown();
    initToastContainer();
    initTooltips();
    loadCsrfToken();
});

// ===== DARK MODE =====
function initDarkMode() {
    if (state.darkMode) {
        document.documentElement.classList.add('dark');
        document.body.classList.add('dark');
    }
    
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
    
    // Listen to system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (localStorage.getItem('darkMode') === null) {
            state.darkMode = e.matches;
            document.documentElement.classList.toggle('dark', e.matches);
            document.body.classList.toggle('dark', e.matches);
        }
    });
}

function toggleDarkMode() {
    state.darkMode = !state.darkMode;
    localStorage.setItem('darkMode', state.darkMode);
    document.documentElement.classList.toggle('dark', state.darkMode);
    document.body.classList.toggle('dark', state.darkMode);
}

// ===== MOBILE MENU =====
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

// ===== USER DROPDOWN =====
function initUserDropdown() {
    const userMenuButton = document.getElementById('userMenuButton');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuButton && userDropdown) {
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuButton.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });
    }
}

// ===== TOAST NOTIFICATIONS =====
function initToastContainer() {
    const container = document.getElementById('toast-container');
    if (container) {
        // Clear expired toasts
        setInterval(() => {
            const toasts = container.querySelectorAll('.toast');
            toasts.forEach(toast => {
                if (toast.dataset.timeout) {
                    const remaining = parseInt(toast.dataset.timeout) - 1000;
                    if (remaining <= 0) {
                        removeToast(toast);
                    } else {
                        toast.dataset.timeout = remaining;
                    }
                }
            });
        }, 1000);
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in shadow-lg`;
    toast.setAttribute('role', 'alert');
    toast.dataset.timeout = duration / 1000;
    
    const icons = {
        success: '<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
        error: '<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
        warning: '<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
        info: '<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
    };
    
    toast.innerHTML = `
        <div class="flex items-center">
            ${icons[type] || icons.info}
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
    toast.style.transform = 'translateX(100%)';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
}

// ===== TOOLTIPS =====
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-900 dark:bg-gray-700 rounded';
            tooltip.textContent = trigger.dataset.tooltip;
            tooltip.style.top = '-30px';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translateX(-50%)';
            trigger.style.position = 'relative';
            trigger.appendChild(tooltip);
        });
        
        trigger.addEventListener('mouseleave', () => {
            const tooltip = trigger.querySelector('[class*="bg-gray-900"]');
            if (tooltip) tooltip.remove();
        });
    });
}

// ===== CSRF TOKEN =====
async function loadCsrfToken() {
    try {
        const response = await fetch('/csrf-token', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            state.csrfToken = data.csrf_token;
        }
    } catch (error) {
        console.error('Failed to load CSRF token:', error);
    }
}

// ===== API HELPERS =====
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(state.csrfToken ? { 'X-CSRF-Token': state.csrfToken } : {}),
            ...options.headers
        }
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
}

// ===== MODAL HELPERS =====
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// ===== CONFIRM DIALOG =====
function confirmAction(message, onConfirm) {
    if (confirm(message)) {
        onConfirm();
    }
}

// ===== FORM HELPERS =====
function setFormErrors(form, errors) {
    // Clear previous errors
    form.querySelectorAll('.form-error').forEach(el => el.remove());
    
    Object.entries(errors).forEach(([field, messages]) => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = messages.join(', ');
            input.parentNode.appendChild(errorDiv);
            input.classList.add('border-red-500', 'focus:ring-red-500');
        }
    });
}

function clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach(el => el.remove());
    form.querySelectorAll('.border-red-500').forEach(el => {
        el.classList.remove('border-red-500', 'focus:ring-red-500');
    });
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function truncateText(text, length = 50) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

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

// ===== EXPORTS =====
window.APP = {
    state,
    showToast,
    showModal,
    hideModal,
    confirmAction,
    apiRequest,
    formatDate,
    truncateText,
    setFormErrors,
    clearFormErrors,
    debounce
};
