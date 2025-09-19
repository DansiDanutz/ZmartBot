// Simple Login - One page, minimal fields

function quickLogin(provider) {
    // Save minimal data
    localStorage.setItem('zmarty_onboarding_complete', 'true');
    localStorage.setItem('zmarty_user', JSON.stringify({
        provider: provider,
        plan: 'free',
        createdAt: new Date().toISOString()
    }));

    // Go to dashboard
    window.location.href = 'dashboard.html';
}

function quickStart() {
    const email = document.getElementById('email').value;
    const country = document.getElementById('country').value;

    if (!email) {
        showError('Please enter your email');
        return;
    }

    if (!email.includes('@')) {
        showError('Please enter a valid email');
        return;
    }

    // Save minimal data
    localStorage.setItem('zmarty_onboarding_complete', 'true');
    localStorage.setItem('zmarty_user', JSON.stringify({
        email: email,
        country: country || 'US',
        plan: 'free',
        createdAt: new Date().toISOString()
    }));

    // Go to dashboard
    window.location.href = 'dashboard.html';
}

function showError(message) {
    const error = document.createElement('div');
    error.className = 'error-toast';
    error.textContent = message;
    error.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff4757;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideDown 0.3s ease;
    `;
    document.body.appendChild(error);

    setTimeout(() => error.remove(), 3000);
}

// Enable enter key
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('email').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            quickStart();
        }
    });
});