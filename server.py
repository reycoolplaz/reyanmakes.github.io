#!/usr/bin/env python3
"""
Development server with API endpoint for build script execution
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import subprocess
import os
from pathlib import Path
import threading
import time

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent

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

if __name__ == '__main__':
    print("🚀 Starting development server...")
    print("📝 Main site: http://localhost:5000")
    print("🔧 Admin panel: http://localhost:5000/admin")
    print(f"🔑 Admin password: {ADMIN_PASSWORD}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
