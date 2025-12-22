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
IMAGE_ORDER_FILE = BASE_DIR / 'image-orders.json'
HIDDEN_IMAGES_FILE = BASE_DIR / 'hidden-images.json'

THUMBNAIL_SIZE = (800, 800)
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


def load_image_orders():
    """Load custom image orders from JSON file"""
    if not IMAGE_ORDER_FILE.exists():
        return {}

    with open(IMAGE_ORDER_FILE, 'r') as f:
        return json.load(f)


def load_hidden_images():
    """Load hidden images from JSON file"""
    if not HIDDEN_IMAGES_FILE.exists():
        return {}

    with open(HIDDEN_IMAGES_FILE, 'r') as f:
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

def generate_manifest(slug, info, image_orders=None, hidden_images=None):
    """Generate JSON manifest for a project"""
    images = info['images'].copy()

    # Filter out hidden images
    if hidden_images and slug in hidden_images:
        hidden_list = hidden_images[slug]
        images = [img for img in images if img not in hidden_list]

    # Apply custom order if exists
    if image_orders and slug in image_orders:
        custom_order = image_orders[slug]
        # Sort images based on custom order, keeping new images at the end
        def sort_key(img):
            if img in custom_order:
                return custom_order.index(img)
            return len(custom_order) + info['images'].index(img)
        images = sorted(images, key=sort_key)

    manifest = {
        "project": str(info['rel_path']),
        "slug": slug,
        "count": len(images),  # Count visible images only
        "total_count": info['image_count'],  # Total including hidden
        "images": images,
        "generated": datetime.now().isoformat()
    }

    # Determine manifest path
    manifest_file = MANIFESTS_BASE / f"{slug}.json"
    manifest_file.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest_file

def generate_all_manifests(discovered_folders, image_orders=None, hidden_images=None):
    """Generate manifest files for all projects"""
    print("📋 Generating manifests in /gen/manifests/...\n")

    for slug, info in discovered_folders.items():
        manifest_file = generate_manifest(slug, info, image_orders, hidden_images)
        rel_manifest = manifest_file.relative_to(BASE_DIR)
        has_custom_order = image_orders and slug in image_orders
        has_hidden = hidden_images and slug in hidden_images
        order_indicator = " (custom order)" if has_custom_order else ""
        hidden_indicator = f" ({len(hidden_images[slug])} hidden)" if has_hidden else ""
        print(f"  ✓ {slug} → {rel_manifest}{order_indicator}{hidden_indicator}")

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

def generate_project_page(slug, info, metadata, template='default', layout='default'):
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
    <script src="{asset_prefix}config-loader.js"></script>
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
    template = metadata_config.get("siteSettings", {}).get("template", "default")
    layout = metadata_config.get("siteSettings", {}).get("layout", "default")

    for slug, info in discovered_folders.items():
        metadata = get_project_metadata(slug, projects_meta, defaults)

        output_file = PROJECTS_BASE / f"{slug}.html"
        html = generate_project_page(slug, info, metadata, template, layout)

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
# STEP 6: UPDATE INDEX.HTML FEATURED SECTION
# ============================================================================

