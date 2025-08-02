function fixPageShort() {
  if (window.innerHeight > document.body.offsetHeight) {
    var footer = document.getElementById("footer");
    if (footer) {
      footer.style.position = "fixed";
      footer.style.bottom = "0";
      footer.style.right = "0";
      footer.style.left = "0";
      footer.style.width = "100%";
    }
  }
}

// Run on page load and resize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', fixPageShort);
} else {
  fixPageShort();
}

window.addEventListener('resize', fixPageShort);