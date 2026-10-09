import os
import glob
from urllib.parse import quote

# Ensure working directory is the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

portfolio_dir = "../pORTFOLIO"
web_images_dir = "assets/images_web"
content_dir = "content"
output_dir = "."

def has_images(cat_name):
    cat_dir = os.path.join(web_images_dir, cat_name)
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    for ext in extensions:
        for f in glob.glob(os.path.join(cat_dir, '**', ext), recursive=True):
            if not os.path.basename(f).startswith('._'):
                return True
    return False

import json

raw_categories = [d for d in os.listdir(web_images_dir) if os.path.isdir(os.path.join(web_images_dir, d)) and not d.startswith('.') and d.lower() != 'thumbnail' and has_images(d)]
raw_categories.sort()

series_order_path = os.path.join(content_dir, "series_order.json")
custom_order = []
if os.path.exists(series_order_path):
    try:
        with open(series_order_path, 'r', encoding='utf-8') as f:
            custom_order = json.load(f)
    except Exception:
        custom_order = []

categories = []
for item in custom_order:
    if item in raw_categories and item not in categories:
        categories.append(item)
for cat in raw_categories:
    if cat not in categories:
        categories.append(cat)

def get_nav_links(active_category):
    links = []
    is_home_active = "active" if active_category == "All Work" else ""
    links.append(f'<li><a href="index.html" class="{is_home_active}">Home / All Work</a></li>')
    
    for cat in categories:
        if cat.startswith('.'): continue
        if cat.lower() == 'thumbnail': continue
        filename = cat.lower().replace(' ', '-') + '.html'
        active_cls = 'active' if cat == active_category else ''
        links.append(f'<li><a href="{filename}" class="{active_cls}">{cat}</a></li>')
        
    # Static pages
    links.append(f'<li style="margin-top: 2rem;"><a href="video.html" class="{"active" if active_category == "Video" else ""}">&mdash; Video</a></li>')
    links.append(f'<li><a href="about.html" class="{"active" if active_category == "About" else ""}">&mdash; About</a></li>')
    links.append(f'<li><a href="contact.html" class="{"active" if active_category == "Contact" else ""}">&mdash; Contact</a></li>')
    
    return "\n                ".join(links)

# --- INDEX TEMPLATE ---
index_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Portfolio of CheGu (Vignesh Rathinam), a documentary photographer and filmmaker based in Tamil Nadu, capturing social and environmental narratives.">
    <meta property="og:title" content="CheGu - Documentary Photographer">
    <meta property="og:description" content="Portfolio of CheGu (Vignesh Rathinam), a documentary photographer and filmmaker based in Tamil Nadu.">
    <meta property="og:image" content="assets/images_web/about.jpg">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0f0f0f">
    <link rel="apple-touch-icon" href="assets/images_web/about.jpg">
    <title>CheGu - PORTFOLIO</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Person",
      "name": "CheGu",
      "alternateName": "Vignesh Rathinam",
      "jobTitle": "Documentary Photographer & Filmmaker",
      "url": "https://chegu.in"
    }}
    </script>
</head>
<body class="home-page">

    <header>
        <div class="logo"><a href="index.html">CheGu</a></div>
        <div class="series-title" style="text-align: center;"></div>
        <div class="header-actions">
            <button class="menu-btn" id="menu-btn">Menu</button>
        </div>
    </header>

    <main class="home-gallery">
        {gallery_items}
    </main>

    <div class="menu-overlay" id="menu-overlay">
        <div class="menu-header">
            <span>INDEX</span>
            <button class="close-menu" id="close-menu">Close</button>
        </div>
        <nav class="menu-nav">
            <ul class="nav-links">
                {nav_links}
            </ul>
        </nav>
    </div>

    <!-- Lightbox Modal for Home -->
    <div id="lightbox" class="lightbox">
        <span class="close-lightbox" id="close-lightbox">&times;</span>
        <button class="lb-arrow lb-prev" id="lb-prev" aria-label="Previous">&larr;</button>
        <img class="lightbox-content" id="lightbox-img" alt="Gallery Photo">
        <button class="lb-arrow lb-next" id="lb-next" aria-label="Next">&rarr;</button>
    </div>

    <script src="js/main.js?v=3"></script>
