#!/usr/bin/env python3
"""
Generate image manifest JSON files for all project galleries
This allows galleries to load images dynamically without hardcoding filenames

Usage: python generate_manifests.py
"""

import json
import os
from pathlib import Path

def generate_manifest_for_folder(folder_path, output_path):
    """Generate JSON manifest of image filenames for a folder"""
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        return None

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG'}
    images = sorted([
        f.name for f in folder.iterdir()
        if f.is_file() and f.suffix in image_extensions
    ])

    if not images:
        return None

    # Create manifest
    manifest = {
        "project": folder.name,
        "count": len(images),
        "images": images
    }

    # Write JSON file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    return len(images)

def main():
    """Generate manifests for all project folders"""
    base_path = Path(__file__).parent / 'images' / 'Engeneering'
    manifest_base = Path(__file__).parent / 'manifests'

    # Create manifests directory
    manifest_base.mkdir(exist_ok=True)

    print("Generating image manifests...\n")

    total_projects = 0
    total_images = 0

    # Process main project folders
    for project_folder in sorted(base_path.iterdir()):
        if not project_folder.is_dir():
            continue

        # Skip BSA folder for now (will process subfolders)
        if project_folder.name == 'BSA':
            # Process BSA subfolders
            bsa_manifest_path = manifest_base / 'bsa'
            for sub_folder in sorted(project_folder.iterdir()):
                if not sub_folder.is_dir():
                    continue

                manifest_file = bsa_manifest_path / f"{sub_folder.name.lower().replace(' ', '-')}.json"
                count = generate_manifest_for_folder(sub_folder, manifest_file)

                if count:
                    print(f"✓ BSA/{sub_folder.name}: {count} images -> {manifest_file.relative_to(Path.cwd())}")
                    total_projects += 1
                    total_images += count
        else:
            # Regular project folder
            manifest_file = manifest_base / f"{project_folder.name.lower().replace(' ', '-')}.json"
            count = generate_manifest_for_folder(project_folder, manifest_file)

            if count:
                print(f"✓ {project_folder.name}: {count} images -> {manifest_file.relative_to(Path.cwd())}")
                total_projects += 1
                total_images += count

    # Also process Drawings folder
    drawings_folder = Path(__file__).parent / 'images' / 'Drawings'
    if drawings_folder.exists():
        manifest_file = manifest_base / 'drawings.json'
        count = generate_manifest_for_folder(drawings_folder, manifest_file)
        if count:
            print(f"✓ Drawings: {count} images -> {manifest_file.relative_to(Path.cwd())}")
            total_projects += 1
            total_images += count

    print(f"\n{'='*60}")
    print(f"Generated {total_projects} manifests for {total_images} total images")
    print(f"{'='*60}\n")
    print("Now project pages can load images dynamically from these manifests!")

if __name__ == "__main__":
    main()
