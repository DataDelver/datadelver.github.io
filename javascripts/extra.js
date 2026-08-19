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

/* Share Link Copy */
(function() {
  const button = document.querySelector(".md-post__share-copy");
  if (!button) return;

  function showCopied() {
    const original = button.innerHTML;
    button.classList.add("copied");
    button.innerHTML = "Copied!";
    setTimeout(function() {
      button.classList.remove("copied");
      button.innerHTML = original;
    }, 2000);
  }

  function fallbackCopy(text) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  button.addEventListener("click", function() {
    const url = button.dataset.shareUrl;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(showCopied, function() {
        fallbackCopy(url);
        showCopied();
      });
    } else {
      fallbackCopy(url);
      showCopied();
    }
  });
})();
