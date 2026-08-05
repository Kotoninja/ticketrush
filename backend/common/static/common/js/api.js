/**
 * TicketRush — API layer
 * ------------------------------------------------------------
 * All calls go through django's session-cookie auth. Since this
 * front end is meant to be served by Django itself (same origin),
 * API_BASE is left empty. If you serve it from somewhere else,
 * set API_BASE to your Django host, e.g. "https://api.ticketrush.dev"
 * — and make sure CORS + CSRF trust that origin.
 */
const API_BASE = "";

/** Pull django's csrftoken cookie for unsafe methods (POST/PUT/PATCH/DELETE). */
function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

/**
 * Thin wrapper around fetch():
 * - always sends/receives cookies (session auth)
 * - attaches CSRF token on non-GET requests
 * - throws ApiError with status + parsed body on non-2xx responses
 * - returns null for empty (204 / no-body 200) responses
 */
async function apiFetch(path, { method = "GET", body, params } = {}) {
  let url = API_BASE + path;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    if (qs) url += (url.includes("?") ? "&" : "?") + qs;
  }

  const headers = {};
  let payload;
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrftoken = getCookie("csrftoken");
    if (csrftoken) headers["X-CSRFToken"] = csrftoken;
  }

  let res;
  try {
    res = await fetch(url, {
      method,
      headers,
      body: payload,
      credentials: "include",
    });
  } catch (networkErr) {
    throw new ApiError(0, "Could not reach the server. Check your connection.", null);
  }

  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Request failed (${res.status})`;
    throw new ApiError(res.status, message, data);
  }
  return data;
}

class ApiError extends Error {
  constructor(status, message, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

/* ----------------------------- endpoints ----------------------------- */

const Api = {
  // venues
  venues: () => apiFetch("/api/venue/"),

  // sessions
  sessions: (venue) => apiFetch("/api/session/", { params: { venue } }),
  sessionSearch: (search, venue) =>
    apiFetch("/api/session/search/", { params: { search, venue } }),
  sessionDetail: (id) => apiFetch(`/api/session/${id}/`),
  seatDetail: (eventSessionId, seatSessionId) =>
    apiFetch(`/api/session/seat/${eventSessionId}/${seatSessionId}`),

  // booking
  createBooking: (seatSessionId) =>
    apiFetch("/api/booking/", { method: "POST", body: { seat_session: seatSessionId } }),
  cancelBooking: (id) => apiFetch(`/api/booking/${id}/`, { method: "DELETE" }),
  payBooking: (id) => apiFetch(`/api/booking/${id}/pay/`, { method: "POST" }),
  myBookings: (venuePk) => apiFetch("/api/booking/list/", { params: { venue_pk: venuePk } }),
  bookingBySeatSession: (seatSessionPk) =>
    apiFetch(`/api/booking/session/${seatSessionPk}/`),

  // fake payment webhook
  confirmPayment: (paymentId, result = "success") =>
    apiFetch("/api/payment/webhook/", { method: "POST", body: { payment_id: paymentId, result } }),
};