import os
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ExifTags

# Paths relative to project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
WEBSITE_DIR = os.path.join(PROJECT_ROOT, "Website")
IMAGES_WEB_DIR = os.path.join(WEBSITE_DIR, "assets", "images_web")
CONTENT_DIR = os.path.join(WEBSITE_DIR, "content")

MAX_DIMENSION = 1600
JPEG_QUALITY = 80

def correct_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            val = exif.get(orientation, None)
            if val == 3:
                image = image.rotate(180, expand=True)
            elif val == 6:
                image = image.rotate(270, expand=True)
            elif val == 8:
                image = image.rotate(90, expand=True)
    except Exception:
        pass
    return image

def optimize_single_image(src_path, dest_path):
    with Image.open(src_path) as img:
        img = correct_orientation(img)
        if img.mode in ("RGBA", "P", "CMYK"):
            img = img.convert("RGB")
        width, height = img.size
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            if width > height:
                nw = MAX_DIMENSION
                nh = int(MAX_DIMENSION * height / width)
            else:
                nh = MAX_DIMENSION
                nw = int(MAX_DIMENSION * width / height)
            img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True)

class CheGuPublisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CheGu Website — Photo Publisher")
        self.geometry("640x700")
        self.minsize(550, 600)
        self.configure(bg="#181818")

        self.selected_files = []
        self.setup_ui()
        self.refresh_categories()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#181818", pady=15)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="CHEGU PORTFOLIO MANAGER", font=("Helvetica", 18, "bold"), fg="#ffffff", bg="#181818")
        lbl_title.pack()
        lbl_sub = tk.Label(header_frame, text="Add photos & publish directly to chegu.netlify.app without touching code", font=("Helvetica", 10), fg="#888888", bg="#181818")
        lbl_sub.pack(pady=3)

        # Card Container
        card = tk.Frame(self, bg="#242424", padx=20, pady=20, bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=25, pady=10)

        # 1. Category Selection
        lbl_cat = tk.Label(card, text="1. Select Photo Series / Project:", font=("Helvetica", 11, "bold"), fg="#ffffff", bg="#242424")
        lbl_cat.pack(anchor="w", pady=(0, 5))

        cat_row = tk.Frame(card, bg="#242424")
        cat_row.pack(fill="x", pady=(0, 15))

        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(cat_row, textvariable=self.cat_var, state="readonly", font=("Helvetica", 11))
        self.cat_combo.pack(side="left", fill="x", expand=True, ipady=4)
        self.cat_combo.bind("<<ComboboxSelected>>", self.on_category_selected)

        btn_new_cat = tk.Button(cat_row, text="+ New Series", command=self.prompt_new_category, bg="#3a3a3a", fg="#ffffff", font=("Helvetica", 10), relief="groove", padx=10)
        btn_new_cat.pack(side="left", padx=(8, 0))

        # 2. File Selection
        lbl_files = tk.Label(card, text="2. Choose High-Res Photos from Computer:", font=("Helvetica", 11, "bold"), fg="#ffffff", bg="#242424")
        lbl_files.pack(anchor="w", pady=(0, 5))

        file_row = tk.Frame(card, bg="#242424")
        file_row.pack(fill="x", pady=(0, 5))

        btn_choose = tk.Button(file_row, text="📁 Browse Photos...", command=self.choose_photos, bg="#2e64b6", fg="#ffffff", font=("Helvetica", 11, "bold"), padx=12, pady=5, relief="groove")
        btn_choose.pack(side="left")

        btn_clear = tk.Button(file_row, text="Clear List", command=self.clear_photos, bg="#3a3a3a", fg="#ffffff", font=("Helvetica", 10), padx=8, pady=5, relief="groove")
        btn_clear.pack(side="left", padx=8)

        self.lbl_file_count = tk.Label(file_row, text="0 photos selected", font=("Helvetica", 10, "italic"), fg="#aaaaaa", bg="#242424")
        self.lbl_file_count.pack(side="left", padx=5)

        # File Listbox
        self.file_listbox = tk.Listbox(card, height=4, bg="#1a1a1a", fg="#00ffcc", font=("Helvetica", 9), selectbackground="#333333", bd=0, highlightthickness=1, highlightbackground="#444")
        self.file_listbox.pack(fill="x", pady=(0, 15))

        # 3. Series Description
        lbl_desc = tk.Label(card, text="3. Series Story / Description (Optional):", font=("Helvetica", 11, "bold"), fg="#ffffff", bg="#242424")
        lbl_desc.pack(anchor="w", pady=(0, 5))

        self.txt_desc = tk.Text(card, height=4, bg="#1a1a1a", fg="#ffffff", font=("Helvetica", 10), insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#444")
        self.txt_desc.pack(fill="x", pady=(0, 15))

        # Progress / Status Box
        self.status_var = tk.StringVar(value="Ready. Select series and photos to publish.")
        lbl_status = tk.Label(card, textvariable=self.status_var, font=("Helvetica", 10, "bold"), fg="#e0a800", bg="#242424", wraplength=520, justify="left")
        lbl_status.pack(fill="x", pady=(0, 8))

        self.progress_bar = ttk.Progressbar(card, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 15))

        # 4. BIG ACTION BUTTON
        self.btn_publish = tk.Button(self, text="🚀 OPTIMIZE & PUBLISH LIVE", command=self.start_publish, bg="#1b853e", fg="#ffffff", font=("Helvetica", 13, "bold"), pady=12, relief="raised", cursor="hand2")
        self.btn_publish.pack(fill="x", padx=25, pady=(0, 20))

    def refresh_categories(self):
        categories = []
        if os.path.exists(IMAGES_WEB_DIR):
            for d in sorted(os.listdir(IMAGES_WEB_DIR)):
                if os.path.isdir(os.path.join(IMAGES_WEB_DIR, d)) and not d.startswith('.') and d.lower() != 'thumbnail':
                    categories.append(d)
        self.cat_combo['values'] = categories
        if categories:
            if not self.cat_var.get() or self.cat_var.get() not in categories:
                self.cat_combo.current(0)
            self.on_category_selected()

    def on_category_selected(self, event=None):
        cat = self.cat_var.get()
        if not cat:
            return
        desc_path = os.path.join(IMAGES_WEB_DIR, cat, "description.txt")
        self.txt_desc.delete("1.0", tk.END)
        if os.path.exists(desc_path):
            try:
                with open(desc_path, 'r', encoding='utf-8') as f:
                    self.txt_desc.insert("1.0", f.read())
            except Exception:
                pass

    def prompt_new_category(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Series")
        dialog.geometry("380x160")
        dialog.configure(bg="#222222")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Enter New Series Name:", font=("Helvetica", 11, "bold"), fg="#fff", bg="#222222").pack(pady=(20, 8))
        entry = tk.Entry(dialog, font=("Helvetica", 12), width=28)
        entry.pack(pady=5)
        entry.focus_set()

        def save():
            name = entry.get().strip()
            if name:
                new_dir = os.path.join(IMAGES_WEB_DIR, name)
                os.makedirs(new_dir, exist_ok=True)
                self.refresh_categories()
                self.cat_var.set(name)
                self.on_category_selected()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Series name cannot be empty.", parent=dialog)

        btn_save = tk.Button(dialog, text="Create", command=save, bg="#2e64b6", fg="#fff", font=("Helvetica", 10, "bold"), padx=15, pady=4)
        btn_save.pack(pady=10)

    def choose_photos(self):
        files = filedialog.askopenfilenames(
            title="Select Photos to Add",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.webp *.JPG *.JPEG *.PNG"),
                ("All files", "*.*")
            ]
        )
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    self.file_listbox.insert(tk.END, os.path.basename(f))
            self.lbl_file_count.config(text=f"{len(self.selected_files)} photos selected")

    def clear_photos(self):
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.lbl_file_count.config(text="0 photos selected")

    def set_ui_busy(self, busy=True):
        if busy:
            self.btn_publish.config(state="disabled", text="Processing... Please Wait")
        else:
            self.btn_publish.config(state="normal", text="🚀 OPTIMIZE & PUBLISH LIVE")

    def start_publish(self):
        cat = self.cat_var.get()
        if not cat:
            messagebox.showerror("Error", "Please select or create a series.")
            return

        desc_text = self.txt_desc.get("1.0", tk.END).strip()
        
        if not self.selected_files and not desc_text:
            messagebox.showinfo("Nothing to Update", "Please select photos or write a description to update.")
            return

        self.set_ui_busy(True)
        thread = threading.Thread(target=self.run_publish_pipeline, args=(cat, desc_text, list(self.selected_files)))
        thread.daemon = True
        thread.start()

    def run_publish_pipeline(self, category, description, files):
        try:
            target_cat_dir = os.path.join(IMAGES_WEB_DIR, category)
            os.makedirs(target_cat_dir, exist_ok=True)

            # 1. Save Description if provided
            if description:
                self.status_var.set(f"Saving description for '{category}'...")
                with open(os.path.join(target_cat_dir, "description.txt"), "w", encoding="utf-8") as f:
                    f.write(description)

            # 2. Optimize images
            total_files = len(files)
            if total_files > 0:
                self.progress_bar['maximum'] = total_files
                for i, src in enumerate(files):
                    fname = os.path.basename(src)
                    bname, _ = os.path.splitext(fname)
                    dest_file = os.path.join(target_cat_dir, f"{bname}.jpg")

                    self.status_var.set(f"Optimizing ({i+1}/{total_files}): {fname}")
                    self.progress_bar['value'] = i + 1

                    optimize_single_image(src, dest_file)

            # 3. Rebuild HTML pages
            self.status_var.set("Rebuilding website HTML pages...")
            gen_script = os.path.join(WEBSITE_DIR, "generate_pages.py")
            subprocess.run([sys.executable, gen_script], cwd=WEBSITE_DIR, check=True)

            # 4. Git Commit & Push
            self.status_var.set("Pushing updates live to GitHub & Netlify...")
            try:
                subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
                commit_msg = f"Update '{category}': Added {total_files} photos and updated site"
                # Check if there is anything to commit
                diff_proc = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=PROJECT_ROOT)
                if diff_proc.returncode != 0:
                    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
                    push_proc = subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, capture_output=True, text=True)
                    if push_proc.returncode != 0:
                        raise Exception(push_proc.stderr or "git push failed")
                    published_online = True
                else:
                    published_online = False
            except Exception as git_err:
                # If git credentials not set up or offline, website is still built locally
                print("Git error:", git_err)
                published_online = False

            # Complete!
            self.progress_bar['value'] = 0
            self.status_var.set("🎉 Done! Website updated.")
            self.after(0, lambda: self.on_publish_success(category, total_files, published_online))

        except Exception as e:
            self.status_var.set("❌ Error occurred during publishing.")
            self.after(0, lambda: messagebox.showerror("Publish Error", f"An error occurred:\n{str(e)}"))
        finally:
            self.after(0, lambda: self.set_ui_busy(False))

    def on_publish_success(self, category, count, published_online):
        self.clear_photos()
        if published_online:
            msg = f"Successfully added {count} photo(s) to '{category}'.\n\nUpdates pushed to GitHub!\nNetlify will publish changes to https://chegu.netlify.app in ~1 minute."
        else:
            msg = f"Successfully added {count} photo(s) to '{category}' and rebuilt HTML.\n\n(Tip: If not connected to internet or GitHub, push via GitHub Desktop when ready)."
        messagebox.showinfo("Success! 🎉", msg)

if __name__ == "__main__":
    app = CheGuPublisherApp()
    app.mainloop()
