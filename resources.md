---
layout: page
title: Resources
lead: "Public references, tools, and repository activity."
permalink: /resources/
uses_repo_browser: true
---
<section class="section-tight">
  <h2>Related Publications</h2>
  {% assign pubs = site.data.publications | sort: "year" | reverse %}
  {% assign pub_preview = pubs | slice: 0, 1 %}
  {% assign pub_rest    = pubs | slice: 1, pubs.size %}
  <div class="pub-list">
    {% for pub in pub_preview %}
    <div class="pub-item">
      <p class="pub-title">
        {% if pub.year %}<span class="pub-year">({{ pub.year }})</span>{% endif %}
        {% if pub.doi %}
          <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">{{ pub.title }}</a>
        {% else %}
          {{ pub.title }}
        {% endif %}
      </p>
    </div>
    {% endfor %}
    {% if pub_rest.size > 0 %}
    <details class="pub-more">
      <summary>Show all {{ pubs.size }} publications</summary>
      {% for pub in pub_rest %}
      <div class="pub-item">
        <p class="pub-title">
          {% if pub.year %}<span class="pub-year">({{ pub.year }})</span>{% endif %}
          {% if pub.doi %}
            <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">{{ pub.title }}</a>
          {% else %}
            {{ pub.title }}
          {% endif %}
        </p>
      </div>
      {% endfor %}
    </details>
    {% endif %}
  </div>
</section>

{% comment %}
====== COMMENTED OUT — uncomment when content is ready ======

<section class="section-tight">
  <h2>Public Resources</h2>
  <div class="grid grid-2">
    {% for resource in site.data.resources %}
    <article class="card">
      <p class="eyebrow">{{ resource.type }}</p>
      <h3><a href="{{ resource.url }}">{{ resource.title }}</a></h3>
      <p>{{ resource.description }}</p>
    </article>
    {% endfor %}
  </div>
</section>

<section class="section-tight">
  <h2>Featured Repositories</h2>
  <div class="grid grid-2">
    {% assign featured = site.data.repos_featured | sort: "priority" %}
    {% for repo in featured %}
    <article class="card">
      <h3><a href="https://github.com/{{ repo.repo }}">{{ repo.display_name }}</a></h3>
      <p>{{ repo.summary }}</p>
      <p class="meta">Tags: {{ repo.tags | join: ", " }}</p>
    </article>
    {% endfor %}
  </div>
</section>

<section class="section-tight">
  <h2>Repository Activity</h2>
  <p class="meta">
    Live data source last updated:
    <span id="repo-last-updated">{{ site.data.repos_live.generated_at | default: "Not available" }}</span>
  </p>
  <div class="repo-controls card">
    <label for="repo-language-filter">Language</label>
    <select id="repo-language-filter">
      <option value="">All</option>
    </select>
    <label for="repo-topic-filter">Topic</label>
    <select id="repo-topic-filter">
      <option value="">All</option>
    </select>
    <label for="repo-sort">Sort</label>
    <select id="repo-sort">
      <option value="updated">Recently updated</option>
      <option value="stars">Most stars</option>
      <option value="name">Name</option>
    </select>
  </div>
  <div id="repo-browser-results" class="grid grid-2" aria-live="polite"></div>
  <noscript>
    <p>Enable JavaScript for interactive filtering. Featured repositories remain visible above.</p>
  </noscript>
</section>

<script type="application/json" id="repos-featured-data">{{ site.data.repos_featured | jsonify }}</script>
<script type="application/json" id="repos-live-data">{{ site.data.repos_live.repos | default: empty | jsonify }}</script>

====== END COMMENTED OUT ======
{% endcomment %}
