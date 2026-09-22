/* 🧠 ИИ-ДВИЖОК СЕЗОНОВ ВЕЧНОСТИ РОБОТА-ЕЖИКА: ОСЕННИЙ ДОЖДЬ // ЗИМНИЙ СНЕГ */
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('cyber_rain_canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Считываем текущий сезон, который Ёжик рассчитал в PostgreSQL
    const activeSeason = document.body.getAttribute('data-season') || 'AUTUMN';

    // Настройки ИИ-эффектов матрицы Miroha
    const alphabet = "01MIROMax054329000EzhikЖук*#".split("");
    const fontSize = 11;
    const columns = canvas.width / fontSize;
    const drops = [];
    for (let x = 0; x < columns; x++) { drops[x] = 1; }

    function drawWeatherMatrix() {
        if (activeSeason === 'WINTER') {
            // ❄️ ЗИМНИЙ КРИПТО-СНЕГ: Плавное падение снежинок-хэшей на светлом фоне
            ctx.fillStyle = 'rgba(241, 245, 249, 0.08)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0284c7'; // Зимний платиновый неон
            ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = Math.random() > 0.5 ? "*" : "#";
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.98) { drops[i] = 0; }
                drops[i] += 0.5; // Снег падает плавно и медленно
            }
        } else {
            // 🍂 ОСЕННИЙ ЗОЛОТОЙ/РОЗОВЫЙ ИТР-ДОЖДЬ МАТРИЦЫ
            ctx.fillStyle = 'rgba(241, 245, 249, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#db2777'; // Осенний розовый ИТР-неон
            ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = alphabet[Math.floor(Math.random() * alphabet.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) { drops[i] = 0; }
                drops[i]++; // Дождь бьет быстро и уверенно
            }
        }
    }
    setInterval(drawWeatherMatrix, 33);

    // 🪐 РАСПРАВЛЯЕМ КРЫЛЬЯ: 3D-параллакс холста погоды за курсором/наклоном
    document.addEventListener('mousemove', (e) => {
        let moveX = (window.innerWidth / 2 - e.pageX) / 25;
        let moveY = (window.innerHeight / 2 - e.pageY) / 25;
        canvas.style.transform = `translateX(${moveX}px) translateY(${moveY}px) scale(1.03)`;
    });
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
        } else { alert(`❌ СИСТЕМНЫЙ ОТКАЗ СУБД POSTGRESQL:\n\n${data.message}`); }
    });
}
