/**
 * VLSI Cadence Virtuoso Presentation Deck Controller
 * Provides instantaneous slide navigation via keyboard, mouse, and hash routing.
 * Strictly zero animations / immediate layout switching.
 */

(function () {
  if (new URLSearchParams(window.location.search).has('export')) {
    document.documentElement.classList.add('export-mode');
  }

  const slides = document.querySelectorAll('.slide');
  const totalSlides = slides.length;
  let currentSlideIndex = 0;

  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const fsBtn = document.getElementById('fsBtn');

  function updateSlide(index) {
    if (index < 0) index = 0;
    if (index >= totalSlides) index = totalSlides - 1;
    currentSlideIndex = index;

    // Direct display switch with zero animations
    slides.forEach((slide, i) => {
      if (i === currentSlideIndex) {
        slide.classList.add('active');
      } else {
        slide.classList.remove('active');
      }
    });

    // Update nav dots across all slides
    document.querySelectorAll('.footer-center').forEach((container) => {
      const dots = container.querySelectorAll('.nav-dot');
      dots.forEach((dot, i) => {
        if (i === currentSlideIndex) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });
    });

    // Update buttons
    if (prevBtn) prevBtn.disabled = currentSlideIndex === 0;
    if (nextBtn) nextBtn.disabled = currentSlideIndex === totalSlides - 1;

    // Update hash without scrolling
    history.replaceState(null, null, `#${currentSlideIndex + 1}`);
  }

  function nextSlide() {
    if (currentSlideIndex < totalSlides - 1) {
      updateSlide(currentSlideIndex + 1);
    }
  }

  function prevSlide() {
    if (currentSlideIndex > 0) {
      updateSlide(currentSlideIndex - 1);
    }
  }

  function toggleFullScreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }
  }

  // Keyboard Event Handlers
  window.addEventListener('keydown', (e) => {
    // Ignore input fields if any
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
      case 'PageDown':
      case ' ': // Spacebar
      case 'Enter':
        e.preventDefault();
        nextSlide();
        break;

      case 'ArrowLeft':
      case 'ArrowUp':
      case 'PageUp':
      case 'Backspace':
        e.preventDefault();
        prevSlide();
        break;

      case 'Home':
        e.preventDefault();
        updateSlide(0);
        break;

      case 'End':
        e.preventDefault();
        updateSlide(totalSlides - 1);
        break;

      case 'f':
      case 'F':
        e.preventDefault();
        toggleFullScreen();
        break;

      default:
        // Number keys 1-9
        if (e.key >= '1' && e.key <= '9') {
          const target = parseInt(e.key, 10) - 1;
          if (target < totalSlides) {
            e.preventDefault();
            updateSlide(target);
          }
        } else if (e.key === '0') {
          // '0' key for Slide 10
          e.preventDefault();
          updateSlide(9);
        }
        break;
    }
  });

  // Button Listeners
  if (prevBtn) prevBtn.addEventListener('click', prevSlide);
  if (nextBtn) nextBtn.addEventListener('click', nextSlide);
  if (fsBtn) fsBtn.addEventListener('click', toggleFullScreen);

  // Setup click handlers on all nav dots
  document.querySelectorAll('.slide').forEach((slide) => {
    const dots = slide.querySelectorAll('.nav-dot');
    dots.forEach((dot, idx) => {
      dot.addEventListener('click', () => updateSlide(idx));
    });
  });

  function parseHash() {
    const hash = window.location.hash.replace('#', '').replace('slide-', '');
    const slideNum = parseInt(hash, 10);
    if (!isNaN(slideNum) && slideNum >= 1 && slideNum <= totalSlides) {
      return slideNum - 1;
    }
    return 0;
  }

  // Hash Navigation on Load
  window.addEventListener('load', () => {
    updateSlide(parseHash());
  });

  window.addEventListener('hashchange', () => {
    const target = parseHash();
    if (target !== currentSlideIndex) {
      updateSlide(target);
    }
  });

  // Expose global methods for direct inline triggers if needed
  window.VLSI_DECK = {
    updateSlide,
    nextSlide,
    prevSlide,
    toggleFullScreen,
  };
})();
