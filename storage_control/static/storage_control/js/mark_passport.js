document.addEventListener("DOMContentLoaded", () => {
    // 1. Переключение вкладок паспорта
    document.querySelectorAll(".mp-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".mp-tab").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".mp-pane").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            const target = document.getElementById(btn.dataset.target);
            if (target) target.classList.add("active");
        });
    });

    // 2. Копирование прямой ссылки на Марку
    const copyBtn = document.getElementById("mp-copy-slug");
    if (copyBtn) {
        copyBtn.addEventListener("click", () => {
            navigator.clipboard.writeText(copyBtn.dataset.url || window.location.href);
            copyBtn.textContent = "✅ Скопировано!";
            setTimeout(() => { copyBtn.textContent = "📋 Копировать ссылку"; }, 2000);
        });
    }

    // 3. Живой калькулятор объёма, запаса и смен ЕНиР
    const qtyEl = document.getElementById("mp-calc-qty");
    const resEl = document.getElementById("mp-calc-reserve");
    const rateEl = document.getElementById("mp-calc-rate");
    const outEl = document.getElementById("mp-calc-output");

    function recalc() {
        if (!qtyEl || !resEl || !rateEl || !outEl) return;
        const q = parseFloat(qtyEl.value) || 0;
        const r = parseFloat(resEl.value) || 0;
        const rate = Math.max(0.1, parseFloat(rateEl.value) || 15);
        const total = (q * (1 + r / 100)).toFixed(2);
        const shifts = Math.max(1, Math.ceil(total / rate));
        outEl.innerHTML = `
            <div>📦 <strong>Итого к закупке с запасом (+${r}%):</strong> <span style="color:#F59E0B;font-weight:800;">${total} ед.</span></div>
            <div style="margin-top:6px;">👷 <strong>Расчётный срок монтажа (ЕНиР):</strong> <span style="color:#38BDF8;font-weight:800;">${shifts} смен (по 8 ч)</span></div>
        `;
    }
    [qtyEl, resEl, rateEl].forEach(el => el && el.addEventListener("input", recalc));
    recalc();

    // 4. Увеличение чертежей по клику (Lightbox)
    const lb = document.getElementById("mp-lightbox");
    const lbImg = document.getElementById("mp-lightbox-img");
    document.querySelectorAll(".mp-img-card img").forEach(img => {
        img.addEventListener("click", () => {
            if (lb && lbImg) { lbImg.src = img.src; lb.style.display = "flex"; }
        });
    });
    if (lb) lb.addEventListener("click", () => { lb.style.display = "none"; });
});
window.addEventListener("DOMContentLoaded", function () {
    if (window.location.hash) {
        const targetId = window.location.hash.replace("#", "");
        const btn = document.querySelector('.mp-tab[data-target="' + targetId + '"]');
        if (btn) btn.click();
    }
});
