(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function asNum(value) {
    var n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function focusCard(memberId) {
    var cards = document.querySelectorAll(".member-card");
    cards.forEach(function (card) {
      var active = card.dataset.memberId === memberId;
      card.classList.toggle("is-active", active);
      if (active) {
        card.focus({ preventScroll: false });
      }
    });
  }

  function initFocusButtons(markers, map) {
    var buttons = document.querySelectorAll(".member-focus");
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var id = button.getAttribute("data-focus-id");
        if (id && markers[id]) {
          markers[id].openPopup();
          map.panTo(markers[id].getLatLng());
          focusCard(id);
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var mapEl = byId("member-map");
    if (!mapEl || typeof L === "undefined") {
      return;
    }

    var map = L.map(mapEl, { worldCopyJump: true, minZoom: 1 }).setView([15, 10], 2);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var bounds = [];
    var markers = {};
    var cards = document.querySelectorAll(".member-card");
    cards.forEach(function (card) {
      var id = card.dataset.memberId;
      var lat = asNum(card.dataset.lat);
      var lon = asNum(card.dataset.lon);
      if (!id || lat === null || lon === null) {
        return;
      }

      var title = card.querySelector("h3") ? card.querySelector("h3").textContent.trim() : id;
      var subtitle = card.dataset.popupSubtitle ? card.dataset.popupSubtitle.trim() : "";
      var popupHtml = "<strong>" + title + "</strong>";
      if (subtitle) {
        popupHtml += "<br>" + subtitle;
      }

      var marker = L.marker([lat, lon]).addTo(map);
      marker.bindPopup(popupHtml);
      marker.on("click", function () {
        focusCard(id);
      });
      markers[id] = marker;
      bounds.push([lat, lon]);
    });

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [35, 35] });
    } else if (bounds.length === 1) {
      map.setView(bounds[0], 4);
    }

    initFocusButtons(markers, map);
  });
})();