</body>
</html>
"""

# --- SERIES TEMPLATE ---
series_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Documentary photography series: {category_name} by CheGu.">
    <meta property="og:title" content="{category_name} - CheGu">
    <meta property="og:description" content="Documentary photography series: {category_name} by CheGu.">
    <meta property="og:image" content="{first_image}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0f0f0f">
    <link rel="apple-touch-icon" href="assets/images_web/about.jpg">
    <title>CheGu - {category_name}</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body class="series-page">

    <header>
        <div class="logo"><a href="index.html">CheGu</a></div>
        <div class="series-title" style="text-align: center;">{category_name}</div>
        <div class="header-actions">
            <button class="menu-btn" id="menu-btn">Menu</button>
        </div>
    </header>

    <main class="slideshow-container">
        <div class="gallery-layout">
            <div class="hero-view">
                <button class="nav-arrow left-arrow" id="hero-prev">&larr;</button>
                <img id="hero-img" src="{first_image}" alt="Hero Image">
                <button class="nav-arrow right-arrow" id="hero-next">&rarr;</button>
            </div>
            
            <div class="thumbnail-strip-container">
                <div class="thumbnail-strip" id="thumbnail-strip">
                    {thumbnails}
                </div>
            </div>
        </div>
        {scroll_indicator}
        {series_info}
    </main>

    <div class="menu-overlay" id="menu-overlay">
        <div class="menu-header">
            <span>INDEX</span>
            <button class="close-menu" id="close-menu">Close</button>
        </div>
        <nav class="menu-nav">
            <ul class="nav-links">
                {nav_links}
            </ul>
        </nav>
    </div>

    <!-- Lightbox for Series Hero Image -->
    <div id="lightbox" class="lightbox">
        <span class="close-lightbox" id="close-lightbox">&times;</span>
        <button class="lb-arrow lb-prev" id="lb-prev" aria-label="Previous">&larr;</button>
        <img class="lightbox-content" id="lightbox-img" alt="Series Photo">
        <button class="lb-arrow lb-next" id="lb-next" aria-label="Next">&rarr;</button>
    </div>

    <script src="js/main.js?v=3"></script>
</body>
</html>
"""

# --- STATIC TEMPLATE ---
static_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{title} - Portfolio of CheGu (Vignesh Rathinam), a documentary photographer.">
    <meta property="og:title" content="CheGu - {title}">
    <meta property="og:description" content="{title} - Portfolio of CheGu.">
    <meta property="og:image" content="assets/images_web/about.jpg">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0f0f0f">
    <link rel="apple-touch-icon" href="assets/images_web/about.jpg">
    <title>CheGu - {title}</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="static-page">

    <header>
        <div class="logo"><a href="index.html">CheGu</a></div>
        <div class="series-title" style="text-align: center;">{title}</div>
        <div class="header-actions">
            <button class="menu-btn" id="menu-btn">Menu</button>
        </div>
    </header>

    <main class="static-container">
        {content}
    </main>

    <div class="menu-overlay" id="menu-overlay">
        <div class="menu-header">
            <span>INDEX</span>
            <button class="close-menu" id="close-menu">Close</button>
        </div>
        <nav class="menu-nav">
            <ul class="nav-links">
                {nav_links}
            </ul>
        </nav>
    </div>
    
    <script src="js/main.js?v=3"></script>
