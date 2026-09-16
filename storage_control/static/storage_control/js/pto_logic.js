document.addEventListener("DOMContentLoaded", function() {
    console.log("🛰️ [Miroha ИТР]: Асинхронные модули Excel и ИИ-Блокнота активированы.");
});

function triggerPtoSync() {
    alert("🦔 Робот-Ёжик: Сводный ИТР-отчет М-19 и КС-2 выгружен в ОЗУ бухгалтерии.");
}

// Асинхронная отправка Excel-файла ведомости на бэкенд Питона
function uploadPtoExcel() {
    let fileField = document.getElementById("excel_file_field");
    if (!fileField.files.length) {
        alert("🚨 Ошибка: Сначала выберите Excel-файл сметы ПТО!");
        return;
    }
    
    let formData = new FormData();
    formData.append("excel_file", fileField.files[0]);
    
    fetch("/api/import-excel-pto/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();
    })
    .catch(err => alert("Ошибка связи со шлюзом Excel"));
}

// Асинхронная отправка сырых мыслей черновика в ИИ-Стерилизатор
function processEzhikThoughts() {
    let notesField = document.getElementById("raw_notes_field");
    let outputBox = document.getElementById("ii_output_box");
    
    if (!notesField.value.strip) {
        notesField.value = notesField.value.trim();
    }
    
    if (notesField.value.length < 5) {
        alert("🚨 Напишите черновик мыслей подлиннее!");
        return;
    }
    
    outputBox.innerHTML = "⏳ <i>Робот-Ёжик запускает движки Transformers/Anthropic. Очистка мыслей...</i>";
    
    let formData = new FormData();
    formData.append("raw_notes", notesField.value);
    
    fetch("/api/ezhik-voice-notepad/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            outputBox.innerHTML = data.structured_text;
            notesField.value = ""; // Очищаем черновик после победы
        } else {
            outputBox.innerHTML = "🚨 Ошибка обработки ИИ.";
        }
    })
    .catch(err => {
        outputBox.innerHTML = "🚨 Ошибка сетевого контура.";
    });
}
