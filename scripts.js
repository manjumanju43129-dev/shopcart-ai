/* MyShop E-commerce Frontend
   - Fetch products from /api/products and categories from /api/categories
   - Uses JWT (localStorage.access_token) for authenticated cart/checkout
   - Falls back to localStorage for unauthenticated users
   - Product detail modal with reviews from /api/reviews (if ASIN present)
*/

console.log('=== MyShop Loading ===');
console.log('Current URL:', window.location.href);
console.log('Hostname:', window.location.hostname);
console.log('Port:', window.location.port);
console.log('Protocol:', window.location.protocol);

// Check if loading from file:// protocol
if (window.location.protocol === 'file:') {
  console.error('ERROR: MyShop must be accessed through HTTP server!');
  const errorDiv = document.createElement('div');
  errorDiv.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:99999;';
  errorDiv.innerHTML = `
    <div style="background:white;padding:30px;border-radius:10px;text-align:center;max-width:500px;">
      <h1 style="color:#FF6B6B;margin-top:0;">❌ Configuration Error</h1>
      <p style="font-size:16px;color:#333;">MyShop must be accessed through the Flask server, not as a local file.</p>
      <p style="font-size:14px;color:#666;margin:20px 0;">You're currently accessing:<br/><code style="background:#f0f0f0;padding:10px;border-radius:5px;display:block;word-break:break-all;">${window.location.href}</code></p>
      <p style="font-size:14px;color:#666;"><strong>Please use one of these URLs instead:</strong></p>
      <ul style="text-align:left;display:inline-block;color:#0066cc;font-weight:bold;">
        <li><code style="background:#f0f0f0;padding:5px;border-radius:3px;">http://localhost:10000</code></li>
        <li><code style="background:#f0f0f0;padding:5px;border-radius:3px;">http://127.0.0.1:10000</code></li>
        <li><code style="background:#f0f0f0;padding:5px;border-radius:3px;">http://192.168.1.10:10000</code></li>
      </ul>
      <p style="font-size:12px;color:#999;margin-top:20px;">Make sure the Flask server is running on port 10000</p>
    </div>
  `;
  document.body.appendChild(errorDiv);
  throw new Error('MyShop must be accessed via HTTP, not file://');
}

let products = [];
let categories = [];
let localCart = JSON.parse(localStorage.getItem('localbite_cart') || '{}');

function getAuthToken(){ return localStorage.getItem('access_token') }

async function fetchProducts(){
  try{
    console.log('Fetching products from /api/products...');
    const resp = await fetch('/api/products');
    console.log('Response status:', resp.status);
    console.log('Response headers:', {
      'content-type': resp.headers.get('content-type'),
      'access-control-allow-origin': resp.headers.get('access-control-allow-origin')
    });
    
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
    }
    
    const text = await resp.text();
    console.log('Response length:', text.length, 'bytes');
    
    products = JSON.parse(text);
    console.log('Products loaded:', products.length);
    
    // Add visible indicator showing products were loaded
    const indicator = document.createElement('div');
    indicator.style.cssText = 'position:fixed;bottom:10px;right:10px;background:#2874F0;color:white;padding:10px 15px;border-radius:5px;font-size:12px;z-index:9999;font-weight:bold;';
    indicator.textContent = `✅ ${products.length} products loaded`;
    document.body.appendChild(indicator);
    
    renderProducts();
    console.log('Products rendered');
  }catch(e){ 
    console.error('failed to fetch products:', e.message, e);
    const errorIndicator = document.createElement('div');
    errorIndicator.style.cssText = 'position:fixed;bottom:10px;right:10px;background:#FF6B6B;color:white;padding:10px 15px;border-radius:5px;font-size:12px;z-index:9999;max-width:300px;';
    errorIndicator.innerHTML = `❌ Error: ${e.message}<br/><small>Check browser console for details</small>`;
    document.body.appendChild(errorIndicator);
  }
}

async function fetchCategories(){
  try{
    const resp = await fetch('/api/categories');
    categories = await resp.json();
    renderCategories();
  }catch(e){ /* ignore */ }
}

// Render categories as filter buttons
function renderCategories() {
  const container = document.getElementById('categories');
  if (!container) return;
  container.innerHTML = '';
  categories.forEach(c => {
    const d = document.createElement('div');
    d.className = 'cat-item';
    d.textContent = c.name;
    d.onclick = () => {
      document.querySelectorAll('.cat-item').forEach(x => x.style.opacity = '0.6');
      d.style.opacity = '1';
      filterByCategory(c.id);
    };
    container.appendChild(d);
  });
}

