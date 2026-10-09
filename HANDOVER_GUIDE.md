# CheGu Website — Handover Guide

Everything Chegu needs to manage the website himself, from a single USB pendrive.

---

## What's in This Folder

```
CheGu_Website_Project/
│
├── Add_Photos_And_Publish.command  ← Mac: double-click to add photos & publish live
├── Add_Photos_And_Publish.bat      ← Windows: double-click to add photos & publish live
│
├── Start_Admin_Panel.command       ← Mac: double-click to run full web admin CMS
├── Start_Admin_Panel.bat           ← Windows: double-click to run full web admin CMS
│
├── Rebuild_Site.command            ← Mac: manual rebuild helper
├── Rebuild_Site.bat                ← Windows: manual rebuild helper
│
├── Website/                        ← The website files & web-optimized photos
│   ├── assets/images_web/          ← Web photos organized by series
│   └── content/                    ← Text content (about.txt, contact.txt, videos.json)
│
└── netlify.toml                    ← Netlify deployment config
```

---

## Easiest Workflow: Add Photos & Publish Live (No Coding!)

1. **Double-click:**
   - **Mac:** `Add_Photos_And_Publish.command`
   - **Windows:** `Add_Photos_And_Publish.bat`

2. **A clean window opens:**
   - **Step 1:** Select the series from the dropdown (or click `+ New Series` to make a new page).
   - **Step 2:** Click **`📁 Browse Photos...`** and select any photos from anywhere on your computer or memory card.
   - **Step 3 (Optional):** Edit or write the story/description for this series in the text box.
   - **Step 4:** Click **`🚀 OPTIMIZE & PUBLISH LIVE`**.

3. **That's it!**
   - The app compresses the photos to web size.
   - Rebuilds all the HTML pages.
   - Automatically publishes the changes to GitHub & Netlify.
   - Site updates live at `https://chegu.netlify.app` in ~1 minute.

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
