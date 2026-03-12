#!/usr/bin/env python3
"""Reads tasks.md and generates index.html.

Supports two formats:
  Flat:       just `- item` lines
  Categorized: `## Category` headings followed by `- item` lines
"""

import re, os, html, json

def parse_tasks(path="tasks.md"):
    categories = {}
    flat = []
    current_cat = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("## "):
                current_cat = line[3:].strip()
                categories[current_cat] = []
                continue
            if not line.startswith("- "):
                continue
            text = line[2:]
            m = re.match(r'\[(.+?)\]\((.+?)\)', text)
            task = {"title": m.group(1), "url": m.group(2)} if m else {"title": text, "url": None}
            if current_cat:
                categories[current_cat].append(task)
            else:
                flat.append(task)

    if not categories and flat:
        return {"_flat": flat}, []
    return categories, flat

def build():
    categories, top_tasks = parse_tasks()
    is_flat = "_flat" in categories and len(categories) == 1

    # Build JSON data for JS routing
    json_cats = {}
    for cat, tasks in categories.items():
        key = cat if is_flat else cat.lower().replace(" ", "-")
        json_cats[key] = [{"title": t["title"], "url": t["url"]} for t in tasks]

    json_top = [{"title": t["title"], "url": t["url"]} for t in top_tasks]

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>what u doin?</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Georgia', serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fff;
      color: #222;
    }}

    .container {{
      width: 100%;
      max-width: 420px;
      padding: 3rem 2rem;
      border-left: 1.5px solid #ddd;
    }}

    h1 {{
      font-size: 1.1rem;
      font-weight: 400;
      margin-bottom: 2rem;
      line-height: 1.4;
      color: #999;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    h1 img {{
      width: 24px;
      height: 24px;
    }}

    .tasks {{
      display: flex;
      flex-direction: column;
    }}

    .item {{
      display: block;
      font-size: 1.05rem;
      color: #222;
      text-decoration: none;
      padding: 0.8rem 0;
      line-height: 1.7;
      cursor: pointer;
    }}

    .item + .item {{
      border-top: 1px solid #f0eeea;
    }}

    a.item:hover, .item.cat:hover {{
      color: #888;
    }}

    span.item:not(.cat) {{
      color: #222;
      cursor: default;
    }}

    .item.cat::after {{
      content: '\\2192';
      float: right;
      color: #ccc;
      transition: transform 0.2s;
    }}

    .item.cat:hover::after {{
      transform: translateX(3px);
      color: #888;
    }}

    .cat-header {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: #bbb;
      margin-bottom: 0.8rem;
      cursor: pointer;
      text-decoration: none;
    }}

    .cat-header::before {{
      content: '\\2190';
      font-size: 0.85rem;
    }}

    .cat-header:hover {{
      color: #555;
    }}

    @media (prefers-color-scheme: dark) {{
      body {{
        background: #111;
        color: #d5d5d5;
      }}

      .container {{
        border-left-color: #333;
      }}

      h1 {{
        color: #666;
      }}

      .item {{
        color: #d5d5d5;
      }}

      .item + .item {{
        border-top-color: #222;
      }}

      a.item:hover, .item.cat:hover {{
        color: #888;
      }}

      span.item:not(.cat) {{
        color: #d5d5d5;
      }}

      .item.cat::after {{
        color: #444;
      }}

      .item.cat:hover::after {{
        color: #888;
      }}

      .cat-header {{
        color: #444;
      }}

      .cat-header:hover {{
        color: #999;
      }}
    }}

    @media (max-width: 480px) {{
      .container {{
        margin: 1.5rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1><img src="https://media.giphy.com/media/WUlplcMpOCEmTGBtBW/giphy.gif" alt="">Working on</h1>
    <div id="view" class="tasks"></div>
  </div>
  <script>
    var CATS = {json.dumps(json_cats)};
    var TOP = {json.dumps(json_top)};
    var IS_FLAT = {'true' if is_flat else 'false'};
    var CAT_KEYS = Object.keys(CATS);

    function render() {{
      var params = new URLSearchParams(window.location.search);
      var cat = params.get('cat');
      var view = document.getElementById('view');

      if (IS_FLAT) {{
        view.innerHTML = renderTasks(CATS['_flat']);
        return;
      }}

      if (cat && CATS[cat]) {{
        var displayName = cat.replace(/-/g, ' ');
        displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1);
        view.innerHTML =
          '<a class="cat-header" onclick="go(null)">' + esc(displayName) + '</a>' +
          renderTasks(CATS[cat]);
      }} else {{
        var html = CAT_KEYS.map(function(c) {{
          var displayName = c.replace(/-/g, ' ');
          displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1);
          var count = CATS[c].length;
          return '<span class="item cat" onclick="go(\\'' + c + '\\')">' +
            esc(displayName) + ' <span style="color:#bbb;font-size:0.85em">(' + count + ')</span></span>';
        }}).join('');
        html += renderTasks(TOP);
        view.innerHTML = html;
      }}
    }}

    function renderTasks(tasks) {{
      return tasks.map(function(t) {{
        if (t.url) {{
          return '<a href="' + esc(t.url) + '" target="_blank" rel="noopener" class="item">' + esc(t.title) + '</a>';
        }}
        return '<span class="item">' + esc(t.title) + '</span>';
      }}).join('');
    }}

    function go(cat) {{
      var url = window.location.pathname;
      if (cat) url += '?cat=' + encodeURIComponent(cat);
      history.pushState(null, '', url);
      render();
    }}

    function esc(s) {{
      var d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }}

    window.addEventListener('popstate', render);
    render();
  </script>
</body>
</html>
'''
    os.makedirs("dist", exist_ok=True)
    with open("dist/index.html", "w") as f:
        f.write(page)
    print("dist/index.html")

if __name__ == "__main__":
    build()
