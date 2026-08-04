document.addEventListener("DOMContentLoaded", function () {
renderNav("bookings");

const listEl = document.getElementById("bookings-list");

const SEAT_CATEGORY_LABELS = { standart: "Standard", comfort: "Comfort", vip: "VIP" };

const STATUS_PILL = {
  draft: "pending",
  confirmed: "pending",
  paid: "free",
  cancelled: "busy",
  expired: "busy",
};

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function fmtDateTime(iso) {
  if (!iso) return "—";
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

function bookingCard(booking) {
  const ss = booking.seat_session || {};
  const seat = ss.seat || {};
  const eventSession = ss.event_session || {};
  const event = eventSession.event || {};
  const pillKind = STATUS_PILL[booking.status] || "neutral";
  const canAct = booking.status === "draft" || booking.status === "confirmed";

  return `
    <div class="ticket booking-card" data-booking-id="${booking.id}">
      <div class="ticket__body">
        <p class="ticket__kicker">
          <span class="pill pill--${pillKind}">${escapeHtml(booking.status)}</span>
        </p>
        <h3 class="ticket__title">${escapeHtml(event.name || "Event")}</h3>
        <div class="ticket__meta">
          <span><b>${fmtDateTime(eventSession.timestamp)}</b></span>
          <span>Seat ${escapeHtml(seat.number ?? "—")}</span>
          <span>${SEAT_CATEGORY_LABELS[seat.category] || seat.category || ""}</span>
        </div>
        ${canAct ? `
          <div class="tr-panel__actions" style="flex-direction:row; margin-top:14px;">
            <button class="btn btn--pay btn--sm" data-action="pay">Pay now</button>
            <button class="btn btn--danger btn--sm" data-action="cancel">Cancel</button>
          </div>` : ""}
      </div>
      <div class="ticket__stub">
        <span class="ticket__code">BOOKING #${booking.id}</span>
        <div style="text-align:right;">
          <div class="ticket__seats" style="font-size:16px;">$${ss.price ?? booking.price ?? "—"}</div>
          <div class="ticket__seats-label">price</div>
        </div>
      </div>
    </div>
  `;
}

function renderBookings(bookings) {
  if (!Array.isArray(bookings) || bookings.length === 0) {
    listEl.innerHTML = `
      <div class="tr-empty-state">
        <h3>No tickets yet</h3>
        <p>Once you hold a seat, it'll show up here.</p>
        <a class="btn" style="margin-top:16px;" href="index.html">Browse sessions</a>
      </div>`;
    return;
  }
  listEl.innerHTML = bookings.map(bookingCard).join("");

  listEl.querySelectorAll("[data-action='pay']").forEach((btn) =>
    btn.addEventListener("click", (e) => payBooking(e, btn))
  );
  listEl.querySelectorAll("[data-action='cancel']").forEach((btn) =>
    btn.addEventListener("click", (e) => cancelBooking(e, btn))
  );
}

async function loadBookings() {
  try {
    const data = await Api.myBookings();
    renderBookings(Array.isArray(data) ? data : data ? [data] : []);
  } catch (err) {
    if (err.status === 401 || err.status === 403) {
      listEl.innerHTML = `
        <div class="tr-empty-state">
          <h3>Sign in to see your tickets</h3>
          <p>Log in through the site to view and manage your bookings.</p>
        </div>`;
    } else {
      listEl.innerHTML = `
        <div class="tr-empty-state">
          <h3>Couldn't load your tickets</h3>
          <p>${escapeHtml(err.message || "Something went wrong.")}</p>
        </div>`;
    }
  }
}

async function payBooking(e, btn) {
  const card = btn.closest(".booking-card");
  const bookingId = Number(card.dataset.bookingId);
  btn.disabled = true;
  btn.textContent = "Processing…";
  try {
    const payRes = await Api.payBooking(bookingId);
    const paymentUrl = payRes && (payRes.payment_url || payRes.paymentUrl);
    const uuidMatch = paymentUrl && paymentUrl.match(
      /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
    );
    const paymentId = uuidMatch ? uuidMatch[0] : (payRes && payRes.payment_id);
    if (paymentId) await Api.confirmPayment(paymentId, "success");
    showToast("Payment confirmed.", "success");
    loadBookings();
  } catch (err) {
    showToast(err.message || "Payment failed.", "error");
    btn.disabled = false;
    btn.textContent = "Pay now";
  }
}

async function cancelBooking(e, btn) {
  const card = btn.closest(".booking-card");
  const bookingId = Number(card.dataset.bookingId);
  btn.disabled = true;
  btn.textContent = "Cancelling…";
  try {
    await Api.cancelBooking(bookingId);
    showToast("Booking cancelled.");
    loadBookings();
  } catch (err) {
    showToast(err.message || "Could not cancel.", "error");
    btn.disabled = false;
    btn.textContent = "Cancel";
  }
}

loadBookings();
});