#!/usr/bin/env python3
"""Writes the dynamic dist/index.html wrapper used by the static site.

The site itself now loads tasks.md at runtime, so this script is optional and
kept only as a compatibility helper.
"""

from pathlib import Path


DIST_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>what u doin?</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body data-tasks-path="../tasks.md">
  <div class="container">
    <h1><img src="https://media.giphy.com/media/WUlplcMpOCEmTGBtBW/giphy.gif" alt="">Working on</h1>
    <div id="view" class="tasks"></div>
  </div>
  <script src="../app.js"></script>
</body>
</html>
"""


def build() -> None:
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    output = dist_dir / "index.html"
    output.write_text(DIST_INDEX, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    build()
