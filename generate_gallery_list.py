#!/usr/bin/env python3
"""
Generate image list arrays for project galleries
Makes it easy to add/remove images without manually editing HTML

Usage: python generate_gallery_list.py <project_folder>
Example: python generate_gallery_list.py "images/Engeneering/Gokart"
"""

import sys
import os
from pathlib import Path

def generate_image_array(folder_path):
    """Generate JavaScript array of image filenames"""
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist")
        return

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG'}
    images = sorted([
        f.name for f in folder.iterdir()
        if f.is_file() and f.suffix in image_extensions
    ])

    if not images:
        print(f"No images found in '{folder_path}'")
        return

    # Generate JavaScript array
    print(f"// {len(images)} images found in {folder.name}")
    print("const images = [")
    for img in images:
        print(f"    '{img}',")
    print("];")
    print()
    print(f"// Copy this array into your {folder.name}.html project page")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_gallery_list.py <project_folder>")
        print("Example: python generate_gallery_list.py images/Engeneering/Gokart")
        sys.exit(1)

    folder_path = sys.argv[1]
    generate_image_array(folder_path)
