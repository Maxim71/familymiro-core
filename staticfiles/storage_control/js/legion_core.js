/* 🧠 ИГРОВОЙ ФОНОВЫЙ 3D-ПАРАЛЛАКС ДЛЯ МАКСИМА // БЕЗ ДЕРГАНИЯ КОНТЕНТА */
document.addEventListener('DOMContentLoaded', () => {
    const bgLayer = document.getElementById('parallax_bg_layer');
    if (bgLayer) {
        document.addEventListener('mousemove', (e) => {
            let moveX = (window.innerWidth / 2 - e.pageX) / 30;
            let moveY = (window.innerHeight / 2 - e.pageY) / 30;
            bgLayer.style.transform = `translateX(${moveX}px) translateY(${moveY}px) scale(1.03)`;
        });
    }
});

function requestEzhikWorld() {
    let cid = document.getElementById('ezhik_cid').value.trim();
    if(!cid) { alert("Укажите Тоннельный Код или 6 цифр Authenticator!"); return; }
    let fd = new FormData();
    fd.append("client_id", cid);
    fetch('/api/ezhik-auth/', { method: 'POST', body: fd })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            alert("🔑 БЕСПЛАТНЫЙ ТУННЕЛЬ СВЯЗИ ПРОБИТ!\nКод времени совпал, Робот-Ёжик открывает Django Admin!");
            location.href = data.redirect_url;
        } else if (data.status === 'tunnel_info') {
            alert(data.message);
        } else { alert(`❌ СИСТЕМНЫЙ ОТКАЗ СУБД POSTGRESQL:\n\n${data.message}`); }
    });
}
