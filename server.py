#!/usr/bin/env python3
"""
Development server with API endpoint for build script execution
Includes endpoints for portfolio management
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import subprocess
import os
import json
import shutil
from pathlib import Path
import threading
import time
from PIL import Image
import pillow_heif

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
METADATA_FILE = BASE_DIR / 'projects-metadata.json'
IMAGE_ORDER_FILE = BASE_DIR / 'image-orders.json'
HIDDEN_IMAGES_FILE = BASE_DIR / 'hidden-images.json'
SITE_CONFIG_FILE = BASE_DIR / 'site-config.json'


def update_site_config(layout=None, theme=None):
    """Update site-config.json with layout/theme settings"""
    config = {}
    if SITE_CONFIG_FILE.exists():
        with open(SITE_CONFIG_FILE, 'r') as f:
            config = json.load(f)

    if layout is not None:
        config['layout'] = layout
    if theme is not None:
        config['theme'] = theme

    with open(SITE_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def regenerate_manifest(project_path, slug):
    """Regenerate manifest for a specific project after upload"""
    from datetime import datetime

    images_dir = BASE_DIR / 'images' / project_path
    manifest_dir = BASE_DIR / 'gen' / 'manifests'
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Get all images in the folder
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    images = []
    if images_dir.exists():
        for f in images_dir.iterdir():
            if f.is_file() and f.suffix.lower() in image_extensions:
                images.append(f.name)

    # Load hidden images to exclude from count
    hidden_list = []
    if HIDDEN_IMAGES_FILE.exists():
        with open(HIDDEN_IMAGES_FILE, 'r') as f:
            hidden_data = json.load(f)
            hidden_list = hidden_data.get(slug, [])

    # Load custom order if exists
    custom_order = []
    if IMAGE_ORDER_FILE.exists():
        with open(IMAGE_ORDER_FILE, 'r') as f:
            order_data = json.load(f)
            custom_order = order_data.get(slug, [])

    # Apply custom order
    if custom_order:
        def get_order_index(img):
            try:
                return custom_order.index(img)
            except ValueError:
                return len(custom_order) + images.index(img)
        images.sort(key=get_order_index)

    # Filter out hidden images for the manifest
    visible_images = [img for img in images if img not in hidden_list]

    # Create manifest
    manifest = {
        'project': project_path,
        'slug': slug,
        'count': len(visible_images),
        'total_count': len(images),
        'images': visible_images,
        'generated': datetime.now().isoformat()
    }

    manifest_file = manifest_dir / f'{slug}.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Also update site-index.json
    update_site_index(project_path, slug, len(visible_images))

    return manifest


def update_site_index(project_path, slug, image_count):
    """Update site-index.json with new image count"""
    site_index_file = BASE_DIR / 'gen' / 'site-index.json'

    if site_index_file.exists():
        with open(site_index_file, 'r') as f:
            site_index = json.load(f)
    else:
        site_index = {'projects': {}, 'generated': ''}

    if slug in site_index.get('projects', {}):
        site_index['projects'][slug]['image_count'] = image_count
    else:
        # Add new project entry
        site_index['projects'][slug] = {
            'title': slug.replace('-', ' ').title(),
            'path': project_path,
            'image_count': image_count,
            'manifest': f'gen/manifests/{slug}.json'
        }

    from datetime import datetime
    site_index['generated'] = datetime.now().isoformat()

    with open(site_index_file, 'w') as f:
        json.dump(site_index, f, indent=2)

# Simple password protection (change this!)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'reyan2025')

# Store build status
build_status = {
    'running': False,
    'last_run': None,
    'last_result': None,
    'output': ''
}

def run_build_script():
    """Run the build script in a separate thread"""
    global build_status

    build_status['running'] = True
    build_status['output'] = ''

    try:
        # Run the build script
        process = subprocess.Popen(
            ['python3', 'build_site.py'],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Capture output
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            build_status['output'] = ''.join(output_lines)

        process.wait()

        build_status['last_result'] = {
            'success': process.returncode == 0,
            'returncode': process.returncode,
            'output': build_status['output']
        }

    except Exception as e:
        build_status['last_result'] = {
            'success': False,
            'error': str(e)
        }

    finally:
        build_status['running'] = False
        build_status['last_run'] = time.time()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

@app.route('/api/build', methods=['POST'])
def trigger_build():
    """API endpoint to trigger the build script"""

    # Check password
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    # Check if build is already running
    if build_status['running']:
        return jsonify({
            'error': 'Build already in progress',
            'running': True
        }), 409

    # Start build in background thread
    thread = threading.Thread(target=run_build_script)
    thread.daemon = True
    thread.start()

    return jsonify({
        'message': 'Build started',
        'running': True
    })

@app.route('/api/build/status', methods=['GET'])
def build_status_endpoint():
    """Get current build status"""
    return jsonify(build_status)


@app.route('/api/git-pull', methods=['POST'])
def git_pull():
    """Pull latest changes from GitHub"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        result = subprocess.run(
            ['git', 'pull'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Pull successful',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or result.stdout
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/publish', methods=['POST'])
def publish_site():
    """Commit and push changes to git"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        import subprocess

        # Stage all changes
        subprocess.run(['git', 'add', '-A'], cwd=BASE_DIR, check=True)

        # Check if there are changes to commit
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            return jsonify({'message': 'No changes to publish'})

        # Commit with a standard message
        commit_msg = 'chore: update site content via admin panel'
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=BASE_DIR,
            check=True
        )

        # Push to remote
        subprocess.run(['git', 'push'], cwd=BASE_DIR, check=True)

        return jsonify({'success': True, 'message': 'Published successfully'})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Git operation failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata', methods=['POST'])
def save_metadata():
    """Save project metadata to JSON file"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    new_metadata = data.get('metadata')
    if not new_metadata:
        return jsonify({'error': 'No metadata provided'}), 400

    try:
        # Backup existing file
        if METADATA_FILE.exists():
            backup_file = BASE_DIR / 'projects-metadata.backup.json'
            with open(METADATA_FILE, 'r') as f:
                backup_data = f.read()
            with open(backup_file, 'w') as f:
                f.write(backup_data)

        # Write new metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump(new_metadata, f, indent=2)

        return jsonify({'message': 'Metadata saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/template', methods=['POST'])
def save_template():
    """Save site template selection to metadata"""
    data = request.get_json()
    password = request.headers.get('X-Admin-Password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    template = data.get('template')
    if not template:
        return jsonify({'error': 'No template provided'}), 400

    # Validate template name
    valid_templates = ['default', 'dark', 'ocean', 'forest', 'sunset']
    if template not in valid_templates:
        return jsonify({'error': f'Invalid template. Must be one of: {", ".join(valid_templates)}'}), 400

    try:
        # Load existing metadata
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        # Update siteSettings
        if 'siteSettings' not in metadata:
            metadata['siteSettings'] = {}
        metadata['siteSettings']['template'] = template

        # Save metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Also update site-config.json for dynamic loading
        update_site_config(theme=template)

        return jsonify({'message': f'Template changed to {template}', 'template': template})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/layout', methods=['POST'])
def save_layout():
    """Save site layout selection to metadata"""
    data = request.get_json()
    password = request.headers.get('X-Admin-Password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    layout = data.get('layout')
    if not layout:
        return jsonify({'error': 'No layout provided'}), 400

    # Validate layout name
    valid_layouts = ['default', 'pinterest', 'instagram', 'portfolio']
    if layout not in valid_layouts:
        return jsonify({'error': f'Invalid layout. Must be one of: {", ".join(valid_layouts)}'}), 400

    try:
        # Load existing metadata
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        # Update siteSettings
        if 'siteSettings' not in metadata:
            metadata['siteSettings'] = {}
        metadata['siteSettings']['layout'] = layout

        # Save metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Also update site-config.json for dynamic loading
        update_site_config(layout=layout)

        return jsonify({'message': f'Layout changed to {layout}', 'layout': layout})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/image-order', methods=['POST'])
def save_image_order():
    """Save custom image order for a project"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    project = data.get('project')
    order = data.get('order')

    if not project or not order:
        return jsonify({'error': 'Missing project or order'}), 400

    try:
        # Load existing orders
        orders = {}
        if IMAGE_ORDER_FILE.exists():
            with open(IMAGE_ORDER_FILE, 'r') as f:
                orders = json.load(f)

        # Update order for this project
        orders[project] = order

        # Save
        with open(IMAGE_ORDER_FILE, 'w') as f:
            json.dump(orders, f, indent=2)

        return jsonify({'message': 'Image order saved'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/image-order', methods=['GET'])
def get_image_orders():
    """Get all saved image orders"""
    try:
        if IMAGE_ORDER_FILE.exists():
            with open(IMAGE_ORDER_FILE, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hidden-images', methods=['POST'])
def save_hidden_images():
    """Save hidden images for a project"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    project = data.get('project')
    hidden = data.get('hidden', [])

    if not project:
        return jsonify({'error': 'Missing project'}), 400

    try:
        # Load existing hidden images
        hidden_data = {}
        if HIDDEN_IMAGES_FILE.exists():
            with open(HIDDEN_IMAGES_FILE, 'r') as f:
                hidden_data = json.load(f)

        # Update hidden images for this project
        if hidden:
            hidden_data[project] = hidden
        elif project in hidden_data:
            # Remove project if no hidden images
            del hidden_data[project]

        # Save
        with open(HIDDEN_IMAGES_FILE, 'w') as f:
            json.dump(hidden_data, f, indent=2)

        return jsonify({'message': 'Hidden images saved', 'hidden': hidden})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hidden-images', methods=['GET'])
def get_hidden_images():
    """Get all hidden images"""
    try:
        if HIDDEN_IMAGES_FILE.exists():
            with open(HIDDEN_IMAGES_FILE, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/toggle-image-visibility', methods=['POST'])
def toggle_image_visibility():
    """Toggle visibility of a single image"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    project = data.get('project')
    image = data.get('image')
    hide = data.get('hide', True)

    if not project or not image:
        return jsonify({'error': 'Missing project or image'}), 400

    try:
        # Load existing hidden images
        hidden_data = {}
        if HIDDEN_IMAGES_FILE.exists():
            with open(HIDDEN_IMAGES_FILE, 'r') as f:
                hidden_data = json.load(f)

        # Get or create hidden list for this project
        hidden_list = hidden_data.get(project, [])

        if hide and image not in hidden_list:
            hidden_list.append(image)
        elif not hide and image in hidden_list:
            hidden_list.remove(image)

        # Update or remove project entry
        if hidden_list:
            hidden_data[project] = hidden_list
        elif project in hidden_data:
            del hidden_data[project]

        # Save
        with open(HIDDEN_IMAGES_FILE, 'w') as f:
            json.dump(hidden_data, f, indent=2)

        return jsonify({
            'message': f'Image {"hidden" if hide else "shown"}',
            'image': image,
            'hidden': hide
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin-enhanced')
def admin_enhanced():
    """Serve enhanced admin panel"""
    return send_from_directory('.', 'admin-enhanced.html')


@app.route('/api/upload', methods=['POST'])
def upload_images():
    """Upload images to a project folder"""
    password = request.form.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    project_path = request.form.get('project_path')
    if not project_path:
        return jsonify({'error': 'No project path provided'}), 400

    # Ensure the path is within images directory
    target_dir = BASE_DIR / 'images' / project_path
    if not str(target_dir.resolve()).startswith(str((BASE_DIR / 'images').resolve())):
        return jsonify({'error': 'Invalid project path'}), 400

    # Create folder if it doesn't exist
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    uploaded = []
    errors = []

    for file in files:
        if file.filename:
            # Sanitize filename
            filename = file.filename.replace('/', '_').replace('\\', '_')
            # Check extension
            ext = Path(filename).suffix.lower()
            if ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif'}:
                errors.append(f'{filename}: invalid file type')
                continue

            # For HEIC/HEIF, we'll convert to JPG
            is_heic = ext in {'.heic', '.heif'}
            if is_heic:
                # Change extension to .jpg for the saved file
                base_name = Path(filename).stem
                filename = f"{base_name}.jpg"
                ext = '.jpg'

            filepath = target_dir / filename

            # Don't overwrite existing files
            if filepath.exists():
                # Add number suffix
                base = filepath.stem
                counter = 1
                while filepath.exists():
                    filepath = target_dir / f"{base}_{counter}{ext}"
                    counter += 1

            try:
                if is_heic:
                    # Convert HEIC to JPG
                    img = Image.open(file)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    img.save(filepath, 'JPEG', quality=90)
                else:
                    file.save(filepath)

                # Generate thumbnail immediately
                try:
                    thumb_dir = BASE_DIR / 'gen' / 'thumbnails' / project_path
                    thumb_dir.mkdir(parents=True, exist_ok=True)
                    thumb_path = thumb_dir / f"{filepath.stem}.jpg"

                    with Image.open(filepath) as img:
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                        img.save(thumb_path, 'JPEG', quality=80, optimize=True)
                except Exception as thumb_err:
                    print(f"Thumbnail error for {filepath.name}: {thumb_err}")

                uploaded.append(str(filepath.name))
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')

    # Regenerate manifest for this project so gallery updates immediately
    if uploaded:
        # Convert project_path to slug (e.g., "Makers stuff/Furniture/Temple" -> "makers-stuff-furniture-temple")
        slug = project_path.lower().replace(' ', '-').replace('/', '-').replace('--', '-').strip('-')
        print(f"[UPLOAD] Regenerating manifest for {project_path} -> {slug}")
        try:
            manifest = regenerate_manifest(project_path, slug)
            print(f"[UPLOAD] Manifest regenerated: {manifest.get('count')} images")
        except Exception as e:
            import traceback
            print(f"Warning: Failed to regenerate manifest: {e}")
            traceback.print_exc()

    return jsonify({
        'uploaded': uploaded,
        'errors': errors,
        'message': f'Uploaded {len(uploaded)} files'
    })


@app.route('/api/delete-image', methods=['POST'])
def delete_image():
    """Delete an image from a project folder"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    project_path = data.get('project_path')
    image_name = data.get('image_name')

    if not project_path or not image_name:
        return jsonify({'error': 'Missing project path or image name'}), 400

    # Sanitize inputs to prevent path traversal
    if '..' in project_path or '..' in image_name:
        return jsonify({'error': 'Invalid path'}), 400

    # Build paths
    image_path = BASE_DIR / 'images' / project_path / image_name

    # Ensure the path is within images directory
    if not str(image_path.resolve()).startswith(str((BASE_DIR / 'images').resolve())):
        return jsonify({'error': 'Invalid image path'}), 400

    if not image_path.exists():
        return jsonify({'error': 'Image not found'}), 404

    try:
        # Delete the main image
        image_path.unlink()

        # Delete thumbnail if it exists
        thumb_name = Path(image_name).stem + '.jpg'
        thumb_path = BASE_DIR / 'gen' / 'thumbnails' / project_path / thumb_name
        if thumb_path.exists():
            thumb_path.unlink()

        # Regenerate manifest after deletion
        slug = project_path.lower().replace(' ', '-').replace('/', '-').replace('--', '-').strip('-')
        print(f"Regenerating manifest for {project_path} (slug: {slug}) after delete")
        try:
            regenerate_manifest(project_path, slug)
            print(f"Successfully regenerated manifest for {slug}")
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to regenerate manifest after delete: {e}")
            traceback.print_exc()

        return jsonify({'message': 'Image deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create-project', methods=['POST'])
def create_project():
    """Create a new project folder and add to metadata"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    title = data.get('title', '').strip()
    slug = data.get('slug', '').strip()
    category = data.get('category', 'makers')
    year = data.get('year', str(time.localtime().tm_year))

    if not title or not slug:
        return jsonify({'error': 'Title and slug are required'}), 400

    # Validate slug format
    import re
    if not re.match(r'^[a-z0-9-]+$', slug):
        return jsonify({'error': 'Slug can only contain lowercase letters, numbers, and hyphens'}), 400

    # Check if project already exists
    project_dir = BASE_DIR / 'images' / slug
    if project_dir.exists():
        return jsonify({'error': 'A project with this folder name already exists'}), 409

    try:
        # Create the project folder
        project_dir.mkdir(parents=True, exist_ok=True)

        # Add to metadata
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        metadata['projects'][slug] = {
            'title': title,
            'year': year,
            'tags': 'Project • Build • Maker',
            'description': f'{title} project documentation.',
            'featured': False,
            'category': category
        }

        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

        return jsonify({
            'message': 'Project created successfully',
            'slug': slug,
            'path': str(project_dir)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bulk-upload', methods=['POST'])
def bulk_upload():
    """Bulk upload images to create a new project or add to existing"""
    password = request.form.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get project details
    title = request.form.get('title', '').strip()
    slug = request.form.get('slug', '').strip()
    year = request.form.get('year', str(time.localtime().tm_year))
    tags = request.form.get('tags', 'Project • Build • Maker')
    description = request.form.get('description', '')
    category = request.form.get('category', 'makers')
    parent_folder = request.form.get('parent_folder', '')  # e.g., "Makers stuff" or empty

    if not title or not slug:
        return jsonify({'error': 'Title and slug are required'}), 400

    # Validate slug format
    import re
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        return jsonify({'error': 'Slug can only contain letters, numbers, and hyphens'}), 400

    # Build the project path
    if parent_folder:
        project_rel_path = f"{parent_folder}/{slug}"
        project_dir = BASE_DIR / 'images' / parent_folder / slug
    else:
        project_rel_path = slug
        project_dir = BASE_DIR / 'images' / slug

    # Ensure path is safe
    if not str(project_dir.resolve()).startswith(str((BASE_DIR / 'images').resolve())):
        return jsonify({'error': 'Invalid project path'}), 400

    files = request.files.getlist('images')
    if not files or all(not f.filename for f in files):
        return jsonify({'error': 'No files provided'}), 400

    try:
        # Create the project folder
        project_dir.mkdir(parents=True, exist_ok=True)

        uploaded = []
        errors = []

        for file in files:
            if file.filename:
                # Get original path info for folder uploads
                original_path = file.filename
                # Extract just filename (handles both folder/file.jpg and file.jpg)
                filename = Path(original_path).name

                # Sanitize filename
                filename = filename.replace('/', '_').replace('\\', '_')

                # Check extension
                ext = Path(filename).suffix.lower()
                if ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif'}:
                    errors.append(f'{filename}: invalid file type')
                    continue

                # For HEIC/HEIF, convert to JPG
                is_heic = ext in {'.heic', '.heif'}
                if is_heic:
                    base_name = Path(filename).stem
                    filename = f"{base_name}.jpg"
                    ext = '.jpg'

                filepath = project_dir / filename

                # Don't overwrite existing files
                if filepath.exists():
                    base = filepath.stem
                    counter = 1
                    while filepath.exists():
                        filepath = project_dir / f"{base}_{counter}{ext}"
                        counter += 1

                try:
                    if is_heic:
                        # Convert HEIC to JPG
                        img = Image.open(file)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        img.save(filepath, 'JPEG', quality=90)
                    else:
                        file.save(filepath)

                    # Generate thumbnail
                    try:
                        thumb_dir = BASE_DIR / 'gen' / 'thumbnails' / project_rel_path
                        thumb_dir.mkdir(parents=True, exist_ok=True)
                        thumb_path = thumb_dir / f"{filepath.stem}.jpg"

                        with Image.open(filepath) as img:
                            if img.mode == 'RGBA':
                                img = img.convert('RGB')
                            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                            img.save(thumb_path, 'JPEG', quality=80, optimize=True)
                    except Exception as thumb_err:
                        print(f"Thumbnail error for {filepath.name}: {thumb_err}")

                    uploaded.append(str(filepath.name))
                except Exception as e:
                    errors.append(f'{filename}: {str(e)}')

        # Determine the correct slug for metadata (with parent folder prefix if needed)
        if parent_folder:
            # Convert path like "Makers stuff/Go-Cart" to "makers-stuff-go-cart"
            metadata_slug = f"{parent_folder.lower().replace(' ', '-')}-{slug.lower()}"
        else:
            metadata_slug = slug.lower()

        # Add/update metadata
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        if metadata_slug not in metadata.get('projects', {}):
            metadata['projects'][metadata_slug] = {
                'title': title,
                'year': year,
                'tags': tags,
                'description': description or f'{title} project documentation.',
                'featured': False,
                'category': category
            }
        else:
            # Update existing project
            metadata['projects'][metadata_slug].update({
                'title': title,
                'year': year,
                'tags': tags,
                'description': description or metadata['projects'][metadata_slug].get('description', ''),
                'category': category
            })

        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

        return jsonify({
            'message': f'Uploaded {len(uploaded)} files to {project_rel_path}',
            'uploaded': uploaded,
            'errors': errors,
            'slug': metadata_slug,
            'path': project_rel_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/parent-folders', methods=['GET'])
def get_parent_folders():
    """Get list of existing parent folders in images directory"""
    try:
        images_dir = BASE_DIR / 'images'
        folders = []

        for item in images_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if this folder contains subfolders (parent folder pattern)
                has_subfolders = any(
                    subitem.is_dir() and not subitem.name.startswith('.')
                    for subitem in item.iterdir()
                )
                if has_subfolders:
                    folders.append(item.name)

        return jsonify({'folders': sorted(folders)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-project', methods=['POST'])
def delete_project():
    """Delete a project and all its files"""
    data = request.get_json()
    password = data.get('password', '')

    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401

    slug = data.get('slug', '').strip()

    if not slug:
        return jsonify({'error': 'Project slug is required'}), 400

    # Prevent path traversal
    if '..' in slug or '/' in slug or '\\' in slug:
        return jsonify({'error': 'Invalid project slug'}), 400

    try:
        deleted_items = []

        # Delete images folder
        images_dir = BASE_DIR / 'images' / slug
        if images_dir.exists():
            shutil.rmtree(images_dir)
            deleted_items.append(f'images/{slug}')

        # Also check for "Makers stuff" style paths
        for parent in ['Makers stuff', 'Engeneering']:
            alt_dir = BASE_DIR / 'images' / parent / slug
            if alt_dir.exists():
                shutil.rmtree(alt_dir)
                deleted_items.append(f'images/{parent}/{slug}')

        # Delete thumbnails folder
        thumb_dir = BASE_DIR / 'gen' / 'thumbnails' / slug
        if thumb_dir.exists():
            shutil.rmtree(thumb_dir)
            deleted_items.append(f'gen/thumbnails/{slug}')

        # Also check alternative thumbnail paths
        for parent in ['Makers stuff', 'Engeneering']:
            alt_thumb = BASE_DIR / 'gen' / 'thumbnails' / parent / slug
            if alt_thumb.exists():
                shutil.rmtree(alt_thumb)
                deleted_items.append(f'gen/thumbnails/{parent}/{slug}')

        # Delete manifest
        manifest_file = BASE_DIR / 'gen' / 'manifests' / f'{slug}.json'
        if manifest_file.exists():
            manifest_file.unlink()
            deleted_items.append(f'gen/manifests/{slug}.json')

        # Delete project page
        project_page = BASE_DIR / 'projects' / f'{slug}.html'
        if project_page.exists():
            project_page.unlink()
            deleted_items.append(f'projects/{slug}.html')

        # Remove from metadata
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        if slug in metadata.get('projects', {}):
            del metadata['projects'][slug]

        # Remove from featuredOrder if present
        if 'featuredOrder' in metadata and slug in metadata['featuredOrder']:
            metadata['featuredOrder'].remove(slug)

        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Regenerate site index by running build script
        subprocess.run(['python3', 'build_site.py'], cwd=BASE_DIR, capture_output=True)

        return jsonify({
            'message': 'Project deleted successfully',
            'deleted': deleted_items
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting development server...")
    print("Main site: http://localhost:5000")
    print("Admin panel: http://localhost:5000/admin")
    print("Enhanced admin: http://localhost:5000/admin-enhanced")
    print(f"Admin password: {ADMIN_PASSWORD}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
