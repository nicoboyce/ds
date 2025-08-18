// YouTube facade script for lazy loading
document.addEventListener('DOMContentLoaded', function() {
  const facade = document.querySelector('.youtube-facade');
  if (facade) {
    facade.addEventListener('click', function() {
      const videoId = this.getAttribute('data-video-id');
      const iframe = document.createElement('iframe');
      iframe.setAttribute('src', 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&cc_load_policy=1&cc_lang_pref=en');
      iframe.setAttribute('title', 'Zendesk tips and tech contractor life video');
      iframe.setAttribute('allow', 'autoplay; encrypted-media');
      iframe.setAttribute('allowfullscreen', '');
      iframe.style.position = 'absolute';
      iframe.style.top = '0';
      iframe.style.left = '0';
      iframe.style.width = '100%';
      iframe.style.height = '100%';
      iframe.style.border = 'none';
      
      this.innerHTML = '';
      this.appendChild(iframe);
    });
  }
});