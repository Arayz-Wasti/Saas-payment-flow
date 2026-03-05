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
            <a href="dashboard.html" class="nav-link" style="margin-right: 1rem; color: var(--color-text-secondary);">Dashboard</a>
            <button onclick="handleLogout()" class="btn btn-secondary">Logout</button>
        `;
    } else {
        navAuth.innerHTML = `
            <a href="login.html" class="nav-link" style="margin-right: 1rem; color: var(--color-text-secondary);">Log In</a>
            <a href="register.html" class="btn btn-primary">Start Free Trial</a>
        `;
    }
}

function handleLogout() {
    window.api.logout();
    window.location.href = 'index.html';
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
        window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.pathname);
    }
}
