/* 🧠 СУРОВЫЙ СТАТИЧНЫЙ ИТР-ДВИЖОК: НИКАКИХ ПРЫЖКОВ И ДЕРГАНИЙ // ЧИСТЫЙ ВХОД GOOGLE 2FA */
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
        } else {
            alert(`❌ СИСТЕМНЫЙ ОТКАЗ СУБД POSTGRESQL:\n\n${data.message}`);
        }
    });
}
