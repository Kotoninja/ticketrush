document.addEventListener("DOMContentLoaded", function () {
renderNav("home");

const listEl = document.getElementById("sessions-list");
const searchInput = document.getElementById("search-input");
const venueSelect = document.getElementById("venue-select");
const searchBtn = document.getElementById("search-btn");

const AGE_LABELS = { "0": "0+", "6": "6+", "12": "12+", "16": "16+", "18": "18+" };
const CATEGORY_LABELS = { theater: "Theater", cinema: "Cinema", other: "Other" };

function fmtDateTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      weekday: "short", day: "2-digit", month: "short",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function sessionCard(s) {
  const event = s.event || {};
  const hall = s.hall || {};
  return `
  <a class="ticket" href="/session/?id=${s.id}">
  <div class="ticket__body">
        <p class="ticket__kicker">${CATEGORY_LABELS[event.category] || event.category || "Event"} · ${AGE_LABELS[event.age_available] || ""}</p>
        <h3 class="ticket__title">${escapeHtml(event.name || "Untitled event")}</h3>
        <div class="ticket__meta">
          <span><b>${fmtDateTime(s.timestamp)}</b></span>
          <span>Hall ${escapeHtml(hall.name || hall.number || "—")}</span>
          <span>${event.duration ? escapeHtml(event.duration) : ""}</span>
        </div>
      </div>
      <div class="ticket__stub">
        <span class="ticket__code">SESSION #${s.id}</span>
        <div style="text-align:right;">
          <div class="ticket__seats">${s.seats_count ?? "—"}</div>
          <div class="ticket__seats-label">seats</div>
        </div>
      </div>
    </a>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function renderSessions(sessions) {
  if (!Array.isArray(sessions) || sessions.length === 0) {
    listEl.innerHTML = `
      <div class="tr-empty-state">
        <h3>No sessions found</h3>
        <p>Try a different search term or venue.</p>
      </div>`;
    return;
  }
  listEl.innerHTML = `<div class="tr-grid">${sessions.map(sessionCard).join("")}</div>`;
}

async function loadVenues() {
  try {
    const venues = await Api.venues();
    if (Array.isArray(venues)) {
      venueSelect.insertAdjacentHTML(
        "beforeend",
        venues.map((v) => `<option value="${v.id}">${escapeHtml(v.name)}</option>`).join("")
      );
    }
  } catch (err) {
    // Venue filter is a nice-to-have; fail silently.
    console.warn("Could not load venues", err);
  }
}

async function loadSessions() {
  listEl.innerHTML = `<p class="tr-skeleton">Loading sessions…</p>`;
  const venue = venueSelect.value || undefined;
  const search = searchInput.value.trim();
  try {
    const data = search
      ? await Api.sessionSearch(search, venue)
      : await Api.sessions(venue);
    renderSessions(Array.isArray(data) ? data : data ? [data] : []);
  } catch (err) {
    listEl.innerHTML = `
      <div class="tr-empty-state">
        <h3>Couldn't load sessions</h3>
        <p>${escapeHtml(err.message || "Something went wrong.")}</p>
      </div>`;
  }
}

searchBtn.addEventListener("click", loadSessions);
searchInput.addEventListener("keydown", (e) => { if (e.key === "Enter") loadSessions(); });
venueSelect.addEventListener("change", loadSessions);

loadVenues();
loadSessions();
});