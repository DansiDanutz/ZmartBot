// Force first slide to be visible
console.log('Fixing slide visibility...');

setTimeout(() => {
    const slide1 = document.getElementById('slide-1');
    const allSlides = document.querySelectorAll('.slide');
    
    console.log('Total slides found:', allSlides.length);
    
    // Check current state
    allSlides.forEach((slide, index) => {
        console.log(`Slide ${index + 1}:`, slide.id, 'Classes:', slide.className);
    });
    
    // Force slide 1 to be active if no slide is active
    const activeSlide = document.querySelector('.slide.active');
    if (!activeSlide && slide1) {
        console.log('No active slide found, activating slide 1');
        slide1.classList.add('active');
    }
    
    // Also ensure goToSlide works
    if (typeof goToSlide === 'function') {
        console.log('goToSlide function exists, forcing slide 1');
        goToSlide(1);
    }
}, 100);
