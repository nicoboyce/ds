window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

// Extract tracking ID from the gtag script URL
const gtagScripts = document.querySelectorAll('script[src*="googletagmanager.com/gtag/js"]');
if (gtagScripts.length > 0) {
  const gtagSrc = gtagScripts[0].src;
  const trackingId = gtagSrc.match(/id=([^&]+)/);
  if (trackingId && trackingId[1]) {
    gtag("config", trackingId[1]);
  }
}