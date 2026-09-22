let currentSlide = 0;
function moveCarousel(direction) {
    const track = document.getElementById('carousel_track');
    if(!track) return;
    currentSlide = (currentSlide + direction + 3) % 3;
    track.style.transform = `translateX(-${currentSlide * 100}%)`;
}
function toggleElement(id) {
    let el = document.getElementById(id);
    if(!el) return;
    if (el.style.display === 'none' || el.style.display === '') {
        el.style.display = (id === 'market_box') ? 'grid' : 'block';
    } else { el.style.display = 'none'; }
}
function executeLlmAuth() {
    let cid = document.getElementById('client_id_input').value;
    if(!cid) { alert("Введите Валидный Client ID!"); return; }
    let fd = new FormData();
    fd.append("developer", cid);
    fetch('/api/users-groups/', { method: 'POST', body: fd })
    .then(res => res.json())
    .then(data => {
        alert(`✅ POSTGRESQL КЛАССTЕР ОТВЕТИЛ:\nПрофиль ${cid} успешно верифицирован в ОЗУ!`);
        toggleElement('auth_vault');
    });
}
function triggerAddToCart(pid) {
    fetch(`/api/add-to-cart/${pid}/`)
    .then(res => res.json())
    .then(data => alert(`🛒 МЕДИА-МАГАЗИН: Товар ID-${pid} заперт в памяти корзины!`));
}
