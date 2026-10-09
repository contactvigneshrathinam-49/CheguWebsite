# CheGu Website — Handover Guide

Everything CheGu needs to manage the website himself, from a single folder.

---

## What's in This Folder

```
CheGu_Website_Project/
│
├── Add_Photos_And_Publish.command  ← Mac: double-click to launch CheGu Studio
├── Add_Photos_And_Publish.bat      ← Windows: double-click to launch CheGu Studio
│
├── Rebuild_Site.command            ← Mac: manual rebuild helper
├── Rebuild_Site.bat                ← Windows: manual rebuild helper
├── Setup_GitHub.bat/.command       ← Helper to connect or switch GitHub repository
│
├── Website/                        ← The website files & web-optimized photos
│   ├── assets/images_web/          ← Web photos organized by series
│   └── content/                    ← Text content (about.txt, contact.txt, videos.json)
│
└── netlify.toml                    ← Netlify deployment config (auto-deploys on push)
```

---

## Recommended Workflow: CheGu Portfolio Studio (No Coding Needed!)

1. **Double-click:**
   - **Windows:** `Add_Photos_And_Publish.bat`
   - **Mac:** `Add_Photos_And_Publish.command`

2. **The CheGu Portfolio Studio window opens:**

   - **📸 Photo Series & Galleries Tab:**
     - Select series from the dropdown (or click `+ New Series`, `Rename`, or `Delete Series`).
     - **Current Photos:** View all photos currently in the gallery with live thumbnail preview.
     - **Reorder Photos:** Select a photo and click `⬆ Move Up` or `⬇ Move Down` to change display order.
     - **Delete Photos:** Select an accidental/unwanted photo and click `🗑️ Delete Photo`.
     - **Add New Photos:** Click `📁 Browse Photos...`. If you select any photo by mistake, click `✕ Remove Selected` to unstage it!
     - **Story / Description:** Write or update the narrative text for the series.

   - **🎬 Video Works Tab:**
     - Add, edit, or reorder YouTube videos visually.
     - Just paste any YouTube URL (e.g. `https://youtu.be/...`) — the app extracts the ID automatically.
     - Add titles, subtitles, and descriptions without touching JSON code.

   - **📝 About & Contact Tab:**
     - Edit your About artist biography.
     - Update phone, email, location, Instagram (`@chegu__`), and LinkedIn links.

3. **Click `🚀 OPTIMIZE & PUBLISH LIVE`:**
   - Compresses new photos to web size (maximum 1600px, 80% JPEG quality).
   - Rebuilds all HTML pages instantly.
   - Pushes all changes to your GitHub (`contactvigneshrathinam-49/CheguWebsite`).
   - Netlify automatically updates `https://chegu.netlify.app` within ~1 minute!

---

## Connecting Your GitHub Repo

Your site is linked to your GitHub account:
`https://github.com/contactvigneshrathinam-49/CheguWebsite.git`

Every time you click **`🚀 OPTIMIZE & PUBLISH LIVE`** or commit in GitHub Desktop, Netlify automatically redeploys the live site.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Add_Photos_And_Publish.bat` opens and closes instantly | Right-click → **Run as administrator** |
| "Python not found" error | Reinstall Python from python.org, check "Add Python to PATH" |
| Photos not appearing after rebuild | Ensure they are standard image files (`.jpg`, `.jpeg`, `.png`) |
| Site not updating after GitHub push | Wait ~1 minute, then check your Netlify dashboard for the latest deploy status |

---

*Updated: October 2026*
