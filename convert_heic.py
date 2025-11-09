#!/usr/bin/env python3
"""
Convert all HEIC images to JPEG format
Preserves folder structure and keeps original HEIC files
"""

import os
from pathlib import Path
from pillow_heif import register_heif_opener
from PIL import Image

# Register HEIF opener with Pillow
register_heif_opener()

def convert_heic_to_jpg(heic_path, quality=90):
    """Convert a single HEIC file to JPEG"""
    try:
        # Open HEIC file
        img = Image.open(heic_path)

        # Create output path (same location, different extension)
        jpg_path = heic_path.with_suffix('.jpg')

        # Convert and save as JPEG
        img.convert('RGB').save(jpg_path, 'JPEG', quality=quality)

        print(f"✓ Converted: {heic_path.name} -> {jpg_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed: {heic_path.name} - {str(e)}")
        return False

def main():
    # Find all HEIC files in images folder
    images_dir = Path('/home/ujjal/code/reyanmakes.github.io/images')
    heic_files = list(images_dir.rglob('*.HEIC')) + list(images_dir.rglob('*.heic'))

    total = len(heic_files)
    print(f"\n{'='*60}")
    print(f"Found {total} HEIC files to convert")
    print(f"{'='*60}\n")

    if total == 0:
        print("No HEIC files found!")
        return

    # Convert all files
    converted = 0
    failed = 0

    for i, heic_file in enumerate(heic_files, 1):
        print(f"[{i}/{total}] ", end="")
        if convert_heic_to_jpg(heic_file):
            converted += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Conversion Complete!")
    print(f"{'='*60}")
    print(f"✓ Successfully converted: {converted}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {total}")
    print(f"\nOriginal HEIC files have been kept.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