let activeCategory = null;
function filterByCategory(catId) {
  activeCategory = activeCategory === catId ? null : catId;
  renderProducts(document.getElementById('search').value);
}

// Render product grid with search and category filter
function renderProducts(q = '') {
  console.log('renderProducts called with query:', q);
  const root = document.getElementById('restaurants');
  console.log('Root container:', root);
  if (!root) {
    console.error('ERROR: #restaurants container not found!');
    return;
  }
  root.innerHTML = '';
  const query = (q || '').trim().toLowerCase();
  const list = products.filter(p => {
    if (activeCategory && p.category_id !== activeCategory) return false;
    if (!query) return true;
    return p.name.toLowerCase().includes(query) || (p.description || '').toLowerCase().includes(query);
  });
  console.log('Filtered products:', list.length);
  list.forEach(p => {
    const card = document.createElement('article');
    card.className = 'card';
    const discountPct = p.discount_price ? Math.round(((p.price - p.discount_price) / p.price) * 100) : 0;
    const priceHtml = p.discount_price
      ? `<div style="display:flex;align-items:center;gap:8px"><span class="price">₹${p.discount_price}</span><span class="old-price">₹${p.price}</span><span class="discount">${discountPct}% OFF</span></div>`
      : `<div class="price">₹${p.price}</div>`;
    card.innerHTML = `
      <img loading="lazy" src="${p.image_url || 'o2_featured_v2.avif'}" alt="${p.name}" />
      <div class="meta">
        <div>
          <div style="font-weight:800;margin-bottom:4px">${p.name}</div>
          <div class="desc">${(p.description || '').slice(0, 60)}</div>
        </div>
        <div class="badge">${(p.rating || 0).toFixed(1)}★</div>
      </div>
      ${priceHtml}
      <button class="add-btn" data-id="${p.id}">Add to Cart</button>
    `;
    // Open product detail on card click (not on button click)
    card.onclick = (e) => {
      if (e.target && e.target.classList && e.target.classList.contains('add-btn')) return;
      openProductDetails(p.id);
    };
    root.appendChild(card);
  });
  // Wire all add-to-cart buttons
  document.querySelectorAll('.add-btn').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      await addToCartApi(id, 1);
      updateCartCount();
      btn.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.04)' }, { transform: 'scale(1)' }], { duration: 160 });
    };
  });
  console.log('Rendered ' + list.length + ' product cards in grid');
}

async function addToCartApi(productId, qty=1){
  const token = getAuthToken();
  if(token){
    try{
      const resp = await fetch('/api/cart/add', {method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body: JSON.stringify({product_id:productId, quantity:qty})});
      if(resp.ok) return true;
    }catch(e){ console.warn('cart API failed', e) }
  }
  // fallback to local cart
  if(!localCart[productId]) localCart[productId] = {id: productId, qty:0};
  localCart[productId].qty += qty;
  localStorage.setItem('localbite_cart', JSON.stringify(localCart));
  return true;
}