</body>
</html>
"""

# --- VIDEO TEMPLATE ---
video_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Video & Documentary Film Works by CheGu (Vignesh Rathinam).">
    <meta property="og:title" content="CheGu - Video">
    <meta property="og:description" content="Documentary filmmaking, featurettes, and behind-the-scenes cinematography by CheGu.">
    <meta property="og:image" content="assets/images_web/video.jpg">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0f0f0f">
    <link rel="apple-touch-icon" href="assets/images_web/about.jpg">
    <title>CheGu - Video</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body class="video-page">

    <header>
        <div class="logo"><a href="index.html">CheGu</a></div>
        <div class="series-title" style="text-align: center;">Video</div>
        <div class="header-actions">
            <button class="menu-btn" id="menu-btn">Menu</button>
        </div>
    </header>

    <main class="video-container">
        <div class="video-header-intro">
            <h1>FILM &amp; VIDEO WORKS</h1>
            <p>Documentary filmmaking, featurettes, and political field reportage.</p>
        </div>
        {video_content}
    </main>

    <div class="menu-overlay" id="menu-overlay">
        <div class="menu-header">
            <span>INDEX</span>
            <button class="close-menu" id="close-menu">Close</button>
        </div>
        <nav class="menu-nav">
            <ul class="nav-links">
                {nav_links}
            </ul>
        </nav>
    </div>

    <script src="js/main.js?v=3"></script>
</body>
</html>
"""


# Generate index.html (Home)
generated_files = []

def make_category_card(cat):
    if cat.startswith('.'): return None
    cat_dir = os.path.join(web_images_dir, cat)
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(cat_dir, '**', ext), recursive=True))
    images = [img for img in images if not os.path.basename(img).startswith('._')]
    images.sort()
    if not images: return None

    # 1. Per-series thumbnail selection from thumbnail.txt (no separate folder needed)
    selected_img_url = None
    thumb_txt_path = os.path.join(cat_dir, "thumbnail.txt")
    if os.path.exists(thumb_txt_path):
        try:
            with open(thumb_txt_path, 'r', encoding='utf-8') as tf:
                target_fname = tf.read().strip()
            if target_fname:
                for img_path in images:
                    b_target = os.path.splitext(target_fname)[0].lower()
                    b_curr = os.path.splitext(os.path.basename(img_path))[0].lower()
                    if b_target == b_curr or target_fname.lower() == os.path.basename(img_path).lower():
                        rel_path = os.path.relpath(img_path, web_images_dir)
                        selected_img_url = "assets/images_web/" + "/".join(quote(p) for p in rel_path.split(os.sep))
                        break
        except Exception:
            pass

    # 2. Fallback to first image
    if not selected_img_url:
        img = images[0]
        rel_path = os.path.relpath(img, web_images_dir)
        selected_img_url = "assets/images_web/" + "/".join(quote(p) for p in rel_path.split(os.sep))

    series_link = cat.lower().replace(' ', '-') + '.html'
    return (
        f'<a href="{series_link}" class="home-gallery-item">'
        f'  <div class="image-wrapper">'
        f'    <img src="{selected_img_url}" loading="lazy" alt="{cat}">'
        f'  </div>'
        f'  <div class="item-meta">'
        f'    <span class="title">{cat}</span>'
        f'    <span class="arrow">&rarr;</span>'
        f'  </div>'
        f'</a>'
    )

def make_video_card():
    video_img = "assets/images_web/video.jpg" if os.path.exists(os.path.join(web_images_dir, "video.jpg")) else "https://img.youtube.com/vi/c_qrtaSdcIE/maxresdefault.jpg"
    return (
        f'<a href="video.html" class="home-gallery-item">'
        f'  <div class="image-wrapper">'
        f'    <img src="{video_img}" loading="lazy" alt="Video">'
        f'  </div>'
        f'  <div class="item-meta">'
        f'    <span class="title">Video</span>'
        f'    <span class="arrow">&rarr;</span>'
        f'  </div>'
        f'</a>'
    )

