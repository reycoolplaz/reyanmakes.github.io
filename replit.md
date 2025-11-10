# Reyan Makes - Personal Portfolio Website

## Overview
Personal portfolio website for Reyan Bhattacharjee, a high school maker and builder from Plainsboro, NJ. The site showcases his projects including welding, woodworking, and fabrication work.

## Project Type
Static HTML/CSS/JavaScript portfolio website

## Architecture
- **Frontend**: Pure HTML, CSS, and JavaScript (no framework)
- **Server**: Python 3.11 HTTP server serving static files
- **Port**: 5000 (configured for Replit webview)
- **Host**: 0.0.0.0 (allows proxy access)

## Project Structure
- `index.html` - Main homepage with hero, featured projects, timeline, about, and contact sections
- `styles.css` - All styling including responsive design and lightbox gallery
- `script.js` - Smooth scrolling navigation and intersection observer animations
- `lightbox.js` - Image gallery lightbox viewer with keyboard and touch support
- `projects/` - Individual project gallery pages (HTML files)
- `images/` - Project images organized in subdirectories
- `server.py` - Simple Python HTTP server with cache control headers

## Key Features
- Responsive design that works on desktop and mobile
- Smooth scrolling navigation
- Animated project cards on scroll
- Image lightbox gallery viewer
- Touch swipe support for mobile galleries
- Multiple project showcase pages

## Running the Project
The project runs automatically via the configured workflow:
- Command: `python server.py`
- Server binds to: `0.0.0.0:5000`
- Cache headers are disabled for development

## Recent Changes
- **2025-11-10**: Initial Replit setup & Comprehensive Mobile Optimization
  - Installed Python 3.11
  - Created HTTP server with cache control headers
  - Configured workflow for webview on port 5000
  - Configured deployment for autoscale
  
  - **Mobile Optimizations & Fullscreen Fix:**
    - Updated lightbox.js to properly handle dynamically loaded images
    - Fixed click-to-fullscreen functionality for all 13 gallery pages
    - Implemented true fullscreen lightbox on mobile devices (100vh/100vw)
    - Added improved touch feedback and visual cues for thumbnails
    - Enhanced swipe navigation for image galleries
    - Added proper event handling to prevent duplicate listeners
    - Gallery now loads thumbnails on mobile for faster performance
    - Fullscreen lightbox uses full viewport on mobile with solid black background
    - Improved touch controls with better button sizing and positioning
    - All gallery pages now properly call initializeGallery() after images load
  
  - **Mobile Look & Feel Enhancements:**
    - **Hero Section:** Increased font sizes, better spacing, full-width CTA button
    - **Navigation:** Improved touch targets and spacing
    - **Project Cards:** Better rounded corners (16px), larger images, optimized padding
    - **Typography:** Improved readability with larger base font (16px) and better line heights
    - **Gallery Grid:** Better spacing and box shadows on thumbnails
    - **Timeline:** Optimized layout with better spacing and typography
    - **About Section:** 2-column skills grid, improved text sizing
    - **Contact Section:** Stack buttons vertically, full-width with max-width constraint
    - **Section Titles:** Larger, more readable with proper padding
    - **Breadcrumb:** Better sizing and positioning
    - **Touch Interactions:** Added active states for all interactive elements
    - **Project Hero:** Improved sizing and spacing for better mobile experience
    - **Overall:** Better spacing throughout (3rem sections), improved visual hierarchy

## Notes
- Some featured project thumbnail images (gokart.jpg, lakehouse.jpg, bed.jpg) are referenced but not in the main images folder - they use fallback SVG placeholders
- All actual project images are stored in subdirectories under `images/`
- The site uses modern CSS features like CSS Grid, Flexbox, and CSS variables
- Gallery pages dynamically load images from JSON manifests in the `manifests/` directory
- On mobile (<768px), thumbnails are loaded first for performance, then full images shown in lightbox
- Touch interactions include visual feedback (opacity changes) for better UX
