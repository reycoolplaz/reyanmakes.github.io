/**
 * Lightbox Image Viewer
 * Simple, responsive lightbox for image galleries
 * Optimized for mobile with fullscreen support
 */

class Lightbox {
    constructor() {
        this.currentIndex = 0;
        this.images = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        const lightboxHTML = `
            <div class="lightbox" id="lightbox">
                <div class="lightbox-overlay"></div>
                <div class="lightbox-content">
                    <button class="lightbox-close" aria-label="Close">&times;</button>
                    <button class="lightbox-prev" aria-label="Previous">&#8249;</button>
                    <button class="lightbox-next" aria-label="Next">&#8250;</button>
                    <img class="lightbox-image" src="" alt="">
                    <div class="lightbox-counter"></div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', lightboxHTML);

        this.lightbox = document.getElementById('lightbox');
        this.lightboxImg = this.lightbox.querySelector('.lightbox-image');
        this.lightboxCounter = this.lightbox.querySelector('.lightbox-counter');
        this.closeBtn = this.lightbox.querySelector('.lightbox-close');
        this.prevBtn = this.lightbox.querySelector('.lightbox-prev');
        this.nextBtn = this.lightbox.querySelector('.lightbox-next');
        this.overlay = this.lightbox.querySelector('.lightbox-overlay');

        this.bindEvents();
    }

    bindEvents() {
        this.closeBtn.addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', () => this.close());

        this.prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.prev();
        });
        
        this.nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.next();
        });

        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;

            switch(e.key) {
                case 'Escape':
                    this.close();
                    break;
                case 'ArrowLeft':
                    this.prev();
                    break;
                case 'ArrowRight':
                    this.next();
                    break;
            }
        });

        let touchStartX = 0;
        let touchEndX = 0;

        this.lightboxImg.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        this.lightboxImg.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
        });
    }

    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        const diff = startX - endX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.next();
            } else {
                this.prev();
            }
        }
    }

    open(images, startIndex = 0) {
        this.images = images;
        this.currentIndex = startIndex;
        this.isOpen = true;

        this.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';

        this.updateImage();
    }

    close() {
        this.isOpen = false;
        this.lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    updateImage() {
        const currentImage = this.images[this.currentIndex];

        this.lightboxImg.src = currentImage.src;
        this.lightboxImg.alt = currentImage.alt || '';

        this.lightboxCounter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;

        this.prevBtn.style.display = this.currentIndex === 0 ? 'none' : 'block';
        this.nextBtn.style.display = this.currentIndex === this.images.length - 1 ? 'none' : 'block';
    }

    next() {
        if (this.currentIndex < this.images.length - 1) {
            this.currentIndex++;
            this.updateImage();
        }
    }

    prev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateImage();
        }
    }
}

let lightbox;
document.addEventListener('DOMContentLoaded', () => {
    lightbox = new Lightbox();
    initializeGallery();
});

function initializeGallery() {
    const galleryImages = document.querySelectorAll('.gallery-image');
    
    if (galleryImages.length === 0) {
        console.log('No gallery images found yet');
        return;
    }

    galleryImages.forEach((img, index) => {
        if (img.dataset.lightboxInitialized) {
            return;
        }
        
        img.dataset.lightboxInitialized = 'true';
        img.style.cursor = 'pointer';
        
        const clickHandler = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const allImages = Array.from(document.querySelectorAll('.gallery-image')).map(imgEl => ({
                src: imgEl.dataset.fullImage || imgEl.src,
                alt: imgEl.alt
            }));

            if (lightbox) {
                lightbox.open(allImages, index);
            }
        };
        
        img.addEventListener('click', clickHandler);
        img.addEventListener('touchend', (e) => {
            e.preventDefault();
            clickHandler(e);
        });
        
        img.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        });
        
        img.addEventListener('touchcancel', function() {
            this.style.opacity = '1';
        });
    });
    
    console.log(`Gallery initialized with ${galleryImages.length} images`);
}
