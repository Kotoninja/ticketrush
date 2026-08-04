/**
 * Renders the shared navbar into <div id="site-nav"></div>.
 * Pass the current page key ("home" | "bookings") to highlight it.
 */
function renderNav(active) {
  const mount = document.getElementById("site-nav");
  if (!mount) return;

  mount.innerHTML = `
    <nav class="tr-nav">
      <div class="tr-nav__inner">
        <a class="tr-nav__logo" href="/">
          <span class="tr-nav__logo-mark">TR</span>
          <span class="tr-nav__logo-text">TICKET<em>RUSH</em></span>
        </a>

        <div class="tr-nav__links">
          <a href="/" class="tr-nav__link ${active === "home" ? "is-active" : ""}">Events</a>
          <a href="/bookings/" class="tr-nav__link ${active === "bookings" ? "is-active" : ""}">My tickets</a>
        </div>

        <button type="button" class="tr-nav__user" id="nav-user-btn" aria-label="My account">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="8" r="3.5"/>
            <path d="M4.5 20c1.6-3.6 4.6-5.5 7.5-5.5s5.9 1.9 7.5 5.5"/>
          </svg>
          <span>Account</span>
        </button>
      </div>
    </nav>
  `;

  const userBtn = document.getElementById("nav-user-btn");
  if (userBtn) {
    userBtn.addEventListener("click", () => {
      window.location.href = "/bookings/";
    });
  }
}