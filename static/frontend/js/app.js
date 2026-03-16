/**
 * App Level Utility Functions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check auth state for nav updates
    updateNavigation();
});

function updateNavigation() {
    const isAuth = window.api.isAuthenticated();
    const navAuth = document.getElementById('nav-auth');

    if (!navAuth) return;

    if (isAuth) {
        navAuth.innerHTML = `
            <a href="/dashboard/" class="nav-link" style="margin-right: 1rem; color: var(--color-text-secondary);">Dashboard</a>
            <button onclick="handleLogout()" class="btn btn-secondary">Logout</button>
        `;
    } else {
        navAuth.innerHTML = `
            <a href="/login/" class="nav-link" style="margin-right: 1rem; color: var(--color-text-secondary);">Log In</a>
            <a href="/register/" class="btn btn-primary">Start Free Trial</a>
        `;
    }
}

function handleLogout() {
    window.api.logout();
    window.location.href = '/';
}

// Form state handler
function setButtonLoading(btn, isLoading, text = 'Processing...') {
    if (!btn) return;
    if (isLoading) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `<span class="spinner"></span> ${text}`;
        btn.disabled = true;
    } else {
        btn.innerHTML = btn.dataset.originalText || btn.innerText;
        btn.disabled = false;
    }
}

// Protect routes
function requireAuth() {
    if (!window.api.isAuthenticated()) {
        window.location.href = '/login/?redirect=' + encodeURIComponent(window.location.pathname);
    }
}

// Reset button states when page is shown (handles Back button / bfcache)
window.addEventListener('pageshow', (event) => {
    // We always reset on pageshow to be safe, especially if coming back from Stripe
    document.querySelectorAll('.btn').forEach(btn => {
        if (btn.disabled && btn.dataset.originalText) {
            setButtonLoading(btn, false);
        }
    });
});
