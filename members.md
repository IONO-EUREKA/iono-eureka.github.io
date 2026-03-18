---
layout: page
title: Members
lead: "GO-EUREKA is a collaborative effort involving institutions across Europe and beyond."
permalink: /members/
uses_leaflet: true
---
<section class="member-map-panel card">
  <h2>Global Institution Map</h2>
  <p>Interactive pins show participating institutions by location.</p>
  <div id="member-map" class="member-map" aria-label="World map with institution locations"></div>
  <noscript>
    <p>Map interaction requires JavaScript. The institution list below remains fully available.</p>
  </noscript>
</section>

<section class="section-tight">
  <h2>Institution Directory</h2>
  <div id="member-list" class="grid grid-2">
    {% for member in site.data.members %}
    {% capture location_label %}{{ member.city | default: "" }}{% if member.city %}, {% endif %}{{ member.country }}{% endcapture %}
    <article
      id="{{ member.id }}"
      class="card member-card"
      data-member-id="{{ member.id }}"
      data-lat="{{ member.lat }}"
      data-lon="{{ member.lon }}"
      data-popup-subtitle="{{ location_label | strip }}"
      tabindex="-1"
    >
      <h3>{{ member.name }}</h3>
      <p>{{ location_label | strip }}</p>
      <button class="button button-subtle member-focus" type="button" data-focus-id="{{ member.id }}">
        Highlight institution on map
      </button>
    </article>
    {% endfor %}
  </div>
</section>
