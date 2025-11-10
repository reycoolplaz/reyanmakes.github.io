# Reyan Makes - Portfolio Website

## Overview
Personal portfolio website for Reyan Bhattacharjee, showcasing maker projects including woodworking, welding, and creative builds. This is a static website originally hosted on GitHub Pages (reyanmakes.github.io).

**Project Type:** Static HTML/CSS/JavaScript portfolio
**Current State:** Ready to serve - all project pages and manifests are pre-generated
**Last Updated:** November 10, 2025

## Project Structure

```
.
├── index.html              # Main portfolio homepage
├── styles.css              # Global styles
├── script.js               # Homepage interactions
├── lightbox.js            # Image gallery lightbox functionality
├── images/                # All project images
│   ├── Drawings/          # Art and sketches
│   └── Engeneering/       # Engineering projects
│       ├── Bed/
│       ├── BSA/           # Boy Scout projects
│       ├── Baby Head/
│       └── [other projects]
├── projects/              # Pre-generated project gallery pages
│   ├── gokart.html
│   ├── bed.html
│   ├── lakehouse.html
│   └── [other projects]
├── manifests/             # JSON manifests listing images for each project
│   ├── gokart.json
│   ├── bed.json
│   └── bsa/              # BSA sub-projects
└── [Python build scripts] # Used to regenerate content when images change
```

## How It Works

### Runtime
- Simple static HTTP server serves HTML, CSS, JS, images, and JSON manifests
- Gallery pages dynamically load image lists from JSON manifests via client-side fetch
- Lightbox provides full-screen image viewing with keyboard/touch navigation
- No server-side processing required at runtime

### Content Updates (Optional)
Python scripts are used **only when adding/removing images** (not needed for deployment):

1. `generate_thumbnails.py` - Creates thumbnail versions of images
2. `generate_manifests.py` - Scans image folders and creates JSON manifests
3. `generate_project_pages.py` - Generates gallery HTML pages from manifests
4. `convert_heic.py` / `convert_cr2.py` - Convert image formats if needed

**Workflow for adding new images:**
1. Add images to appropriate folder in `images/`
2. Run `python3 generate_thumbnails.py` (if needed)
3. Run `python3 generate_manifests.py`
4. Run `python3 generate_project_pages.py`
5. Redeploy static files

## Deployment Setup

### Development (Current)
- Workflow: `python3 -m http.server 5000`
- Port: 5000 (required for Replit webview)
- Host: 0.0.0.0 (automatic with Python http.server)

### Production
Simple static site deployment - no special configuration needed:
- All content is pre-generated
- No build step required
- No dependencies at runtime

## Architecture Notes
- **Frontend-only:** All image loading happens client-side via fetch API
- **Manifest-driven:** Gallery contents defined in JSON files, not hardcoded
- **Responsive:** Mobile-friendly design with CSS Grid layouts
- **Performance:** Lazy loading for images, intersection observer for animations

## Recent Changes
- November 10, 2025: Imported from GitHub, configured for Replit deployment
  - Static server workflow set up on port 5000 for webview compatibility
  - Fixed GitHub link to point to correct repository: https://github.com/reycoolplaz/reyanmakes.github.io
  - Deployment configuration set up for autoscale static hosting
