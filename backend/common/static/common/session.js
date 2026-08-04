document.addEventListener("DOMContentLoaded", function () {
renderNav("home");

const params = new URLSearchParams(window.location.search);
const sessionId = params.get("id");

const eventNameEl = document.getElementById("event-name");
const sessionMetaEl = document.getElementById("session-meta");
const seatMapEl = document.getElementById("seat-map");
const panelEl = document.getElementById("booking-panel");

const AGE_LABELS = { "0": "0+", "6": "6+", "12": "12+", "16": "16+", "18": "18+" };
const CATEGORY_LABELS = { theater: "Theater", cinema: "Cinema", other: "Other" };
const SEAT_CATEGORY_LABELS = { standart: "Standard", comfort: "Comfort", vip: "VIP" };

let currentSeats = [];          // seat_session list from the session detail call
let selected = null;            // { seatSessionId, detail } while choosing a seat
let activeBooking = null;       // { id, seatSessionId, draft_expire_time }
let countdownTimer = null;
let pollTimer = null;

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

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

if (!sessionId) {
  eventNameEl.textContent = "No session selected";
  sessionMetaEl.textContent = "";
  seatMapEl.innerHTML = `<p class="seat-map__empty">Go back and pick a session from the list.</p>`;
} else {
  init();
}

async function init() {
  await loadSession();
  pollTimer = setInterval(loadSession, 20000); // fetch-based refresh, no websocket needed
}

async function loadSession(silent) {
  try {
    const data = await Api.sessionDetail(sessionId);
    const detail = Array.isArray(data) ? data[0] : data;
    if (!detail) throw new Error("Session not found");
    renderHeader(detail);
    currentSeats = detail.seats || [];
    renderSeatMap();
  } catch (err) {
    if (!silent) {
      eventNameEl.textContent = "Couldn't load this session";
      sessionMetaEl.textContent = err.message || "";
      seatMapEl.innerHTML = "";
    }
  }
}

function renderHeader(detail) {
  const event = detail.event || {};
  const hall = detail.hall || {};
  eventNameEl.textContent = event.name || "Untitled event";
  sessionMetaEl.innerHTML = `
    <span>${CATEGORY_LABELS[event.category] || event.category || ""}</span>
    <span>·</span>
    <span>${AGE_LABELS[event.age_available] || ""}</span>
    <span>·</span>
    <span><b>${fmtDateTime(detail.timestamp)}</b></span>
    <span>·</span>
    <span>Hall ${escapeHtml(hall.name || hall.number || "—")}</span>
  `;
}

/**
 * The API only returns a flat list of seat sessions (id, status, price,
 * seat id) — no row/column data. To still draw something that reads as
 * "a theater" rather than a grid, we chunk that flat list into rows that
 * widen towards the back (a fan shape) and curve each row towards the
 * stage, the way a real raked auditorium looks from above. It's an
 * approximation of the layout, not the venue's real seat map.
 */
function computeRowLengths(total) {
  if (total <= 6) return [total];
  const rowCount = Math.max(3, Math.min(11, Math.round(Math.sqrt(total / 1.3))));
  const base = Math.floor(total / rowCount);
  const remainder = total - base * rowCount;
  const lengths = new Array(rowCount).fill(base);
  for (let i = 0; i < remainder; i++) lengths[rowCount - 1 - i] += 1; // extra seats -> back rows

  // Fan effect: nudge a couple of seats from front rows to their mirrored
  // back row. This only transfers seats between rows, so the total is
  // always preserved exactly.
  const shift = Math.min(2, Math.floor(base / 4));
  for (let i = 0; i < Math.floor(rowCount / 2); i++) {
    const amt = shift - Math.floor(i / 2);
    if (amt <= 0) continue;
    if (lengths[i] - amt >= 3) {
      lengths[i] -= amt;
      lengths[rowCount - 1 - i] += amt;
    }
  }
  return lengths;
}

function seatButton(seatSession, label, curveOffset) {
  const status = seatSession.status; // free | pending | busy
  const isMine = activeBooking && activeBooking.seatSessionId === seatSession.id;
  const isSelected = selected && selected.seatSessionId === seatSession.id;
  const disabled = status !== "free" && !isMine;
  const classes = ["seat", `seat--${status}`];
  if (isMine || isSelected) classes.push("seat--mine");
  return `
    <button
      type="button"
      class="${classes.join(" ")}"
      style="transform: translateY(${curveOffset}px)"
      data-seat-session-id="${seatSession.id}"
      ${disabled ? "disabled" : ""}
      title="Seat session #${seatSession.id} · ${status}"
    >${label}</button>
  `;
}

function rowLabel(index) {
  // A, B, C … Z, AA, AB …
  let n = index, s = "";
  do {
    s = String.fromCharCode(65 + (n % 26)) + s;
    n = Math.floor(n / 26) - 1;
  } while (n >= 0);
  return s;
}

function renderSeatMap() {
  if (!currentSeats.length) {
    seatMapEl.className = "";
    seatMapEl.innerHTML = `<p class="seat-map__empty">This session has no seats configured.</p>`;
    return;
  }

  const rowLengths = computeRowLengths(currentSeats.length);
  let cursor = 0;
  let seatNumber = 0;

  const rowsHtml = rowLengths
    .map((len, rowIndex) => {
      const rowSeats = currentSeats.slice(cursor, cursor + len);
      cursor += len;
      // Curve amplitude grows for longer / further-back rows, bowing the
      // row ends away from the stage while the centre stays closest to it.
      const amplitude = 3 + len * 0.55 + rowIndex * 0.6;
      const mid = (rowSeats.length - 1) / 2 || 1;

      const seatsHtml = rowSeats
        .map((seatSession, i) => {
          seatNumber += 1;
          const posRatio = mid ? (i - mid) / mid : 0;
          const curveOffset = Math.round(amplitude * posRatio * posRatio);
          const withAisle =
            rowSeats.length > 7 && (i === Math.ceil(rowSeats.length / 2) - 1)
              ? `<span class="theater-row__aisle"></span>`
              : "";
          return seatButton(seatSession, seatNumber, curveOffset) + withAisle;
        })
        .join("");

      return `
        <div class="theater-row">
          <span class="theater-row__label">${rowLabel(rowIndex)}</span>
          <div class="theater-row__seats">${seatsHtml}</div>
          <span class="theater-row__label">${rowLabel(rowIndex)}</span>
        </div>
      `;
    })
    .join("");

  seatMapEl.className = "theater";
  seatMapEl.innerHTML = rowsHtml;

  seatMapEl.querySelectorAll(".seat").forEach((btn) => {
    btn.addEventListener("click", () => onSeatClick(Number(btn.dataset.seatSessionId)));
  });
}

async function onSeatClick(seatSessionId) {
  // Clicking the seat that's already mine just reopens the panel.
  if (activeBooking && activeBooking.seatSessionId === seatSessionId) {
    renderActiveBookingPanel();
    return;
  }
  panelEl.innerHTML = `<p class="tr-panel__empty">Loading seat details…</p>`;
  try {
    const detail = await Api.seatDetail(sessionId, seatSessionId);
    selected = { seatSessionId, detail };
    renderSeatMap();
    renderSelectionPanel();
  } catch (err) {
    showToast(err.message || "Couldn't load that seat.", "error");
    renderIdlePanel();
  }
}

function renderIdlePanel() {
  selected = null;
  renderSeatMap();
  panelEl.innerHTML = `
    <h3>Your seat</h3>
    <p class="tr-panel__empty">Tap any green seat in the map to hold it. You'll have 5 minutes to complete payment before it's released.</p>
  `;
}

function renderSelectionPanel() {
  const seat = selected.detail.seat || {};
  panelEl.innerHTML = `
    <h3>Seat ${escapeHtml(seat.number ?? "—")}</h3>
    <div class="tr-panel__row"><span>Category</span><span>${SEAT_CATEGORY_LABELS[seat.category] || seat.category || "—"}</span></div>
    <div class="tr-panel__row"><span>Price</span><span class="tr-panel__price">$${selected.detail.price ?? "—"}</span></div>
    <div class="tr-panel__actions">
      <button class="btn btn--block" id="reserve-btn">Hold this seat</button>
      <button class="btn btn--ghost btn--block" id="cancel-select-btn">Choose another</button>
    </div>
  `;
  document.getElementById("reserve-btn").addEventListener("click", reserveSeat);
  document.getElementById("cancel-select-btn").addEventListener("click", renderIdlePanel);
}

async function reserveSeat() {
  const btn = document.getElementById("reserve-btn");
  btn.disabled = true;
  btn.textContent = "Holding…";
  try {
    const booking = await Api.createBooking(selected.seatSessionId);
    activeBooking = {
      id: booking.id,
      seatSessionId: selected.seatSessionId,
      seatDetail: selected.detail,
      draftExpireTime: booking.draft_expire_time,
      status: booking.status,
    };
    selected = null;
    showToast("Seat held. Complete payment before the timer runs out.", "success");
    await loadSession(true);
    renderActiveBookingPanel();
  } catch (err) {
    showToast(err.message || "Could not reserve that seat.", "error");
    renderSelectionPanel();
  }
}

function renderActiveBookingPanel() {
  if (!activeBooking) return renderIdlePanel();
  const seat = activeBooking.seatDetail.seat || {};
  panelEl.innerHTML = `
    <h3>Seat ${escapeHtml(seat.number ?? "—")} held</h3>
    <div class="tr-panel__row"><span>Category</span><span>${SEAT_CATEGORY_LABELS[seat.category] || seat.category || "—"}</span></div>
    <div class="tr-panel__row"><span>Price</span><span class="tr-panel__price">$${activeBooking.seatDetail.price ?? "—"}</span></div>
    <div class="tr-panel__row"><span>Status</span><span class="pill pill--pending">${activeBooking.status}</span></div>
    <div class="tr-panel__actions">
      <button class="btn btn--pay btn--block" id="pay-btn">Pay now</button>
      <button class="btn btn--danger btn--block" id="cancel-btn">Cancel hold</button>
    </div>
    <p class="tr-panel__timer" id="panel-timer"></p>
  `;
  document.getElementById("pay-btn").addEventListener("click", payForBooking);
  document.getElementById("cancel-btn").addEventListener("click", cancelBooking);
  startCountdown();
}

function startCountdown() {
  clearInterval(countdownTimer);
  const timerEl = document.getElementById("panel-timer");
  if (!activeBooking.draftExpireTime || !timerEl) return;
  const expiry = new Date(activeBooking.draftExpireTime).getTime();
  countdownTimer = setInterval(() => {
    const remaining = Math.max(0, Math.floor((expiry - Date.now()) / 1000));
    const m = String(Math.floor(remaining / 60)).padStart(2, "0");
    const s = String(remaining % 60).padStart(2, "0");
    timerEl.textContent = remaining > 0 ? `Expires in ${m}:${s}` : "Hold expired — refreshing…";
    if (remaining <= 0) {
      clearInterval(countdownTimer);
      activeBooking = null;
      loadSession(true).then(renderIdlePanel);
    }
  }, 1000);
}

async function cancelBooking() {
  const btn = document.getElementById("cancel-btn");
  btn.disabled = true;
  btn.textContent = "Cancelling…";
  try {
    await Api.cancelBooking(activeBooking.id);
    clearInterval(countdownTimer);
    activeBooking = null;
    showToast("Hold cancelled.");
    await loadSession(true);
    renderIdlePanel();
  } catch (err) {
    showToast(err.message || "Could not cancel.", "error");
    btn.disabled = false;
    btn.textContent = "Cancel hold";
  }
}

async function payForBooking() {
  const btn = document.getElementById("pay-btn");
  btn.disabled = true;
  btn.textContent = "Processing…";
  try {
    const payRes = await Api.payBooking(activeBooking.id);
    // API is documented as returning a payment_url the client should
    // extract a UUID from and post to the fake bank webhook.
    const paymentUrl = payRes && (payRes.payment_url || payRes.paymentUrl);
    const uuidMatch = paymentUrl && paymentUrl.match(
      /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
    );
    const paymentId = uuidMatch ? uuidMatch[0] : (payRes && payRes.payment_id);

    if (paymentId) {
      await Api.confirmPayment(paymentId, "success");
    }

    clearInterval(countdownTimer);
    activeBooking = null;
    showToast("Payment confirmed — see it under My tickets.", "success");
    await loadSession(true);
    renderIdlePanel();
  } catch (err) {
    showToast(err.message || "Payment failed.", "error");
    btn.disabled = false;
    btn.textContent = "Pay now";
  }
}
});