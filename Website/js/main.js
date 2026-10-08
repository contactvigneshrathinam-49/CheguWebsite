document.addEventListener('DOMContentLoaded', () => {
    // Menu Overlay Functionality
    const menuBtn = document.getElementById('menu-btn');
    const closeMenuBtn = document.getElementById('close-menu');
    const menuOverlay = document.getElementById('menu-overlay');

    if (menuBtn && menuOverlay) {
        menuBtn.addEventListener('click', () => {
            menuOverlay.classList.add('active');
        });
    }

    if (closeMenuBtn && menuOverlay) {
        closeMenuBtn.addEventListener('click', () => {
            menuOverlay.classList.remove('active');
        });
    }

    // Series Page: Hero Image & Thumbnails
    const heroImg = document.getElementById('hero-img');
    const thumbnails = document.querySelectorAll('.thumb');
    const heroPrev = document.getElementById('hero-prev');
    const heroNext = document.getElementById('hero-next');
    let currentIndex = 0;

    const updateHeroImage = (index) => {
        if (!thumbnails.length || !heroImg) return;
        
        // Remove active class from all
        thumbnails.forEach(t => t.classList.remove('active'));
        
        // Set new active
        const newActive = thumbnails[index];
        newActive.classList.add('active');
        
        // Fade effect
        heroImg.style.opacity = 0;
        setTimeout(() => {
            heroImg.src = newActive.src;
            heroImg.style.opacity = 1;
        }, 200);

        // Scroll thumbnail strip to keep active in view
        newActive.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        currentIndex = index;
    };

    if (thumbnails.length > 0) {
        thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('click', () => {
                updateHeroImage(index);
            });
        });

        if (heroPrev) {
            heroPrev.addEventListener('click', () => {
                let newIdx = currentIndex - 1;
                if (newIdx < 0) newIdx = thumbnails.length - 1;
                updateHeroImage(newIdx);
            });
        }

        if (heroNext) {
            heroNext.addEventListener('click', () => {
                let newIdx = currentIndex + 1;
                if (newIdx >= thumbnails.length) newIdx = 0;
                updateHeroImage(newIdx);
            });
        }
    }

    // Lightbox Functionality
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeLightboxBtn = document.getElementById('close-lightbox');

    const openLightbox = (src) => {
        if (!lightbox || !lightboxImg) return;
        lightboxImg.src = src;
        lightbox.classList.add('active');
    };

    const closeLightbox = () => {
        if (!lightbox) return;
        lightbox.classList.remove('active');
        setTimeout(() => {
            if (lightboxImg) lightboxImg.src = '';
        }, 400); 
    };

    // Hero image opens lightbox
    if (heroImg) {
        heroImg.addEventListener('click', () => {
            openLightbox(heroImg.src);
        });
    }

    if (closeLightboxBtn) {
        closeLightboxBtn.addEventListener('click', closeLightbox);
    }

    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target !== lightboxImg && !e.target.classList.contains('lightbox-arrow')) {
                closeLightbox();
            }
        });
    }

    const lbPrev = document.getElementById('lb-prev');
    const lbNext = document.getElementById('lb-next');

    if (lbPrev && heroPrev) {
        lbPrev.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent closing lightbox
            heroPrev.click(); // advance hero image
            lightboxImg.src = heroImg.src; // sync lightbox
        });
    }

    if (lbNext && heroNext) {
        lbNext.addEventListener('click', (e) => {
            e.stopPropagation();
            heroNext.click();
            lightboxImg.src = heroImg.src;
        });
    }

    // Keyboard Navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLightbox();
            if (menuOverlay && menuOverlay.classList.contains('active')) {
                menuOverlay.classList.remove('active');
            }
        }
        
        if (e.key === 'ArrowLeft') {
            if (lightbox && lightbox.classList.contains('active') && lbPrev) {
                lbPrev.click();
            } else if (heroPrev) {
                heroPrev.click();
            }
        }
        
        if (e.key === 'ArrowRight') {
            if (lightbox && lightbox.classList.contains('active') && lbNext) {
                lbNext.click();
            } else if (heroNext) {
                heroNext.click();
            }
        }
    });
    // --- PWA SERVICE WORKER ---
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('sw.js').catch(err => {
                console.log('SW Registration failed: ', err);
            });
        });
    }

    // --- ADMIN PANEL ---
    const adminBtn = document.getElementById('admin-trigger-btn');
    
    if (adminBtn) {
        adminBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showAdminLogin();
        });
    }
    
    function showAdminLogin() {
        let loginModal = document.getElementById('admin-login-modal');
        if (!loginModal) {
            loginModal = document.createElement('div');
            loginModal.id = 'admin-login-modal';
            loginModal.innerHTML = `
                <div class="admin-modal-content">
                    <h2 style="font-family: 'Inter', sans-serif; text-transform: uppercase;">Admin Access</h2>
                    <input type="email" id="admin-user" placeholder="Username" />
                    <input type="password" id="admin-pass" placeholder="Password" />
                    <button id="admin-login-btn">Login</button>
                    <button id="admin-close-btn" class="close-btn">Cancel</button>
                    <p id="admin-error" style="color:red; display:none; margin-top:10px; font-family: 'Inter', sans-serif;">Invalid Credentials or Server Offline.</p>
                </div>
            `;
            document.body.appendChild(loginModal);
            
            const style = document.createElement('style');
            style.innerHTML = `
                #admin-login-modal, #admin-dashboard {
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.9); z-index: 9999;
                    display: flex; justify-content: center; align-items: center;
                    text-transform: none;
                }
                .admin-modal-content {
                    background: #fff; padding: 3rem; width: 400px;
                    display: flex; flex-direction: column; gap: 1rem;
                    font-family: 'Inter', sans-serif;
                    max-height: 90vh; overflow-y: auto;
                }
                .admin-modal-content h2 { margin-bottom: 1rem; font-size: 1.5rem; letter-spacing: -0.02em; color: #000; }
                .admin-modal-content p { font-size: 1rem; line-height: 1.5; color: #333; text-transform: none; }
                .admin-modal-content input, .admin-modal-content select { padding: 0.8rem; border: 1px solid #ccc; font-size: 1rem; font-family: 'Inter', sans-serif; }
                .admin-modal-content button { padding: 1rem; background: #000; color: #fff; cursor: pointer; text-transform: uppercase; border: none; font-weight: bold; letter-spacing: 0.05em; font-family: 'Inter', sans-serif;}
                .admin-modal-content button.close-btn { background: #e0e0e0; color: #000; }
                #admin-dashboard .admin-modal-content { width: 600px; }
            `;
            document.head.appendChild(style);
            
            document.getElementById('admin-close-btn').addEventListener('click', () => {
                loginModal.style.display = 'none';
            });
            
            document.getElementById('admin-login-btn').addEventListener('click', async () => {
                const u = document.getElementById('admin-user').value;
                const p = document.getElementById('admin-pass').value;
                const errorEl = document.getElementById('admin-error');
                
                try {
                    const res = await fetch('/api/admin/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username: u, password: p})
                    });
                    if (res.ok) {
                        const data = await res.json();
                        loginModal.style.display = 'none';
                        showAdminDashboard(data.token);
                    } else {
                        errorEl.innerText = "Invalid Credentials";
                        errorEl.style.display = 'block';
                    }
                } catch (e) {
                    errorEl.innerText = "Cannot connect to Local Admin Server. Are you running the Start_Admin_Panel app?";
                    errorEl.style.display = 'block';
                }
            });
        }
        document.getElementById('admin-error').style.display = 'none';
        document.getElementById('admin-user').value = '';
        document.getElementById('admin-pass').value = '';
        loginModal.style.display = 'flex';
    }
    
    async function showAdminDashboard(token) {
        let dashboard = document.getElementById('admin-dashboard');
        if (dashboard) dashboard.remove();
        
        dashboard = document.createElement('div');
        dashboard.id = 'admin-dashboard';
        
        // Massive UI for CMS
        dashboard.innerHTML = `
            <div class="cms-container">
                <div class="cms-sidebar">
                    <h2>CheGu Admin</h2>
                    <ul class="cms-nav">
                        <li data-view="projects" class="active">Projects / Galleries</li>
                        <li data-view="pages">Static Pages</li>
                        <li data-view="build">Rebuild Site</li>
                        <li data-view="logout" style="color:red; margin-top:2rem;">Log Out</li>
                    </ul>
                </div>
                <div class="cms-main" id="cms-main">
                    <div id="cms-loading" style="font-size:1.5rem;">Loading data from server...</div>
                </div>
            </div>
        `;
        
        const style = document.createElement('style');
        style.innerHTML = `
            #admin-dashboard {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #f7f7f5; z-index: 9999;
                font-family: 'Inter', sans-serif; text-transform: none; color: #000;
            }
            .cms-container { display: flex; width: 100%; height: 100%; }
            .cms-sidebar { 
                width: 280px; background: #fff; border-right: 1px solid #ddd;
                padding: 2rem; display: flex; flex-direction: column; 
            }
            .cms-sidebar h2 { font-size: 1.5rem; letter-spacing:-0.02em; margin-bottom: 2rem; text-transform: uppercase; font-family: 'Inter', sans-serif;}
            .cms-nav { list-style: none; padding: 0; display:flex; flex-direction:column; gap: 1rem; margin:0;}
            .cms-nav li { cursor: pointer; font-size: 1.1rem; color: #666; font-weight: 500; transition:0.2s;}
            .cms-nav li:hover { color: #000; }
            .cms-nav li.active { color: #000; font-weight: 700; }
            .cms-main { flex: 1; padding: 3rem; overflow-y: auto; background: #f7f7f5; }
            
            .cms-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
            .cms-header h1 { font-size: 2.2rem; text-transform: uppercase; letter-spacing: -0.02em; margin:0; font-family: 'Inter', sans-serif;}
            
            .btn { background: #000; color: #fff; border: none; padding: 0.8rem 1.5rem; cursor: pointer; text-transform: uppercase; font-weight: bold; font-family: 'Inter', sans-serif; letter-spacing: 0.05em; font-size:0.8rem;}
            .btn-outline { background: transparent; border: 1px solid #000; color: #000; }
            .btn-danger { background: #d93025; color: #fff; }
            
            .project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
            .project-card { background: #fff; border: 1px solid #ddd; cursor: pointer; transition: 0.2s; display:flex; flex-direction:column;}
            .project-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .project-card img { width: 100%; height: 200px; object-fit: cover; border-bottom: 1px solid #ddd; }
            .project-card .info { padding: 1.5rem; }
            .project-card .info h3 { margin: 0; font-size: 1.2rem; text-transform: uppercase; font-family: 'Inter', sans-serif;}
            
            .editor-section { background: #fff; padding: 2rem; border: 1px solid #ddd; margin-bottom: 2rem; }
            .editor-section h3 { margin-top:0; margin-bottom: 1rem; text-transform: uppercase; font-size: 1.1rem; font-family: 'Inter', sans-serif;}
            textarea.cms-textarea { width: 100%; height: 250px; padding: 1rem; border: 1px solid #ccc; font-family: 'Inter', sans-serif; font-size: 1rem; resize: vertical; line-height:1.5;}
            
            .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
            .image-thumb-wrap { position: relative; border: 1px solid #eee; background:#fafafa;}
            .image-thumb-wrap img { width: 100%; height: 150px; object-fit: cover; display: block; }
            .delete-img-btn { position: absolute; top: 5px; right: 5px; background: rgba(217,48,37,0.9); color: white; border: none; width: 30px; height: 30px; border-radius:50%; cursor: pointer; font-weight: bold; }
            
            .upload-zone { border: 2px dashed #ccc; padding: 4rem; text-align: center; cursor: pointer; background: #fafafa; font-size:1.2rem; color:#666;}
            .upload-zone:hover { border-color: #000; color:#000; background:#f0f0f0;}
        `;
        document.head.appendChild(style);
        document.body.appendChild(dashboard);
        
        let cmsData = { categories: [], static_pages: {} };
        
        // Fetch Data
        async function loadData() {
            try {
                const res = await fetch('/api/admin/data', { headers: {'Authorization': 'Bearer ' + token} });
                cmsData = await res.json();
                renderProjects();
            } catch (e) {
                document.getElementById('cms-main').innerHTML = `<h2 style="color:red">Failed to load data. Is the local Python server running?</h2>`;
            }
        }
        
        // Router
        document.querySelectorAll('.cms-nav li').forEach(li => {
            li.addEventListener('click', (e) => {
                document.querySelectorAll('.cms-nav li').forEach(n => n.classList.remove('active'));
                e.target.classList.add('active');
                const view = e.target.getAttribute('data-view');
                if (view === 'projects') renderProjects();
                if (view === 'pages') renderStaticPages();
                if (view === 'build') renderBuild();
                if (view === 'logout') dashboard.remove();
            });
        });
        
        function renderProjects() {
            let html = `
                <div class="cms-header">
                    <h1>Projects & Galleries</h1>
                    <button class="btn" id="add-project-btn">+ New Project</button>
                </div>
                <div class="project-grid">
            `;
            
            cmsData.categories.forEach((cat, index) => {
                const cover = cat.images.length > 0 ? encodeURI(cat.images[0]) : '';
                html += `
                    <div class="project-card" data-index="${index}">
                        <img src="${cover}" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\'><rect width=\\'100%\\' height=\\'100%\\' fill=\\'%23eee\\'/></svg>'">
                        <div class="info">
                            <h3>${cat.name}</h3>
                            <p style="font-size:0.9rem; color:#666; margin-top:0.5rem;">${cat.images.length} images uploaded</p>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
            document.getElementById('cms-main').innerHTML = html;
            
            document.querySelectorAll('.project-card').forEach(card => {
                card.addEventListener('click', () => {
                    renderProjectEditor(cmsData.categories[card.getAttribute('data-index')]);
                });
            });
            
            document.getElementById('add-project-btn').addEventListener('click', () => {
                const name = prompt("Enter new project name:");
                if (name) {
                    cmsData.categories.push({ name: name, description: "", images: [] });
                    renderProjectEditor(cmsData.categories[cmsData.categories.length - 1]);
                }
            });
        }
        
        function renderProjectEditor(cat) {
            let html = `
                <div class="cms-header">
                    <div style="display:flex; align-items:center; gap:2rem;">
                        <button class="btn btn-outline" id="back-btn">&larr; Back</button>
                        <h1>Editing: ${cat.name}</h1>
                    </div>
                    <button class="btn btn-danger" id="delete-cat-btn">Delete Project</button>
                </div>
                
                <div class="editor-section">
                    <h3>Project Description (Metadata)</h3>
                    <textarea class="cms-textarea" id="cat-desc">${cat.description}</textarea>
                    <button class="btn" id="save-desc-btn" style="margin-top:1rem;">Save Text</button>
                </div>
                
                <div class="editor-section">
                    <h3>Upload New Photos</h3>
                    <div class="upload-zone" id="upload-zone">
                        <strong>Click to select High-Res JPEGs for ${cat.name}</strong>
                        <p style="font-size:0.9rem; margin-top:0.5rem;">You can select multiple files at once.</p>
                        <input type="file" id="file-input" multiple accept="image/jpeg, image/jpg, image/png" style="display:none;" />
                    </div>
                    <p id="upload-status" style="margin-top:1rem; font-weight:bold; font-size:1.1rem;"></p>
                </div>
                
                <div class="editor-section">
                    <h3>Current Photos in Gallery (${cat.images.length})</h3>
                    <div class="image-grid">
            `;
            
            cat.images.forEach(img => {
                html += `
                    <div class="image-thumb-wrap">
                        <img src="${encodeURI(img)}?t=${Date.now()}">
                        <button class="delete-img-btn" data-img="${img}">X</button>
                    </div>
                `;
            });
            
            html += `</div></div>`;
            document.getElementById('cms-main').innerHTML = html;
            
            document.getElementById('back-btn').addEventListener('click', renderProjects);
            
            document.getElementById('save-desc-btn').addEventListener('click', async () => {
                const text = document.getElementById('cat-desc').value;
                document.getElementById('save-desc-btn').innerText = "Saving...";
                await fetch('/api/admin/update_text', {
                    method: 'POST',
                    headers: {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
                    body: JSON.stringify({target: cat.name, content: text})
                });
                cat.description = text;
                document.getElementById('save-desc-btn').innerText = "Saved!";
                setTimeout(() => document.getElementById('save-desc-btn').innerText = "Save Text", 2000);
            });
            
            document.getElementById('delete-cat-btn').addEventListener('click', async () => {
                if (confirm("Are you sure you want to delete this entire project and all its photos?")) {
                    await fetch('/api/admin/delete_category', {
                        method: 'POST',
                        headers: {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
                        body: JSON.stringify({category: cat.name})
                    });
                    loadData();
                }
            });
            
            document.querySelectorAll('.delete-img-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const imgUrl = e.target.getAttribute('data-img');
                    if(confirm("Delete this image?")) {
                        await fetch('/api/admin/delete_image', {
                            method: 'POST',
                            headers: {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
                            body: JSON.stringify({image: imgUrl})
                        });
                        e.target.parentElement.remove();
                        cat.images = cat.images.filter(i => i !== imgUrl);
                    }
                });
            });
            
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            uploadZone.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', async (e) => {
                const files = e.target.files;
                if (!files.length) return;
                const status = document.getElementById('upload-status');
                
                status.style.color = "blue";
                
                for(let i=0; i<files.length; i++) {
                    status.innerText = `Uploading image ${i+1} of ${files.length}...`;
                    const formData = new FormData();
                    formData.append('file', files[i]);
                    formData.append('category', cat.name);
                    await fetch('/api/admin/upload', {
                        method: 'POST',
                        headers: {'Authorization': 'Bearer ' + token},
                        body: formData
                    });
                }
                status.style.color = "green";
                status.innerText = "Uploads complete! Updating view...";
                setTimeout(loadData, 1000);
            });
        }
        
        function renderStaticPages() {
            let html = `
                <div class="cms-header">
                    <h1>Static Pages</h1>
                </div>
                
                <div class="editor-section">
                    <h3>About Page Text</h3>
                    <p style="color:#666; margin-bottom:1rem; font-size:0.9rem;">This text appears on the About page. Paragraphs are automatically formatted.</p>
                    <textarea class="cms-textarea" id="about-text">${cmsData.static_pages['about.txt'] || ''}</textarea>
                    <button class="btn" id="save-about-btn" style="margin-top:1rem;">Save About Text</button>
                </div>
                
                <div class="editor-section">
                    <h3>Contact Page Text</h3>
                    <p style="color:#666; margin-bottom:1rem; font-size:0.9rem;">This text drives the grid on the Contact page.</p>
                    <textarea class="cms-textarea" id="contact-text">${cmsData.static_pages['contact.txt'] || ''}</textarea>
                    <button class="btn" id="save-contact-btn" style="margin-top:1rem;">Save Contact Text</button>
                </div>
            `;
            document.getElementById('cms-main').innerHTML = html;
            
            document.getElementById('save-about-btn').addEventListener('click', async () => {
                const text = document.getElementById('about-text').value;
                document.getElementById('save-about-btn').innerText = "Saving...";
                await fetch('/api/admin/update_text', {
                    method: 'POST',
                    headers: {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
                    body: JSON.stringify({target: 'about.txt', content: text})
                });
                cmsData.static_pages['about.txt'] = text;
                document.getElementById('save-about-btn').innerText = "Saved!";
                setTimeout(() => document.getElementById('save-about-btn').innerText = "Save About Text", 2000);
            });
            
            document.getElementById('save-contact-btn').addEventListener('click', async () => {
                const text = document.getElementById('contact-text').value;
                document.getElementById('save-contact-btn').innerText = "Saving...";
                await fetch('/api/admin/update_text', {
                    method: 'POST',
                    headers: {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
                    body: JSON.stringify({target: 'contact.txt', content: text})
                });
                cmsData.static_pages['contact.txt'] = text;
                document.getElementById('save-contact-btn').innerText = "Saved!";
                setTimeout(() => document.getElementById('save-contact-btn').innerText = "Save Contact Text", 2000);
            });
        }
        
        function renderBuild() {
            let html = `
                <div class="cms-header">
                    <h1>Publish Changes</h1>
                </div>
                <div class="editor-section" style="text-align:center; padding: 5rem 2rem;">
                    <h2 style="font-size:2rem; margin-bottom:1rem; font-family:'Inter', sans-serif;">Rebuild Website</h2>
                    <p style="margin-bottom:2rem; font-size:1.1rem; color:#555; max-width:600px; margin-left:auto; margin-right:auto;">
                        Whenever you are done uploading high-res photos or editing text, you must click Rebuild. 
                        This automatically shrinks and optimizes the images for the web, and generates the final HTML files.
                    </p>
                    <button class="btn" id="run-build-btn" style="font-size: 1.2rem; padding: 1.5rem 3rem;">Start Image Processing & Rebuild</button>
                    <p id="build-status" style="margin-top:2rem; font-weight:bold; font-size:1.2rem;"></p>
                </div>
            `;
            document.getElementById('cms-main').innerHTML = html;
            
            document.getElementById('run-build-btn').addEventListener('click', async () => {
                const status = document.getElementById('build-status');
                status.style.color = "blue";
                status.innerText = "Processing images and building site... please wait. Do not close this window. (This may take minutes if you uploaded huge files).";
                
                try {
                    const res = await fetch('/api/admin/build', {
                        method: 'POST',
                        headers: {'Authorization': 'Bearer ' + token}
                    });
                    if (res.ok) {
                        status.style.color = "green";
                        status.innerText = "Build Complete! Everything is updated. You can now sync to Github/Netlify. Refreshing preview in 3 seconds...";
                        setTimeout(() => window.location.reload(), 3000);
                    } else {
                        status.style.color = "red";
                        status.innerText = "Build Failed. Check server logs.";
                    }
                } catch(e) {
                    status.style.color = "red";
                    status.innerText = "Connection lost during build.";
                }
            });
        }
        
        // Init
        loadData();
    }
});
