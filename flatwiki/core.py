import sys
from argon2 import PasswordHasher
import os
import json
import markdown
from datetime import datetime
from flask import Flask, abort, render_template_string, request, session, redirect, url_for, send_from_directory
import secrets
from waitress import serve

ph = PasswordHasher()

app = Flask(__name__)

CURRENT_DIR = os.getcwd()
CONFIG_PATH = os.path.join(CURRENT_DIR, "flatwiki.json")

if not os.path.exists(CONFIG_PATH):
    print(f"Error: Could not find 'flatwiki.json' in {CURRENT_DIR}")
    sys.exit(1)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    try:
        CONFIG = json.load(f)
    except:
        print("Error: Invalid JSON content in flatwiki.json")
        exit(1)

PAGES_DIR = os.path.join(CURRENT_DIR, CONFIG["pages_directory"])
WIKI_TITLE = CONFIG["wiki_title"]
PORT = CONFIG["port"]

ADMINS = CONFIG["admins"]

app.secret_key = secrets.token_hex(32)

os.makedirs(PAGES_DIR, exist_ok=True)

@app.route('/admin/static/style.css')
def admin_style():
    css = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 13px;
    color: #333;
    background: linear-gradient(to bottom, #dbe3eb 0%, #f0f4f7 300px, #f5f5f5 100%);
    background-repeat: no-repeat;
    background-attachment: fixed;
    min-height: 100vh;
}
a {
    color: #005580;
    text-decoration: none;
    font-weight: bold;
}
a:hover {
    text-decoration: underline;
}

#main-header {
    background: linear-gradient(to bottom, #4c4d50 0%, #353638 50%, #222324 51%, #1b1c1d 100%);
    color: #fff;
    height: 50px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    border-bottom: 3px solid #ff9900; /* High-contrast orange or teal accent strip */
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
#main-header .logo {
    font-size: 16px;
    color: #fff;
    text-shadow: 0 -1px 0 rgba(0,0,0,0.8);
}
#main-header .logo strong {
    color: #ff9900;
}
#main-header .user-profile {
    font-size: 11px;
    color: #ddd;
    text-shadow: 0 1px 0 rgba(0,0,0,0.5);
}
#main-header .user-profile a {
    color: #fff;
    background: linear-gradient(to bottom, #555, #333);
    padding: 3px 8px;
    border: 1px solid #222;
    border-radius: 3px;
    font-weight: normal;
}

#app-container {
    display: flex;
    min-height: calc(100vh - 50px);
}

