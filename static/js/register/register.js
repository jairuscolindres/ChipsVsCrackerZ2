/* ChipsvsCrackerZ - Register Interactions */
(function () {
  'use strict';
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
