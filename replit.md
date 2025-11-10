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
- **2025-11-10**: Initial Replit setup
  - Installed Python 3.11
  - Created HTTP server with cache control headers
  - Configured workflow for webview on port 5000
  - Verified site loads and displays correctly

## Notes
- Some featured project thumbnail images (gokart.jpg, lakehouse.jpg, bed.jpg) are referenced but not in the main images folder - they use fallback SVG placeholders
- All actual project images are stored in subdirectories under `images/`
- The site uses modern CSS features like CSS Grid, Flexbox, and CSS variables
