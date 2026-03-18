---
layout: page
title: News
lead: "Announcements, milestones, and project updates."
permalink: /news/
---
{% comment %}
====== COMMENTED OUT — uncomment when news is updated ======
{% assign news_items = site.news | sort: "date" | reverse %}
{% if news_items.size > 0 %}
<div class="grid grid-2">
  {% for item in news_items %}
  <article class="card">
    <h2><a href="{{ item.url | relative_url }}">{{ item.title }}</a></h2>
    <p class="meta">{{ item.date | date: "%B %d, %Y" }}</p>
    {% if item.summary %}
    <p>{{ item.summary }}</p>
    {% endif %}
    <p><a href="{{ item.url | relative_url }}">Read full update</a></p>
  </article>
  {% endfor %}
</div>
{% else %}
<p>No news published yet.</p>
{% endif %}
====== END COMMENTED OUT ======
{% endcomment %}

<p>No news published yet.</p>
