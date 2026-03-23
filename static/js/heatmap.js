// ═══════════════════════════════════════════════
//  HEATMAP.JS — Overlay Slider (Original vs Heatmap)
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  const sliderRange     = document.getElementById('overlay-slider');
  const imgBefore       = document.getElementById('img-before');   // original
  const sliderDivider   = document.getElementById('slider-divider');
  const sliderHandle    = document.getElementById('slider-handle');

  // ── RANGE SLIDER CONTROL ─────────────────────
  if (sliderRange && imgBefore) {
    sliderRange.addEventListener('input', () => {
      const val = sliderRange.value + '%';
      imgBefore.style.clipPath      = `inset(0 ${100 - sliderRange.value}% 0 0)`;
      sliderDivider.style.left      = val;
      sliderHandle.style.left       = val;
    });
  }

  // ── DRAG SLIDER WITH MOUSE ───────────────────
  const sliderContainer = document.getElementById('slider-container');
  let isDragging = false;

  if (sliderContainer) {
    sliderContainer.addEventListener('mousedown', () => isDragging = true);
    document.addEventListener('mouseup',          () => isDragging = false);

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const rect = sliderContainer.getBoundingClientRect();
      let pct  = ((e.clientX - rect.left) / rect.width) * 100;
      pct = Math.min(100, Math.max(0, pct));
      imgBefore.style.clipPath    = `inset(0 ${100 - pct}% 0 0)`;
      sliderDivider.style.left    = pct + '%';
      sliderHandle.style.left     = pct + '%';
      if (sliderRange) sliderRange.value = pct;
    });

    // Touch support
    sliderContainer.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      const rect  = sliderContainer.getBoundingClientRect();
      let pct = ((touch.clientX - rect.left) / rect.width) * 100;
      pct = Math.min(100, Math.max(0, pct));
      imgBefore.style.clipPath  = `inset(0 ${100 - pct}% 0 0)`;
      sliderDivider.style.left  = pct + '%';
      sliderHandle.style.left   = pct + '%';
      if (sliderRange) sliderRange.value = pct;
    });
  }

  // ── COLORMAP SWITCHER ─────────────────────────
  const colormapCards = document.querySelectorAll('.colormap-card');
  const mainOverlay   = document.getElementById('img-after');   // heatmap side

  colormapCards.forEach(card => {
    card.addEventListener('click', () => {
      colormapCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const newSrc = card.getAttribute('data-img');
      if (mainOverlay && newSrc) {
        mainOverlay.style.opacity = '0';
        setTimeout(() => {
          mainOverlay.src = newSrc;
          mainOverlay.style.opacity = '1';
        }, 200);
      }
    });
  });

  // ── FULLSCREEN TOGGLE ─────────────────────────
  const fullscreenBtns = document.querySelectorAll('.fullscreen-btn');
  fullscreenBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const imgSrc = btn.getAttribute('data-src');
      const modal  = document.getElementById('img-modal');
      const modalImg = document.getElementById('modal-img');
      if (modal && modalImg) {
        modalImg.src = imgSrc;
        modal.style.display = 'flex';
      }
    });
  });

  const modal = document.getElementById('img-modal');
  if (modal) {
    modal.addEventListener('click', () => modal.style.display = 'none');
  }

});
