import { apiRequest } from './config.js';

// Current user from the backend, or null when logged out / server unreachable
export function getCredentials() {
    return apiRequest('/api/id').catch(() => null);
}

// Swap the "Log In" nav link for the user's profile link when logged in
document.addEventListener('DOMContentLoaded', async () => {
    const loginLink = document.querySelector('.main-nav a[href="login.html"]');
    if (!loginLink) return;
    const user = await getCredentials();
    window.user = user;
    if (user) {
        loginLink.textContent = "My Profile";
        loginLink.href = "profile.html";
    }
});
