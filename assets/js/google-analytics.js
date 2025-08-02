window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag("js", new Date());

// The tracking ID will be set by the calling page
if (window.GA_TRACKING_ID) {
  gtag("config", window.GA_TRACKING_ID);
}