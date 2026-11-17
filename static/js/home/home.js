/* ==========================================================================
   ChipsvsCrackerZ - Home / Dashboard Scripts
   ========================================================================== */

(function () {
  'use strict';

  // SFX Toggle
  const sfxBtn = document.getElementById('sfx-toggle-btn');
  if (sfxBtn) {
    let sfxEnabled = localStorage.getItem('sfx_enabled') !== 'false';
    const updateBtn = () => {
      sfxBtn.classList.toggle('active', sfxEnabled);
      sfxBtn.innerHTML = sfxEnabled ? '<span>🔊</span> SFX: ON' : '<span>🔇</span> SFX: OFF';
    };
    updateBtn();

    sfxBtn.addEventListener('click', () => {
      sfxEnabled = !sfxEnabled;
      localStorage.setItem('sfx_enabled', sfxEnabled ? 'true' : 'false');
      updateBtn();
    });
  }
})();
