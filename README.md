# Reyan Makes - Portfolio Website

Personal portfolio website showcasing maker projects, woodworking, welding, photography, and creative work by Reyan Bhattacharjee.

The site is intentionally framework-free and uses an **automated build system** to keep everything in sync. Just add images and run one command!

## 🚀 Quick Start - The Easy Way

**Just added new images? Run this ONE command:**

```bash
python3 build_site.py
```

That's it! The script automatically:
- ✅ Discovers all image folders
- ✅ Generates optimized thumbnails in `/gen/thumbnails/`
- ✅ Creates manifest files in `/gen/manifests/`
- ✅ Generates project gallery pages
- ✅ Updates the complete site index

## 🛠️ Tech Stack

- Static HTML + CSS (no framework)
- Vanilla JavaScript for navigation and lightbox galleries
- Python build system for automation
- PIL/Pillow for image processing

## 📁 Directory Structure

```
reyanmakes.github.io/
├── images/                          # 📸 ADD YOUR IMAGES HERE
│   ├── Makers stuff/
│   │   ├── Go-Cart/
│   │   ├── Furniture/
│   │   ├── metal-work/
│   │   └── wood-work/
│   ├── photograph/
│   ├── sketching/
│   └── school/
│
├── gen/                             # ⚙️ AUTO-GENERATED (by build_site.py)
│   ├── thumbnails/                  # Optimized 200x200 thumbnails
│   ├── manifests/                   # JSON image lists
│   └── site-index.json              # Complete project index
│
├── projects/                        # 📄 AUTO-GENERATED PAGES
│   ├── makers-stuff-go-cart.html
│   ├── photograph.html
│   └── ... (17 project pages)
│
├── build_site.py                    # 🏗️ MASTER BUILD SCRIPT (RUN THIS!)
├── projects-metadata.json           # ✏️ EDIT PROJECT INFO HERE
├── index.html                       # Main homepage
├── styles.css                       # Site styling
├── lightbox.js                      # Gallery viewer
└── README.md                        # This file
```

## 🖥️ Local Development

### Quick Start
```bash
# Run the development server (automatically sets up venv)
./run_server.sh
```

Or manually:
```bash
# Install dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Start server
./venv/bin/python server.py
```

Then visit:
- **Main site**: http://localhost:5000
- **Admin panel**: http://localhost:5000/admin

### Admin Panel Features

The admin panel (`/admin`) provides a web interface to:
- ✅ Run the build script with a button click
- ✅ Monitor build progress in real-time
- ✅ View build output and logs
- ✅ Check build status and history

**Default password**: `reyan2025` (change via `ADMIN_PASSWORD` environment variable)

## 📸 Content Workflow

### Two Ways to Build

#### Option 1: Command Line (Fastest)
```bash
# After adding/removing images
python3 build_site.py
```

#### Option 2: Admin Panel (Easiest)
1. Start the server: `./run_server.sh`
2. Visit http://localhost:5000/admin
3. Login with password: `reyan2025`
4. Click "Run Build Script" button
5. Watch progress in real-time

### Add or Remove Project Images
1. Drop/remove files in `images/Your Project/`
2. Run build (command line or admin panel)
3. Commit and push

### Create a New Project Gallery
1. Create folder under `images/` with your photos
2. (Optional) Edit `projects-metadata.json` to add title, description, tags
3. Run build script
4. Done! New gallery page auto-generated

## Tips & Gotchas
- Supported formats: JPG, JPEG, PNG, GIF, WEBP (others should be converted first).
- Filenames matter: manifests are alphabetical, so use descriptive, zero-padded names if order is important.
- When previewing galleries locally, always run through `server.py`; the fetch API requires an HTTP origin to load manifests.
- Keep raw images below ~5 MB for faster publish times—use the provided `convert_heic.py` / `convert_cr2.py` scripts if needed.

## 🎯 Key Files

- `build_site.py` - Master build script (run after image changes)
- `projects-metadata.json` - Edit project titles, descriptions, tags
- `server.py` - Flask development server with admin API
- `admin.html` - Web-based admin panel for builds
- `run_server.sh` - Quick start script for development
- `requirements.txt` - Python dependencies (Flask, Pillow)
- `/gen/` - Auto-generated (thumbnails, manifests, index)
- `/projects/` - Auto-generated gallery pages

## 💡 Tips & Best Practices

- **Image formats**: JPG, JPEG, PNG, GIF, WEBP supported
- **File naming**: Use descriptive names; manifests are alphabetical
- **Image size**: Keep under ~5 MB for faster loading
- **Admin panel**: Best for quick builds when testing locally
- **Command line**: Best for automation and batch operations
- **Preview**: Always test galleries through the server (not file://)

---

**Quick Help**:
- Command line build: `python3 build_site.py`
- Web admin panel: `./run_server.sh` → http://localhost:5000/admin (password: `reyan2025`)