def make_about_card():
    about_img = "assets/images_web/about.jpg" if os.path.exists(os.path.join(web_images_dir, "about.jpg")) else "content/about.jpeg"
    return (
        f'<a href="about.html" class="home-gallery-item">'
        f'  <div class="image-wrapper">'
        f'    <img src="{about_img}" loading="lazy" alt="About">'
        f'  </div>'
        f'  <div class="item-meta">'
        f'    <span class="title">About</span>'
        f'    <span class="arrow">&rarr;</span>'
        f'  </div>'
        f'</a>'
    )

def make_contact_card():
    contact_img = "assets/images_web/contact.jpg" if os.path.exists(os.path.join(web_images_dir, "contact.jpg")) else "assets/images_web/about.jpg"
    return (
        f'<a href="contact.html" class="home-gallery-item">'
        f'  <div class="image-wrapper">'
        f'    <img src="{contact_img}" loading="lazy" alt="Contact">'
        f'  </div>'
        f'  <div class="item-meta">'
        f'    <span class="title">Contact</span>'
        f'    <span class="arrow">&rarr;</span>'
        f'  </div>'
        f'</a>'
    )

all_work_items = []
placed_items = set()

# Process custom order from series_order.json
for item in custom_order:
    if item in categories and item not in placed_items:
        card = make_category_card(item)
        if card:
            all_work_items.append(card)
            placed_items.add(item)
    elif item.lower() == 'video' and 'video' not in placed_items:
        all_work_items.append(make_video_card())
        placed_items.add('video')
    elif item.lower() == 'about' and 'about' not in placed_items:
        all_work_items.append(make_about_card())
        placed_items.add('about')
    elif item.lower() == 'contact' and 'contact' not in placed_items:
        all_work_items.append(make_contact_card())
        placed_items.add('contact')

# Add any categories that weren't in custom_order
for cat in categories:
    if cat not in placed_items:
        card = make_category_card(cat)
        if card:
            all_work_items.append(card)
            placed_items.add(cat)

# Add Video, About, Contact if not already placed
if 'video' not in placed_items:
    all_work_items.append(make_video_card())
if 'about' not in placed_items:
    all_work_items.append(make_about_card())
if 'contact' not in placed_items:
    all_work_items.append(make_contact_card())

html_index = index_template.format(
    nav_links=get_nav_links("All Work"),
    gallery_items="\n        ".join(all_work_items)
)
with open(os.path.join(output_dir, 'index.html'), 'w') as f:
    f.write(html_index)

# Generate category pages
for cat in categories:
    if cat.startswith('.'): continue
    if cat.lower() == 'thumbnail': continue
    
    cat_dir = os.path.join(web_images_dir, cat)
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(cat_dir, '**', ext), recursive=True))
    images.sort()
    
    if not images: continue
    
    first_rel_path = os.path.relpath(images[0], web_images_dir)
    first_image_url = "assets/images_web/" + "/".join(quote(p) for p in first_rel_path.split(os.sep))
    
    # Check for description.txt in the web category folder first, then raw portfolio folder
    desc_path = os.path.join(web_images_dir, cat, "description.txt")
    if not os.path.exists(desc_path):
        desc_path = os.path.join(portfolio_dir, cat, "description.txt")
    series_info_html = ""
    scroll_indicator_html = ""
    if os.path.exists(desc_path):
        with open(desc_path, 'r') as df:
            desc_text = df.read().strip()
        if desc_text:
            import re
            # Parse bold **text**
            desc_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', desc_text)
            
            # If text only used single newlines, separate title and body
            if '\n\n' not in desc_text and '\n' in desc_text:
                lines = desc_text.split('\n')
                desc_text = lines[0] + '\n\n' + ' '.join(l.strip() for l in lines[1:] if l.strip())
                
            paragraphs = desc_text.split('\n\n')
            p_html = []
            for p in paragraphs:
                p_clean = p.strip()
                if not p_clean: continue
                # In prose paragraphs without markdown list/breaks, join soft-wrapped lines with spaces
                if '<strong>' not in p_clean and '\n' in p_clean:
                    p_clean = ' '.join(line.strip() for line in p_clean.split('\n') if line.strip())
                else:
                    p_clean = p_clean.replace('\n', '<br>')
                p_html.append(f"<p>{p_clean}</p>")
                
            series_info_html = f'<div class="series-info">{"".join(p_html)}</div>'
            scroll_indicator_html = '<div class="scroll-prompt-banner" onclick="window.scrollBy({top: window.innerHeight, behavior: \'smooth\'})">Read Project Info <span>&darr;</span></div>'
    
    thumbnails_html = []
    for idx, img in enumerate(images):
        rel_path = os.path.relpath(img, web_images_dir)
        img_url = "assets/images_web/" + "/".join(quote(p) for p in rel_path.split(os.sep))
        active_class = "active" if idx == 0 else ""
        thumbnails_html.append(f'<img src="{img_url}" class="thumb {active_class}" data-index="{idx}">')
        
    html = series_template.format(
        category_name=cat,
        nav_links=get_nav_links(cat),
        first_image=first_image_url,
        scroll_indicator=scroll_indicator_html,
        series_info=series_info_html,
        thumbnails="\n                ".join(thumbnails_html)
    )
    
    filename = cat.lower().replace(' ', '-') + '.html'
    generated_files.append(filename)
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(html)

