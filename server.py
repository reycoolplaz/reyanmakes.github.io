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
    valid_layouts = ['modern', 'minimal', 'magazine']
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

    if not target_dir.exists():
        return jsonify({'error': 'Project folder not found'}), 404

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
                        img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                        img.save(thumb_path, 'JPEG', quality=75, optimize=True)
                except Exception as thumb_err:
                    print(f"Thumbnail error for {filepath.name}: {thumb_err}")

                uploaded.append(str(filepath.name))
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')

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
    print("🚀 Starting development server...")
    print("📝 Main site: http://localhost:5000")
    print("🔧 Admin panel: http://localhost:5000/admin")
    print("✨ Enhanced admin: http://localhost:5000/admin-enhanced")
    print(f"🔑 Admin password: {ADMIN_PASSWORD}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
