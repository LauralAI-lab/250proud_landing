// Copyright © 2026 Today In History. All rights reserved. White-Label Distribution.
(function() {
    // 1. Locate the script element to extract configuration attributes
    const scripts = document.getElementsByTagName('script');
    let currentScript = null;
    
    // Find this script in the DOM
    for (let i = 0; i < scripts.length; i++) {
        if (scripts[i].src && scripts[i].src.indexOf('tih-widget-loader.js') !== -1) {
            currentScript = scripts[i];
            break;
        }
    }

    if (!currentScript) {
        // Fallback: use the last script tag if not found by name
        currentScript = scripts[scripts.length - 1];
    }

    // 2. Extract configuration parameters with safe defaults
    const color = currentScript.getAttribute('data-color') || '#D4AF37';
    const ctaText = currentScript.getAttribute('data-cta-text') || 'Find Your Home';
    const ctaLink = currentScript.getAttribute('data-cta-link') || 'https://250proud.net';
    const theme = currentScript.getAttribute('data-theme') || 'dark';

    // 3. Find or create the target container
    let container = document.getElementById('tih-widget-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'tih-widget-container';
        // Insert right before the script tag for plug-and-play ease
        currentScript.parentNode.insertBefore(container, currentScript);
    }

    // Ensure container has clean layout properties
    container.style.width = '100%';
    container.style.maxWidth = '900px';
    container.style.margin = '0 auto';
    container.style.padding = '0';

    // 4. Create the iframe
    const iframe = document.createElement('iframe');
    
    // Base URL of the hosted widget
    const baseUrl = 'https://250proud.net/tih-widget.html';
    
    // Build query params
    const queryParams = new URLSearchParams({
        primaryColor: color,
        ctaText: ctaText,
        ctaLink: ctaLink,
        theme: theme
    });

    iframe.src = `${baseUrl}?${queryParams.toString()}`;
    iframe.style.width = '100%';
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';
    iframe.style.display = 'block';
    iframe.style.borderRadius = '16px';
    iframe.scrolling = 'no';
    
    // Set safe starting heights
    const isMobile = window.innerWidth <= 768;
    iframe.style.height = isMobile ? '760px' : '520px';

    container.appendChild(iframe);

    // 5. Setup dynamic height resizing via postMessage
    window.addEventListener('message', function(event) {
        // Check if message is a resize request from our widget
        if (event.data && event.data.type === 'tih-resize' && event.data.height) {
            iframe.style.height = event.data.height + 'px';
        }
    });
})();
