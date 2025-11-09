#!/usr/bin/env python3
"""
Generate thumbnail versions of all images for faster mobile loading
Creates 200x200px thumbnails in a 'thumbnails' subdirectory

Usage: python3 generate_thumbnails.py
"""

from PIL import Image
from pathlib import Path
import os

def generate_thumbnail(image_path, thumb_path, size=(200, 200)):
    """Generate a thumbnail for an image"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save as JPEG with reduced quality
            img.save(thumb_path, 'JPEG', quality=75, optimize=True)
            return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def main():
    """Generate thumbnails for all project images"""
    base_path = Path(__file__).parent / 'images'

    print("Generating thumbnails for faster mobile loading...\n")

    total_images = 0
    total_thumbnails = 0

    # Process Engineering folder (including BSA subfolders)
    eng_path = base_path / 'Engeneering'
    if eng_path.exists():
        for project_folder in eng_path.iterdir():
            if not project_folder.is_dir():
                continue

            # Handle BSA subfolders
            if project_folder.name == 'BSA':
                for bsa_subfolder in project_folder.iterdir():
                    if not bsa_subfolder.is_dir():
                        continue

                    thumb_dir = bsa_subfolder / 'thumbnails'
                    thumb_dir.mkdir(exist_ok=True)

                    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
                    for img_file in bsa_subfolder.iterdir():
                        if img_file.suffix not in image_extensions or img_file.parent.name == 'thumbnails':
                            continue

                        total_images += 1
                        thumb_path = thumb_dir / f"{img_file.stem}.jpg"

                        if thumb_path.exists() and thumb_path.stat().st_mtime > img_file.stat().st_mtime:
                            total_thumbnails += 1
                            continue

                        if generate_thumbnail(img_file, thumb_path):
                            print(f"✓ BSA/{bsa_subfolder.name}/{img_file.name}")
                            total_thumbnails += 1
                continue

            # Create thumbnails subdirectory
            thumb_dir = project_folder / 'thumbnails'
            thumb_dir.mkdir(exist_ok=True)

            # Process each image
            image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
            for img_file in project_folder.iterdir():
                if img_file.suffix not in image_extensions or img_file.parent.name == 'thumbnails':
                    continue

                total_images += 1
                thumb_path = thumb_dir / f"{img_file.stem}.jpg"

                # Skip if thumbnail already exists and is newer
                if thumb_path.exists() and thumb_path.stat().st_mtime > img_file.stat().st_mtime:
                    total_thumbnails += 1
                    continue

                if generate_thumbnail(img_file, thumb_path):
                    print(f"✓ {project_folder.name}/{img_file.name}")
                    total_thumbnails += 1

    # Process Drawings folder
    drawings_path = base_path / 'Drawings'
    if drawings_path.exists():
        thumb_dir = drawings_path / 'thumbnails'
        thumb_dir.mkdir(exist_ok=True)

        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        for img_file in drawings_path.iterdir():
            if img_file.suffix not in image_extensions or img_file.parent.name == 'thumbnails':
                continue

            total_images += 1
            thumb_path = thumb_dir / f"{img_file.stem}.jpg"

            if thumb_path.exists() and thumb_path.stat().st_mtime > img_file.stat().st_mtime:
                total_thumbnails += 1
                continue

            if generate_thumbnail(img_file, thumb_path):
                print(f"✓ Drawings/{img_file.name}")
                total_thumbnails += 1

    print(f"\n{'='*60}")
    print(f"Generated {total_thumbnails}/{total_images} thumbnails")
    print(f"{'='*60}\n")
    print("Thumbnails saved in 'thumbnails' subdirectories")
    print("Mobile devices will now load small thumbnails instead of full images!")

if __name__ == "__main__":
    main()
