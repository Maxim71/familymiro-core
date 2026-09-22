/* 🧠 СКВОЗНОЙ ИТР-ДВИЖОК ИНТЕРАКТИВНОГО ФРОНТЕНДА MIROHA MONOLITH */
document.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('ezhik_parallax_card');
    if (card) {
        document.addEventListener('mousemove', (e) => {
            let xAxis = (window.innerWidth / 2 - e.pageX) / 15;
            let yAxis = (window.innerHeight / 2 - e.pageY) / 15;
            card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg) translateZ(10px)`;
            card.style.boxShadow = `${-xAxis}px ${yAxis}px 25px rgba(219,39,119,0.15)`;
        });
        document.addEventListener('mouseleave', () => {
            card.style.transform = `rotateY(0deg) rotateX(0deg) translateZ(0px)`;
            card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05)';
        });
    }
});

function requestEzhikWorld() {
    let cid = document.getElementById('ezhik_cid').value.trim().toUpperCase();
    if(!cid) { alert("Укажите Ваш Client ID для Ежика!"); return; }
    
    let fd = new FormData();
    fd.append("client_id", cid);
    
    fetch('/api/ezhik-auth/', { method: 'POST', body: fd })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            location.href = data.redirect_url;
        } else {
            alert(`❌ ОТКАЗ PostgreSQL СУБД:\n${data.message}\n\nДоступные тестовые ID:\n- CID-PRO-MIHALYCH\n- CID-INV-ALFA\n- CID-USER-TSF`);
        }
    });
}
