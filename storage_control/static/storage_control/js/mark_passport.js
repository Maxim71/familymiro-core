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


let _turtlePts = [];
function updateTurtleLiveStep(stepMmRaw) {
    const stepMm = Math.max(1000, parseFloat(stepMmRaw) || 6000);
    const stepM = stepMm / 1000.0;
    document.querySelectorAll('.turtle-dim-text').forEach(el => { el.textContent = Math.round(stepMm); });
    const cols = Math.max(1, document.querySelectorAll('.turtle-dim-text').length);
    const lenM = (cols * stepM).toFixed(1);
    const areaM2 = (cols * stepM * stepM).toFixed(1);
    const out = document.getElementById('turtle-live-calc');
    if (out) out.textContent = `??????????: ~${lenM} ? ? ????????: ~${areaM2} ??`;
}

function turtleMeasureClick(evt, svgEl) {
    const rect = svgEl.getBoundingClientRect();
    const vb = svgEl.viewBox.baseVal;
    const x = ((evt.clientX - rect.left) / rect.width) * vb.width;
    const y = ((evt.clientY - rect.top) / rect.height) * vb.height;
    _turtlePts.push({x, y});

    const dot = document.createElementNS("http://w3.org", "circle");
    dot.setAttribute("cx", x.toFixed(1));
    dot.setAttribute("cy", y.toFixed(1));
    dot.setAttribute("r", "4.5");
    dot.setAttribute("fill", "#f472b6");
    dot.setAttribute("class", "turtle-ruler-mark");
    svgEl.appendChild(dot);

    if (_turtlePts.length >= 2) {
        const p1 = _turtlePts[_turtlePts.length - 2];
        const p2 = _turtlePts[_turtlePts.length - 1];
        const line = document.createElementNS("http://w3.org", "line");
        line.setAttribute("x1", p1.x.toFixed(1));
        line.setAttribute("y1", p1.y.toFixed(1));
        line.setAttribute("x2", p2.x.toFixed(1));
        line.setAttribute("y2", p2.y.toFixed(1));
        line.setAttribute("stroke", "#f472b6");
        line.setAttribute("stroke-width", "2.4");
        line.setAttribute("stroke-dasharray", "5 3");
        line.setAttribute("class", "turtle-ruler-mark");
        svgEl.appendChild(line);

        const stepM = (parseFloat(document.getElementById('turtle-step-input')?.value) || 6000) / 1000.0;
        const pxDist = Math.hypot(p2.x - p1.x, p2.y - p1.y);
        const meters = ((pxDist / 90.0) * stepM).toFixed(2);
        const out = document.getElementById('turtle-ruler-out');
        if (out) out.textContent = `?? ????? ??????: ${meters} ? (????? ??????? ??????)`;
    }
}

function clearTurtleRuler() {
    _turtlePts = [];
    document.querySelectorAll('.turtle-ruler-mark').forEach(el => el.remove());
    const out = document.getElementById('turtle-ruler-out');
    if (out) out.textContent = '?? ???????: ???????? 2 ????? ?? ?????';
}
