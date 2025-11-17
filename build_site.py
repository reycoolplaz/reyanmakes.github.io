#!/usr/bin/env python3
"""
Master Site Builder - Automated Website Content Generation
==========================================================

This script orchestrates the entire website build process:
1. Scans images folder structure automatically
2. Generates thumbnails in /gen/thumbnails/
3. Creates manifest JSON files in /gen/manifests/
4. Generates project gallery pages
5. Creates site index

Usage: python3 build_site.py

After adding/removing images, just run this script and everything updates!
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent
IMAGES_BASE = BASE_DIR / 'images'
GEN_BASE = BASE_DIR / 'gen'
THUMBNAILS_BASE = GEN_BASE / 'thumbnails'
MANIFESTS_BASE = GEN_BASE / 'manifests'
PROJECTS_BASE = BASE_DIR / 'projects'
METADATA_FILE = BASE_DIR / 'projects-metadata.json'

THUMBNAIL_SIZE = (200, 200)
THUMBNAIL_QUALITY = 75

ASSET_VERSION = datetime.now().strftime("%Y%m%d")

# Folders to exclude from processing
EXCLUDE_FOLDERS = {'thumbnails', 'gen', '.git', '__pycache__', 'venv', 'node_modules', '.DS_Store'}

# Image extensions to process
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP'}

# ============================================================================
# LOAD PROJECT METADATA
# ============================================================================

def load_metadata():
    """Load project metadata from JSON file"""
    if not METADATA_FILE.exists():
        print(f"⚠️  Warning: {METADATA_FILE} not found. Using defaults.")
        return {"projects": {}, "defaults": {}}

    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

# ============================================================================
# STEP 1: DISCOVER IMAGE FOLDERS
# ============================================================================

def discover_image_folders(base_path):
    """
    Discover top-level project folders containing images
    Skips nested subfolders to avoid duplicate galleries
    Returns dict mapping project_slug -> folder_path
    """
    print("🔍 Discovering image folders...")

    discovered = {}

    def scan_directory(path, depth=0, max_depth=3):
        """Scan directories for images, limited depth to avoid nested duplicates"""
        if not path.is_dir():
            return

        # Skip excluded folders and special subfolders
        if path.name in EXCLUDE_FOLDERS or path.name.lower() in ['final', 'page1', 'page2', 'section1-process', 'section2-team', 'shelf_final', 'temple final']:
            return

        # Skip if too deep (prevents nested galleries)
        if depth > max_depth:
            return

        # Check if this folder contains images
        images = [f for f in path.iterdir()
                 if f.is_file() and f.suffix in IMAGE_EXTENSIONS]

        if images:
            # Create slug from relative path
            rel_path = path.relative_to(base_path)
            slug = str(rel_path).lower().replace(' ', '-').replace('/', '-')

            discovered[slug] = {
                'path': path,
                'rel_path': rel_path,
                'image_count': len(images),
                'images': sorted([img.name for img in images])
            }

            print(f"  ✓ Found: {rel_path} ({len(images)} images) -> {slug}")

        # Always recurse into subdirectories unless too deep
        for subdir in sorted(path.iterdir()):
            if subdir.is_dir() and subdir.name not in EXCLUDE_FOLDERS:
                scan_directory(subdir, depth + 1, max_depth)

    scan_directory(base_path)

    print(f"\n📊 Discovered {len(discovered)} image folders\n")
    return discovered

# ============================================================================
# STEP 2: GENERATE THUMBNAILS
# ============================================================================

def generate_thumbnail(image_path, thumb_path, size=THUMBNAIL_SIZE):
    """Generate a thumbnail for an image"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Ensure parent directory exists
            thumb_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as JPEG with reduced quality
            img.save(thumb_path, 'JPEG', quality=THUMBNAIL_QUALITY, optimize=True)
            return True
    except Exception as e:
        print(f"    ⚠️  Error processing {image_path.name}: {e}")
        return False

def generate_all_thumbnails(discovered_folders):
    """Generate thumbnails for all images"""
    print("📸 Generating thumbnails in /gen/thumbnails/...\n")

    total_images = 0
    total_thumbnails = 0
    total_new = 0

    for slug, info in discovered_folders.items():
        folder_path = info['path']
        rel_path = info['rel_path']

        # Create thumbnail directory mirroring source structure
        thumb_dir = THUMBNAILS_BASE / rel_path
        thumb_dir.mkdir(parents=True, exist_ok=True)

        new_thumbs = 0
        for img_name in info['images']:
            img_file = folder_path / img_name
            thumb_file = thumb_dir / f"{img_file.stem}.jpg"

            total_images += 1

            # Skip if thumbnail exists and is newer
            if thumb_file.exists() and thumb_file.stat().st_mtime > img_file.stat().st_mtime:
                total_thumbnails += 1
                continue

            if generate_thumbnail(img_file, thumb_file):
                total_thumbnails += 1
                new_thumbs += 1
                total_new += 1

        if new_thumbs > 0:
            print(f"  ✓ {rel_path}: {new_thumbs} new thumbnails")

    print(f"\n  📊 Thumbnails: {total_thumbnails}/{total_images} ({total_new} new)\n")
    return total_thumbnails

