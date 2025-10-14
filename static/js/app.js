async function addToCart(productId) {
  const res = await fetch(`/cart/add/${productId}`, {
    method: "POST",
    headers: {"X-CSRFToken": getCSRFToken()}
  });
  if (res.ok) {
    const data = await res.json();
    const badge = document.getElementById("cart-count");
    if (badge) badge.textContent = data.cart_count;
    showToast("Producto agregado al carrito");
  } else {
    showToast("No se pudo agregar el producto");
  }
}

function getCSRFToken() {
  const el = document.querySelector('meta[name="csrf-token"]');
  return el ? el.getAttribute("content") : "";
}

function showToast(msg) {
  const t = document.getElementById("liveToast");
  const b = document.getElementById("toast-body");
  if (!t || !b) return alert(msg);
  b.textContent = msg;
  const toast = new bootstrap.Toast(t);
  toast.show();
}