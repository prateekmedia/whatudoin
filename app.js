(function () {
  var view = document.getElementById("view");
  var tasksPath = document.body.getAttribute("data-tasks-path") || "./tasks.md";
  var state = {
    categories: {},
    topTasks: [],
    isFlat: false,
  };

  function slugify(value) {
    return value.trim().toLowerCase().replace(/\s+/g, "-");
  }

  function parseTask(text) {
    var match = text.match(/^\[(.+?)\]\((.+?)\)$/);
    if (match) {
      return { title: match[1], url: match[2] };
    }

    return { title: text, url: null };
  }

  function parseTasks(markdown) {
    var categories = {};
    var flat = [];
    var currentCategory = null;

    markdown.split(/\r?\n/).forEach(function (rawLine) {
      var line = rawLine.trim();

      if (line.startsWith("## ")) {
        currentCategory = line.slice(3).trim();
        categories[currentCategory] = [];
        return;
      }

      if (!line.startsWith("- ")) {
        return;
      }

      var task = parseTask(line.slice(2).trim());
      if (currentCategory) {
        categories[currentCategory].push(task);
      } else {
        flat.push(task);
      }
    });

    var categoryNames = Object.keys(categories);
    if (categoryNames.length === 0 && flat.length > 0) {
      return {
        categories: { _flat: flat },
        topTasks: [],
        isFlat: true,
      };
    }

    var sluggedCategories = {};
    categoryNames.forEach(function (name) {
      sluggedCategories[slugify(name)] = categories[name];
    });

    return {
      categories: sluggedCategories,
      topTasks: flat,
      isFlat: false,
    };
  }

  function esc(value) {
    var div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
  }

  function displayName(slug) {
    return slug
      .split("-")
      .filter(Boolean)
      .map(function (part) {
        return part.charAt(0).toUpperCase() + part.slice(1);
      })
      .join(" ");
  }

  function renderTasks(tasks) {
    return tasks
      .map(function (task) {
        if (task.url) {
          return '<a href="' + esc(task.url) + '" target="_blank" rel="noopener" class="item">' + esc(task.title) + "</a>";
        }

        return '<span class="item">' + esc(task.title) + "</span>";
      })
      .join("");
  }

  function setState(nextState) {
    state = nextState;
    render();
  }

  function renderError(message) {
    view.innerHTML = '<div class="status error">' + esc(message) + "</div>";
  }

  function renderLoading() {
    view.innerHTML = '<div class="status">Loading latest tasks...</div>';
  }

  function render() {
    var params = new URLSearchParams(window.location.search);
    var cat = params.get("cat");
    var categories = state.categories;
    var topTasks = state.topTasks;

    if (state.isFlat) {
      view.innerHTML = renderTasks(categories._flat || []);
      return;
    }

    if (cat && categories[cat]) {
      view.innerHTML =
        '<a class="cat-header" onclick="go(null)">' + esc(displayName(cat)) + "</a>" +
        renderTasks(categories[cat]);
      return;
    }

    var html = Object.keys(categories)
      .map(function (key) {
        return (
          '<span class="item cat" onclick="go(\'' + esc(key) + '\')">' +
          esc(displayName(key)) +
          ' <span class="count">(' +
          categories[key].length +
          ")</span></span>"
        );
      })
      .join("");

    html += renderTasks(topTasks);
    view.innerHTML = html;
  }

  window.go = function (cat) {
    var url = window.location.pathname;
    if (cat) {
      url += "?cat=" + encodeURIComponent(cat);
    }
    history.pushState(null, "", url);
    render();
  };

  function loadTasks() {
    renderLoading();

    fetch(tasksPath, { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Could not load " + tasksPath);
        }
        return response.text();
      })
      .then(function (markdown) {
        setState(parseTasks(markdown));
      })
      .catch(function () {
        renderError("Couldn't load tasks.md. Serve the repo root with python or GitHub Pages so this page can fetch the latest tasks.");
      });
  }

  window.addEventListener("popstate", render);
  loadTasks();
})();
