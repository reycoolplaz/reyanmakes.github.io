#!/usr/bin/env python3
"""
Generate project HTML pages from manifests using template
This creates individual gallery pages for each project

Usage: python3 generate_project_pages.py
"""

import json
from pathlib import Path

ASSET_VERSION = "20241110"

# Project metadata - titles, descriptions, years, and tags
PROJECT_METADATA = {
    "lakehouse": {
        "title": "Lake House Projects",
        "year": "2023-2024",
        "tags": "Woodworking • Renovation • Lakeside",
        "description": "Various projects and improvements around the family lake house. From dock repairs to furniture builds."
    },
    "bed": {
        "title": "Custom Platform Bed",
        "year": "2023",
        "tags": "Woodworking • Furniture • Design",
        "description": "Built a custom platform bed frame with storage. Learned joinery techniques and wood finishing."
    },
    "njit": {
        "title": "NJIT Projects",
        "year": "2021-2024",
        "tags": "Engineering • College • Manufacturing",
        "description": "Engineering projects from my time at New Jersey Institute of Technology. Machining, design, and fabrication work."
    },
    "temple": {
        "title": "Temple Construction",
        "year": "2023",
        "tags": "Woodworking • Carpentry • Community",
        "description": "Volunteering on temple construction project. Framing, finishing, and learning from master carpenters."
    },
    "knife-&-hatchet": {
        "title": "Knife & Hatchet Making",
        "year": "2022",
        "tags": "Metalworking • Grinding • Tools",
        "description": "Hand-ground knives and hatchets from reclaimed materials. Learning edge geometry and heat treating."
    },
    "canoe-hauler-for-bike": {
        "title": "Bike Canoe Hauler",
        "year": "2023",
        "tags": "Welding • Design • Transportation",
        "description": "Custom welded trailer attachment for hauling canoes with my bike. Solved a practical problem with metal fabrication."
    },
    "freshman-bridge": {
        "title": "Freshman Bridge Project",
        "year": "2021",
        "tags": "Engineering • Design • Competition",
        "description": "First-year engineering bridge design and build competition at NJIT. Structural analysis and load testing."
    },
    "room-draws": {
        "title": "Room Drawings & Sketches",
        "year": "2022-2024",
        "tags": "Design • Planning • Visualization",
        "description": "Room layouts, project sketches, and design ideas. Planning before building."
    },
    "baby-head": {
        "title": "Baby Head Sculpture",
        "year": "2023",
        "tags": "Sculpture • Art • Experimentation",
        "description": "Experimental sculpture project. Learning 3D form and artistic expression."
    },
    "skulls-&-bones-&-restoration": {
        "title": "Skull & Bone Restoration",
        "year": "2021-2023",
        "tags": "Restoration • Biology • Preservation",
        "description": "Found skull and bone cleaning and restoration. Learning anatomy and preservation techniques."
    },
    "drawings": {
        "title": "Art & Drawings",
        "year": "2020-2024",
        "tags": "Art • Sketching • Creative",
        "description": "Various drawings and artistic work over the years. Exploring different styles and subjects."
    },
    "canoes": {
        "title": "Canoe Projects",
        "year": "2023",
        "tags": "Watercraft • Repair • Outdoor",
        "description": "Canoe repairs and modifications. Learning fiberglass work and boat maintenance."
    },
    "cupper-grabber": {
        "title": "Copper Grabber Tool",
        "year": "2022",
        "tags": "Tools • Metalworking • Practical",
        "description": "Custom tool for grabbing and handling copper pieces. Solving a specific workshop need."
    },
    "random": {
        "title": "Random Projects",
        "year": "Various",
        "tags": "Miscellaneous • Experiments • Fun",
        "description": "Various projects and experiments that didn't fit other categories. Always tinkering and trying new things."
    },
    "recycleapult": {
        "title": "Recycleapult",
        "year": "2022",
        "tags": "Engineering • Fun • Catapult",
        "description": "Built a catapult for launching recyclables. Fun engineering project with practical applications."
    },
    "vouleenteer-with-mugdha,-mc": {
        "title": "Volunteer Work with Mugdha MC",
        "year": "2024",
        "tags": "Community • Service • Volunteering",
        "description": "Community service and volunteer activities. Giving back and helping others."
    }
}

