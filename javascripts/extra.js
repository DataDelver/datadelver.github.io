/* Reading Progress Bar */
(function() {
  function updateProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
    document.body.style.setProperty('--progress-width', progress + '%');
  }

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();
})();
