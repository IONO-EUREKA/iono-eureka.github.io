(function () {
  function parseJsonScript(id, fallback) {
    var node = document.getElementById(id);
    if (!node || !node.textContent) return fallback;
    try {
      return JSON.parse(node.textContent);
    } catch (err) {
      return fallback;
    }
  }

  function uniqueSorted(values) {
    return Array.from(new Set(values.filter(Boolean))).sort(function (a, b) {
      return String(a).localeCompare(String(b));
    });
  }

  function normalizeFeatured(featured) {
    return (featured || []).map(function (item) {
      return {
        name: item.repo || "",
        html_url: "https://github.com/" + item.repo,
        description: item.summary || "",
        language: "",
        topics: item.tags || [],
        stargazers_count: 0,
        updated_at: "",
        archived: false
      };
    });
  }

  function mergeDedup(primary, secondary) {
    var index = {};
    var merged = [];
    (primary || []).forEach(function (repo) {
      if (!repo || !repo.name || index[repo.name]) return;
      index[repo.name] = true;
      merged.push(repo);
    });
    (secondary || []).forEach(function (repo) {
      if (!repo || !repo.name || index[repo.name]) return;
      index[repo.name] = true;
      merged.push(repo);
    });
    return merged;
  }

  function makeCard(repo) {
    var article = document.createElement("article");
    article.className = "card";

    var title = document.createElement("h3");
    var link = document.createElement("a");
    link.href = repo.html_url;
    link.textContent = repo.name;
    title.appendChild(link);
    article.appendChild(title);

    if (repo.description) {
      var desc = document.createElement("p");
      desc.textContent = repo.description;
      article.appendChild(desc);
    }

    var meta = document.createElement("p");
    meta.className = "meta";
    var language = repo.language || "Unspecified";
    var stars = typeof repo.stargazers_count === "number" ? repo.stargazers_count : 0;
    var updated = repo.updated_at ? new Date(repo.updated_at).toISOString().slice(0, 10) : "unknown";
    meta.textContent = "Language: " + language + " | Stars: " + stars + " | Updated: " + updated;
    article.appendChild(meta);

    if (Array.isArray(repo.topics) && repo.topics.length > 0) {
      var topics = document.createElement("p");
      topics.className = "meta";
      topics.textContent = "Topics: " + repo.topics.join(", ");
      article.appendChild(topics);
    }

    return article;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var results = document.getElementById("repo-browser-results");
    if (!results) return;

    var featured = normalizeFeatured(parseJsonScript("repos-featured-data", []));
    var live = parseJsonScript("repos-live-data", []);
    var allRepos = mergeDedup(featured, live).filter(function (repo) {
      return !repo.archived;
    });

    var languageFilter = document.getElementById("repo-language-filter");
    var topicFilter = document.getElementById("repo-topic-filter");
    var sortControl = document.getElementById("repo-sort");

    uniqueSorted(
      allRepos.map(function (repo) {
        return repo.language;
      })
    ).forEach(function (language) {
      var option = document.createElement("option");
      option.value = language;
      option.textContent = language;
      languageFilter.appendChild(option);
    });

    uniqueSorted(
      allRepos.flatMap(function (repo) {
        return Array.isArray(repo.topics) ? repo.topics : [];
      })
    ).forEach(function (topic) {
      var option = document.createElement("option");
      option.value = topic;
      option.textContent = topic;
      topicFilter.appendChild(option);
    });

    function render() {
      var selectedLanguage = languageFilter.value;
      var selectedTopic = topicFilter.value;
      var selectedSort = sortControl.value;

      var filtered = allRepos.filter(function (repo) {
        var langOk = !selectedLanguage || repo.language === selectedLanguage;
        var topicOk = !selectedTopic || (Array.isArray(repo.topics) && repo.topics.indexOf(selectedTopic) >= 0);
        return langOk && topicOk;
      });

      filtered.sort(function (a, b) {
        if (selectedSort === "stars") {
          return (b.stargazers_count || 0) - (a.stargazers_count || 0);
        }
        if (selectedSort === "name") {
          return String(a.name).localeCompare(String(b.name));
        }
        return new Date(b.updated_at || 0).getTime() - new Date(a.updated_at || 0).getTime();
      });

      results.innerHTML = "";
      if (filtered.length === 0) {
        var empty = document.createElement("p");
        empty.textContent = "No repositories match the selected filters.";
        results.appendChild(empty);
        return;
      }

      filtered.forEach(function (repo) {
        results.appendChild(makeCard(repo));
      });
    }

    languageFilter.addEventListener("change", render);
    topicFilter.addEventListener("change", render);
    sortControl.addEventListener("change", render);
    render();
  });
})();