def generate_featured_card(slug, project_info, metadata, is_first=False):
    """Generate HTML for a single featured project card"""
    rel_path = str(project_info['rel_path'])  # Use rel_path, not path
    images = project_info['image_count']

    # Get first image for the card
    manifest_file = MANIFESTS_BASE / f"{slug}.json"
    first_image = ""
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
            if manifest.get('images'):
                first_image = manifest['images'][0]

    image_path = f"images/{rel_path}/{first_image}" if first_image else ""

    # Parse tags into individual spans
    tags = metadata.get('tags', '').split(' • ')
    tags_html = '\n                            '.join(f'<span class="tag">{tag.strip()}</span>' for tag in tags if tag.strip())

    featured_class = ' featured' if is_first else ''

    return f'''                <div class="project-card{featured_class}">
                    <div class="project-header">
                        <span class="year-badge">{metadata.get('year', '2024')}</span>
                        <h3>{metadata.get('title', slug)}</h3>
                        <a href="projects/{slug}.html" class="view-gallery-btn">View Gallery ({images} images)</a>
                    </div>
                    <div class="project-image">
                        <img src="{image_path}" alt="{metadata.get('title', slug)}" loading="lazy"
                             onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23667eea%22 width=%22400%22 height=%22300%22/%3E%3Ctext fill=%22white%22 font-size=%2236%22 x=%22100%22 y=%22160%22%3E{metadata.get('title', slug)}%3C/text%3E%3C/svg%3E'">
                    </div>
                    <div class="project-details">
                        <p class="project-description">{metadata.get('description', '')}</p>
                        <div class="project-tags">
                            {tags_html}
                        </div>
                    </div>
                </div>'''


def update_index_theme(metadata_config):
    """Update the theme CSS link in index.html based on metadata"""
    import re

    index_file = BASE_DIR / 'index.html'
    if not index_file.exists():
        return

    template = metadata_config.get("siteSettings", {}).get("template", "default")
    version_suffix = f'?v={ASSET_VERSION}'

    with open(index_file, 'r') as f:
        content = f.read()

    # Check if theme link already exists
    theme_link = f'<link rel="stylesheet" href="themes/{template}.css{version_suffix}">'

    if 'themes/' in content:
        # Update existing theme link
        content = re.sub(
            r'<link rel="stylesheet" href="themes/[^"]+\.css[^"]*">',
            theme_link,
            content
        )
    else:
        # Add theme link after styles.css
        content = re.sub(
            r'(<link rel="stylesheet" href="styles\.css[^"]*">)',
            f'\\1\n    {theme_link}',
            content
        )

    with open(index_file, 'w') as f:
        f.write(content)

    print(f"  ✓ Applied '{template}' theme to index.html\n")


def update_index_layout(metadata_config):
    """Update the layout CSS link and body class in index.html based on metadata"""
    import re

    index_file = BASE_DIR / 'index.html'
    if not index_file.exists():
        return

    layout = metadata_config.get("siteSettings", {}).get("layout", "default")
    version_suffix = f'?v={ASSET_VERSION}'

    with open(index_file, 'r') as f:
        content = f.read()

    # Update layout CSS link
    layout_link = f'<link rel="stylesheet" href="layouts/{layout}.css{version_suffix}">'

    if 'layouts/' in content:
        # Update existing layout link
        content = re.sub(
            r'<link rel="stylesheet" href="layouts/[^"]+\.css[^"]*">',
            layout_link,
            content
        )
    else:
        # Add layout link after theme link
        if 'themes/' in content:
            content = re.sub(
                r'(<link rel="stylesheet" href="themes/[^"]+\.css[^"]*">)',
                f'\\1\n    {layout_link}',
                content
            )
        else:
            # Add after styles.css
            content = re.sub(
                r'(<link rel="stylesheet" href="styles\.css[^"]*">)',
                f'\\1\n    {layout_link}',
                content
            )

    # Update body class
    body_class = f'class="layout-{layout}"'

    if 'class="layout-' in content:
        # Update existing layout class
        content = re.sub(
            r'<body class="layout-[^"]*">',
            f'<body {body_class}>',
            content
        )
    elif '<body>' in content:
        # Add class to body tag
        content = content.replace('<body>', f'<body {body_class}>')

    with open(index_file, 'w') as f:
        f.write(content)

    print(f"  ✓ Applied '{layout}' layout to index.html\n")