# Clean up orphaned HTML files (pages that no longer have a corresponding category)
for file in os.listdir(output_dir):
    if file.endswith('.html') and file != 'index.html' and file not in ['about.html', 'contact.html', 'video.html']:
        if file not in generated_files:
            os.remove(os.path.join(output_dir, file))
            print(f"Removed orphaned page: {file}")

# Generate About page
about_txt = os.path.join(content_dir, 'about.txt')
if not os.path.exists(about_txt):
    about_txt = os.path.join(portfolio_dir, 'about.txt')
about_text_html = ""
if os.path.exists(about_txt):
    with open(about_txt, 'r') as f:
        text = f.read().strip()
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        paragraphs = text.split('\n\n')
        p_html = "\n".join(f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip())
        about_text_html = f'<div class="static-content">{p_html}</div>'

# Add about image if exists
about_img_html = '<div class="about-image-column"></div>'
if os.path.exists(os.path.join(web_images_dir, 'about.jpg')):
    about_img_html = '<div class="about-image-column"><img src="assets/images_web/about.jpg" class="about-img" alt="About"></div>'
elif os.path.exists(os.path.join(content_dir, 'about.jpeg')):
    about_img_html = '<div class="about-image-column"><img src="content/about.jpeg" class="about-img" alt="About"></div>'

about_content = f"""
<div class="about-wrapper">
    {about_img_html}
    <div class="about-text-column">
        {about_text_html}
    </div>
</div>
"""

about_html = static_template.format(
    title="About",
    nav_links=get_nav_links("About"),
    content=about_content
)
with open(os.path.join(output_dir, 'about.html'), 'w') as f:
    f.write(about_html)

# Generate Contact page
contact_txt = os.path.join(content_dir, 'contact.txt')
if not os.path.exists(contact_txt):
    contact_txt = os.path.join(portfolio_dir, 'contact.txt')
