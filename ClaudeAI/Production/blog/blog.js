// Blog-specific JavaScript
// Category filtering, search, and dynamic content loading

// Category filtering
const categoryButtons = document.querySelectorAll('.category-btn');
const blogCards = document.querySelectorAll('.blog-card');
const featuredCard = document.querySelector('.featured-card');

categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Update active button
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        const category = button.dataset.category;

        // Filter cards
        blogCards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.classList.remove('hidden');
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 10);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.classList.add('hidden');
                }, 300);
            }
        });

        // Show/hide featured card
        if (featuredCard) {
            if (category === 'all' || featuredCard.dataset.category === category) {
                featuredCard.style.display = 'grid';
            } else {
                featuredCard.style.display = 'none';
            }
        }
    });
});

// Search functionality
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();

        blogCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const content = card.querySelector('p').textContent.toLowerCase();
            const category = card.querySelector('.blog-category').textContent.toLowerCase();

            if (title.includes(searchTerm) || content.includes(searchTerm) || category.includes(searchTerm)) {
                card.classList.remove('hidden');
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.classList.add('hidden');
                }, 300);
            }
        });

        // Handle featured card search
        if (featuredCard) {
            const featuredTitle = featuredCard.querySelector('h2').textContent.toLowerCase();
            const featuredContent = featuredCard.querySelector('p').textContent.toLowerCase();

            if (searchTerm === '' || featuredTitle.includes(searchTerm) || featuredContent.includes(searchTerm)) {
                featuredCard.style.display = 'grid';
            } else {
                featuredCard.style.display = 'none';
            }
        }

        // Show "No results" message if needed
        const visibleCards = Array.from(blogCards).filter(card => !card.classList.contains('hidden'));
        const noResults = document.querySelector('.no-results');

        if (visibleCards.length === 0 && (!featuredCard || featuredCard.style.display === 'none')) {
            if (!noResults) {
                const message = document.createElement('div');
                message.className = 'no-results';
                message.style.textAlign = 'center';
                message.style.padding = '60px 20px';
                message.style.color = 'var(--text-secondary)';
                message.innerHTML = `
                    <h3 style="font-size: 24px; margin-bottom: 12px;">No articles found</h3>
                    <p>Try a different search term or category.</p>
                `;
                document.querySelector('.blog-grid').appendChild(message);
            }
        } else if (noResults) {
            noResults.remove();
        }
    });
}

// Load more functionality (simulated - can be replaced with API call)
const loadMoreBtn = document.getElementById('loadMore');
let currentPage = 1;
const articlesPerPage = 9;

if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
        // Simulate loading more articles
        loadMoreBtn.textContent = 'Loading...';
        loadMoreBtn.disabled = true;

        setTimeout(() => {
            // In a real app, this would fetch from an API
            console.log('Loading more articles...');
            currentPage++;

            // Simulate end of content after 3 pages
            if (currentPage >= 3) {
                loadMoreBtn.textContent = 'No More Articles';
                loadMoreBtn.disabled = true;
            } else {
                loadMoreBtn.textContent = 'Load More Articles';
                loadMoreBtn.disabled = false;
            }
        }, 1000);
    });
}

// Newsletter form submission
const newsletterForm = document.getElementById('newsletterForm');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = newsletterForm.querySelector('input[type="email"]').value;

        // Simulate API call
        const submitBtn = newsletterForm.querySelector('button');
        submitBtn.textContent = 'Subscribing...';
        submitBtn.disabled = true;

        setTimeout(() => {
            // Show success message
            newsletterForm.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#10b981" style="margin: 0 auto 16px;">
                        <circle cx="12" cy="12" r="10" stroke-width="2"/>
                        <path d="M9 12l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h3 style="font-size: 24px; margin-bottom: 8px; color: var(--text-primary);">You're subscribed!</h3>
                    <p style="color: var(--text-secondary);">Check your email for a confirmation message.</p>
                </div>
            `;

            // Log for automation hook (future implementation)
            console.log('Newsletter subscription:', { email, timestamp: new Date() });

            // TODO: Send to backend API
            // fetch('/api/newsletter/subscribe', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ email })
            // });
        }, 1500);
    });
}

// Reading time calculation (for future blog posts)
function calculateReadingTime(text) {
    const wordsPerMinute = 200;
    const wordCount = text.trim().split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / wordsPerMinute);
    return `${readingTime} min read`;
}

// Automation hook for blog post creation (future feature)
// This function will be called by automated systems to add new blog posts
window.ZmartyBlog = {
    addPost: function(post) {
        console.log('Adding new blog post:', post);
        // Structure: { title, excerpt, category, date, image, link }
        // TODO: Implement dynamic post creation
    },

    updatePost: function(postId, updates) {
        console.log('Updating blog post:', postId, updates);
        // TODO: Implement post updates
    },

    deletePost: function(postId) {
        console.log('Deleting blog post:', postId);
        // TODO: Implement post deletion
    },

    getPosts: function(filters = {}) {
        // Returns filtered list of posts
        // Filters: category, dateRange, searchTerm
        console.log('Getting posts with filters:', filters);
        return [];
    }
};

// Scroll progress indicator for blog articles
function createProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.style.position = 'fixed';
    progressBar.style.top = '0';
    progressBar.style.left = '0';
    progressBar.style.width = '0%';
    progressBar.style.height = '3px';
    progressBar.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
    progressBar.style.zIndex = '9999';
    progressBar.style.transition = 'width 0.1s ease';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrolled = window.scrollY;
        const progress = (scrolled / (documentHeight - windowHeight)) * 100;
        progressBar.style.width = progress + '%';
    });
}

// Initialize progress bar on article pages
if (window.location.pathname.includes('blog/') && !window.location.pathname.includes('index')) {
    createProgressBar();
}

// Social share functionality (for future implementation)
window.ZmartyBlog.share = function(platform, postData) {
    const shareUrls = {
        twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(postData.url)}&text=${encodeURIComponent(postData.title)}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(postData.url)}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(postData.url)}`,
        reddit: `https://reddit.com/submit?url=${encodeURIComponent(postData.url)}&title=${encodeURIComponent(postData.title)}`
    };

    if (shareUrls[platform]) {
        window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
};

console.log('🤖 Zmarty Blog initialized');
console.log('📝 Automation hooks available via window.ZmartyBlog');
