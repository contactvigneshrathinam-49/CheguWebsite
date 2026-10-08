# CheGu Portfolio - Handover Guide

This document explains how to launch the site, manage it, and push updates to the internet.

## 1. System Requirements
To run this control panel, you must install Python on your computer.
- **Mac:** Open Terminal and type `brew install python`
- **Windows:** Go to the Microsoft Store, search "Python", and click Install.

## 2. Launching the Admin Panel
Plug in the memory card or copy this entire folder to your computer.
- **If you use Mac:** Double-click `Start_Admin_Panel.command`.
- **If you use Windows:** Double-click `Start_Admin_Panel.bat`.

*Note: A black terminal window will open. Leave it open! This is the engine running your site.*

## 3. Editing the Site
1. Open your web browser and go to `http://localhost:5000`
2. Click **ADMIN** in the top right.
3. Login using `contactvigneshrathinam@gmail.com` and `sherwin9`.
4. Use the Visual CMS to create projects, write text, and upload **High-Res JPEGs**. *(Note: RAW formats like .NEF are not supported. Please upload JPEGs).*
5. Click **Rebuild Site** when done.

## 4. Pushing to Netlify (The Git Process)
Whenever you finish making changes locally and click "Rebuild Site", you must push those changes to GitHub so Netlify can publish them.

**First-Time Setup for Netlify:**
When you connect this Github repository to Netlify for the first time, you MUST set the **Publish Directory** to `Website`. This tells Netlify where the HTML files live!

**Option A: Using Github Desktop (Easiest for Beginners)**
1. Download & Install [Github Desktop](https://desktop.github.com/) on your Mac/Windows.
2. Log in to your GitHub account.
3. Drag and drop the `CheGu_Website_Project` folder into Github Desktop. (Do NOT drag the entire memory card).
4. Github will automatically ignore the heavy raw photos and only prepare the small web files.
5. In the bottom left, type a summary like "Added new Politics photos".
6. Click **Commit to main**.
7. Click **Push origin** at the top.
*Netlify will automatically detect the push and update the live website within 60 seconds.*

**Option B: Using Terminal/Command Prompt**
1. Open Terminal/Command Prompt and navigate to this folder.
2. Run `git status` to see what changed.
3. Run `git add .` to stage all changes.
4. Run `git commit -m "Updated website content"`
5. Run `git push origin main`

## Technical Notes for Netlify
The live website hosted on Netlify is a static snapshot. The Admin button on the live site is a dummy button that will reject logins as a security measure. You must *always* edit the site locally using `Start_Admin_Panel` and then push the changes via Git.