# ============================================================================
# STEP 3: GENERATE MANIFESTS
# ============================================================================

def generate_manifest(slug, info):
    """Generate JSON manifest for a project"""
    manifest = {
        "project": str(info['rel_path']),
        "slug": slug,
        "count": info['image_count'],
        "images": info['images'],
        "generated": datetime.now().isoformat()
    }

    # Determine manifest path
    manifest_file = MANIFESTS_BASE / f"{slug}.json"
    manifest_file.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest_file

def generate_all_manifests(discovered_folders):
    """Generate manifest files for all projects"""
    print("📋 Generating manifests in /gen/manifests/...\n")

    for slug, info in discovered_folders.items():
        manifest_file = generate_manifest(slug, info)
        rel_manifest = manifest_file.relative_to(BASE_DIR)
        print(f"  ✓ {slug} → {rel_manifest}")

    print(f"\n  📊 Generated {len(discovered_folders)} manifests\n")

# ============================================================================
# STEP 4: GENERATE PROJECT PAGES
# ============================================================================

def get_project_metadata(slug, metadata_db, defaults):
    """Get metadata for a project, falling back to defaults"""
    if slug in metadata_db:
        return metadata_db[slug]

    # Create default metadata
    title = slug.replace('-', ' ').title()
    return {
        "title": title,
        "year": defaults.get("year", "2024"),
        "tags": defaults.get("tags", "Project • Build • Maker"),
        "description": defaults.get("description", f"Project gallery for {title}."),
        "featured": False,
        "category": "makers"
    }

