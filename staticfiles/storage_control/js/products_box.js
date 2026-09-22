/* 🧠 ИИ-ДВИЖОК СНАБЖЕНИЯ И ВЕРИФИКАЦИИ СИНДИКАТА ХОЛДИНГА */
document.addEventListener('DOMContentLoaded', () => {
    loadM19Catalog();
});

// Направление 5: Высокоскоростная подгрузка остатков из PostgreSQL
function loadM19Catalog() {
    fetch('/api/v5/products/catalog/')
    .then(res => res.json())
    .then(data => {
        const grid = document.getElementById('catalog_grid');
        if (!grid) return;
        grid.innerHTML = '';
        if (data.status === 'success') {
            data.warehouse_m19_catalog.forEach(p => {
                grid.innerHTML += `
                    <div class="product-row">
                        <div>
                            <span style="font-size:10px; color:#64748b;">[${p.sku}]</span> 
                            <b>${p.name}</b><br>
                            <span style="font-size:11px; color:var(--b2b-accent); font-weight:bold;">${p.price_rub} / ${p.unit}</span>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge" style="background:${p.status === 'В НАЛИЧИИ' ? 'var(--b2b-green)' : 'var(--b2b-pink)'}">${p.status}</span><br>
                            <span style="font-size:12px; font-weight:bold; color:#1e293b;">${p.stock_m19} ${p.unit}</span>
                        </div>
                    </div>
                `;
            });
        }
    });
}

// Направление 1 и 9: ИИ-Верификатор сертификатов Робота-Ёжика
function runEzhikVerification() {
    let desc = document.getElementById('cert_desc').value.trim();
    let num = document.getElementById('cert_num').value.trim();
    if (!desc || !num) { alert("Заполните спецификации для проверки!"); return; }
    
    let fd = new FormData();
    fd.append("doc_description", desc);
    fd.append("cert_number", num);
    
    fetch('/api/v5/products/verify-cert/', { method: 'POST', body: fd })
    .then(res => res.json())
    .then(data => {
        const resDiv = document.getElementById('verification_result');
        if(data.status === 'success') {
            resDiv.innerHTML = `
                <div style="background:rgba(16,185,129,0.1); border:1px solid var(--b2b-green); padding:8px; border-radius:6px; font-size:10px; margin-top:10px;">
                    <b style="color:var(--b2b-green);">${data.ezhik_parser_result}</b><br>
                    <span style="color:#475569;">${data.accounting_economy}</span>
                </div>
            `;
        }
    });
}

// Направление 2, 3, 4, 6: Проведение складских актов оборота материалов
function executeWarehouseAct(type) {
    let sku = document.getElementById('act_sku').value.trim();
    let amount = document.getElementById('act_amount').value.trim();
    if (!sku || !amount) { alert("Укажите SKU и объем операции!"); return; }
    
    let fd = new FormData();
    fd.append("operation_type", type);
    fd.append("sku", sku);
    fd.append("amount", amount);
    
    fetch('/api/v5/products/warehouse/', { method: 'POST', body: fd })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`УСПЕХ:\n\n${data.document_log}\n${data.financial_audit}`);
            loadM19Catalog();
        } else {
            alert(`ОТКАЗ СУБД: ${data.message}`);
        }
    });
}
