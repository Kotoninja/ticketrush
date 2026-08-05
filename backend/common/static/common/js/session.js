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

  let currentSeats = [];
  let selected = null;
  let activeBooking = null;
  let countdownTimer = null;
  let pollTimer = null;
  let wsConnection = null;
  let currentHallId = null;

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
    pollTimer = setInterval(loadSession, 60000); // Раз в минуту, т.к. WebSocket обновляет быстрее
  }

  function setupWebSocket(hallId) {
    if (wsConnection) {
      wsConnection.disconnect();
      wsConnection = null;
    }
    
    wsConnection = new SeatWebSocket(hallId);
    
    wsConnection.on('seatUpdate', (data) => {
      console.log('📨 WebSocket update:', data);
      
      // data.seat_id - это ID места (поле "seat" в нашем объекте)
      const seatSession = currentSeats.find(s => s.seat === data.seat_id);
      
      if (seatSession) {
        console.log(`🔄 Updating seat ${seatSession.seat}: ${seatSession.status} → ${data.status}`);
        seatSession.status = data.status;
        
        // Если это наше забронированное место и его освободили
        if (activeBooking && 
            activeBooking.seatSessionId === seatSession.id && 
            data.status === 'free') {
          showToast('Your held seat has been released', 'warning');
          clearInterval(countdownTimer);
          activeBooking = null;
          renderIdlePanel();
        }
        
        renderSeatMap();
      } else {
        console.warn('Seat not found for WebSocket update, reloading all');
        loadSession(true);
      }
    });
    
    wsConnection.on('connected', () => {
      console.log('✅ WebSocket connected');
    });
    
    wsConnection.connect();
  }

  async function loadSession(silent) {
    try {
      const data = await Api.sessionDetail(sessionId);
      const detail = Array.isArray(data) ? data[0] : data;
      if (!detail) throw new Error("Session not found");
      
      renderHeader(detail);
      
      // Сортируем места по номеру (поле "seat")
      currentSeats = (detail.seats || []).sort((a, b) => a.seat - b.seat);
      
      if (detail.hall && detail.hall.id) {
        if (!currentHallId || currentHallId !== detail.hall.id) {
          currentHallId = detail.hall.id;
          setupWebSocket(currentHallId);
        }
      }
      
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

  function seatButton(seatSession) {
    const status = seatSession.status;
    const isMine = activeBooking && activeBooking.seatSessionId === seatSession.id;
    const isSelected = selected && selected.seatSessionId === seatSession.id;
    const disabled = status !== "free" && !isMine;
    const classes = ["seat", `seat--${status}`];
    if (isMine || isSelected) classes.push("seat--mine");
    
    return `
      <button
        type="button"
        class="${classes.join(" ")}"
        data-seat-session-id="${seatSession.id}"
        data-seat-id="${seatSession.seat}"
        ${disabled ? "disabled" : ""}
        title="Seat #${seatSession.seat} · ${status}"
      >${seatSession.seat}</button>
    `;
  }

  function renderSeatMap() {
    if (!currentSeats.length) {
      seatMapEl.className = "";
      seatMapEl.innerHTML = `<p class="seat-map__empty">This session has no seats configured.</p>`;
      return;
    }

    // Группируем места по 10 в ряд для красивого отображения
    const seatsPerRow = 10;
    const rows = [];
    
    for (let i = 0; i < currentSeats.length; i += seatsPerRow) {
      const rowSeats = currentSeats.slice(i, i + seatsPerRow);
      const rowIndex = Math.floor(i / seatsPerRow);
      const amplitude = 3 + rowSeats.length * 0.55 + rowIndex * 0.6;
      const mid = (rowSeats.length - 1) / 2 || 1;
      
      const seatsHtml = rowSeats
        .map((seatSession, idx) => {
          const posRatio = mid ? (idx - mid) / mid : 0;
          const curveOffset = Math.round(amplitude * posRatio * posRatio);
          
          // Добавляем проход посередине для длинных рядов
          const withAisle = rowSeats.length > 7 && idx === Math.ceil(rowSeats.length / 2) - 1
            ? `<span class="theater-row__aisle"></span>`
            : "";
          
          return seatButton(seatSession) + withAisle;
        })
        .join("");

      rows.push(`
        <div class="theater-row">
          <span class="theater-row__label">${rowLabel(rowIndex)}</span>
          <div class="theater-row__seats">${seatsHtml}</div>
          <span class="theater-row__label">${rowLabel(rowIndex)}</span>
        </div>
      `);
    }

    seatMapEl.className = "theater";
    seatMapEl.innerHTML = rows.join('');

    seatMapEl.querySelectorAll(".seat").forEach((btn) => {
      btn.addEventListener("click", () => onSeatClick(Number(btn.dataset.seatSessionId)));
    });
  }

  function rowLabel(index) {
    let n = index, s = "";
    do {
      s = String.fromCharCode(65 + (n % 26)) + s;
      n = Math.floor(n / 26) - 1;
    } while (n >= 0);
    return s;
  }

  async function onSeatClick(seatSessionId) {
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
    // Ищем номер места в currentSeats
    const seatSession = currentSeats.find(s => s.id === selected.seatSessionId);
    const seatNumber = seatSession ? seatSession.seat : "—";
    
    panelEl.innerHTML = `
      <h3>Seat ${escapeHtml(seatNumber)}</h3>
      <div class="tr-panel__row"><span>Category</span><span>Standard</span></div>
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
    
    // Находим номер места
    const seatSession = currentSeats.find(s => s.id === activeBooking.seatSessionId);
    const seatNumber = seatSession ? seatSession.seat : "—";
    
    panelEl.innerHTML = `
      <h3>Seat ${escapeHtml(seatNumber)} held</h3>
      <div class="tr-panel__row"><span>Category</span><span>Standard</span></div>
      <div class="tr-panel__row"><span>Price</span><span class="tr-panel__price">$${seatSession ? seatSession.price : "—"}</span></div>
      <div class="tr-panel__row"><span>Status</span><span class="pill pill--pending">${activeBooking.status || 'pending'}</span></div>
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

  // Очистка при уходе со страницы
  window.addEventListener('beforeunload', () => {
    if (wsConnection) {
      wsConnection.disconnect();
    }
    clearInterval(pollTimer);
    clearInterval(countdownTimer);
  });
});