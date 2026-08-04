/** Small toast helper: showToast("Message", "success" | "error" | "") */
let toastTimer = null;
function showToast(message, kind = "") {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  el.className = "tr-toast is-visible" + (kind ? ` tr-toast--${kind}` : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.remove("is-visible");
  }, 3600);
}