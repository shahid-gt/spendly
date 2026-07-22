/**
 * landing.js — Video modal controller for Spendly landing page
 *
 * Responsibilities:
 *   - Open modal on "See how it works" button click
 *   - Close on: close button, backdrop click, Escape key
 *   - Stop video on close by clearing iframe src; restore on re-open
 */

(function () {
  'use strict';

  // ── Element refs ──────────────────────────────────────────────────
  const openBtn   = document.getElementById('hero-cta-video');
  const modal     = document.getElementById('video-modal');
  const closeBtn  = document.getElementById('video-modal-close');
  const backdrop  = document.getElementById('video-modal-backdrop');
  const iframe    = document.getElementById('video-modal-iframe');

  if (!openBtn || !modal || !iframe) return; // guard: elements must exist

  // The real YouTube URL lives in data-src so it's easy to swap later
  const VIDEO_SRC = iframe.dataset.src;

  // ── Helpers ───────────────────────────────────────────────────────

  /** Opens the modal and starts the video */
  function openModal() {
    iframe.src = VIDEO_SRC;          // load / restart the video
    modal.removeAttribute('hidden'); // reveal (CSS transition kicks in)
    document.body.style.overflow = 'hidden'; // prevent body scroll
    closeBtn.focus();                // move focus into the dialog
  }

  /** Closes the modal and stops the video */
  function closeModal() {
    iframe.src = '';                 // stops playback immediately
    modal.setAttribute('hidden', '');
    document.body.style.overflow = '';
    openBtn.focus();                 // return focus to the trigger
  }

  // ── Event listeners ───────────────────────────────────────────────

  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);

  // Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.hasAttribute('hidden')) {
      closeModal();
    }
  });

  // Trap focus inside modal while open (Tab / Shift+Tab cycle)
  modal.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;

    const focusable = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last  = focusable[focusable.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

})();
