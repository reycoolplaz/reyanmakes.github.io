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

## 📝 Complete Workflow

### 1. Setup (One Time)

```bash
pip install Pillow
```

### 2. Add New Project

```bash
# Add images
mkdir "images/My Cool Project"
cp ~/Downloads/*.jpg "images/My Cool Project/"

# Edit projects-metadata.json (optional)
# Run build
python3 build_site.py
```

### 3. Update Existing Project

```bash
# Add/remove images
cp ~/more-photos/*.jpg "images/Existing Project/"

# Rebuild
python3 build_site.py
```

## 🎯 Key Files

- `projects-metadata.json` - Edit project info here
- `build_site.py` - Run this after any changes
- `/gen/` - Auto-generated (thumbnails, manifests, index)
- `/projects/` - Auto-generated gallery pages

---

**Need help?** Run `python3 build_site.py` to regenerate everything!