def generate_index_html(discovered_folders, metadata_config):
    """Generate complete index.html from siteContent configuration"""
    print("🏠 Generating index.html from configuration...\n")

    site_content = metadata_config.get("siteContent", {})
    site_settings = metadata_config.get("siteSettings", {})
    projects_meta = metadata_config.get("projects", {})
    featured_order = metadata_config.get("featuredOrder", [])

    template = site_settings.get("template", "default")
    layout = site_settings.get("layout", "default")
    version_suffix = f'?v={ASSET_VERSION}'

    # Extract content sections
    hero = site_content.get("hero", {})
    featured_section = site_content.get("featuredSection", {})
    timeline = site_content.get("timeline", {})
    about = site_content.get("about", {})
    contact = site_content.get("contact", {})
    footer = site_content.get("footer", {})

    # Show ALL projects for all layouts (enables layout switching without rebuild)
    # Featured projects appear first (in featuredOrder), then non-featured projects
    featured_cards = []
    non_featured_cards = []
    defaults = metadata_config.get("defaults", {})
    processed_slugs = set()

    # First, add featured projects in the order specified by featuredOrder
    for slug in featured_order:
        if slug in discovered_folders:
            info = discovered_folders[slug]
            meta = projects_meta.get(slug) or get_project_metadata(slug, projects_meta, defaults)
            card = generate_featured_card(slug, info, meta, is_first=(len(featured_cards) == 0))
            featured_cards.append(card)
            processed_slugs.add(slug)

    # Then add remaining projects (featured ones not in order, then non-featured)
    for slug, info in discovered_folders.items():
        if slug in processed_slugs:
            continue
        meta = projects_meta.get(slug) or get_project_metadata(slug, projects_meta, defaults)
        project_meta = projects_meta.get(slug, {})
        is_featured = project_meta.get('featured', False)
        card = generate_featured_card(slug, info, meta, is_first=False)

        if is_featured:
            featured_cards.append(card)
        else:
            non_featured_cards.append(card)

    # Combine: featured first, then non-featured
    all_cards = featured_cards + non_featured_cards

    featured_cards_html = '\n\n'.join(all_cards) if all_cards else ''

    # Calculate stats for Instagram profile header
    total_projects = len(discovered_folders)
    total_images = sum(info['image_count'] for info in discovered_folders.values())

    # Generate timeline milestones
    milestones_html = []
    for milestone in timeline.get("milestones", []):
        focus_pills = '\n                        '.join(
            f'<span class="milestone-pill">{area}</span>'
            for area in milestone.get("focusAreas", [])
        )

        links_html = '\n                        '.join(
            f'<a href="projects/{link["project"]}.html" class="milestone-link">{link["label"]}</a>'
            for link in milestone.get("links", [])
        )

        milestones_html.append(f'''            <article class="milestone">
                <span class="milestone-dot" aria-hidden="true"></span>
                <span class="milestone-year">{milestone.get("year", "")}</span>
                <div class="milestone-card">
                    <h3>{milestone.get("title", "")}</h3>
                    <p>{milestone.get("description", "")}</p>
                    <p class="milestone-label">Focus Areas</p>
                    <div class="milestone-pill-group">
                        {focus_pills}
                    </div>
                    <p class="milestone-label">Project Galleries</p>
                    <div class="milestone-links">
                        {links_html}
                    </div>
                </div>
            </article>''')

    timeline_html = '\n\n'.join(milestones_html)

    # Generate about paragraphs
    about_paragraphs = '\n                    '.join(
        f'<p>{p}</p>' for p in about.get("paragraphs", [])
    )

    # Generate skills
    skills_html = '\n                        '.join(
        f'<div class="skill">{skill}</div>' for skill in about.get("skills", [])
    )

    # Generate contact links
    contact_links = '\n                '.join(
        f'<a href="{link["url"]}" class="contact-button" {"target=\"_blank\"" if not link["url"].startswith("mailto:") else ""}>{link["label"]}</a>'
        for link in contact.get("links", [])
    )

    # Generate YouTube social pill
    youtube = hero.get("social", {}).get("youtube", {})
    youtube_html = ""
    if youtube.get("url"):
        youtube_html = f'''<a href="{youtube["url"]}" target="_blank" rel="noreferrer" class="social-pill youtube" aria-label="Watch on YouTube">
                    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                        <path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.4 3.6 12 3.6 12 3.6s-7.4 0-9.4.5A3 3 0 0 0 .5 6.2 31.7 31.7 0 0 0 0 12a31.7 31.7 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c2 .5 9.4.5 9.4.5s7.4 0 9.4-.5a3 3 0 0 0 2.1-2.1 31.7 31.7 0 0 0 .5-5.8 31.7 31.7 0 0 0-.5-5.8Z" fill="#ff0000"/>
                        <path d="m9.75 8.7 6.2 3.3-6.2 3.3Z" fill="#fff"/>
                    </svg>
                    <span>{youtube.get("label", "@reyanmakes")}</span>
                </a>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_content.get("siteTitle", "Reyan Makes")}</title>
    <meta name="description" content="{site_content.get("siteDescription", "")}">
    <link rel="stylesheet" href="styles.css{version_suffix}">
    <script src="config-loader.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="logo">{site_content.get("siteName", "Reyan Makes")}</a>
            <ul class="nav-menu">
                <li><a href="#home" class="nav-link active">Home</a></li>
                <li><a href="#featured" class="nav-link">Featured</a></li>
                <li><a href="#timeline" class="nav-link">Journey</a></li>
                <li><a href="#contact" class="nav-link">Contact</a></li>
            </ul>
        </div>
    </nav>

    <section id="home" class="hero">
        <div class="hero-content">
            <div class="profile-avatar">R</div>
            <h1 class="hero-title">{hero.get("title", "")}</h1>
            <p class="hero-subtitle">{hero.get("subtitle", "")}</p>
            <div class="profile-stats">
                <div class="stat"><span class="stat-value">{total_projects}</span><span class="stat-label">projects</span></div>
                <div class="stat"><span class="stat-value">{total_images}</span><span class="stat-label">images</span></div>
            </div>
            <div class="hero-about">
                {about_paragraphs}
            </div>
            <div class="hero-skills">
                <h3>{about.get("skillsTitle", "Skills & Experience")}</h3>
                <div class="skills-grid">
                    {skills_html}
                </div>
            </div>
            <div class="hero-actions">
                {youtube_html}
                <a href="{hero.get("ctaLink", "#featured")}" class="cta-button">{hero.get("ctaText", "Explore My Work")}</a>
            </div>
        </div>
    </section>

    <section id="featured" class="featured-projects">
        <div class="container">
            <h2 class="section-title">{featured_section.get("title", "Featured Builds")}</h2>
            <p class="section-subtitle">{featured_section.get("subtitle", "")}</p>

            <div class="projects-grid">
{featured_cards_html}

            </div>
        </div>
    </section>

    <section id="timeline" class="timeline timeline--glow">
        <div class="container">
            <h2 class="section-title">{timeline.get("title", "My Maker Journey")}</h2>
            <p class="section-subtitle">{timeline.get("subtitle", "")}</p>
        </div>

        <div class="journey-track">
{timeline_html}
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="container">
            <h2 class="section-title">{contact.get("title", "Let's Connect")}</h2>
            <p class="contact-description">{contact.get("description", "")}</p>
            <div class="contact-links">
                {contact_links}
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>{footer.get("copyright", "&copy; 2025 Reyan Bhattacharjee | Built with passion")}</p>
        </div>
    </footer>

    <script src="script.js{version_suffix}"></script>
</body>
</html>
'''

    # Write the generated index.html
    index_file = BASE_DIR / 'index.html'
    with open(index_file, 'w') as f:
        f.write(html)

    print(f"  ✓ Generated index.html with {len(featured_cards)} featured projects")
    print(f"  ✓ Theme: {template}, Layout: {layout}")
    print(f"  ✓ Timeline: {len(timeline.get('milestones', []))} milestones\n")


