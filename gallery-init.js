/**
 * Universal Gallery Initialization Script
 * Include this in project pages after defining gallery, basePath, and manifestPath
 */

(function() {
    'use strict';
    
    function loadGallery() {
        if (typeof gallery === 'undefined' || typeof manifestPath === 'undefined' || typeof basePath === 'undefined') {
            console.error('Gallery configuration missing. Please define: gallery, basePath, and manifestPath');
            return;
        }

        const isMobile = window.innerWidth <= 768;
        const pathParts = basePath.split('/');
        const thumbPath = pathParts.slice(0, -1).join('/') + '/thumbnails/';

        fetch(manifestPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(manifest => {
                const subtitle = document.querySelector('.section-subtitle');
                if (subtitle && manifest.count) {
                    subtitle.textContent = `From concept to completion - ${manifest.count} images documenting the entire build process`;
                }

                manifest.images.forEach((filename, index) => {
                    const item = document.createElement('div');
                    item.className = 'gallery-item';

                    const img = document.createElement('img');
                    
                    const thumbFilename = filename.replace(/\.(jpg|jpeg|png|JPG|JPEG|PNG)$/i, '.jpg');
                    img.src = isMobile ? thumbPath + thumbFilename : basePath + filename;
                    
                    img.dataset.fullImage = basePath + filename;
                    img.alt = document.title || 'Gallery image';
                    img.className = 'gallery-image';
                    img.loading = 'lazy';

                    item.appendChild(img);
                    gallery.appendChild(item);
                });

                if (typeof initializeGallery === 'function') {
                    setTimeout(() => {
                        initializeGallery();
                    }, 100);
                }
            })
            .catch(error => {
                console.error('Error loading gallery:', error);
                gallery.innerHTML = `<p style="text-align:center; color: var(--text-light); padding: 2rem;">Unable to load images. Please try refreshing the page.</p>`;
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadGallery);
    } else {
        loadGallery();
    }
})();
