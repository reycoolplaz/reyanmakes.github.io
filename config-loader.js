// Synchronous site config loader - prevents flash of unstyled content
// This script should be in <head> and loads CSS before page renders
(function() {
    'use strict';

    // Determine if we're in a subdirectory
    const path = window.location.pathname;
    const isProjectPage = path.includes('/projects/');
    const prefix = isProjectPage ? '../' : '';

    // Synchronous XHR to load config (blocking intentionally to prevent FOUC)
    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', prefix + 'site-config.json', false); // false = synchronous
        xhr.send(null);

        if (xhr.status === 200) {
            const config = JSON.parse(xhr.responseText);
            const timestamp = Date.now();

            // Inject layout CSS
            if (config.layout) {
                document.write('<link rel="stylesheet" href="' + prefix + 'layouts/' + config.layout + '.css?v=' + timestamp + '">');
                // Store for body class
                window.__siteLayout = config.layout;
            }

            // Inject theme CSS
            if (config.theme) {
                document.write('<link rel="stylesheet" href="' + prefix + 'themes/' + config.theme + '.css?v=' + timestamp + '">');
                window.__siteTheme = config.theme;
            }
        }
    } catch (e) {
        console.warn('Could not load site config:', e);
    }

    // Add body classes when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        if (window.__siteLayout) {
            document.body.classList.add('layout-' + window.__siteLayout);
        }
        if (window.__siteTheme) {
            document.body.classList.add('theme-' + window.__siteTheme);
        }
    });
})();