def update_index_featured(discovered_folders, metadata_config):
    """Update the Featured Builds section in index.html based on metadata"""
    print("🏠 Updating Featured Builds in index.html...\n")

    index_file = BASE_DIR / 'index.html'
    if not index_file.exists():
        print("  ⚠️  index.html not found, skipping featured update")
        return

    # Get featured projects from metadata
    projects_meta = metadata_config.get("projects", {})
    featured_order = metadata_config.get("featuredOrder", [])
    featured_projects = []

    # Use featuredOrder if available, otherwise fall back to featured flag
    if featured_order:
        for slug in featured_order:
            if slug in projects_meta and slug in discovered_folders:
                meta = projects_meta[slug]
                featured_projects.append((slug, discovered_folders[slug], meta))
    else:
        # Fallback: use featured flag
        for slug, meta in projects_meta.items():
            if meta.get('featured', False) and slug in discovered_folders:
                featured_projects.append((slug, discovered_folders[slug], meta))
        # Sort by year (newest first)
        featured_projects.sort(key=lambda x: x[2].get('year', '0'), reverse=True)

    if not featured_projects:
        print("  ⚠️  No featured projects found in metadata")
        return

    print(f"  Found {len(featured_projects)} featured projects:")
    for slug, _, meta in featured_projects:
        print(f"    • {meta.get('title', slug)} ({meta.get('year', 'N/A')})")

    # Generate the cards HTML
    cards_html = []
    for i, (slug, info, meta) in enumerate(featured_projects):
        cards_html.append(generate_featured_card(slug, info, meta, is_first=(i == 0)))

    featured_section = '''            <div class="projects-grid">
''' + '\n\n'.join(cards_html) + '''

            </div>'''

    # Read current index.html
    with open(index_file, 'r') as f:
        content = f.read()

    # Find and replace the projects-grid section
    import re
    pattern = r'<div class="projects-grid">.*?</div>\s*</div>\s*</section>\s*<section id="timeline"'
    replacement = featured_section + '''
        </div>
    </section>

    <section id="timeline"'''

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        with open(index_file, 'w') as f:
            f.write(new_content)
        print(f"\n  ✓ Updated index.html with {len(featured_projects)} featured projects\n")
    else:
        print("\n  ℹ️  No changes needed to index.html\n")