def generate_project_page(slug, info, metadata):
    """Generate HTML page for a project"""

    rel_path = info['rel_path']
    image_count = info['image_count']

    # Relative paths for assets
    asset_prefix = '../'
    version_suffix = f'?v={ASSET_VERSION}'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} | Reyan Makes</title>
    <meta name="description" content="{metadata['description']}">
    <link rel="stylesheet" href="{asset_prefix}styles.css{version_suffix}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="{asset_prefix}index.html" class="logo">Reyan Makes</a>
            <ul class="nav-menu">
                <li><a href="{asset_prefix}index.html" class="nav-link">Home</a></li>
                <li><a href="{asset_prefix}index.html#featured" class="nav-link">Featured</a></li>
                <li><a href="{asset_prefix}index.html#timeline" class="nav-link">Journey</a></li>
                <li><a href="{asset_prefix}index.html#about" class="nav-link">About</a></li>
                <li><a href="{asset_prefix}index.html#contact" class="nav-link">Contact</a></li>
            </ul>
        </div>
    </nav>

    <div class="breadcrumb">
        <div class="container">
            <ul class="breadcrumb-list">
                <li><a href="{asset_prefix}index.html" class="breadcrumb-link">Home</a></li>
                <li><span class="breadcrumb-current">{metadata['title']}</span></li>
            </ul>
        </div>
    </div>

    <section class="project-hero">
        <div class="project-hero-content">
            <h1>{metadata['title']}</h1>
            <div class="project-hero-meta">
                <span class="year-badge">{metadata['year']}</span>
                <span>•</span>
                <span>{metadata['tags']}</span>
            </div>
            <p class="project-hero-description">
                {metadata['description']}
            </p>
        </div>
    </section>

    <section style="padding: 4rem 0; background: var(--bg-secondary);">
        <div class="container">
            <h2 class="section-title">Gallery</h2>
            <p class="section-subtitle">Documenting the entire process - {image_count} images</p>

            <div class="gallery-grid" id="gallery">
                <!-- Images will be loaded dynamically from the manifest -->
            </div>
        </div>
    </section>

    <section style="padding: 3rem 0; text-align: center;">
        <div class="container">
            <a href="{asset_prefix}index.html" class="contact-button">← Back to Home</a>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Reyan Bhattacharjee | Built with passion</p>
        </div>
    </footer>

    <script src="{asset_prefix}lightbox.js{version_suffix}"></script>
    <script>
        // Load gallery images dynamically from manifest
        const gallery = document.getElementById('gallery');
        const basePath = '{asset_prefix}images/{rel_path}/';
        const thumbPath = '{asset_prefix}gen/thumbnails/{rel_path}/';
        const manifestPath = '{asset_prefix}gen/manifests/{slug}.json';
        const isMobile = window.innerWidth <= 768;

        fetch(manifestPath)
            .then(response => {{
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(manifest => {{
                manifest.images.forEach(filename => {{
                    const item = document.createElement('div');
                    item.className = 'gallery-item';

                    const img = document.createElement('img');
                    const thumbFilename = filename.replace(/\\.(jpg|jpeg|png|JPG|JPEG|PNG)$/i, '.jpg');
                    img.src = isMobile ? thumbPath + thumbFilename : basePath + filename;
                    img.dataset.fullImage = basePath + filename;
                    img.alt = '{metadata['title']}';
                    img.className = 'gallery-image';
                    img.loading = 'lazy';

                    item.appendChild(img);
                    gallery.appendChild(item);
                }});

                if (typeof initializeGallery === 'function') {{
                    initializeGallery();
                }}
            }})
            .catch(error => {{
                console.error('Error loading gallery:', error);
                gallery.innerHTML = `<p style="text-align:center; color: var(--text-light);">Error loading images: ${{error.message}}. Please try refreshing the page.</p>`;
            }});
    </script>
</body>
</html>
'''

    return html

def generate_all_project_pages(discovered_folders, metadata_config):
    """Generate HTML pages for all projects"""
    print("📄 Generating project pages in /projects/...\n")

    # Ensure projects directory exists
    PROJECTS_BASE.mkdir(parents=True, exist_ok=True)

    projects_meta = metadata_config.get("projects", {})
    defaults = metadata_config.get("defaults", {})

    for slug, info in discovered_folders.items():
        metadata = get_project_metadata(slug, projects_meta, defaults)

        output_file = PROJECTS_BASE / f"{slug}.html"
        html = generate_project_page(slug, info, metadata)

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"  ✓ {slug}.html ({info['image_count']} images)")

    print(f"\n  📊 Generated {len(discovered_folders)} project pages\n")

# ============================================================================
# STEP 5: GENERATE SITE INDEX
# ============================================================================

def generate_site_index(discovered_folders, metadata_config):
    """Generate a JSON index of all projects for easy reference"""
    print("📇 Generating site index...\n")

    projects_meta = metadata_config.get("projects", {})
    defaults = metadata_config.get("defaults", {})

    index = {
        "generated": datetime.now().isoformat(),
        "total_projects": len(discovered_folders),
        "total_images": sum(info['image_count'] for info in discovered_folders.values()),
        "projects": {}
    }

    for slug, info in discovered_folders.items():
        metadata = get_project_metadata(slug, projects_meta, defaults)

        index["projects"][slug] = {
            "path": str(info['rel_path']),
            "images": info['image_count'],
            "title": metadata['title'],
            "year": metadata['year'],
            "tags": metadata['tags'],
            "category": metadata.get('category', 'makers'),
            "featured": metadata.get('featured', False),
            "page": f"projects/{slug}.html",
            "manifest": f"gen/manifests/{slug}.json"
        }

    index_file = GEN_BASE / 'site-index.json'
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"  ✓ Site index: {index_file.relative_to(BASE_DIR)}")
    print(f"  📊 {index['total_projects']} projects, {index['total_images']} total images\n")

    return index

# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Main build process"""
    print("=" * 70)
    print("🏗️  REYAN MAKES - AUTOMATED SITE BUILDER")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Ensure gen directories exist
    GEN_BASE.mkdir(exist_ok=True)
    THUMBNAILS_BASE.mkdir(exist_ok=True)
    MANIFESTS_BASE.mkdir(exist_ok=True)

    try:
        # Load metadata
        print("📖 Loading project metadata...\n")
        metadata_config = load_metadata()
        print(f"  ✓ Loaded {len(metadata_config.get('projects', {}))} project metadata entries\n")

        # Step 1: Discover all image folders
        discovered = discover_image_folders(IMAGES_BASE)

        if not discovered:
            print("\n⚠️  No image folders found! Check your images directory.")
            return 1

        # Step 2: Generate thumbnails
        generate_all_thumbnails(discovered)

        # Step 3: Generate manifests
        generate_all_manifests(discovered)

        # Step 4: Generate project pages
        generate_all_project_pages(discovered, metadata_config)

        # Step 5: Generate site index
        site_index = generate_site_index(discovered, metadata_config)

        print("=" * 70)
        print("✅ BUILD COMPLETE!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"  • Projects: {site_index['total_projects']}")
        print(f"  • Total Images: {site_index['total_images']}")
        print(f"  • Thumbnails: /gen/thumbnails/")
        print(f"  • Manifests: /gen/manifests/")
        print(f"  • Pages: /projects/")
        print("\n📝 Next steps:")
        print("  1. Review generated files in /gen/ and /projects/")
        print("  2. Update index.html if needed")
        print("  3. Test the site locally")
        print("  4. Commit and deploy!")
        print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        return 0

    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
