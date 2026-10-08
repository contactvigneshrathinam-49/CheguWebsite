#!/bin/bash

# Directories
SOURCE_DIR="/Volumes/Che-Card-1/pORTFOLIO"
DEST_DIR="/Volumes/Che-Card-1/Website/assets/images_web"

# Create destination if it doesn't exist
mkdir -p "$DEST_DIR"

# Clean up orphaned directories in DEST_DIR (e.g. if a folder was renamed in pORTFOLIO)
for dest_cat in "$DEST_DIR"/*; do
    if [ -d "$dest_cat" ]; then
        cat_name=$(basename "$dest_cat")
        if [ ! -d "$SOURCE_DIR/$cat_name" ] && [ "$cat_name" != "Thumbnail" ]; then
            echo "Removing orphaned directory: $cat_name"
            rm -rf "$dest_cat"
        fi
    fi
done

# Find all images recursively inside SOURCE_DIR (including RAW files)
find "$SOURCE_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.nef" -o -iname "*.cr2" -o -iname "*.arw" -o -iname "*.tiff" -o -iname "*.tif" \) | while read img; do
    # Skip hidden files/folders
    if [[ "$img" == */.* ]]; then
        continue
    fi

    # Get relative path of image from SOURCE_DIR
    rel_path="${img#$SOURCE_DIR/}"
    category=$(echo "$rel_path" | cut -d'/' -f1)
    
    # Change extension to .jpg in destination for web compatibility
    base_name="${rel_path%.*}"
    dest_file="$DEST_DIR/${base_name}.jpg"
    dest_folder=$(dirname "$dest_file")
    
    mkdir -p "$dest_folder"
    
    # Skip if already exists and destination is newer than source
    if [ -f "$dest_file" ] && [ "$dest_file" -nt "$img" ]; then
        continue
    fi
    
    echo "Optimizing: $rel_path"
    
    # Resize so longest edge is 1200px (good for web/retina while keeping size small)
    # and compress quality to 80%. Explicitly set format to jpeg for RAW conversions.
    sips -Z 1200 -s format jpeg -s formatOptions 80 "$img" --out "$dest_file" > /dev/null
done

echo "Optimization complete!"
