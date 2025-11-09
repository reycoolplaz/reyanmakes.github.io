# How to Add/Remove Images

This website uses a **manifest-based system** that makes it easy to add or remove images without editing any code.

## Quick Start

### To Add Images:
1. Upload your images to the appropriate folder in `images/Engeneering/[ProjectName]/`
2. Run: `python3 generate_manifests.py`
3. Commit and push both the new images AND the updated manifest file
4. Done! Your images will automatically appear on the website

### To Remove Images:
1. Delete the image files from `images/Engeneering/[ProjectName]/`
2. Run: `python3 generate_manifests.py`
3. Commit and push the changes
4. Done! The images will no longer appear

## How It Works

- Each project folder has a corresponding JSON manifest file in `/manifests/`
- The manifest lists all image filenames in that folder
- Project pages load images dynamically from these manifests
- No need to hardcode filenames in HTML!

## Workflow Example

```bash
# 1. Add images to a project folder
cp ~/new-images/*.jpg images/Engeneering/Gokart/

# 2. Regenerate manifests
python3 generate_manifests.py

# 3. Commit everything
git add images/ manifests/
git commit -m "Add new go-kart build photos"
git push

# 4. Your website automatically updates!
```

## Adding a New Project

To add a completely new project:

1. Create a new folder: `images/Engeneering/YourProjectName/`
2. Add your images to that folder
3. Run `python3 generate_manifests.py` - this creates the manifest
4. Create a new HTML page in `projects/yourproject.html` using an existing project as a template
5. Update the `basePath` and `manifestPath` in the JavaScript
6. Add a link to your project in `index.html`
7. Commit and push

## File Structure

```
reyanmakes.github.io/
├── images/
│   └── Engeneering/
│       ├── Gokart/           # Project images
│       ├── Bed/
│       ├── LakeHouse/
│       └── ...
├── manifests/                # Auto-generated JSON files
│   ├── gokart.json
│   ├── bed.json
│   └── ...
├── projects/                 # HTML pages
│   ├── gokart.html
│   ├── bed.html
│   └── ...
└── generate_manifests.py     # Manifest generator script
```

## Tips

- Supported formats: JPG, JPEG, PNG, GIF, WEBP
- Images load with lazy loading for better performance
- Keep image sizes reasonable (< 5MB each)
- Use descriptive filenames (they're sorted alphabetically in galleries)
- Run `generate_manifests.py` after ANY change to image folders

## Questions?

The manifest system ensures you can manage images directly from GitHub's web interface without breaking the website. Just remember to regenerate manifests after adding/removing files!