# BSA sub-project metadata
BSA_METADATA = {
    "eagle-scout-project,-in-the-old-school,-dad-miata": {
        "title": "Eagle Scout Project",
        "year": "2020",
        "tags": "BSA • Leadership • Community Service",
        "description": "My Eagle Scout service project. Led a team to complete a community improvement initiative."
    },
    "2021-white-water-rafting": {
        "title": "White Water Rafting 2021",
        "year": "2021",
        "tags": "BSA • Adventure • Outdoor",
        "description": "BSA white water rafting adventure. Teamwork, paddling, and outdoor skills on the rapids."
    },
    "white-water-rafting-2025": {
        "title": "White Water Rafting 2025",
        "year": "2025",
        "tags": "BSA • Adventure • Outdoor",
        "description": "Another year, another rafting adventure. Building on skills and enjoying the outdoors with the troop."
    },
    "2024-biking-trip": {
        "title": "BSA Biking Trip 2024",
        "year": "2024",
        "tags": "BSA • Cycling • Adventure",
        "description": "Multi-day bike touring trip with BSA. Navigation, endurance, and outdoor camping."
    },
    "bharath-sevashram": {
        "title": "Bharath Sevashram Service",
        "year": "2023",
        "tags": "BSA • Service • Community",
        "description": "Service project at Bharath Sevashram. Community engagement and helping those in need."
    },
    "bsa-trash-sled": {
        "title": "BSA Trash Sled",
        "year": "2023",
        "tags": "BSA • Conservation • Project",
        "description": "Built a sled for hauling trash out of wilderness areas. Leave No Trace principles in action."
    },
    "daniel-javick-shed": {
        "title": "Daniel Javick's Shed",
        "year": "2022",
        "tags": "BSA • Construction • Carpentry",
        "description": "Helped build a storage shed as a scout service project. Learned framing and construction basics."
    },
    "other": {
        "title": "BSA Miscellaneous",
        "year": "Various",
        "tags": "BSA • Scouting • Activities",
        "description": "Various Boy Scout activities, camping trips, and memories from my time in the troop."
    }
}

