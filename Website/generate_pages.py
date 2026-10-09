import os
import glob
from urllib.parse import quote

portfolio_dir = "../pORTFOLIO"
web_images_dir = "assets/images_web"
output_dir = "."

categories = [d for d in os.listdir(web_images_dir) if os.path.isdir(os.path.join(web_images_dir, d))]
categories.sort()

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
    links.append(f'<li style="margin-top: 2rem;"><a href="about.html" class="{"active" if active_category == "About" else ""}">&mdash; About</a></li>')
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
        <div class="series-title" style="text-align: center;">All Work</div>
        <div class="header-actions">
            <button class="admin-btn" id="admin-trigger-btn">Admin</button>
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
        <button class="nav-arrow left-arrow" id="lb-prev">&larr;</button>
        <img class="lightbox-content" id="lightbox-img">
        <button class="nav-arrow right-arrow" id="lb-next">&rarr;</button>
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
        <button class="nav-arrow left-arrow" id="lb-prev" style="position:fixed; z-index:1001;">&larr;</button>
        <img class="lightbox-content" id="lightbox-img">
        <button class="nav-arrow right-arrow" id="lb-next" style="position:fixed; z-index:1001;">&rarr;</button>
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

# Generate index.html (Home)
thumbnail_dir = "/Volumes/Che-Card-1/Website/thumbnail"
all_work_items = []
generated_files = []

for cat in categories:
    if cat.startswith('.'): continue
    if cat.lower() == 'thumbnail': continue # Skip the Thumbnail folder itself as a category
    
    cat_dir = os.path.join(web_images_dir, cat)
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(cat_dir, '**', ext), recursive=True))
    images.sort()
    
    if not images: continue
    
    # Check if there is a specific thumbnail for this category in the user's thumbnail folder
    # We do this by checking if any file in the thumbnail folder matches an image in this category
    selected_img_url = None
    if os.path.exists(thumbnail_dir):
        thumb_files = os.listdir(thumbnail_dir)
        for t_file in thumb_files:
            # t_file could be .NEF, .jpg, etc.
            base_t = os.path.splitext(t_file)[0]
            # See if base_t exists in the category's optimized images
            for img_path in images:
                if os.path.splitext(os.path.basename(img_path))[0] == base_t:
                    # Found a match! Use the optimized version of this file
                    rel_path = os.path.relpath(img_path, web_images_dir)
                    selected_img_url = "assets/images_web/" + "/".join(quote(p) for p in rel_path.split(os.sep))
                    break
            if selected_img_url:
                break
    
    # Fallback to the first image if no specific thumbnail was found
    if not selected_img_url:
        img = images[0]
        rel_path = os.path.relpath(img, web_images_dir)
        selected_img_url = "assets/images_web/" + "/".join(quote(p) for p in rel_path.split(os.sep))
        
    series_link = cat.lower().replace(' ', '-') + '.html'
    all_work_items.append(
        f'<a href="{series_link}" class="home-gallery-item">'
        f'  <div class="image-wrapper">'
        f'    <img src="{selected_img_url}" loading="lazy">'
        f'  </div>'
        f'  <div class="item-meta">'
        f'    <span class="title">{cat}</span>'
        f'    <span class="arrow">&rarr;</span>'
        f'  </div>'
        f'</a>'
    )

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
    
    # Check for description.txt in the raw portfolio folder
    raw_cat_dir = os.path.join(portfolio_dir, cat)
    desc_path = os.path.join(raw_cat_dir, "description.txt")
    series_info_html = ""
    scroll_indicator_html = ""
    if os.path.exists(desc_path):
        with open(desc_path, 'r') as df:
            desc_text = df.read().strip()
        if desc_text:
            import re
            # Parse bold **text**
            desc_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', desc_text)
            # Wrap paragraphs in <p> tags
            paragraphs = desc_text.split('\n\n')
            p_html = "\n".join(f"<p>{p.strip().replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip())
            series_info_html = f'<div class="series-info">{p_html}</div>'
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
    if file.endswith('.html') and file != 'index.html' and file not in ['about.html', 'contact.html']:
        if file not in generated_files:
            os.remove(os.path.join(output_dir, file))
            print(f"Removed orphaned page: {file}")

# Generate About page
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
                    <span class="contact-label">SOCIAL</span>
                    <a href="https://{social.replace('https://', '')}" target="_blank" class="contact-link">LinkedIn</a>
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

print("Generated HTML pages recursively with Swiss Reduce structure.")
