document.addEventListener('DOMContentLoaded', () => {
    // Menu Overlay Functionality
    const menuBtn = document.getElementById('menu-btn');
    const closeMenuBtn = document.getElementById('close-menu');
    const menuOverlay = document.getElementById('menu-overlay');

    if (menuBtn && menuOverlay) {
        menuBtn.addEventListener('click', () => {
            menuOverlay.classList.add('active');
        });
    }

    if (closeMenuBtn && menuOverlay) {
        closeMenuBtn.addEventListener('click', () => {
            menuOverlay.classList.remove('active');
        });
    }

    // Series Page: Hero Image & Thumbnails
    const heroImg = document.getElementById('hero-img');
    const thumbnails = document.querySelectorAll('.thumb');
    const heroPrev = document.getElementById('hero-prev');
    const heroNext = document.getElementById('hero-next');
    let currentIndex = 0;

    const updateHeroImage = (index) => {
        if (!thumbnails.length || !heroImg) return;
        
        // Remove active class from all
        thumbnails.forEach(t => t.classList.remove('active'));
        
        // Set new active
        const newActive = thumbnails[index];
        newActive.classList.add('active');
        
        // Fade effect
        heroImg.style.opacity = 0;
        setTimeout(() => {
            heroImg.src = newActive.src;
            heroImg.style.opacity = 1;
        }, 180);

        // Scroll thumbnail strip to keep active in view
        newActive.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        currentIndex = index;

        // Sync with lightbox if currently open
        if (lightbox && lightbox.classList.contains('active') && lightboxImg) {
            lightboxImg.src = newActive.src;
        }
    };

    if (thumbnails.length > 0) {
        thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('click', () => {
                updateHeroImage(index);
            });
        });

        if (heroPrev) {
            heroPrev.addEventListener('click', (e) => {
                e.stopPropagation();
                let newIdx = currentIndex - 1;
                if (newIdx < 0) newIdx = thumbnails.length - 1;
                updateHeroImage(newIdx);
            });
        }

        if (heroNext) {
            heroNext.addEventListener('click', (e) => {
                e.stopPropagation();
                let newIdx = currentIndex + 1;
                if (newIdx >= thumbnails.length) newIdx = 0;
                updateHeroImage(newIdx);
            });
        }
    }

    // Lightbox Functionality
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeLightboxBtn = document.getElementById('close-lightbox');
    const lbPrev = document.getElementById('lb-prev');
    const lbNext = document.getElementById('lb-next');

    const openLightbox = (src) => {
        if (!lightbox || !lightboxImg) return;
        lightboxImg.src = src;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // prevent scrolling background
    };

    const closeLightbox = () => {
        if (!lightbox) return;
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => {
            if (lightboxImg) lightboxImg.src = '';
        }, 300); 
    };

    // Hero image opens lightbox
    if (heroImg) {
        heroImg.addEventListener('click', () => {
            openLightbox(heroImg.src);
        });
    }

    if (closeLightboxBtn) {
        closeLightboxBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeLightbox();
        });
    }

    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            // Close if clicking anywhere in the backdrop outside the photo and navigation controls
            if (e.target !== lightboxImg && !e.target.closest('.lb-arrow') && !e.target.closest('.close-lightbox')) {
                closeLightbox();
            }
        });
    }

    if (lbPrev && heroPrev) {
        lbPrev.addEventListener('click', (e) => {
            e.stopPropagation();
            heroPrev.click();
        });
    }

    if (lbNext && heroNext) {
        lbNext.addEventListener('click', (e) => {
            e.stopPropagation();
            heroNext.click();
        });
    }

    // Keyboard Navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLightbox();
            if (menuOverlay && menuOverlay.classList.contains('active')) {
                menuOverlay.classList.remove('active');
            }
        }
        
        if (e.key === 'ArrowLeft') {
            if (lightbox && lightbox.classList.contains('active') && lbPrev) {
                lbPrev.click();
            } else if (heroPrev) {
                heroPrev.click();
            }
        }
        
        if (e.key === 'ArrowRight') {
            if (lightbox && lightbox.classList.contains('active') && lbNext) {
                lbNext.click();
            } else if (heroNext) {
                heroNext.click();
            }
        }
    });

    // PWA Service Worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('sw.js').catch(err => {
                console.log('SW Registration failed: ', err);
            });
        });
    }
});