# ============================================================================
# STEP 7: GENERATE SITE CONFIG
# ============================================================================

def generate_site_config(metadata_config):
    """Generate site-config.json for dynamic CSS loading"""
    print("⚙️  Generating site config...\n")

    site_settings = metadata_config.get("siteSettings", {})

    config = {
        "layout": site_settings.get("layout", "default"),
        "theme": site_settings.get("template", "default")
    }

    config_file = BASE_DIR / 'site-config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  ✓ site-config.json: layout={config['layout']}, theme={config['theme']}\n")
    return config


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

        # Load custom image orders
        image_orders = load_image_orders()
        if image_orders:
            print(f"  ✓ Loaded custom image orders for {len(image_orders)} projects\n")

        # Load hidden images
        hidden_images = load_hidden_images()
        if hidden_images:
            total_hidden = sum(len(v) for v in hidden_images.values())
            print(f"  ✓ Loaded {total_hidden} hidden images across {len(hidden_images)} projects\n")

        # Step 1: Discover all image folders
        discovered = discover_image_folders(IMAGES_BASE)

        if not discovered:
            print("\n⚠️  No image folders found! Check your images directory.")
            return 1

        # Step 2: Generate thumbnails
        generate_all_thumbnails(discovered)

        # Step 3: Generate manifests (with custom image orders and hidden images)
        generate_all_manifests(discovered, image_orders, hidden_images)

        # Step 4: Generate project pages
        generate_all_project_pages(discovered, metadata_config)

        # Step 5: Generate site index
        site_index = generate_site_index(discovered, metadata_config)

        # Step 6: Generate index.html from configuration
        generate_index_html(discovered, metadata_config)

        # Step 7: Generate site config for dynamic CSS loading
        generate_site_config(metadata_config)

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