def generate_page_html(manifest_path, project_key, is_bsa=False):
    """Generate HTML page for a project from its manifest"""

    # Read manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Get metadata
    metadata = BSA_METADATA.get(project_key) if is_bsa else PROJECT_METADATA.get(project_key)

    if not metadata:
        print(f"⚠ No metadata found for {project_key}, skipping...")
        return None

    asset_prefix = '../' if not is_bsa else '../../'
    version_suffix = f'?v={ASSET_VERSION}'

    home_link = f'{asset_prefix}index.html'
    featured_link = f'{home_link}#featured'
    timeline_link = f'{home_link}#timeline'
    about_link = f'{home_link}#about'
    contact_link = f'{home_link}#contact'
    styles_path = f'{asset_prefix}styles.css{version_suffix}'
    script_path = f'{asset_prefix}lightbox.js{version_suffix}'

    # Determine paths
    if is_bsa:
        images_path = f'{asset_prefix}images/Engeneering/BSA/{manifest["project"]}/'
        manifest_rel_path = f'{asset_prefix}manifests/bsa/{project_key}.json'
        output_file = f'bsa/{project_key}.html'
        breadcrumb_name = metadata['title']
        back_link = home_link
    else:
        images_path = (f'{asset_prefix}images/Engeneering/{manifest["project"]}/'
                       if project_key != 'drawings'
                       else f'{asset_prefix}images/Drawings/')
        manifest_rel_path = f'{asset_prefix}manifests/{project_key}.json'
        output_file = f'{project_key}.html'
        breadcrumb_name = metadata['title']
        back_link = home_link

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} | Reyan Makes</title>
    <meta name="description" content="{metadata['description']}">
    <link rel="stylesheet" href="{styles_path}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="{home_link}" class="logo">Reyan Makes</a>
            <ul class="nav-menu">
                <li><a href="{home_link}" class="nav-link">Home</a></li>
                <li><a href="{featured_link}" class="nav-link">Featured</a></li>
                <li><a href="{timeline_link}" class="nav-link">Journey</a></li>
                <li><a href="{about_link}" class="nav-link">About</a></li>
                <li><a href="{contact_link}" class="nav-link">Contact</a></li>
            </ul>
        </div>
    </nav>

    <div class="breadcrumb">
        <div class="container">
            <ul class="breadcrumb-list">
                <li><a href="{home_link}" class="breadcrumb-link">Home</a></li>
                <li><span class="breadcrumb-current">{breadcrumb_name}</span></li>
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
            <h2 class="section-title">Build Gallery</h2>
            <p class="section-subtitle">From concept to completion - documenting the entire build process</p>

            <div class="gallery-grid" id="gallery">
                <!-- Images will be loaded dynamically from the images array -->
            </div>
        </div>
    </section>

    <section style="padding: 3rem 0; text-align: center;">
        <div class="container">
            <a href="{back_link}" class="contact-button">← Back to Home</a>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Reyan Bhattacharjee | Built with passion</p>
        </div>
    </footer>

    <script src="{script_path}"></script>
    <script>
        // Load gallery images dynamically from manifest
        // To add/remove images: just add/remove files from the folder and run generate_manifests.py
        const gallery = document.getElementById('gallery');
        const basePath = '{images_path}';
        const manifestPath = '{manifest_rel_path}';

        // Fetch and load images from manifest
        fetch(manifestPath)
            .then(response => response.json())
            .then(manifest => {{
                // Update subtitle with actual count
                const subtitle = document.querySelector('.section-subtitle');
                subtitle.textContent = `From concept to completion - ${{manifest.count}} images documenting the entire build process`;

                // Load each image
                manifest.images.forEach(filename => {{
                    const item = document.createElement('div');
                    item.className = 'gallery-item';

                    const img = document.createElement('img');
                    img.src = basePath + filename;
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
                gallery.innerHTML = '<p style="text-align:center; color: var(--text-light);">Error loading images. Please try refreshing the page.</p>';
            }});
    </script>
</body>
</html>
'''

    return html

def main():
    """Generate all project pages from manifests"""

    manifest_dir = Path(__file__).parent / 'manifests'
    projects_dir = Path(__file__).parent / 'projects'

    # Create projects directory
    projects_dir.mkdir(exist_ok=True)

    # Create BSA subdirectory
    bsa_dir = projects_dir / 'bsa'
    bsa_dir.mkdir(exist_ok=True)

    print("Generating project pages...\n")

    total_pages = 0

    # Generate main project pages
    for manifest_file in sorted(manifest_dir.glob('*.json')):
        project_key = manifest_file.stem

        # Skip if already exists (gokart.html was manually created)
        output_path = projects_dir / f'{project_key}.html'

        html = generate_page_html(manifest_file, project_key, is_bsa=False)

        if html:
            with open(output_path, 'w') as f:
                f.write(html)
            print(f"✓ Created {output_path.relative_to(Path.cwd())}")
            total_pages += 1

    # Generate BSA sub-project pages
    bsa_manifest_dir = manifest_dir / 'bsa'
    if bsa_manifest_dir.exists():
        for manifest_file in sorted(bsa_manifest_dir.glob('*.json')):
            project_key = manifest_file.stem

            html = generate_page_html(manifest_file, project_key, is_bsa=True)

            if html:
                output_path = bsa_dir / f'{project_key}.html'
                with open(output_path, 'w') as f:
                    f.write(html)
                print(f"✓ Created {output_path.relative_to(Path.cwd())}")
                total_pages += 1

    print(f"\n{'='*60}")
    print(f"Generated {total_pages} project pages successfully!")
    print(f"{'='*60}\n")
    print("All pages use manifest-based dynamic image loading.")
    print("To add/remove images: update folders and run generate_manifests.py")

if __name__ == "__main__":
    main()
