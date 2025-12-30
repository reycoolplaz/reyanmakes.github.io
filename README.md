# Reyan Makes - Portfolio Website

Personal portfolio website showcasing maker projects, woodworking, welding, photography, and creative work by Reyan Bhattacharjee.

Framework-free static site with an automated build system. Just add images and run one command.

## Quick Start

```bash
# Build the site (after adding/removing images)
python3 build_site.py

# Run server
./run.sh        # dev mode (Flask)
./run.sh prod   # production mode (Gunicorn)
```

Then visit:
- **Main site**: http://localhost:5000
- **Admin panel**: http://localhost:5000/admin

## Directory Structure

```
reyanmakes.github.io/
├── images/                    # Source images (add your photos here)
├── gen/                       # Auto-generated output
│   ├── thumbnails/            # 200x200 optimized thumbnails
│   ├── manifests/             # JSON image lists
│   └── site-index.json        # Complete project index
├── projects/                  # Auto-generated gallery pages
├── layouts/                   # Gallery layout styles (CSS)
├── themes/                    # Site themes
│
├── build_site.py              # Master build script
├── server.py                  # Flask dev server + admin API
├── projects-metadata.json     # Project titles, descriptions, tags
├── image-orders.json          # Custom image ordering
├── hidden-images.json         # Images to hide from galleries
│
├── index.html                 # Homepage
├── admin-enhanced.html        # Admin panel UI
├── styles.css                 # Site styles
├── lightbox.js                # Gallery viewer
├── script.js                  # Navigation
│
├── convert_heic.py            # Convert HEIC images
├── convert_cr2.py             # Convert CR2 raw images
├── run.sh                     # Start server (dev/prod)
└── .env.example               # Environment template
```

## Workflow

### Add/Remove Images
1. Add or remove files in `images/Your-Project/`
2. Run `python3 build_site.py`
3. Commit and push

### Create New Project
1. Create folder under `images/` with photos
2. (Optional) Edit `projects-metadata.json` for title/description
3. Run build script - gallery page auto-generated

### Admin Panel
Web interface at `/admin` to:
- Run builds with one click
- Monitor build progress
- Manage project metadata
- Reorder/hide images

## Requirements

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

Dependencies: Flask, Pillow, Gunicorn

## Tips

- **Supported formats**: JPG, JPEG, PNG, GIF, WEBP
- **Image size**: Keep under ~5 MB for faster loading
- **File naming**: Use descriptive names (manifests are alphabetical)
- **Preview**: Always test through server, not `file://`
- **Convert images**: Use `convert_heic.py` / `convert_cr2.py` for raw files