// Update cart count badge
function updateCartCount() {
  const token = getAuthToken();
  if (token) {
    fetch('/api/cart', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(r => r.json())
      .then(data => {
        const count = (data.items || []).reduce((s, i) => s + (i.quantity || 0), 0);
        const el = document.getElementById('cartCount');
        if (el) el.textContent = count;
      })
      .catch(() => {});
  } else {
    const count = Object.values(localCart).reduce((s, i) => s + (i.qty || 0), 0);
    const el = document.getElementById('cartCount');
    if (el) el.textContent = count;
  }
}

// Render cart sidebar
function renderCart() {
  const container = document.getElementById('cartItems');
  if (!container) return;
  container.innerHTML = '';
  const token = getAuthToken();
  if (token) {
    fetch('/api/cart', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(r => r.json())
      .then(data => {
        const items = data.items || [];
        if (items.length === 0) {
          container.innerHTML = '<div style="padding:20px;color:var(--muted)">Cart is empty.</div>';
          updateTotals();
          return;
        }
        items.forEach(it => {
          const row = document.createElement('div');
          row.className = 'cart-row';
          row.innerHTML = `<div><div style="font-weight:700">${it.product?.name || '--'}</div></div><div style="text-align:right"><div>₹${((it.product?.price || 0) * it.quantity).toFixed(2)}</div></div>`;
          container.appendChild(row);
        });
        updateTotals();
      })
      .catch(() => { container.innerHTML = '<div style="padding:20px;color:var(--muted)">Cart unavailable.</div>'; });
  } else {
    const ids = Object.keys(localCart || {});
    if (ids.length === 0) {
      container.innerHTML = '<div style="padding:20px;color:var(--muted)">Cart is empty.</div>';
      updateTotals();
      return;
    }
    ids.forEach(pid => {
      const qty = localCart[pid].qty;
      const p = products.find(x => x.id == pid) || { name: 'Unknown', price: 0 };
      const row = document.createElement('div');
      row.className = 'cart-row';
      row.innerHTML = `<div><div style="font-weight:700">${p.name}</div></div><div style="text-align:right"><div>₹${(p.price * qty).toFixed(2)}</div></div>`;
      container.appendChild(row);
    });
    updateTotals();
  }
}

// Update cart totals (subtotal, tax, total)
function updateTotals() {
  const token = getAuthToken();
  let subtotal = 0;
  if (token) {
    fetch('/api/cart', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(r => r.json())
      .then(data => {
        const items = data.items || [];
        subtotal = items.reduce((s, i) => s + ((i.product?.price || 0) * i.quantity), 0);
        const tax = Math.round(subtotal * 0.05 * 100) / 100;
        const total = subtotal + tax;
        const el1 = document.getElementById('subtotal');
        const el2 = document.getElementById('tax');
        const el3 = document.getElementById('total');
        if (el1) el1.textContent = '₹' + subtotal.toFixed(2);
        if (el2) el2.textContent = '₹' + tax.toFixed(2);
        if (el3) el3.textContent = '₹' + total.toFixed(2);
      })
      .catch(() => {});
  } else {
    const ids = Object.keys(localCart || {});
    ids.forEach(pid => {
      const qty = localCart[pid].qty;
      const p = products.find(x => x.id == pid) || { price: 0 };
      subtotal += (p.price * qty);
    });
    const tax = Math.round(subtotal * 0.05 * 100) / 100;
    const total = subtotal + tax;
    const el1 = document.getElementById('subtotal');
    const el2 = document.getElementById('tax');
    const el3 = document.getElementById('total');
    if (el1) el1.textContent = '₹' + subtotal.toFixed(2);
    if (el2) el2.textContent = '₹' + tax.toFixed(2);
    if (el3) el3.textContent = '₹' + total.toFixed(2);
  }
}

// Toggle cart sidebar
function toggleCart(force) {
  const sidebar = document.getElementById('cartSidebar');
  const isHidden = sidebar.classList.contains('hidden');
  const show = (typeof force === 'boolean') ? force : isHidden;
  if (show) sidebar.classList.remove('hidden');
  else sidebar.classList.add('hidden');
}

// Checkout: create order from cart
const checkoutBtn = document.getElementById('checkoutBtn');
if (checkoutBtn) {
  checkoutBtn.onclick = async () => {
    const token = getAuthToken();
    if (!token) {
      alert('Please sign in to checkout');
      return;
    }
    try {
      const resp = await fetch('/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ payment_method: 'online' })
      });
      const data = await resp.json();
      if (data.ok) {
        alert('Order placed! Invoice: ' + data.invoice);
        updateCartCount();
        renderCart();
        toggleCart(false);
      } else {
        alert('Checkout failed: ' + (data.error || 'Unknown error'));
      }
    } catch (e) {
      console.error(e);
      alert('Checkout error');
    }
  };
}

// Product detail modal
async function openProductDetails(id) {
  try {
    const resp = await fetch(`/api/products/${id}`);
    if (!resp.ok) { alert('Product not found'); return; }
    const p = await resp.json();
    document.getElementById('productTitle').textContent = p.name || 'Product';
    document.getElementById('productDetailImage').src = p.image_url || 'o2_featured_v2.avif';
    document.getElementById('productDetailDesc').textContent = p.description || '';
    const priceEl = document.getElementById('productDetailPrice');
    priceEl.textContent = p.discount_price ? `₹${p.discount_price} (was ₹${p.price})` : `₹${p.price}`;
    const modal = document.getElementById('productDetailModal');
    modal.classList.remove('hidden');
    const addBtn = document.getElementById('productAddBtn');
    addBtn.onclick = async () => {
      await addToCartApi(p.id, 1);
      updateCartCount();
      alert('Added to cart!');
    };
    // Fetch reviews
    const reviewsEl = document.getElementById('productReviews');
    reviewsEl.textContent = 'Loading reviews...';
    if (p.asin) {
      try {
        const r = await fetch(`/api/reviews?asin=${encodeURIComponent(p.asin)}`);
        const data = await r.json();
        if (data.ok && data.reviews) {
          const arr = data.reviews?.reviews || data.reviews || [];
          if (arr.length === 0) reviewsEl.textContent = 'No reviews available.';
          else reviewsEl.innerHTML = arr.map(rv => `<div style="margin-bottom:10px"><strong>${rv.title || rv.heading || rv.displayTitle || 'Review'}</strong><div style="font-size:0.95rem;color:var(--muted)">${rv.content || rv.reviewText || rv.review || ''}</div></div>`).join('\n');
        } else {
          reviewsEl.textContent = data.error || 'Unable to fetch reviews.';
        }
      } catch (e) { reviewsEl.textContent = 'Reviews unavailable'; }
    } else {
      reviewsEl.textContent = 'No reviews data available for this product.';
    }
  } catch (e) { console.error(e); alert('Failed to load product'); }
}

// Event listeners on page ready
const closeProductDetailBtn = document.getElementById('closeProductDetail');
if (closeProductDetailBtn) {
  closeProductDetailBtn.onclick = () => {
    const m = document.getElementById('productDetailModal');
    if (m) m.classList.add('hidden');
  };
}

const searchBtn = document.getElementById('searchBtn');
if (searchBtn) {
  searchBtn.onclick = () => {
    renderProducts(document.getElementById('search').value);
  };
}

const search = document.getElementById('search');
if (search) {
  search.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('searchBtn').click();
  });
}

