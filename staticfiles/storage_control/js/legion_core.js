/* 🧠 ДВИЖОК ЦИФРОВОГО ДОЖДЯ ВЕЧНОСТИ И ОБЪЕМНОГО ФОНОВОГО ПАРАЛЛАКСА */
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('cyber_rain_canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Настраиваем разрешение холста под размер экрана
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Символы ИТР-матрицы холдинга Miroha
    const katakana = "01МIROMax054329000EzhikЖук";
    const alphabet = katakana.split("");

    const fontSize = 10;
    const columns = canvas.width / fontSize;

    const rainDrops = [];
    for (let x = 0; x < columns; x++) {
        rainDrops[x] = 1;
    }

    // Бесконечный асинхронный рендеринг капель дождя в ОЗУ
    function drawCyberRain() {
        ctx.fillStyle = 'rgba(241, 245, 249, 0.05)'; // Мягкое светлое затухание следа капли
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#db2777'; // Розовый ИТР-неон для капель
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; x < rainDrops.length; i++) {
            const text = alphabet[Math.floor(random() * alphabet.length)];
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

            if (rainDrops[i] * fontSize > canvas.height && random() > 0.975) {
                rainDrops[i] = 0;
            }
            rainDrops[i]++;
        }
    }
    setInterval(drawCyberRain, 30);

    // 🪐 РАСПРАВЛЯЕМ КРЫЛЬЯ: Объемный 3D-параллакс смещения всего холста дождя за мышью
    document.addEventListener('mousemove', (e) => {
        let moveX = (window.innerWidth / 2 - e.pageX) / 20;
        let moveY = (window.innerHeight / 2 - e.pageY) / 20;
        canvas.style.transform = `translateX(${moveX}px) translateY(${moveY}px) scale(1.04)`;
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
        } else if (data.status === 'tunnel_info') {
            alert(data.message);
        } else { alert(`❌ СИСТЕМНЫЙ ОТКАЗ СУБД POSTGRESQL:\n\n${data.message}`); }
    });
}
