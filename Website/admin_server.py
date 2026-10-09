import os
import shutil
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='/Volumes/Che-Card-1/Website')
portfolio_dir = "/Volumes/Che-Card-1/pORTFOLIO"
web_dir = "/Volumes/Che-Card-1/Website"
web_images_dir = os.path.join(web_dir, "assets", "images_web")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/admin/login', methods=['POST'])
def login():
    data = request.json
    if data and data.get('username') == 'contactvigneshrathinam@gmail.com' and data.get('password') == 'sherwin9':
        return jsonify({"status": "success", "token": "secret-admin-token"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

def check_auth():
    token = request.headers.get('Authorization')
    return token == 'Bearer secret-admin-token'

@app.route('/api/admin/data', methods=['GET'])
def get_data():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
        
    categories = []
    # Read from pORTFOLIO for source of truth, but look at web_images for thumbnails
    if os.path.exists(portfolio_dir):
        for d in sorted(os.listdir(portfolio_dir)):
            if os.path.isdir(os.path.join(portfolio_dir, d)) and not d.startswith('.'):
                cat_data = {"name": d, "description": "", "images": []}
                desc_path = os.path.join(portfolio_dir, d, 'description.txt')
                if os.path.exists(desc_path):
                    with open(desc_path, 'r') as f:
                        cat_data["description"] = f.read()
                
                # Get web-optimized images for preview
                web_cat_dir = os.path.join(web_images_dir, d)
                if os.path.exists(web_cat_dir):
                    images = sorted([img for img in os.listdir(web_cat_dir) if img.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    cat_data["images"] = [f"assets/images_web/{d}/{img}" for img in images]
                
                categories.append(cat_data)
                
    # Also get static pages
    static_pages = {}
    for page in ['about.txt', 'contact.txt']:
        p_path = os.path.join(portfolio_dir, page)
        if os.path.exists(p_path):
            with open(p_path, 'r') as f:
                static_pages[page] = f.read()
        else:
            static_pages[page] = ""
            
    return jsonify({"categories": categories, "static_pages": static_pages})

@app.route('/api/admin/update_text', methods=['POST'])
def update_text():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    target = data.get('target') # e.g. "Politics" or "about.txt"
    content = data.get('content')
    
    if target.endswith('.txt'):
        path = os.path.join(portfolio_dir, target)
    else:
        path = os.path.join(portfolio_dir, target, 'description.txt')
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            
    with open(path, 'w') as f:
        f.write(content)
    return jsonify({"status": "success"})

@app.route('/api/admin/delete_image', methods=['POST'])
def delete_image():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    image_url = data.get('image') # e.g. /assets/images_web/Politics/1.jpg
    
    if not image_url: return jsonify({"error": "No image specified"}), 400
    
    parts = image_url.split('/')
    category = parts[-2]
    filename = parts[-1]
    
    # Delete from pORTFOLIO
    source_path = os.path.join(portfolio_dir, category, filename)
    # Note: filename might have different extension in RAW, so we might need to delete by prefix.
    # For now, if they are JPEGs, this works. We will try to delete the exact name first.
    basename, _ = os.path.splitext(filename)
    deleted_source = False
    if os.path.exists(os.path.join(portfolio_dir, category)):
        for f in os.listdir(os.path.join(portfolio_dir, category)):
            if f.startswith(basename):
                os.remove(os.path.join(portfolio_dir, category, f))
                deleted_source = True
                
    # Also delete from web cache so it disappears immediately
    web_path = os.path.join(web_dir, image_url.lstrip('/'))
    if os.path.exists(web_path):
        os.remove(web_path)
        
    return jsonify({"status": "success"})

@app.route('/api/admin/delete_category', methods=['POST'])
def delete_category():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    category = data.get('category')
    
    if category:
        source_dir = os.path.join(portfolio_dir, category)
        if os.path.exists(source_dir):
            shutil.rmtree(source_dir)
        web_cat_dir = os.path.join(web_images_dir, category)
        if os.path.exists(web_cat_dir):
            shutil.rmtree(web_cat_dir)
    return jsonify({"status": "success"})

@app.route('/api/admin/upload', methods=['POST'])
def upload():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    if 'file' not in request.files or 'category' not in request.form:
        return jsonify({"error": "Missing file or category"}), 400
        
    file = request.files['file']
    category = request.form['category']
    
    cat_dir = os.path.join(portfolio_dir, category)
    if not os.path.exists(cat_dir):
        os.makedirs(cat_dir)
        
    if file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(cat_dir, filename))
        return jsonify({"status": "success", "message": f"Uploaded {filename}"})
    return jsonify({"error": "No file selected"}), 400

@app.route('/api/admin/build', methods=['POST'])
def build():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    try:
        import sys
        subprocess.run([sys.executable, "optimize_images.py"], cwd=web_dir, check=True)
        subprocess.run([sys.executable, "generate_pages.py"], cwd=web_dir, check=True)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("===================================================")
    print(" CHEGU ADMIN PANEL IS RUNNING")
    print(" Open http://localhost:5001 in your browser")
    print("===================================================")
    app.run(host='127.0.0.1', port=5001, debug=False)