const cartToggle = document.getElementById('cartToggle');
if (cartToggle) {
  cartToggle.onclick = () => toggleCart();
}

const closeCart = document.getElementById('closeCart');
if (closeCart) {
  closeCart.onclick = () => toggleCart(false);
}

// Close modals on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const pm = document.getElementById('productDetailModal');
    const cs = document.getElementById('cartSidebar');
    if (pm) pm.classList.add('hidden');
    if (cs) cs.classList.add('hidden');
  }
});

// Admin mode (Ctrl+Shift+Z)
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && e.key && e.key.toLowerCase() === 'z') {
    e.preventDefault();
    const adminBtn = document.getElementById('adminControlBtn');
    const adminPanel = document.getElementById('adminPanelStatic');
    const isNow = document.body.classList.toggle('admin-mode');
    if (adminBtn) {
      adminBtn.classList.toggle('hidden', !isNow);
      adminBtn.setAttribute('aria-hidden', (!isNow).toString());
    }
    if (adminPanel) {
      adminPanel.classList.toggle('hidden', !isNow);
    }
    console.log('Admin mode:', isNow);
  }
});

// WSAD scrolling
document.addEventListener('keydown', (e) => {
  const key = (e.key || '').toLowerCase();
  const scrollAmount = 120;
  if (['w', 'a', 's', 'd'].includes(key)) {
    if (!e.ctrlKey && !e.altKey && !e.metaKey) {
      e.preventDefault();
      if (key === 'w') window.scrollBy({ top: -scrollAmount, behavior: 'smooth' });
      if (key === 's') window.scrollBy({ top: scrollAmount, behavior: 'smooth' });
      if (key === 'a') window.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
      if (key === 'd') window.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  }
});

// Page load initialization
window.addEventListener('load', () => {
  console.log('Page loaded, initializing...');
  
  // Show diagnostic info
  const diag = document.createElement('div');
  diag.style.cssText = 'position:fixed;top:10px;right:10px;background:#f0f0f0;color:#000;padding:10px;border-radius:5px;font-size:10px;z-index:99999;max-width:300px;border:1px solid #ccc;';
  diag.innerHTML = `
    <strong>My Shop Diagnostics</strong><br/>
    URL: ${window.location.href}<br/>
    API: /api/products<br/>
    Status: <span id="diagStatus">Loading...</span>
  `;
  document.body.appendChild(diag);
  
  const brand = document.getElementById('brand');
  if (brand) {
    brand.animate([
      { transform: 'translateY(-6px)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ], { duration: 400, easing: 'ease-out' });
  }
  
  // Test the API first
  fetch('/api/test').then(r => r.json()).then(data => {
    document.getElementById('diagStatus').textContent = `✅ API OK (${data.products} products)`;
    document.getElementById('diagStatus').style.color = 'green';
  }).catch(err => {
    document.getElementById('diagStatus').textContent = `❌ API Error: ${err.message}`;
    document.getElementById('diagStatus').style.color = 'red';
  });
  
  fetchCategories();
  fetchProducts();
  updateCartCount();
  renderCart();
});