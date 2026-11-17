/* ChipsvsCrackerZ - Login Interactions */
(function () {
  'use strict';
  // Terminal input focus helper
  const inputs = document.querySelectorAll('.terminal-input-wrap input');
  inputs.forEach(input => {
    input.addEventListener('focus', () => {
      input.closest('.terminal-input-wrap').classList.add('focused');
    });
    input.addEventListener('blur', () => {
      input.closest('.terminal-input-wrap').classList.remove('focused');
    });
  });
})();
