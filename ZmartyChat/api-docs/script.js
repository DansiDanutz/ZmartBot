// API Documentation JavaScript

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            // Update active state
            updateActiveSection(this.getAttribute('href'));
        }
    });
});

// Update active section in sidebar
function updateActiveSection(hash) {
    document.querySelectorAll('.api-sidebar a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === hash) {
            link.classList.add('active');
        }
    });
}

// Highlight current section on scroll
const sections = document.querySelectorAll('.doc-section');
const navLinks = document.querySelectorAll('.api-sidebar a');

window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Copy code to clipboard
document.addEventListener('DOMContentLoaded', () => {
    // Add copy buttons to code blocks
    document.querySelectorAll('pre').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            padding: 4px 8px;
            background: var(--bg-card-hover);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            cursor: pointer;
            opacity: 0;
            transition: all 0.3s ease;
        `;

        block.style.position = 'relative';
        block.appendChild(button);

        block.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });

        block.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });

        button.addEventListener('click', async () => {
            const code = block.querySelector('code').textContent;
            try {
                await navigator.clipboard.writeText(code);
                button.textContent = 'Copied!';
                button.style.color = 'var(--success-green)';
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.color = 'var(--text-secondary)';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
});

// Try It Out functionality
async function sendTestRequest() {
    const apiKey = document.getElementById('api-key').value;
    const endpoint = document.getElementById('endpoint-select').value;
    const params = document.getElementById('params').value;
    const environment = document.getElementById('environment-select').value;
    const responseOutput = document.getElementById('response-output');

    if (!apiKey) {
        responseOutput.innerHTML = '<code style="color: var(--danger-red)">Please enter your API key</code>';
        return;
    }

    // Show loading state
    responseOutput.innerHTML = '<code style="color: var(--text-secondary)">Sending request...</code>';

    // Determine method and URL
    const [method, path] = endpoint.split(' ');
    const baseUrl = environment === 'production'
        ? 'https://api.zmartychat.com/v1'
        : 'https://sandbox.api.zmartychat.com/v1';
    const url = baseUrl + path;

    try {
        // Build request options
        const options = {
            method: method,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        };

        // Add body for POST/PUT requests
        if (method === 'POST' || method === 'PUT') {
            if (params) {
                try {
                    options.body = JSON.stringify(JSON.parse(params));
                } catch (e) {
                    responseOutput.innerHTML = '<code style="color: var(--danger-red)">Invalid JSON in parameters</code>';
                    return;
                }
            }
        } else if (method === 'GET' && params) {
            // Add query parameters for GET requests
            try {
                const queryParams = new URLSearchParams(JSON.parse(params));
                url += '?' + queryParams.toString();
            } catch (e) {
                responseOutput.innerHTML = '<code style="color: var(--danger-red)">Invalid JSON in parameters</code>';
                return;
            }
        }

        // Simulated response for demo (replace with actual API call in production)
        setTimeout(() => {
            const mockResponses = {
                '/user/profile': {
                    id: 'user_123456',
                    email: 'demo@example.com',
                    name: 'Demo User',
                    plan: 'pro',
                    balance: {
                        USD: 50000.00,
                        BTC: 1.5,
                        ETH: 20.0
                    },
                    created_at: '2025-01-01T00:00:00Z'
                },
                '/market/ticker': {
                    symbol: 'BTC-USD',
                    price: 45000.00,
                    change_24h: 2.5,
                    volume_24h: 1234567890,
                    high_24h: 46000,
                    low_24h: 44000
                },
                '/orders': {
                    order_id: 'ord_' + Math.random().toString(36).substr(2, 9),
                    status: 'pending',
                    created_at: new Date().toISOString()
                }
            };

            const response = mockResponses[path] || { message: 'Demo response for ' + endpoint };
            responseOutput.innerHTML = `<code class="language-json">${JSON.stringify(response, null, 2)}</code>`;

            // Re-highlight syntax
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(responseOutput.querySelector('code'));
            }
        }, 1000);

        // Uncomment for actual API calls:
        // const response = await fetch(url, options);
        // const data = await response.json();
        // responseOutput.innerHTML = `<code class="language-json">${JSON.stringify(data, null, 2)}</code>`;
        // Prism.highlightElement(responseOutput.querySelector('code'));

    } catch (error) {
        responseOutput.innerHTML = `<code style="color: var(--danger-red)">Error: ${error.message}</code>`;
    }
}

// Expandable endpoint details
document.querySelectorAll('.endpoint-header').forEach(header => {
    header.addEventListener('click', () => {
        const content = header.nextElementSibling;
        if (content && content.classList.contains('endpoint-content')) {
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
        }
    });
});

// Search functionality (for future implementation)
function initSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search documentation...';
    searchInput.className = 'search-input';
    searchInput.style.cssText = `
        width: 100%;
        padding: var(--spacing-sm) var(--spacing-md);
        background: var(--bg-dark);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        margin-bottom: var(--spacing-lg);
    `;

    const sidebar = document.querySelector('.api-sidebar');
    if (sidebar) {
        sidebar.insertBefore(searchInput, sidebar.firstChild);

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.sidebar-section li').forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? 'block' : 'none';
            });
        });
    }
}

// Initialize search on load
initSearch();

// Theme toggle (for future dark/light mode)
function initThemeToggle() {
    const themes = {
        dark: {
            '--bg-dark': '#0a0a0a',
            '--bg-card': '#1a1a1a',
            '--text-primary': '#ffffff',
            '--text-secondary': '#8a8a8a'
        },
        light: {
            '--bg-dark': '#ffffff',
            '--bg-card': '#f5f5f5',
            '--text-primary': '#000000',
            '--text-secondary': '#666666'
        }
    };

    let currentTheme = 'dark';

    // Create theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.textContent = '🌙';
    themeToggle.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        cursor: pointer;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        transition: all 0.3s ease;
    `;

    document.body.appendChild(themeToggle);

    themeToggle.addEventListener('click', () => {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        const theme = themes[currentTheme];

        Object.keys(theme).forEach(key => {
            document.documentElement.style.setProperty(key, theme[key]);
        });

        themeToggle.textContent = currentTheme === 'dark' ? '🌙' : '☀️';
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + K for search focus
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('.search-input');
        if (searchInput && searchInput === document.activeElement) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.blur();
        }
    }
});

// Analytics tracking (for production)
function trackEvent(category, action, label) {
    // Google Analytics or similar
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: category,
            event_label: label
        });
    }
}

// Track API endpoint views
document.querySelectorAll('.endpoint').forEach(endpoint => {
    endpoint.addEventListener('click', () => {
        const method = endpoint.querySelector('.method').textContent;
        const path = endpoint.querySelector('.path').textContent;
        trackEvent('API Docs', 'View Endpoint', `${method} ${path}`);
    });
});

// Load saved API key from localStorage
window.addEventListener('load', () => {
    const savedApiKey = localStorage.getItem('api-docs-key');
    if (savedApiKey) {
        document.getElementById('api-key').value = savedApiKey;
    }
});

// Save API key to localStorage
document.getElementById('api-key')?.addEventListener('change', (e) => {
    localStorage.setItem('api-docs-key', e.target.value);
});

console.log('ZmartyChat API Documentation loaded successfully');