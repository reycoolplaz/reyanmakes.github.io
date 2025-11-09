#!/usr/bin/env python3
"""
Convert all CR2 (Canon RAW) images to JPEG format
"""

import os
from pathlib import Path
from PIL import Image
import rawpy

def convert_cr2_to_jpg(cr2_path, quality=90):
    """Convert a single CR2 file to JPEG"""
    try:
        # Open CR2 file with rawpy
        with rawpy.imread(str(cr2_path)) as raw:
            # Process to RGB array
            rgb = raw.postprocess()

        # Convert to PIL Image
        img = Image.fromarray(rgb)

        # Create output path (same location, different extension)
        jpg_path = cr2_path.with_suffix('.jpg')

        # Save as JPEG
        img.save(jpg_path, 'JPEG', quality=quality)

        print(f"✓ Converted: {cr2_path.name} -> {jpg_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed: {cr2_path.name} - {str(e)}")
        return False

def main():
    # Find all CR2 files in images folder
    images_dir = Path('/home/ujjal/code/reyanmakes.github.io/images')
    cr2_files = list(images_dir.rglob('*.CR2')) + list(images_dir.rglob('*.cr2'))

    total = len(cr2_files)
    print(f"\n{'='*60}")
    print(f"Found {total} CR2 files to convert")
    print(f"{'='*60}\n")

    if total == 0:
        print("No CR2 files found!")
        return

    # Convert all files
    converted = 0
    failed = 0

    for i, cr2_file in enumerate(cr2_files, 1):
        print(f"[{i}/{total}] ", end="")
        if convert_cr2_to_jpg(cr2_file):
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
    print(f"\nOriginal CR2 files have been kept.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