contact_content = ""
if os.path.exists(contact_txt):
    with open(contact_txt, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        
    if len(lines) >= 4:
        phone = lines[0]
        email = lines[1]
        location = lines[2]
        social = lines[3]
        instagram = lines[4] if len(lines) >= 5 else "https://www.instagram.com/chegu__/"
        
        # Clean display handles
        insta_clean = instagram.replace('https://', '').replace('http://', '').replace('www.instagram.com/', '').strip('/')
        if not insta_clean.startswith('@'):
            insta_display = f"@{insta_clean}"
        else:
            insta_display = insta_clean
            
        insta_href = instagram if instagram.startswith('http') else f"https://{instagram}"
        social_href = social if social.startswith('http') else f"https://{social}"
        
        contact_content = f"""
        <div class="contact-wrapper">
            <div class="contact-header">
                <h1>GET IN TOUCH</h1>
                <p>Available for assignments, collaborations, and prints.</p>
            </div>
            <div class="contact-grid">
                <div class="contact-item">
                    <span class="contact-label">EMAIL</span>
                    <a href="mailto:{email}" class="contact-link">{email}</a>
                </div>
                <div class="contact-item">
                    <span class="contact-label">PHONE</span>
                    <a href="tel:{phone.replace(' ', '')}" class="contact-link">{phone}</a>
                </div>
                <div class="contact-item">
                    <span class="contact-label">LOCATION</span>
                    <span class="contact-text">{location}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-label">INSTAGRAM</span>
                    <a href="{insta_href}" target="_blank" rel="noopener noreferrer" class="contact-link">{insta_display}</a>
                </div>
                <div class="contact-item">
                    <span class="contact-label">LINKEDIN</span>
                    <a href="{social_href}" target="_blank" rel="noopener noreferrer" class="contact-link">Vignesh Rathinam</a>
                </div>
            </div>
        </div>
        """
    else:
        # Fallback if text format changes
        text = "\n".join(lines)
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        paragraphs = text.split('\n\n')
        p_html = "\n".join(f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip())
        contact_content += f'<div class="static-content">{p_html}</div>'

contact_html = static_template.format(
    title="Contact",
    nav_links=get_nav_links("Contact"),
    content=contact_content
)
with open(os.path.join(output_dir, 'contact.html'), 'w') as f:
    f.write(contact_html)

# Generate Video page
videos_json_path = os.path.join(content_dir, 'videos.json')
if not os.path.exists(videos_json_path):
    videos_json_path = os.path.join(portfolio_dir, 'videos.json')
video_content_html = []
if os.path.exists(videos_json_path):
    import json
    try:
        with open(videos_json_path, 'r') as vf:
            videos_raw = json.load(vf)
    except Exception:
        videos_raw = []
else:
    videos_raw = []

# Normalize to sections
sections = []
if isinstance(videos_raw, list) and len(videos_raw) > 0:
    if "section_title" in videos_raw[0]:
        sections = videos_raw
    else:
        sections = [{"section_title": "All Works", "section_desc": "", "videos": videos_raw}]

for sec in sections:
    sec_title = sec.get("section_title", "")
    sec_desc = sec.get("section_desc", "")
    sec_cards = []
    for v in sec.get("videos", []):
        vid_id = v.get("id", "")
        title = v.get("title", "")
        subtitle = v.get("subtitle", "")
        desc = v.get("description", "")
        card_html = f"""
            <div class="video-card">
                <div class="video-embed-wrapper">
                    <iframe src="https://www.youtube.com/embed/{vid_id}" title="{title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
                </div>
                <div class="video-meta">
                    <div class="video-meta-top">
                        <h2 class="video-title">{title}</h2>
                        <span class="video-subtitle">{subtitle}</span>
                    </div>
                    <p class="video-desc">{desc}</p>
                </div>
            </div>"""
        sec_cards.append(card_html)
    
    sec_html = f"""
    <section class="video-section">
        <div class="video-section-header">
            <h2 class="video-section-title">{sec_title}</h2>
            <span class="video-section-desc">{sec_desc}</span>
        </div>
        <div class="video-grid">
            {"".join(sec_cards)}
        </div>
    </section>"""
    video_content_html.append(sec_html)

video_html = video_template.format(
    nav_links=get_nav_links("Video"),
    video_content="\n".join(video_content_html)
)
with open(os.path.join(output_dir, 'video.html'), 'w') as f:
    f.write(video_html)

print("Generated HTML pages recursively with Swiss Reduce structure.")