#sidebar {
    width: 220px;
    /* Vertical light-to-dark side panel gradient */
    background: linear-gradient(to right, #e4e4e4 0%, #d4d4d4 100%);
    border-right: 1px solid #b3b3b3;
    padding: 10px 0;
    box-shadow: inset -2px 0 5px rgba(0,0,0,0.05);
}
.nav-section h3 {
    font-size: 11px;
    text-transform: uppercase;
    color: #555;
    /* Textured header bars for sub-navigation */
    background: linear-gradient(to bottom, #dadada, #c8c8c8);
    padding: 6px 15px;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #b5b5b5;
    text-shadow: 0 1px 0 rgba(255,255,255,0.6);
    margin-bottom: 5px;
}
.nav-section ul {
    list-style: none;
    margin-bottom: 15px;
}
.nav-section ul li a {
    display: block;
    padding: 8px 20px;
    color: #444;
    font-weight: normal;
    text-shadow: 0 1px 0 rgba(255,255,255,0.5);
    border-bottom: 1px solid #cbcbcb;
}
.nav-section ul li.active a,
.nav-section ul li a:hover {
    background: linear-gradient(to bottom, #ffffff 0%, #e6e6e6 100%);
    color: #000;
    font-weight: bold;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
}

#main-content {
    flex: 1;
    padding: 20px;
}
.breadcrumb {
    font-size: 11px;
    color: #666;
    margin-bottom: 12px;
}

h1 {
    font-size: 20px;
    font-weight: bold;
    color: #222;
    padding: 10px 15px;
    margin-bottom: 20px;
    /* Subtle header canvas gradient styling */
    background: linear-gradient(to bottom, #ffffff, #e1e1e1);
    border: 1px solid #ccc;
    border-radius: 4px;
    text-shadow: 0 1px 0 #fff;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.inner-content {
    background: #fff;
    border: 1px solid #b5b5b5;
    border-radius: 4px;
    padding: 15px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.action-bar {
    background: linear-gradient(to bottom, #fafafa 0%, #eaeaea 100%);
    padding: 10px;
    border: 1px solid #cccccc;
    border-bottom: 2px solid #b3b3b3;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.search-input {
    padding: 5px 8px;
    border: 1px solid #bbb;
    border-radius: 3px;
    font-size: 12px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.btn {
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
    cursor: pointer;
    border-radius: 4px;
    text-shadow: 0 1px 0 #fff;
    border: 1px solid #adc2ce;
    border-top: 1px solid #c2d5e0;
    border-bottom: 1px solid #8fa2ad;
    background: linear-gradient(to bottom, #ffffff 0%, #f3f3f3 50%, #ededed 51%, #e0e0e0 100%);
    color: #444;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.btn:hover {
    background: linear-gradient(to bottom, #f9f9f9 0%, #e3e3e3 50%, #dadada 51%, #cdcdcd 100%);
    border-color: #7a8c97;
}

.btn-primary {
    color: #fff;
    text-shadow: 0 -1px 0 rgba(0,0,0,0.4);
    border: 1px solid #1a7185;
    border-top: 1px solid #54cbfa;
    border-bottom: 1px solid #114f5e;
    background: linear-gradient(to bottom, #49c0dc 0%, #2ca1be 50%, #1f8fa9 51%, #1a7e96 100%);
}
.btn-primary:hover {
    background: linear-gradient(to bottom, #3caec8 0%, #2390ab 50%, #177d95 51%, #126b80 100%);
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #bbb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.data-table th {
    background: linear-gradient(to bottom, #ffffff 0%, #f0f0f0 50%, #e3e3e3 51%, #dfdfdf 100%);
    border: 1px solid #bbb;
    border-top: 1px solid #fff; /* Highlights upper boundaries */
    padding: 10px;
    text-align: left;
    font-size: 12px;
    color: #444;
    font-weight: bold;
    text-shadow: 0 1px 0 #fff;
}
.data-table td {
    padding: 10px;
    border: 1px solid #ddd;
    font-size: 12px;
    background-color: #fff;
}
.data-table tr.alt td {
    background-color: #f6f8fa;
}
.data-table tbody tr:hover td {
    background: linear-gradient(to bottom, #f2f9ff 0%, #e1f0fc 100%) !important;
    color: #000;
}
.delete {
    color: #a90000;
}
"""
    return css, 200, {'Content-Type': 'text/css'}


PUBLIC_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - """ + WIKI_TITLE + """</title>
    <style>
        body { font-family: sans-serif; display: flex; margin: 0; padding: 0; }
        #sidebar { width: 240px; background: #f4f5f7; height: 100vh; padding: 20px; border-right: 1px solid #e1e4e8; }
        #content { flex: 1; padding: 40px; max-width: 800px; line-height: 1.6; }
        a { color: #0366d6; text-decoration: none; }
        ul { list-style: none; padding: 0; }
        li { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h3>""" + WIKI_TITLE + """</h3>
        <a href="/">Home</a><hr>
        <ul>
            {% for route, display in menu_items %}
                <li><a href="/{{ route }}">{{ display }}</a></li>
            {% endfor %}
        </ul>
        <br><a href="/admin" style="font-size:12px; color:#888;">Admin Login</a>
    </div>
    <div id="content">{{ content|safe }}</div>
</body>
</html>
"""

ADMIN_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <link rel="stylesheet" href="/admin/static/style.css">
</head>
<body>
    <header id="main-header">
        <div class="logo">FLATWIKI <strong>ADMIN</strong></div>
        <div class="user-profile"><a href="/logout">Logout</a></div>
    </header>
    <div id="app-container">
        <nav id="sidebar">
            <div class="nav-section">
                <h3>Wiki Structure</h3>
                <ul>
                    <li class="active"><a href="/admin">Dashboard</a></li>
                </ul>
            </div>
        </nav>
        <main id="main-content">
            <div class="breadcrumb">
                <a href="/">Home</a> &raquo; <a href="/admin">Dashboard</a>
            </div>
            <h1>Dashboard</h1>
            <div class="inner-content">
                <div class="action-bar"> 
                    <form method="POST" action="/admin/create" style="border: none; margin: 0; padding: 0;"> 
                        <input type="text" name="filename" placeholder="new-page-name" required class="search-input" autocomplete="off"> 
                        <button type="submit" class="btn btn-primary">Create New Page</button> 
                    </form> 
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th width="5%">ID</th>
                            <th width="50%">Title</th>
                            <th width="25%">Last Modified</th>
                            <th width="20%">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in files_data %}
                        <tr class="{{ 'alt' if loop.index % 2 == 0 else '' }}">
                            <td>{{ loop.index }}</td>
                            <td><strong>{{ item.title }}</strong> ({{ item.filename }})</td>
                            <td>{{ item.modified }}</td>
                            <td>
                                <a href="/admin/edit/{{ item.filename }}">Edit</a> |
                                <form method="POST" action="/admin/delete/{{ item.filename }}" style="display:inline;">
                                    <a href="#" class="delete" 
                                    onclick="if(confirm('Are you sure you want to delete this file permanently?')) { this.closest('form').submit(); } return false;">
                                        Delete
                                    </a>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>
"""

EDIT_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Editing {{ filename }}</title>
    <link rel="stylesheet" href="/admin/static/style.css">
    <style>
        textarea { width: 100%; height: 450px; font-family: monospace; font-size: 14px; padding: 15px; border: 1px solid #bbb; border-radius: 4px; resize: vertical; margin-bottom: 20px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); box-sizing: border-box; }
        .btn { text-decoration: none; display: inline-block; }
        p.note { font-size: 12px; color: #666; margin-bottom: 20px; }
    </style>
</head>
<body>
    <header id="main-header">
        <div class="logo">FLATWIKI <strong>ADMIN</strong></div>
        <div class="user-profile"><a href="/logout">Logout</a></div>
    </header>
    <div id="app-container">
        <nav id="sidebar">
            <div class="nav-section">
                <h3>Wiki Structure</h3>
                <ul>
                    <li><a href="/admin">Dashboard</a></li>
                    <li class="active"><a href="#">{{ filename }}</a></li>
                </ul>
            </div>
        </nav>
        <main id="main-content">
            <div class="breadcrumb">
                <a href="/">Home</a> &raquo; <a href="/admin">Dashboard</a> &raquo; {{ filename }}
            </div>
            <h1>Editing: {{ filename }}</h1>
            <div class="inner-content">
                <p class="note">This editor supports standard Markdown formatting.</p>
                <form method="POST">
                    <textarea name="content">{{ content }}</textarea>
                    <div style="display: flex; gap: 10px;">
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                        <a href="/admin" class="btn">Cancel</a>
                    </div>
                </form>
            </div>
        </main>
    </div>
</body>
</html>
"""

LOGIN_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Login</title>
    <link rel="stylesheet" href="/admin/static/style.css">
</head>
<body>
    <header id="main-header">
        <div class="logo">FLATWIKI <strong>ADMIN</strong></div>
    </header>
    <div style="display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 50px);">
        <div style="background: #fff; border: 1px solid #b5b5b5; border-radius: 4px; padding: 30px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); width: 360px;">
            <h1 style="margin-bottom: 24px; text-align: center;">Admin Login</h1>
            {% if error %}<div style="color: #a90000; font-size: 13px; margin-bottom: 15px; text-align: center;">{{ error }}</div>{% endif %}
            <form method="POST" action="/login">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-size: 12px; color: #555; margin-bottom: 5px; font-weight: bold;">Username</label>
                    <input autocomplete="off" type="text" name="username" required style="width: 100%; padding: 8px 10px; border: 1px solid #bbb; border-radius: 3px; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); box-sizing: border-box;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-size: 12px; color: #555; margin-bottom: 5px; font-weight: bold;">Password</label>
                    <input autocomplete="off" type="password" name="password" required style="width: 100%; padding: 8px 10px; border: 1px solid #bbb; border-radius: 3px; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); box-sizing: border-box;">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; padding: 8px 14px;">Log In</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

def get_sorted_menu():
    """Generates an alphabetical page listing for the sidebar navbar display."""
    if not os.path.exists(PAGES_DIR):
        return []
    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md") and f != "index.md"]
    files.sort()
    
    menu = []
    for f in files:
        route = f.rsplit('.', 1)[0]
        display = route.replace('-', ' ').replace('_', ' ').title()
        menu.append((route, display))
    return menu

@app.route('/admin/create', methods=['POST'])
def admin_create_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    raw_name = request.form.get('filename', '').strip().lower()
    safe_name = os.path.basename(raw_name).replace(' ', '-')
    
    if not safe_name:
        return redirect(url_for('admin_dashboard'))
        
    if not safe_name.endswith('.md'):
        safe_name += '.md'
        
    file_path = os.path.join(PAGES_DIR, safe_name)
    
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {safe_name.rsplit('.', 1)[0].replace('-', ' ').title()}\nWrite content here...")
            
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit/<filename>', methods=['GET', 'POST'])
def admin_edit_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(PAGES_DIR, safe_filename)
    
    if not os.path.exists(file_path):
        return "Error: File does not exist.", 404
        
    if request.method == 'POST':
        updated_markdown = request.form.get('content', '').replace('\r\n', '\n')
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_markdown)
        return redirect(url_for('admin_dashboard'))
        
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        
    return render_template_string(EDIT_LAYOUT, filename=safe_filename, content=file_content)

@app.route('/admin/delete/<filename>', methods=['POST'])
def admin_delete_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(PAGES_DIR, safe_filename)
    
    if safe_filename == "index.md":
        return "Error: Cannot delete the core homepage layout.", 403
        
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            ph.verify(ADMINS[request.form['username']], request.form['password'])
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        except:
            error = "Invalid credentials."
            
    return render_template_string(LOGIN_LAYOUT, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('serve_public_pages'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if not os.path.exists(PAGES_DIR):
        os.makedirs(PAGES_DIR, exist_ok=True)
        
    raw_files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".md")]
    raw_files.sort()
    
    files_data = []
    for f in raw_files:
        f_path = os.path.join(PAGES_DIR, f)
        mtime = os.path.getmtime(f_path)
        formatted_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        
        files_data.append({
            'filename': f,
            'title': f.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title(),
            'modified': formatted_time,
        })
        
    return render_template_string(ADMIN_LAYOUT, files_data=files_data)


@app.route('/', defaults={'path': 'index'})
@app.route('/<path:path>')
def serve_public_pages(path):
    if path in ['admin', 'login', 'logout'] or path.startswith('admin/'):
        abort(404)
        
    safe_path = os.path.basename(path)
    file_path = os.path.join(PAGES_DIR, f"{safe_path}.md")
        
    if not os.path.exists(file_path):
        if safe_path == 'index':
            os.makedirs(PAGES_DIR, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# Welcome to your FlatWiki\nEdit this file or visit `/admin` to add more content.")
        else:
            abort(404)
        
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    html_content = markdown.markdown(md_text)
    current_title = "Home" if safe_path == "index" else safe_path.replace('-', ' ').replace('_', ' ').title()
    
    return render_template_string(
        PUBLIC_LAYOUT,
        title=current_title,
        content=html_content,
        menu_items=get_sorted_menu()
    )

def run_server():
    print(f"FlatWiki Engine Native Service active at http://127.0.0.1:{PORT}")
    serve(app, host="0.0.0.0", port=PORT, threads=4)

if __name__ == '__main__':
    run_server()
