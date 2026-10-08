import os
import shutil
import sys
try:
    from PIL import Image, ExifTags
except ImportError:
    print("Installing Pillow for image optimization...")
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image, ExifTags

PORTFOLIO_DIR = "../pORTFOLIO"
WEB_ASSETS_DIR = "assets/images_web"

# Maximum dimension (width or height)
MAX_DIMENSION = 1600
JPEG_QUALITY = 80

def correct_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_val = exif.get(orientation, None)
            if orientation_val == 3:
                image = image.rotate(180, expand=True)
            elif orientation_val == 6:
                image = image.rotate(270, expand=True)
            elif orientation_val == 8:
                image = image.rotate(90, expand=True)
    except Exception:
        pass
    return image

def optimize_image(src_path, dest_path):
    print(f"Optimizing {src_path} -> {dest_path}")
    try:
        with Image.open(src_path) as img:
            # Correct orientation from EXIF if needed
            img = correct_orientation(img)
            
            # Convert to RGB if it's RGBA (for PNGs) or CMYK
            if img.mode in ("RGBA", "P", "CMYK"):
                img = img.convert("RGB")
            
            # Calculate new size maintaining aspect ratio
            width, height = img.size
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                if width > height:
                    new_width = MAX_DIMENSION
                    new_height = int(MAX_DIMENSION * height / width)
                else:
                    new_height = MAX_DIMENSION
                    new_width = int(MAX_DIMENSION * width / height)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
            # Save as JPEG with optimized compression
            img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    except Exception as e:
        print(f"Failed to process {src_path}: {e}")

def main():
    if not os.path.exists(PORTFOLIO_DIR):
        print(f"Error: {PORTFOLIO_DIR} not found.")
        return

    # Delete the entire output directory to ensure we don't keep orphaned files
    if os.path.exists(WEB_ASSETS_DIR):
        print(f"Cleaning {WEB_ASSETS_DIR}...")
        shutil.rmtree(WEB_ASSETS_DIR)
        
    for category in os.listdir(PORTFOLIO_DIR):
        cat_path = os.path.join(PORTFOLIO_DIR, category)
        if not os.path.isdir(cat_path) or category.startswith('.'):
            continue
            
        out_cat_path = os.path.join(WEB_ASSETS_DIR, category)
        os.makedirs(out_cat_path, exist_ok=True)
        
        for file in os.listdir(cat_path):
            if file.startswith('.'):
                continue
                
            file_lower = file.lower()
            # Support common image formats
            if file_lower.endswith(('.jpg', '.jpeg', '.png', '.nef', '.cr2', '.tif', '.tiff', '.webp')):
                src_file = os.path.join(cat_path, file)
                
                # Base name without extension, force .jpg extension
                base_name = os.path.splitext(file)[0]
                dest_file = os.path.join(out_cat_path, f"{base_name}.jpg")
                
                # Pillow cannot natively read RAW files like .NEF or .CR2 easily without rawpy.
                # If it's a RAW file, Pillow will fail. We must warn them to upload high-res JPEGs.
                if file_lower.endswith(('.nef', '.cr2')):
                    print(f"WARNING: RAW files ({file}) require a Mac. Please upload High-Res JPEGs instead.")
                    continue
                    
                optimize_image(src_file, dest_file)

if __name__ == "__main__":
    main()
