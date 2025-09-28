// CRITICAL NAVIGATION FIX FOR ORIGINAL ZMARTYBRAIN
// This fixes the navigation while keeping all original content

const NAVIGATION_FIX = `
<!-- NAVIGATION FIX INJECTED -->
<script>
(function() {
    console.log('🔧 Applying critical navigation fix to original design...');

    // Wait for DOM and original state to be ready
    function applyNavigationFix() {
        // Override the broken goToStep function
        if (window.state && window.state.goToStep) {
            const originalGoToStep = window.state.goToStep.bind(window.state);

            window.state.goToStep = function(step, direction = 'forward', force = false) {
                if (step < 1 || step > this.totalSteps) return false;

                console.log(\`NAV-FIX: Navigating from step \${this.currentStep} to \${step}\`);

                // Get all steps
                const allSteps = document.querySelectorAll('.step');

                // Hide all steps first
                allSteps.forEach(stepEl => {
                    stepEl.style.display = 'none';
                    stepEl.classList.remove('active');
                    stepEl.style.opacity = '0';
                    stepEl.style.visibility = 'hidden';
                    stepEl.style.position = 'absolute';
                    stepEl.style.left = '-9999px';
                });

                // Show target step
                const targetStep = document.getElementById(\`step\${step}\`);
                if (targetStep) {
                    targetStep.style.display = 'block';
                    targetStep.classList.add('active');
                    targetStep.style.opacity = '1';
                    targetStep.style.visibility = 'visible';
                    targetStep.style.position = 'relative';
                    targetStep.style.left = '0';
                    targetStep.style.transform = 'translateX(0)';
                    targetStep.style.zIndex = '10';
                }

                // Update internal state
                this.currentStep = step;

                // Update progress bar
                const progress = (step / this.totalSteps) * 100;
                const progressFill = document.getElementById('progressFill');
                if (progressFill) {
                    progressFill.style.width = progress + '%';
                }

                // Update progress text
                const progressText = document.getElementById('progressText');
                if (progressText) {
                    progressText.textContent = 'Step ' + step + ' of ' + this.totalSteps;
                }

                // Update navigation arrows
                this.updateNavigation();

                // Update dots if they exist
                this.updateDots();

                // Save state
                this.saveToStorage();

                // Update URL
                window.history.pushState(
                    { step: this.currentStep },
                    '',
                    '#step-' + this.currentStep
                );

                console.log(\`✅ Successfully navigated to step \${step}\`);
                return true;
            };

            // Also fix the navigation methods
            window.state.nextStep = function() {
                if (this.currentStep < this.totalSteps) {
                    return this.goToStep(this.currentStep + 1, 'forward', true);
                }
                return false;
            };

            window.state.prevStep = function() {
                if (this.currentStep > 1) {
                    return this.goToStep(this.currentStep - 1, 'backward', true);
                }
                return false;
            };
        }

        // Fix global navigation functions
        window.nextStep = function() {
            console.log('nextStep called');
            if (window.state) {
                return window.state.nextStep();
            }
        };

        window.prevStep = function() {
            console.log('prevStep called');
            if (window.state) {
                return window.state.prevStep();
            }
        };

        // Fix the Get Started button
        setTimeout(() => {
            const getStartedBtn = document.querySelector('#step1 button.btn.btn-primary');
            if (getStartedBtn) {
                console.log('Fixing Get Started button...');
                getStartedBtn.onclick = function(e) {
                    e.preventDefault();
                    if (window.state) {
                        window.state.goToStep(2, 'forward', true);
                    }
                };
            }
        }, 1000);

        console.log('✅ Navigation fix applied successfully!');
    }

    // Apply fix when DOM is ready and after original code has run
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(applyNavigationFix, 500);
        });
    } else {
        setTimeout(applyNavigationFix, 500);
    }
})();
</script>

<style>
/* Navigation fix styles */
.step {
    transition: opacity 0.3s ease !important;
}

.step.active {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
    position: relative !important;
    left: 0 !important;
    transform: translateX(0) !important;
}

.step:not(.active) {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
    left: -9999px !important;
}
</style>
`;

module.exports = NAVIGATION_FIX;