# CheGu Website — Handover Guide

Everything Chegu needs to manage the website himself, from a single USB pendrive.

---

## What's in This Folder

```
CheGu_Website_Project/
│
├── Rebuild_Site.bat          ← Windows: double-click this to rebuild the site
├── Rebuild_Site.command      ← Mac: double-click this to rebuild the site
│
├── pORTFOLIO/                ← Put all your RAW / high-res photos here
│   ├── Elephant Human Conflicts/
│   ├── Politics/
│   ├── Kaliman/
│   └── ... (one folder per photo series)
│
├── Website/                  ← The actual website files (don't manually edit these)
│   └── assets/images_web/   ← Web-compressed photos (auto-generated, don't touch)
│
└── netlify.toml              ← Netlify deployment config (don't edit)
```

---

## Day-to-Day Workflow (Adding New Photos)

### Step 1 — Add your photos
Drop new high-res **JPEG** photos into the right folder inside `pORTFOLIO/`.

> **Note:** Only JPEG files work. Do **not** drop RAW files (`.NEF`, `.CR2`, etc.) — they won't process.

If the series doesn't have a folder yet, create one:
```
pORTFOLIO/
  My New Series/        ← new folder
    photo1.jpg
    photo2.jpg
    description.txt     ← optional: write the series description here
```

The `description.txt` format:
```
SERIES TITLE IN CAPS

First paragraph of description text here.

Second paragraph here (optional).
```

### Step 2 — Run the rebuild script
- **Windows:** Double-click **`Rebuild_Site.bat`**
- **Mac:** Double-click **`Rebuild_Site.command`**

The script will:
1. Compress all photos from `pORTFOLIO/` into web-ready sizes
2. Rebuild all HTML pages automatically
3. Tell you when it's done

### Step 3 — Push to GitHub
Open **GitHub Desktop**:
1. You'll see a list of changed files
2. Write a short message in the bottom-left box (e.g. *"Added new Kaliman photos"*)
3. Click **Commit to main**
4. Click **Push origin**

Netlify will auto-deploy within about 1 minute. Site is live at `https://chegu.netlify.app`.

---

## First-Time Setup (Do This Once on a New Computer)

### 1. Install Python
Download from: https://www.python.org/downloads/

> **Important:** During install, check the box that says **"Add Python to PATH"**

### 2. Install GitHub Desktop
Download from: https://desktop.github.com/

### 3. Clone the website repo
1. Open GitHub Desktop
2. Go to **File → Clone Repository**
3. Click the **URL** tab
4. Enter: `https://github.com/ssteevez/CheGu_Website_Project.git`
   *(Or use your own fork — see "Setting Up Your Own GitHub Repo" below)*
5. Choose where to save it (e.g. on a USB pendrive)
6. Click **Clone**

### 4. Connect Netlify
1. Go to [https://app.netlify.com](https://app.netlify.com) and sign in
2. Click **Add new site → Import an existing project**
3. Choose **GitHub**, select your repo
4. Under **Build settings**, set:
   - **Publish directory:** `Website`
   - (Leave Build command blank)
5. Click **Deploy site**

---

## Setting Up Your Own GitHub Repo

If you want the site under your own GitHub account instead:

1. Go to [https://github.com/new](https://github.com/new)
2. Create a new repo (e.g. `chegu-website`) — keep it **Public**
3. In GitHub Desktop: **Repository → Repository Settings → Remote**
4. Change the Remote URL to your new repo's URL (e.g. `https://github.com/YOUR-USERNAME/chegu-website.git`)
5. Click **Save**
6. Push all files: click **Push origin**
7. Reconnect Netlify to your new repo

---

## Editing Text on the Site

### Series descriptions
Edit the `description.txt` file inside the series folder in `pORTFOLIO/`, then run `Rebuild_Site.bat`.

### About page
Edit `pORTFOLIO/about.txt`, then run the rebuild script.

### Contact page
Edit `pORTFOLIO/contact.txt`, then run the rebuild script.

### Videos page
Edit `pORTFOLIO/videos.json`. The format is:
```json
[
  {
    "section_title": "Section Name",
    "section_desc": "Optional description of this section.",
    "videos": [
      {
        "youtube_id": "c_qrtaSdcIE",
        "title": "Video Title",
        "description": "Short description."
      }
    ]
  }
]
```
To get the `youtube_id`: from a YouTube URL like `https://youtu.be/c_qrtaSdcIE`, the ID is the part after `/` — `c_qrtaSdcIE`.

After editing, run the rebuild script.

---

## Adding / Removing a Photo Series

| Action | How |
|--------|-----|
| **Add series** | Create a new folder in `pORTFOLIO/` with photos + optional `description.txt`. Run rebuild. |
| **Remove series** | Delete the folder from `pORTFOLIO/`. Run rebuild. The page is removed automatically. |
| **Rename series** | Rename the folder in `pORTFOLIO/`. Run rebuild. |

---

## Optional: Admin Panel (Advanced)

There's also a web-based Admin Panel that lets you upload photos and edit text through a browser UI. It requires Python to be running in the background.

**To start it (Mac):**
```bash
cd Website
python3 admin_server.py
```
Then open: `http://localhost:5001`  
Login: `contactvigneshrathinam@gmail.com` / `sherwin9`

> This is optional and not needed for the normal workflow above.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Rebuild_Site.bat` opens and closes instantly | Right-click → **Run as administrator**, or open Command Prompt and drag the `.bat` file into it |
| "Python not found" error | Reinstall Python from python.org, check "Add to PATH" |
| Photos not appearing after rebuild | Make sure they are `.jpg` or `.jpeg` files (not `.NEF`, `.png`, etc.) |
| Site not updating after GitHub push | Wait 2 minutes, then check Netlify dashboard for any deploy errors |
| Page shows "404" on Netlify | Check that `netlify.toml` is at the root of the repo and contains `publish = "Website"` |

---

*Last updated: October 2026*
