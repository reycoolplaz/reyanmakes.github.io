/**
 * Lightbox Image Viewer
 * Simple, responsive lightbox for image galleries
 */

class Lightbox {
    constructor() {
        this.currentIndex = 0;
        this.images = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        // Create lightbox HTML structure
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

        // Add to body
        document.body.insertAdjacentHTML('beforeend', lightboxHTML);

        // Get elements
        this.lightbox = document.getElementById('lightbox');
        this.lightboxImg = this.lightbox.querySelector('.lightbox-image');
        this.lightboxCounter = this.lightbox.querySelector('.lightbox-counter');
        this.closeBtn = this.lightbox.querySelector('.lightbox-close');
        this.prevBtn = this.lightbox.querySelector('.lightbox-prev');
        this.nextBtn = this.lightbox.querySelector('.lightbox-next');
        this.overlay = this.lightbox.querySelector('.lightbox-overlay');

        // Bind events
        this.bindEvents();
    }

    bindEvents() {
        // Close button
        this.closeBtn.addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', () => this.close());

        // Navigation buttons
        this.prevBtn.addEventListener('click', () => this.prev());
        this.nextBtn.addEventListener('click', () => this.next());

        // Keyboard navigation
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

        // Touch swipe support
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
                this.next(); // Swipe left = next
            } else {
                this.prev(); // Swipe right = previous
            }
        }
    }

    open(images, startIndex = 0) {
        this.images = images;
        this.currentIndex = startIndex;
        this.isOpen = true;

        this.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scroll

        this.updateImage();
    }

    close() {
        this.isOpen = false;
        this.lightbox.classList.remove('active');
        document.body.style.overflow = ''; // Restore scroll
    }

    updateImage() {
        const currentImage = this.images[this.currentIndex];

        // src is already the full image path (set in initializeGallery)
        this.lightboxImg.src = currentImage.src;
        this.lightboxImg.alt = currentImage.alt || '';

        // Update counter
        this.lightboxCounter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;

        // Show/hide navigation buttons
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

// Initialize lightbox when DOM is ready
let lightbox;
document.addEventListener('DOMContentLoaded', () => {
    lightbox = new Lightbox();

    // Auto-attach to gallery images
    initializeGallery();
});

/**
 * Initialize gallery - attach click handlers to images
 */
function initializeGallery() {
    const galleryImages = document.querySelectorAll('.gallery-image');

    galleryImages.forEach((img, index) => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
            // Get all images in the gallery - use full image path if available
            const allImages = Array.from(galleryImages).map(imgEl => ({
                src: imgEl.dataset.fullImage || imgEl.src,
                alt: imgEl.alt
            }));

            lightbox.open(allImages, index);
        });
    });
}
