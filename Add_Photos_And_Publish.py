import os
import sys
import json
import shutil
import subprocess
import threading
import webbrowser
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ExifTags

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

def extract_youtube_id(url_or_id):
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and ' ' not in url_or_id and '/' not in url_or_id:
        return url_or_id
    match = re.search(r'(?:v=|\/|youtu\.be\/|embed\/)([0-9A-Za-z_-]{11})', url_or_id)
    if match:
        return match.group(1)
    return url_or_id

class CheGuStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CheGu Portfolio Studio — Web Manager")
        self.geometry("1020x820")
        self.minsize(940, 740)
        self.configure(bg="#141414")

        self.selected_files = []
        self.current_preview_photo = None
        self.videos_data = []
        self.grid_order = []

        self.setup_styles()
        self.setup_ui()
        self.refresh_all_data()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configure dark colors
        style.configure("TNotebook", background="#141414", borderwidth=0)
        style.configure("TNotebook.Tab", background="#222222", foreground="#aaaaaa", padding=[16, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", "#323232")], foreground=[("selected", "#ffffff")])

        style.configure("TCombobox", fieldbackground="#242424", background="#333333", foreground="#ffffff", borderwidth=1, arrowcolor="#ffffff")
        style.map("TCombobox", fieldbackground=[("readonly", "#242424")], selectbackground=[("readonly", "#3b3b3b")])

        style.configure("TProgressbar", thickness=8, troughcolor="#222222", background="#2e7d32")

    def setup_ui(self):
        # 1. Header Bar
        header = tk.Frame(self, bg="#141414", pady=12, padx=22)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg="#141414")
        title_box.pack(side="left")

        lbl_logo = tk.Label(title_box, text="CHEGU", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#141414")
        lbl_logo.pack(side="left")

        lbl_sub = tk.Label(title_box, text="PORTFOLIO STUDIO", font=("Segoe UI", 13), fg="#4f8ef7", bg="#141414")
        lbl_sub.pack(side="left", padx=10)

        badge = tk.Label(title_box, text="Live at chegu.netlify.app", font=("Segoe UI", 9), fg="#888888", bg="#141414")
        badge.pack(side="left", padx=5)

        # Quick preview link
        btn_preview = tk.Button(header, text="👁️ Open Local Preview", command=self.preview_site_in_browser, bg="#262626", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=12, pady=4, cursor="hand2")
        btn_preview.pack(side="right")

        # 2. Main Tabbed Container
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Tabs
        self.tab_photos = tk.Frame(self.notebook, bg="#1e1e1e")
        self.tab_grid = tk.Frame(self.notebook, bg="#1e1e1e")
        self.tab_videos = tk.Frame(self.notebook, bg="#1e1e1e")
        self.tab_bio = tk.Frame(self.notebook, bg="#1e1e1e")

        self.notebook.add(self.tab_photos, text=" 📸  Photo Series & Galleries ")
        self.notebook.add(self.tab_grid, text=" 🎛️  Homepage Grid Order ")
        self.notebook.add(self.tab_videos, text=" 🎬  Video Works ")
        self.notebook.add(self.tab_bio, text=" 📝  About & Contact ")

        self.setup_photos_tab()
        self.setup_grid_tab()
        self.setup_videos_tab()
        self.setup_bio_tab()

        # 3. Bottom Status and Publish Dock
        bottom_dock = tk.Frame(self, bg="#181818", padx=20, pady=12, bd=1, relief="ridge")
        bottom_dock.pack(fill="x", side="bottom")

        status_left = tk.Frame(bottom_dock, bg="#181818")
        status_left.pack(side="left", fill="x", expand=True)

        self.status_var = tk.StringVar(value="Ready. Any edits can be saved or published live.")
        self.lbl_status = tk.Label(status_left, textvariable=self.status_var, font=("Segoe UI", 10), fg="#e0a800", bg="#181818", anchor="w")
        self.lbl_status.pack(fill="x", pady=(0, 4))

        self.progress_bar = ttk.Progressbar(status_left, mode="determinate")
        self.progress_bar.pack(fill="x")

        # Actions on right
        actions_right = tk.Frame(bottom_dock, bg="#181818")
        actions_right.pack(side="right", padx=(20, 0))

        btn_rebuild = tk.Button(actions_right, text="⚡ Save & Rebuild Locally", command=self.trigger_rebuild_local, bg="#333333", fg="#ffffff", font=("Segoe UI", 10), relief="flat", padx=12, pady=7, cursor="hand2")
        btn_rebuild.pack(side="left", padx=6)

        self.btn_publish = tk.Button(actions_right, text="🚀 SAVE & PUBLISH LIVE", command=self.start_publish, bg="#1b853e", fg="#ffffff", font=("Segoe UI", 11, "bold"), relief="flat", padx=18, pady=7, cursor="hand2")
        self.btn_publish.pack(side="left")

    # =========================================================================
    # TAB 1: PHOTOS & SERIES
    # =========================================================================
    def setup_photos_tab(self):
        container = tk.Frame(self.tab_photos, bg="#1e1e1e", padx=16, pady=16)
        container.pack(fill="both", expand=True)

        # Series Selector Bar
        top_bar = tk.Frame(container, bg="#272727", padx=12, pady=10, bd=1, relief="solid")
        top_bar.pack(fill="x", pady=(0, 14))

        tk.Label(top_bar, text="Series / Project:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#272727").pack(side="left", padx=(0, 10))

        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(top_bar, textvariable=self.cat_var, state="readonly", font=("Segoe UI", 11), width=28)
        self.cat_combo.pack(side="left", ipady=3)
        self.cat_combo.bind("<<ComboboxSelected>>", self.on_category_selected)

        btn_new_cat = tk.Button(top_bar, text="+ New Series", command=self.prompt_new_category, bg="#3b3b3b", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4, cursor="hand2")
        btn_new_cat.pack(side="left", padx=8)

        btn_rename_cat = tk.Button(top_bar, text="✏️ Rename", command=self.prompt_rename_category, bg="#333333", fg="#dddddd", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_rename_cat.pack(side="left", padx=4)

        btn_del_cat = tk.Button(top_bar, text="🗑️ Delete Series", command=self.prompt_delete_category, bg="#552222", fg="#ffcccc", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_del_cat.pack(side="right")

        # Two-column split
        columns = tk.Frame(container, bg="#1e1e1e")
        columns.pack(fill="both", expand=True)

        # LEFT COLUMN: Existing Photos in Series
        left_col = tk.Frame(columns, bg="#232323", padx=14, pady=12, bd=1, relief="solid")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.lbl_existing_photos = tk.Label(left_col, text="Photos in Series (0)", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#232323")
        self.lbl_existing_photos.pack(anchor="w", pady=(0, 8))

        list_frame = tk.Frame(left_col, bg="#232323")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.existing_listbox = tk.Listbox(list_frame, bg="#141414", fg="#ffffff", selectbackground="#4f8ef7", selectforeground="#ffffff", font=("Segoe UI", 10), yscrollcommand=scrollbar.set, bd=0, highlightthickness=1, highlightbackground="#333333")
        self.existing_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.existing_listbox.yview)
        self.existing_listbox.bind("<<ListboxSelect>>", self.on_existing_photo_select)

        # Image preview box
        preview_frame = tk.Frame(left_col, bg="#181818", height=130, bd=1, relief="solid")
        preview_frame.pack(fill="x", pady=(10, 6))
        preview_frame.pack_propagate(False)

        self.lbl_preview_img = tk.Label(preview_frame, text="Select photo to preview", font=("Segoe UI", 9, "italic"), fg="#777777", bg="#181818")
        self.lbl_preview_img.pack(fill="both", expand=True)

        # Buttons under existing photos list
        photo_actions = tk.Frame(left_col, bg="#232323")
        photo_actions.pack(fill="x", pady=(6, 0))

        btn_thumb = tk.Button(photo_actions, text="⭐ Set as Cover", command=self.set_selected_photo_as_thumbnail, bg="#d48806", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_thumb.pack(side="left", padx=(0, 4))

        btn_up = tk.Button(photo_actions, text="⬆ Move Up", command=lambda: self.reorder_existing_photo(-1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_up.pack(side="left", padx=4)

        btn_down = tk.Button(photo_actions, text="⬇ Move Down", command=lambda: self.reorder_existing_photo(1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_down.pack(side="left", padx=4)

        btn_del_photo = tk.Button(photo_actions, text="🗑️ Delete", command=self.delete_selected_existing_photo, bg="#7a1f1d", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_del_photo.pack(side="right")

        # RIGHT COLUMN: Add New Photos & Edit Description
        right_col = tk.Frame(columns, bg="#232323", padx=14, pady=12, bd=1, relief="solid")
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_col, text="Add New Photos to Series:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 6))

        browse_bar = tk.Frame(right_col, bg="#232323")
        browse_bar.pack(fill="x", pady=(0, 6))

        btn_browse = tk.Button(browse_bar, text="📁 Browse Photos...", command=self.choose_photos, bg="#2e64b6", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=5, cursor="hand2")
        btn_browse.pack(side="left")

        btn_remove_staged = tk.Button(browse_bar, text="✕ Remove Selected", command=self.remove_selected_staged_photo, bg="#3b3b3b", fg="#ffaaaa", font=("Segoe UI", 9), relief="flat", padx=8, pady=5, cursor="hand2")
        btn_remove_staged.pack(side="left", padx=6)

        btn_clear_staged = tk.Button(browse_bar, text="Clear All", command=self.clear_photos, bg="#333333", fg="#cccccc", font=("Segoe UI", 9), relief="flat", padx=8, pady=5, cursor="hand2")
        btn_clear_staged.pack(side="left")

        # Staged files list
        staged_frame = tk.Frame(right_col, bg="#232323", height=130)
        staged_frame.pack(fill="x", pady=(0, 10))
        staged_frame.pack_propagate(False)

        staged_scroll = tk.Scrollbar(staged_frame)
        staged_scroll.pack(side="right", fill="y")

        self.staged_listbox = tk.Listbox(staged_frame, bg="#141414", fg="#00e676", selectbackground="#383838", font=("Segoe UI", 9), yscrollcommand=staged_scroll.set, bd=0, highlightthickness=1, highlightbackground="#333333")
        self.staged_listbox.pack(side="left", fill="both", expand=True)
        staged_scroll.config(command=self.staged_listbox.yview)

        # Series Description Editor
        desc_header = tk.Frame(right_col, bg="#232323")
        desc_header.pack(fill="x", pady=(6, 4))

        tk.Label(desc_header, text="Series Story / Description:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#232323").pack(side="left")

        btn_save_desc = tk.Button(desc_header, text="💾 Save Story", command=self.save_current_description, bg="#2d6a4f", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        btn_save_desc.pack(side="right")

        self.txt_desc = tk.Text(right_col, height=7, bg="#141414", fg="#ffffff", font=("Segoe UI", 10), insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#333333", wrap="word")
        self.txt_desc.pack(fill="both", expand=True, pady=(0, 4))

    # =========================================================================
    # TAB 2: HOMEPAGE GRID ORDER
    # =========================================================================
    def setup_grid_tab(self):
        container = tk.Frame(self.tab_grid, bg="#1e1e1e", padx=16, pady=16)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg="#272727", padx=14, pady=10, bd=1, relief="solid")
        header.pack(fill="x", pady=(0, 14))

        tk.Label(header, text="Homepage Grid Order & Card Placement:", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#272727").pack(anchor="w")
        tk.Label(header, text="Arrange how cards appear on the homepage grid (displayed in 3 columns from top to bottom, left to right).", font=("Segoe UI", 9), fg="#aaaaaa", bg="#272727").pack(anchor="w", pady=(2, 0))

        body = tk.Frame(container, bg="#1e1e1e")
        body.pack(fill="both", expand=True)

        # Left: Listbox of grid items
        list_frame = tk.Frame(body, bg="#232323", padx=14, pady=12, bd=1, relief="solid")
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side="right", fill="y")

        self.grid_order_listbox = tk.Listbox(list_frame, bg="#141414", fg="#ffffff", selectbackground="#4f8ef7", font=("Segoe UI", 11), yscrollcommand=scroll.set, bd=0, highlightthickness=1, highlightbackground="#333333")
        self.grid_order_listbox.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.grid_order_listbox.yview)

        # Right: Controls & Info
        ctrl_frame = tk.Frame(body, bg="#232323", padx=14, pady=12, bd=1, relief="solid", width=250)
        ctrl_frame.pack(side="right", fill="y")
        ctrl_frame.pack_propagate(False)

        tk.Label(ctrl_frame, text="Reorder Placement:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 10))

        btn_grid_top = tk.Button(ctrl_frame, text="🔝 Move to Top", command=lambda: self.reorder_grid_item(-999), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=10, pady=6, cursor="hand2")
        btn_grid_top.pack(fill="x", pady=3)

        btn_grid_up = tk.Button(ctrl_frame, text="⬆ Move Up", command=lambda: self.reorder_grid_item(-1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=10, pady=6, cursor="hand2")
        btn_grid_up.pack(fill="x", pady=3)

        btn_grid_down = tk.Button(ctrl_frame, text="⬇ Move Down", command=lambda: self.reorder_grid_item(1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=10, pady=6, cursor="hand2")
        btn_grid_down.pack(fill="x", pady=3)

        btn_grid_bottom = tk.Button(ctrl_frame, text="🔻 Move to Bottom", command=lambda: self.reorder_grid_item(999), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=10, pady=6, cursor="hand2")
        btn_grid_bottom.pack(fill="x", pady=3)

        tk.Frame(ctrl_frame, bg="#333333", height=1).pack(fill="x", pady=12)

        btn_save_grid = tk.Button(ctrl_frame, text="💾 Save Order", command=self.save_grid_order, bg="#2d6a4f", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=8, cursor="hand2")
        btn_save_grid.pack(fill="x", pady=4)

        btn_reset_grid = tk.Button(ctrl_frame, text="Reset to Alphabetical", command=self.reset_grid_order, bg="#2a2a2a", fg="#cccccc", font=("Segoe UI", 8), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_reset_grid.pack(fill="x", pady=4)

    # =========================================================================
    # TAB 3: VIDEOS MANAGER
    # =========================================================================
    def setup_videos_tab(self):
        container = tk.Frame(self.tab_videos, bg="#1e1e1e", padx=16, pady=16)
        container.pack(fill="both", expand=True)

        # Section Selector Bar
        top_bar = tk.Frame(container, bg="#272727", padx=12, pady=10, bd=1, relief="solid")
        top_bar.pack(fill="x", pady=(0, 14))

        tk.Label(top_bar, text="Video Section:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#272727").pack(side="left", padx=(0, 10))

        self.video_sec_var = tk.StringVar()
        self.video_sec_combo = ttk.Combobox(top_bar, textvariable=self.video_sec_var, state="readonly", font=("Segoe UI", 11), width=24)
        self.video_sec_combo.pack(side="left", ipady=3)
        self.video_sec_combo.bind("<<ComboboxSelected>>", self.on_video_section_selected)

        btn_new_sec = tk.Button(top_bar, text="+ Add Section", command=self.prompt_new_video_section, bg="#3b3b3b", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_new_sec.pack(side="left", padx=8)

        btn_del_sec = tk.Button(top_bar, text="🗑️ Delete Section", command=self.prompt_delete_video_section, bg="#552222", fg="#ffcccc", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_del_sec.pack(side="right")

        # Two-column layout for videos
        v_cols = tk.Frame(container, bg="#1e1e1e")
        v_cols.pack(fill="both", expand=True)

        # Left Column: List of videos
        left_v = tk.Frame(v_cols, bg="#232323", padx=14, pady=12, bd=1, relief="solid")
        left_v.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left_v, text="Videos in this Section:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 8))

        v_list_frame = tk.Frame(left_v, bg="#232323")
        v_list_frame.pack(fill="both", expand=True)

        v_scroll = tk.Scrollbar(v_list_frame)
        v_scroll.pack(side="right", fill="y")

        self.videos_listbox = tk.Listbox(v_list_frame, bg="#141414", fg="#ffffff", selectbackground="#4f8ef7", font=("Segoe UI", 10), yscrollcommand=v_scroll.set, bd=0, highlightthickness=1, highlightbackground="#333333")
        self.videos_listbox.pack(side="left", fill="both", expand=True)
        v_scroll.config(command=self.videos_listbox.yview)
        self.videos_listbox.bind("<<ListboxSelect>>", self.on_video_item_select)

        # Video list buttons
        v_btn_row = tk.Frame(left_v, bg="#232323")
        v_btn_row.pack(fill="x", pady=(10, 0))

        btn_v_up = tk.Button(v_btn_row, text="⬆ Move Up", command=lambda: self.reorder_video(-1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_v_up.pack(side="left", padx=(0, 4))

        btn_v_down = tk.Button(v_btn_row, text="⬇ Move Down", command=lambda: self.reorder_video(1), bg="#383838", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_v_down.pack(side="left", padx=4)

        btn_del_v = tk.Button(v_btn_row, text="🗑️ Delete Video", command=self.delete_selected_video, bg="#7a1f1d", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=4, cursor="hand2")
        btn_del_v.pack(side="right")

        # Right Column: Video Details & Add Video Form
        right_v = tk.Frame(v_cols, bg="#232323", padx=14, pady=12, bd=1, relief="solid")
        right_v.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_v, text="Video Details / Add Video:", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 10))

        tk.Label(right_v, text="YouTube URL or Video ID:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_v_url = tk.Entry(right_v, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_v_url.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(right_v, text="Video Title:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_v_title = tk.Entry(right_v, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_v_title.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(right_v, text="Subtitle (e.g. 'Featurette • E1' or 'Documentary'):", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_v_subtitle = tk.Entry(right_v, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_v_subtitle.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(right_v, text="Description:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.txt_v_desc = tk.Text(right_v, height=4, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333", wrap="word")
        self.txt_v_desc.pack(fill="both", expand=True, pady=(2, 12))

        v_actions_bar = tk.Frame(right_v, bg="#232323")
        v_actions_bar.pack(fill="x")

        btn_add_v = tk.Button(v_actions_bar, text="+ Save as New Video", command=self.save_new_video, bg="#2e64b6", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=5, cursor="hand2")
        btn_add_v.pack(side="left")

        btn_update_v = tk.Button(v_actions_bar, text="✏️ Update Selected", command=self.update_existing_video, bg="#3b3b3b", fg="#ffffff", font=("Segoe UI", 9), relief="flat", padx=10, pady=5, cursor="hand2")
        btn_update_v.pack(side="left", padx=8)

        btn_clear_v = tk.Button(v_actions_bar, text="Clear Form", command=self.clear_video_form, bg="#2a2a2a", fg="#cccccc", font=("Segoe UI", 9), relief="flat", padx=8, pady=5, cursor="hand2")
        btn_clear_v.pack(side="right")

    # =========================================================================
    # TAB 4: ABOUT & CONTACT
    # =========================================================================
    def setup_bio_tab(self):
        container = tk.Frame(self.tab_bio, bg="#1e1e1e", padx=16, pady=16)
        container.pack(fill="both", expand=True)

        cols = tk.Frame(container, bg="#1e1e1e")
        cols.pack(fill="both", expand=True)

        # Left Column: About Bio
        left_b = tk.Frame(cols, bg="#232323", padx=14, pady=14, bd=1, relief="solid")
        left_b.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left_b, text="About Artist Biography:", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 4))
        tk.Label(left_b, text="This text appears on the About page. Blank lines create new paragraphs.", font=("Segoe UI", 9), fg="#888888", bg="#232323").pack(anchor="w", pady=(0, 8))

        self.txt_about = tk.Text(left_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333", wrap="word")
        self.txt_about.pack(fill="both", expand=True, pady=(0, 10))

        btn_save_about = tk.Button(left_b, text="💾 Save About Bio", command=self.save_about_text, bg="#2d6a4f", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6, cursor="hand2")
        btn_save_about.pack(anchor="w")

        # Right Column: Contact Info
        right_b = tk.Frame(cols, bg="#232323", padx=14, pady=14, bd=1, relief="solid")
        right_b.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_b, text="Contact Details & Social Links:", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#232323").pack(anchor="w", pady=(0, 4))
        tk.Label(right_b, text="These appear in the grid on the Contact page.", font=("Segoe UI", 9), fg="#888888", bg="#232323").pack(anchor="w", pady=(0, 12))

        tk.Label(right_b, text="Phone Number:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_phone = tk.Entry(right_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_phone.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(right_b, text="Email Address:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_email = tk.Entry(right_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_email.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(right_b, text="Location:", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_location = tk.Entry(right_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_location.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(right_b, text="Instagram URL (e.g. https://www.instagram.com/chegu__/):", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_instagram = tk.Entry(right_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_instagram.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(right_b, text="LinkedIn URL (e.g. https://www.linkedin.com/in/vigneshrathinam):", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#232323").pack(anchor="w")
        self.entry_linkedin = tk.Entry(right_b, bg="#141414", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#333333")
        self.entry_linkedin.pack(fill="x", pady=(2, 14), ipady=3)

        btn_save_contact = tk.Button(right_b, text="💾 Save Contact Information", command=self.save_contact_info, bg="#2d6a4f", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6, cursor="hand2")
        btn_save_contact.pack(anchor="w")

    # =========================================================================
    # DATA LOADING & REFRESH
    # =========================================================================
    def refresh_all_data(self):
        self.refresh_categories()
        self.load_grid_order_data()
        self.load_videos_data()
        self.load_bio_data()

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
        if not cat: return

        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)

        # 1. Load description
        desc_path = os.path.join(cat_dir, "description.txt")
        self.txt_desc.delete("1.0", tk.END)
        if os.path.exists(desc_path):
            try:
                with open(desc_path, 'r', encoding='utf-8') as f:
                    self.txt_desc.insert("1.0", f.read())
            except Exception:
                pass

        # 2. Load existing photos in folder
        self.refresh_existing_photos_list()

    def get_current_series_cover(self, cat):
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        thumb_path = os.path.join(cat_dir, "thumbnail.txt")
        if os.path.exists(thumb_path):
            try:
                with open(thumb_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
        return None

    def refresh_existing_photos_list(self):
        cat = self.cat_var.get()
        self.existing_listbox.delete(0, tk.END)
        self.lbl_preview_img.config(image="", text="Select photo to preview")
        self.current_preview_photo = None

        if not cat: return
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        if not os.path.exists(cat_dir): return

        exts = ('.jpg', '.jpeg', '.png', '.webp')
        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(exts) and not f.startswith('.')])
        cover_fname = self.get_current_series_cover(cat)

        for idx, f in enumerate(files, 1):
            is_cover = False
            if cover_fname and (f == cover_fname or os.path.splitext(f)[0] == os.path.splitext(cover_fname)[0]):
                is_cover = True
            elif not cover_fname and idx == 1:
                is_cover = True

            cover_tag = " ⭐ [COVER]" if is_cover else ""
            self.existing_listbox.insert(tk.END, f"{idx:02d}. {f}{cover_tag}")

        self.lbl_existing_photos.config(text=f"Photos in Series ({len(files)})")

    def on_existing_photo_select(self, event=None):
        sel = self.existing_listbox.curselection()
        if not sel: return
        idx = sel[0]
        cat = self.cat_var.get()
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        exts = ('.jpg', '.jpeg', '.png', '.webp')
        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(exts) and not f.startswith('.')])

        if idx < len(files):
            fname = files[idx]
            fpath = os.path.join(cat_dir, fname)
            try:
                with Image.open(fpath) as img:
                    img = correct_orientation(img)
                    img.thumbnail((220, 115))
                    self.current_preview_photo = ImageTk.PhotoImage(img)
                    self.lbl_preview_img.config(image=self.current_preview_photo, text="")
            except Exception:
                self.lbl_preview_img.config(image="", text="[Preview not available]")

    def set_selected_photo_as_thumbnail(self):
        sel = self.existing_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select Photo", "Please select a photo from the list to set as the cover.")
            return

        idx = sel[0]
        cat = self.cat_var.get()
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        exts = ('.jpg', '.jpeg', '.png', '.webp')
        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(exts) and not f.startswith('.')])
        if idx >= len(files): return

        chosen_file = files[idx]
        with open(os.path.join(cat_dir, "thumbnail.txt"), "w", encoding="utf-8") as f:
            f.write(chosen_file)

        self.refresh_existing_photos_list()
        self.existing_listbox.selection_set(idx)
        self.status_var.set(f"⭐ Set '{chosen_file}' as series cover. Click 'Save & Publish' to update live.")
        messagebox.showinfo("Cover Set", f"'{chosen_file}' is now set as the homepage cover for '{cat}'!")

    def reorder_existing_photo(self, delta):
        sel = self.existing_listbox.curselection()
        if not sel: return
        idx = sel[0]
        cat = self.cat_var.get()
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        exts = ('.jpg', '.jpeg', '.png', '.webp')
        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(exts) and not f.startswith('.')])

        target_idx = idx + delta
        if target_idx < 0 or target_idx >= len(files):
            return

        files[idx], files[target_idx] = files[target_idx], files[idx]

        for i, old_name in enumerate(files, 1):
            base_clean = re.sub(r'^\d+_', '', old_name)
            new_name = f"{i:02d}_{base_clean}"
            old_path = os.path.join(cat_dir, old_name)
            new_path = os.path.join(cat_dir, new_name)
            if old_path != new_path:
                temp_path = os.path.join(cat_dir, f"tmp_{i}_{base_clean}")
                os.rename(old_path, temp_path)
                os.rename(temp_path, new_path)

        self.refresh_existing_photos_list()
        self.existing_listbox.selection_set(target_idx)
        self.existing_listbox.see(target_idx)
        self.on_existing_photo_select()
        self.status_var.set(f"Reordered photo. Click 'Save & Publish Live' (or 'Rebuild') to sync.")

    def delete_selected_existing_photo(self):
        sel = self.existing_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select Photo", "Please select a photo from the list to delete.")
            return

        idx = sel[0]
        cat = self.cat_var.get()
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        exts = ('.jpg', '.jpeg', '.png', '.webp')
        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(exts) and not f.startswith('.')])
        if idx >= len(files): return

        target_file = files[idx]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{target_file}' from '{cat}'?\nThis cannot be undone."):
            os.remove(os.path.join(cat_dir, target_file))
            self.refresh_existing_photos_list()
            self.status_var.set(f"Deleted '{target_file}'. Click 'Save & Publish Live' to update.")

    # =========================================================================
    # ADDING NEW PHOTOS (STAGING)
    # =========================================================================
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
                    self.staged_listbox.insert(tk.END, os.path.basename(f))
            self.status_var.set(f"{len(self.selected_files)} photos staged. Click 'Save & Publish Live' when ready.")

    def remove_selected_staged_photo(self):
        sel = self.staged_listbox.curselection()
        if not sel: return
        idx = sel[0]
        self.staged_listbox.delete(idx)
        if idx < len(self.selected_files):
            self.selected_files.pop(idx)
        self.status_var.set(f"{len(self.selected_files)} photos staged.")

    def clear_photos(self):
        self.selected_files = []
        self.staged_listbox.delete(0, tk.END)
        self.status_var.set("Staged photos cleared.")

    def save_current_description(self):
        cat = self.cat_var.get()
        if not cat: return
        cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
        os.makedirs(cat_dir, exist_ok=True)
        text = self.txt_desc.get("1.0", tk.END).strip()
        with open(os.path.join(cat_dir, "description.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        self.status_var.set(f"Saved story for '{cat}'.")
        messagebox.showinfo("Saved", f"Story text saved for series '{cat}'.")

    # =========================================================================
    # SERIES CREATION / RENAME / DELETE
    # =========================================================================
    def prompt_new_category(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Series")
        dialog.geometry("400x150")
        dialog.configure(bg="#222222")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Enter New Series Name:", font=("Segoe UI", 11, "bold"), fg="#fff", bg="#222222").pack(pady=(18, 8))
        entry = tk.Entry(dialog, font=("Segoe UI", 11), width=28, bg="#141414", fg="#ffffff", insertbackground="white")
        entry.pack(pady=4)
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

        btn_save = tk.Button(dialog, text="Create Series", command=save, bg="#2e64b6", fg="#fff", font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=4)
        btn_save.pack(pady=10)

    def prompt_rename_category(self):
        old_name = self.cat_var.get()
        if not old_name: return

        dialog = tk.Toplevel(self)
        dialog.title("Rename Series")
        dialog.geometry("400x150")
        dialog.configure(bg="#222222")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Rename '{old_name}' to:", font=("Segoe UI", 11, "bold"), fg="#fff", bg="#222222").pack(pady=(18, 8))
        entry = tk.Entry(dialog, font=("Segoe UI", 11), width=28, bg="#141414", fg="#ffffff", insertbackground="white")
        entry.insert(0, old_name)
        entry.pack(pady=4)
        entry.focus_set()

        def save():
            new_name = entry.get().strip()
            if new_name and new_name != old_name:
                old_dir = os.path.join(IMAGES_WEB_DIR, old_name)
                new_dir = os.path.join(IMAGES_WEB_DIR, new_name)
                if os.path.exists(new_dir):
                    messagebox.showerror("Error", f"Series '{new_name}' already exists.", parent=dialog)
                    return
                os.rename(old_dir, new_dir)
                self.refresh_categories()
                self.cat_var.set(new_name)
                self.on_category_selected()
                dialog.destroy()
            else:
                dialog.destroy()

        btn_save = tk.Button(dialog, text="Rename", command=save, bg="#2e64b6", fg="#fff", font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=4)
        btn_save.pack(pady=10)

    def prompt_delete_category(self):
        cat = self.cat_var.get()
        if not cat: return
        if messagebox.askyesno("Confirm Delete Series", f"Are you sure you want to delete the series '{cat}' and all its photos?\nThis cannot be undone."):
            cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
            shutil.rmtree(cat_dir)
            self.refresh_categories()
            messagebox.showinfo("Deleted", f"Series '{cat}' deleted. Click 'Save & Publish Live' to sync.")

    # =========================================================================
    # TAB 2 LOGIC: HOMEPAGE GRID ORDER
    # =========================================================================
    def load_grid_order_data(self):
        order_path = os.path.join(CONTENT_DIR, "series_order.json")
        raw_cats = []
        if os.path.exists(IMAGES_WEB_DIR):
            for d in sorted(os.listdir(IMAGES_WEB_DIR)):
                if os.path.isdir(os.path.join(IMAGES_WEB_DIR, d)) and not d.startswith('.') and d.lower() != 'thumbnail':
                    raw_cats.append(d)

        static_cards = ["Video", "About", "Contact"]
        saved_order = []
        if os.path.exists(order_path):
            try:
                with open(order_path, 'r', encoding='utf-8') as f:
                    saved_order = json.load(f)
            except Exception:
                saved_order = []

        # Build comprehensive list
        all_items = []
        for item in saved_order:
            if item in raw_cats or item in static_cards:
                if item not in all_items:
                    all_items.append(item)

        for cat in raw_cats:
            if cat not in all_items:
                all_items.append(cat)

        for card in static_cards:
            if card not in all_items:
                all_items.append(card)

        self.grid_order = all_items
        self.refresh_grid_listbox()

    def refresh_grid_listbox(self):
        self.grid_order_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.grid_order, 1):
            tag = "  [Static Page]" if item in ("Video", "About", "Contact") else "  [Photo Series]"
            self.grid_order_listbox.insert(tk.END, f"{idx:02d}. {item}{tag}")

    def reorder_grid_item(self, delta):
        sel = self.grid_order_listbox.curselection()
        if not sel: return
        idx = sel[0]
        if delta == -999:
            target_idx = 0
        elif delta == 999:
            target_idx = len(self.grid_order) - 1
        else:
            target_idx = idx + delta

        if target_idx < 0: target_idx = 0
        if target_idx >= len(self.grid_order): target_idx = len(self.grid_order) - 1

        if target_idx != idx:
            item = self.grid_order.pop(idx)
            self.grid_order.insert(target_idx, item)
            self.refresh_grid_listbox()
            self.grid_order_listbox.selection_set(target_idx)
            self.grid_order_listbox.see(target_idx)
            self.status_var.set(f"Moved '{item}' to slot {target_idx + 1}. Click '💾 Save Order' or 'Save & Publish Live'.")

    def save_grid_order(self):
        order_path = os.path.join(CONTENT_DIR, "series_order.json")
        os.makedirs(CONTENT_DIR, exist_ok=True)
        with open(order_path, 'w', encoding='utf-8') as f:
            json.dump(self.grid_order, f, indent=2, ensure_ascii=False)
        self.status_var.set("Saved homepage grid order.")
        messagebox.showinfo("Saved", "Homepage grid order saved successfully!")

    def reset_grid_order(self):
        if messagebox.askyesno("Reset Order", "Reset homepage layout to alphabetical order with Video, About, Contact at the end?"):
            order_path = os.path.join(CONTENT_DIR, "series_order.json")
            if os.path.exists(order_path):
                os.remove(order_path)
            self.load_grid_order_data()
            self.save_grid_order()

    # =========================================================================
    # TAB 3 LOGIC: VIDEOS JSON
    # =========================================================================
    def load_videos_data(self):
        v_file = os.path.join(CONTENT_DIR, "videos.json")
        if os.path.exists(v_file):
            try:
                with open(v_file, 'r', encoding='utf-8') as f:
                    self.videos_data = json.load(f)
            except Exception:
                self.videos_data = []
        else:
            self.videos_data = []

        sections = [s.get("section_title", "Untitled") for s in self.videos_data if isinstance(s, dict)]
        self.video_sec_combo['values'] = sections
        if sections:
            if not self.video_sec_var.get() or self.video_sec_var.get() not in sections:
                self.video_sec_combo.current(0)
            self.on_video_section_selected()

    def save_videos_json(self):
        v_file = os.path.join(CONTENT_DIR, "videos.json")
        os.makedirs(CONTENT_DIR, exist_ok=True)
        with open(v_file, 'w', encoding='utf-8') as f:
            json.dump(self.videos_data, f, indent=2, ensure_ascii=False)

    def get_current_video_section(self):
        sec_name = self.video_sec_var.get()
        for s in self.videos_data:
            if s.get("section_title") == sec_name:
                return s
        return None

    def on_video_section_selected(self, event=None):
        sec = self.get_current_video_section()
        self.videos_listbox.delete(0, tk.END)
        self.clear_video_form()
        if not sec: return

        vids = sec.get("videos", [])
        for idx, v in enumerate(vids, 1):
            t = v.get("title", "Untitled")
            sub = v.get("subtitle", "")
            self.videos_listbox.insert(tk.END, f"{idx:02d}. {t} ({sub})")

    def on_video_item_select(self, event=None):
        sel = self.videos_listbox.curselection()
        if not sel: return
        sec = self.get_current_video_section()
        if not sec: return
        vids = sec.get("videos", [])
        idx = sel[0]
        if idx < len(vids):
            v = vids[idx]
            self.entry_v_url.delete(0, tk.END)
            self.entry_v_url.insert(0, v.get("id", ""))
            self.entry_v_title.delete(0, tk.END)
            self.entry_v_title.insert(0, v.get("title", ""))
            self.entry_v_subtitle.delete(0, tk.END)
            self.entry_v_subtitle.insert(0, v.get("subtitle", ""))
            self.txt_v_desc.delete("1.0", tk.END)
            self.txt_v_desc.insert("1.0", v.get("description", ""))

    def clear_video_form(self):
        self.entry_v_url.delete(0, tk.END)
        self.entry_v_title.delete(0, tk.END)
        self.entry_v_subtitle.delete(0, tk.END)
        self.txt_v_desc.delete("1.0", tk.END)

    def save_new_video(self):
        sec = self.get_current_video_section()
        if not sec:
            messagebox.showwarning("Warning", "Please select or create a video section first.")
            return

        raw_url = self.entry_v_url.get().strip()
        vid_id = extract_youtube_id(raw_url)
        title = self.entry_v_title.get().strip()
        subtitle = self.entry_v_subtitle.get().strip()
        desc = self.txt_v_desc.get("1.0", tk.END).strip()

        if not vid_id or not title:
            messagebox.showwarning("Missing Info", "Please enter at least the YouTube link and Video Title.")
            return

        new_vid = {
            "id": vid_id,
            "title": title,
            "subtitle": subtitle,
            "url": f"https://youtu.be/{vid_id}",
            "description": desc
        }
        if "videos" not in sec:
            sec["videos"] = []
        sec["videos"].append(new_vid)
        self.save_videos_json()
        self.on_video_section_selected()
        self.status_var.set(f"Added video '{title}'.")
        messagebox.showinfo("Success", f"Video '{title}' added to section '{sec.get('section_title')}'.")

    def update_existing_video(self):
        sel = self.videos_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select Video", "Please select a video from the list to update.")
            return
        sec = self.get_current_video_section()
        if not sec: return

        idx = sel[0]
        vids = sec.get("videos", [])
        if idx >= len(vids): return

        raw_url = self.entry_v_url.get().strip()
        vid_id = extract_youtube_id(raw_url)
        title = self.entry_v_title.get().strip()
        subtitle = self.entry_v_subtitle.get().strip()
        desc = self.txt_v_desc.get("1.0", tk.END).strip()

        vids[idx] = {
            "id": vid_id,
            "title": title,
            "subtitle": subtitle,
            "url": f"https://youtu.be/{vid_id}",
            "description": desc
        }
        self.save_videos_json()
        self.on_video_section_selected()
        self.status_var.set(f"Updated video '{title}'.")
        messagebox.showinfo("Saved", "Video details updated successfully.")

    def delete_selected_video(self):
        sel = self.videos_listbox.curselection()
        if not sel: return
        sec = self.get_current_video_section()
        if not sec: return
        idx = sel[0]
        vids = sec.get("videos", [])
        if idx < len(vids):
            target = vids[idx]
            if messagebox.askyesno("Confirm Delete", f"Delete video '{target.get('title')}'?"):
                vids.pop(idx)
                self.save_videos_json()
                self.on_video_section_selected()
                self.clear_video_form()
                self.status_var.set("Video deleted.")

    def reorder_video(self, delta):
        sel = self.videos_listbox.curselection()
        if not sel: return
        sec = self.get_current_video_section()
        if not sec: return
        idx = sel[0]
        vids = sec.get("videos", [])
        target_idx = idx + delta
        if 0 <= target_idx < len(vids):
            vids[idx], vids[target_idx] = vids[target_idx], vids[idx]
            self.save_videos_json()
            self.on_video_section_selected()
            self.videos_listbox.selection_set(target_idx)
            self.videos_listbox.see(target_idx)
            self.on_video_item_select()

    def prompt_new_video_section(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Video Section")
        dialog.geometry("400x180")
        dialog.configure(bg="#222222")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Section Title (e.g. 'Politics', 'Documentaries'):", font=("Segoe UI", 9, "bold"), fg="#fff", bg="#222222").pack(pady=(15, 4))
        entry_t = tk.Entry(dialog, font=("Segoe UI", 10), width=32, bg="#141414", fg="#ffffff", insertbackground="white")
        entry_t.pack()

        tk.Label(dialog, text="Short Description / Subtitle:", font=("Segoe UI", 9), fg="#aaa", bg="#222222").pack(pady=(8, 4))
        entry_d = tk.Entry(dialog, font=("Segoe UI", 10), width=32, bg="#141414", fg="#ffffff", insertbackground="white")
        entry_d.pack()

        def save():
            name = entry_t.get().strip()
            desc = entry_d.get().strip()
            if name:
                self.videos_data.append({"section_title": name, "section_desc": desc, "videos": []})
                self.save_videos_json()
                self.load_videos_data()
                self.video_sec_var.set(name)
                self.on_video_section_selected()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Section title cannot be empty.", parent=dialog)

        tk.Button(dialog, text="Create Section", command=save, bg="#2e64b6", fg="#fff", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=4).pack(pady=12)

    def prompt_delete_video_section(self):
        sec = self.get_current_video_section()
        if not sec: return
        name = sec.get("section_title")
        if messagebox.askyesno("Confirm Delete", f"Delete video section '{name}' and all its videos?"):
            self.videos_data = [s for s in self.videos_data if s.get("section_title") != name]
            self.save_videos_json()
            self.load_videos_data()
            self.status_var.set(f"Deleted video section '{name}'.")

    # =========================================================================
    # TAB 4 LOGIC: ABOUT & CONTACT
    # =========================================================================
    def load_bio_data(self):
        about_path = os.path.join(CONTENT_DIR, "about.txt")
        self.txt_about.delete("1.0", tk.END)
        if os.path.exists(about_path):
            with open(about_path, 'r', encoding='utf-8') as f:
                self.txt_about.insert("1.0", f.read())

        contact_path = os.path.join(CONTENT_DIR, "contact.txt")
        if os.path.exists(contact_path):
            with open(contact_path, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if len(lines) >= 1: self.entry_phone.delete(0, tk.END); self.entry_phone.insert(0, lines[0])
            if len(lines) >= 2: self.entry_email.delete(0, tk.END); self.entry_email.insert(0, lines[1])
            if len(lines) >= 3: self.entry_location.delete(0, tk.END); self.entry_location.insert(0, lines[2])
            if len(lines) >= 4: self.entry_linkedin.delete(0, tk.END); self.entry_linkedin.insert(0, lines[3])
            if len(lines) >= 5: self.entry_instagram.delete(0, tk.END); self.entry_instagram.insert(0, lines[4])

    def save_about_text(self):
        about_path = os.path.join(CONTENT_DIR, "about.txt")
        text = self.txt_about.get("1.0", tk.END).strip()
        os.makedirs(CONTENT_DIR, exist_ok=True)
        with open(about_path, 'w', encoding='utf-8') as f:
            f.write(text)
        self.status_var.set("Saved About Bio text.")
        messagebox.showinfo("Saved", "About bio saved successfully.")

    def save_contact_info(self):
        contact_path = os.path.join(CONTENT_DIR, "contact.txt")
        lines = [
            self.entry_phone.get().strip(),
            self.entry_email.get().strip(),
            self.entry_location.get().strip(),
            self.entry_linkedin.get().strip(),
            self.entry_instagram.get().strip()
        ]
        os.makedirs(CONTENT_DIR, exist_ok=True)
        with open(contact_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")
        self.status_var.set("Saved Contact details.")
        messagebox.showinfo("Saved", "Contact information and Instagram profile saved successfully.")

    # =========================================================================
    # REBUILD & PUBLISH PIPELINE
    # =========================================================================
    def preview_site_in_browser(self):
        index_file = os.path.join(WEBSITE_DIR, "index.html")
        if os.path.exists(index_file):
            webbrowser.open(f"file://{index_file}")
        else:
            messagebox.showinfo("Notice", "Please click 'Save & Rebuild Locally' first.")

    def trigger_rebuild_local(self):
        try:
            # Auto-save description if currently open
            cat = self.cat_var.get()
            desc_text = self.txt_desc.get("1.0", tk.END).strip()
            if cat and desc_text:
                cat_dir = os.path.join(IMAGES_WEB_DIR, cat)
                os.makedirs(cat_dir, exist_ok=True)
                with open(os.path.join(cat_dir, "description.txt"), "w", encoding="utf-8") as f:
                    f.write(desc_text)

            self.status_var.set("Rebuilding HTML pages...")
            gen_script = os.path.join(WEBSITE_DIR, "generate_pages.py")
            subprocess.run([sys.executable, gen_script], cwd=WEBSITE_DIR, check=True)
            self.status_var.set("🎉 Site rebuilt locally! Click 'Open Local Preview' to view.")
            messagebox.showinfo("Rebuild Complete", "All HTML pages have been successfully regenerated!")
        except Exception as e:
            messagebox.showerror("Rebuild Error", f"Failed to rebuild HTML: {e}")

    def set_ui_busy(self, busy=True):
        if busy:
            self.btn_publish.config(state="disabled", text="Processing & Publishing...")
        else:
            self.btn_publish.config(state="normal", text="🚀 SAVE & PUBLISH LIVE")

    def start_publish(self):
        cat = self.cat_var.get()
        desc_text = self.txt_desc.get("1.0", tk.END).strip()
        self.set_ui_busy(True)

        thread = threading.Thread(target=self.run_publish_pipeline, args=(cat, desc_text, list(self.selected_files)))
        thread.daemon = True
        thread.start()

    def run_publish_pipeline(self, category, description, files):
        try:
            target_cat_dir = os.path.join(IMAGES_WEB_DIR, category) if category else None
            if target_cat_dir:
                os.makedirs(target_cat_dir, exist_ok=True)

            # 1. Save Category Description if currently entered
            if target_cat_dir and description:
                self.status_var.set(f"Saving story for '{category}'...")
                with open(os.path.join(target_cat_dir, "description.txt"), "w", encoding="utf-8") as f:
                    f.write(description)

            # 2. Optimize newly staged images if any
            total_files = len(files)
            if total_files > 0 and target_cat_dir:
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
            published_online = False
            try:
                subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
                diff_proc = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=PROJECT_ROOT)
                if diff_proc.returncode != 0:
                    summary = f"Added {total_files} photos to '{category}'" if total_files > 0 else "Updated series, order, and content"
                    commit_msg = f"Studio update: {summary}"
                    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
                    push_proc = subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, capture_output=True, text=True)
                    if push_proc.returncode != 0:
                        raise Exception(push_proc.stderr or "git push failed")
                    published_online = True
                else:
                    published_online = True # Clean working tree, already up to date
            except Exception as git_err:
                print("Git error:", git_err)
                published_online = False

            # Complete!
            self.progress_bar['value'] = 0
            self.status_var.set("🎉 Done! Website published.")
            self.after(0, lambda: self.on_publish_success(category, total_files, published_online))

        except Exception as e:
            self.status_var.set("❌ Error occurred during publishing.")
            self.after(0, lambda: messagebox.showerror("Publish Error", f"An error occurred:\n{str(e)}"))
        finally:
            self.after(0, lambda: self.set_ui_busy(False))

    def on_publish_success(self, category, count, published_online):
        self.clear_photos()
        self.refresh_existing_photos_list()
        self.load_grid_order_data()
        if published_online:
            msg = f"All changes saved and published live to GitHub!\n\nNetlify is updating chegu.netlify.app in the background (~1 minute)."
        else:
            msg = f"Site updated and rebuilt locally.\n\nTip: You can push to GitHub when ready via GitHub Desktop."
        messagebox.showinfo("Success! 🎉", msg)

if __name__ == "__main__":
    app = CheGuStudioApp()
    app.mainloop()
