// Script to update all slide structures with proper header/content/footer
// This will be used to restructure the HTML properly

const slideStructureTemplate = (slideNumber, contentHTML, actionButton = null) => {
    const hasNext = slideNumber < 9;
    const hasPrev = slideNumber > 1;
    const actionBtn = actionButton || `<button class="btn btn-primary" onclick="goToSlide(${slideNumber + 1})">Continue</button>`;

    return `
            <div class="slide ${slideNumber === 1 ? 'active' : ''}" id="slide-${slideNumber}">
                <div class="card-header">
                    <div class="slide-counter">Step ${slideNumber} of 9</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(slideNumber / 9) * 100}%"></div>
                    </div>
                </div>

                <div class="slide-content">
                    ${contentHTML}
                </div>

                <div class="card-footer">
                    <button class="nav-btn" onclick="previousSlide()" ${!hasPrev ? 'disabled' : ''}>
                        ←
                    </button>
                    <div class="footer-action">
                        ${actionBtn}
                    </div>
                    <button class="nav-btn" onclick="nextSlide()" ${!hasNext ? 'disabled' : ''}>
                        →
                    </button>
                </div>
            </div>`;
};

// Export for use
console.log('Template ready for restructuring slides');