import os
import shutil
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import sys

app = Flask(__name__, static_folder=os.path.abspath(os.path.dirname(__file__)))
web_dir = os.path.abspath(os.path.dirname(__file__))
portfolio_dir = os.path.abspath(os.path.join(web_dir, '..', 'pORTFOLIO'))
web_images_dir = os.path.join(web_dir, "assets", "images_web")

content_dir = os.path.join(web_dir, "content")
if not os.path.exists(content_dir):
    os.makedirs(content_dir, exist_ok=True)

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
    # Read categories from web_images_dir
    if os.path.exists(web_images_dir):
        for d in sorted(os.listdir(web_images_dir)):
            if os.path.isdir(os.path.join(web_images_dir, d)) and not d.startswith('.') and d.lower() != 'thumbnail':
                cat_data = {"name": d, "description": "", "images": []}
                desc_path = os.path.join(web_images_dir, d, 'description.txt')
                if not os.path.exists(desc_path) and os.path.exists(portfolio_dir):
                    desc_path = os.path.join(portfolio_dir, d, 'description.txt')
                if os.path.exists(desc_path):
                    try:
                        with open(desc_path, 'r', encoding='utf-8') as f:
                            cat_data["description"] = f.read()
                    except Exception:
                        pass
                
                # Get web images for preview
                web_cat_dir = os.path.join(web_images_dir, d)
                images = sorted([img for img in os.listdir(web_cat_dir) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not img.startswith('._')])
                cat_data["images"] = [f"assets/images_web/{d}/{img}" for img in images]
                
                categories.append(cat_data)
                
    # Also get static pages
    static_pages = {}
    for page in ['about.txt', 'contact.txt', 'videos.json']:
        p_path = os.path.join(content_dir, page)
        if not os.path.exists(p_path) and os.path.exists(portfolio_dir):
            p_path = os.path.join(portfolio_dir, page)
        if os.path.exists(p_path):
            with open(p_path, 'r', encoding='utf-8') as f:
                static_pages[page] = f.read()
        else:
            static_pages[page] = ""
            
    return jsonify({"categories": categories, "static_pages": static_pages})

@app.route('/api/admin/update_text', methods=['POST'])
def update_text():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    target = data.get('target') # e.g. "Politics", "about.txt", or "videos.json"
    content = data.get('content')
    
    if target.endswith('.txt') or target.endswith('.json'):
        path = os.path.join(content_dir, target)
    else:
        path = os.path.join(web_images_dir, target, 'description.txt')
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({"status": "success"})

@app.route('/api/admin/delete_image', methods=['POST'])
def delete_image():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    image_url = data.get('image') # e.g. /assets/images_web/Politics/1.jpg
    
    if not image_url: return jsonify({"error": "No image specified"}), 400
    
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
    
    cat_dir = os.path.join(web_images_dir, category)
    if not os.path.exists(cat_dir):
        os.makedirs(cat_dir)
        
    if file.filename:
        filename = secure_filename(file.filename)
        base, _ = os.path.splitext(filename)
        dest_filename = f"{base}.jpg"
        temp_path = os.path.join(cat_dir, f"temp_{filename}")
        file.save(temp_path)
        
        # Optimize right away into web_images_dir
        try:
            from optimize_images import optimize_image
            optimize_image(temp_path, os.path.join(cat_dir, dest_filename))
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            if os.path.exists(temp_path):
                os.rename(temp_path, os.path.join(cat_dir, filename))
                
        return jsonify({"status": "success", "message": f"Uploaded {filename}"})
    return jsonify({"error": "No file selected"}), 400

@app.route('/api/admin/build', methods=['POST'])
def build():
    if not check_auth(): return jsonify({"error": "Unauthorized"}), 401
    try:
        import sys
        # Generate pages
        subprocess.run([sys.executable, "generate_pages.py"], cwd=web_dir, check=True)
        
        # Also auto-push if git available
        project_root = os.path.abspath(os.path.join(web_dir, '..'))
        try:
            subprocess.run(["git", "add", "."], cwd=project_root, check=True)
            diff_proc = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=project_root)
            if diff_proc.returncode != 0:
                subprocess.run(["git", "commit", "-m", "Website CMS update"], cwd=project_root, check=True)
                subprocess.run(["git", "push", "origin", "main"], cwd=project_root, check=True)
        except Exception as e:
            print("Git push error in admin build:", e)
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("===================================================")
    print(" CHEGU ADMIN PANEL IS RUNNING")
    print(" Open http://localhost:5001 in your browser")
    print("===================================================")
    app.run(host='127.0.0.1', port=5001, debug=False)
