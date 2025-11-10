# Reyan Makes Portfolio Website

Personal site for Reyan Bhattacharjee showcasing hands-on builds, project galleries, and tooling scripts for keeping everything in sync. The repo is intentionally framework-free so it can be hosted anywhere static files are supported (GitHub Pages, Replit, etc.).

## Tech Stack & Key Pieces
- Static HTML (`index.html` plus `projects/*.html`) styled by a single `styles.css`
- Vanilla JS for UX (`script.js` for navigation/animations, `lightbox.js` + `gallery-init.js` for galleries)
- Python helper scripts to auto-generate JSON manifests, thumbnails, and project pages
- Simple dev server (`server.py`) with cache-busting headers for local previews on port 5000

## Repository Structure
```
reyanmakes.github.io/
├── index.html            # Landing page with hero, featured work, timeline, about/contact
├── styles.css            # Global design system + responsive layout
├── script.js             # Smooth scrolling, IntersectionObserver animations
├── lightbox.js           # Fullscreen gallery viewer with keyboard & touch support
├── gallery-init.js       # Fetches manifests, injects gallery images, hooks lightbox
├── projects/             # Generated project galleries (include gallery-init + lightbox)
├── images/
│   ├── Engeneering/      # Project photos (each folder can include thumbnails/)
│   └── Drawings/         # Sketch archives (also supports thumbnails/)
├── manifests/            # Auto-generated JSON image manifests (plus manifests/bsa/)
├── generate_manifests.py # Scans images/* and writes manifests
├── generate_thumbnails.py# Creates 200px JPEG thumbs for mobile perf
├── generate_project_pages.py # Renders HTML pages from manifests + metadata
├── convert_*.py          # Optional helpers for HEIC/CR2 to JPEG
└── server.py             # Local preview server
```

## Local Development
1. (Optional) Activate a virtualenv if you plan to run the Python helpers.
2. Install Pillow if you need thumbnail generation: `pip install Pillow`.
3. Launch the dev server: `python server.py` → visit `http://localhost:5000`.
4. Manual reloads are enough—there is no build step.

## Content Workflow
### Add or Remove Project Images
1. Drop/remove files inside the relevant folder under `images/Engeneering/YourProject/` (or `images/Drawings/`).
2. Run `python generate_manifests.py` so JSON stays in sync.
3. (Recommended) Run `python generate_thumbnails.py` to refresh 200px thumbs for mobile.
4. Commit images **and** updated manifests/thumbnails.

### Create a New Project Gallery
1. Add a new folder under `images/Engeneering/YourProject/` and populate it with photos.
2. Regenerate manifests and thumbnails (commands above).
3. Add metadata for the new key inside `PROJECT_METADATA` (or `BSA_METADATA`) in `generate_project_pages.py`.
4. Run `python generate_project_pages.py` to emit the corresponding HTML into `projects/`.
5. Link to the new page from `index.html` (featured card, timeline item, etc.).

### Update Homepage Imagery
- Hero/featured cards expect `images/gokart.jpg`, `images/lakehouse.jpg`, and `images/bed.jpg`. Replace those filenames directly to update the tiles; the markup already includes SVG fallbacks if a file is missing.

## Tips & Gotchas
- Supported formats: JPG, JPEG, PNG, GIF, WEBP (others should be converted first).
- Filenames matter: manifests are alphabetical, so use descriptive, zero-padded names if order is important.
- When previewing galleries locally, always run through `server.py`; the fetch API requires an HTTP origin to load manifests.
- Keep raw images below ~5 MB for faster publish times—use the provided `convert_heic.py` / `convert_cr2.py` scripts if needed.

With this workflow every gallery page stays in sync with the filesystem, lightbox interactions work on desktop/mobile, and publishing new projects is just a matter of dropping photos plus a quick manifest refresh.
