---
layout: page
title: Events
lead: "Workshops, meetings, and collaborative sessions."
permalink: /events/
---
{% assign event_items = site.events | sort: "date" | reverse %}
{% if event_items.size > 0 %}
<div class="grid grid-2">
  {% for event in event_items %}
  <article class="card">
    <h2><a href="{{ event.url | relative_url }}">{{ event.title }}</a></h2>
    {% if event.display_date %}
    <p class="meta">{{ event.display_date }}</p>
    {% else %}
    <p class="meta">{{ event.date | date: "%B %d, %Y" }}</p>
    {% endif %}
    {% if event.location %}
    <p class="meta">Location: {{ event.location }}</p>
    {% endif %}
    {% if event.summary %}
    <p>{{ event.summary }}</p>
    {% endif %}
    {% if event.external_url %}
    <p><a href="{{ event.external_url }}">External link</a></p>
    {% endif %}
    <p><a href="{{ event.url | relative_url }}">Read event details</a></p>
  </article>
  {% endfor %}
</div>
{% else %}
<p>No events published yet.</p>
{% endif %}
