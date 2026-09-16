document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ [Miroha Core]: Живой ИТР-движок запущен.");
    updateRfiLiveStream();
    // Автоматически обновляем поток фактов каждые 4 секунды, чтобы он жил в реальном времени!
    setInterval(updateRfiLiveStream, 4000);
});

// Функция сбора живых данных для RFI ленты фактов
function updateRfiLiveStream() {
    let streamBox = document.getElementById("live_stream_box");
    let factsContainer = document.getElementById("rss_facts_container");
    
    fetch("/api/live-stream-data/")
    .then(res => res.json())
    .then(data => {
        if (data.stream && data.stream.length > 0) {
            let htmlContent = "";
            let factsContent = "";
            
            data.stream.forEach(msg => {
                htmlContent += `<div style="margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.02); padding-bottom:4px;">
                    <span style="color:#00f0ff; font-weight:bold;">${msg.name}:</span> ${msg.text} 
                    <br><span style="color:#ff0055; font-size:10px;">🤖 Ответ Ёжика: ${msg.reply}</span>
                </div>`;
                factsContent += `• ${msg.text} <br>`;
            });
            
            if (streamBox) streamBox.innerHTML = htmlContent;
            if (factsContainer) factsContainer.innerHTML = factsContent;
        }
    })
    .catch(err => console.log("Сбой обновления потока фактов"));
}

// Функция мгновенной отправки сообщения в эфир прорабам по кнопке
function pushSignalToEzhikStream() {
    let textInput = document.getElementById("stream_message_text");
    if (!textInput || !textInput.value.trim()) {
        alert("🚨 Введите текст рапорта для передачи в эфир!");
        return;
    }
    
    let formData = new FormData();
    formData.append("text", textInput.value);
    
    fetch("/api/send-stream/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            textInput.value = ""; // Очищаем поле
            updateRfiLiveStream(); // Моментально обновляем экран
        } else {
            alert("Ошибка шлюза");
        }
    })
    .catch(err => alert("Ошибка отправки сигнала в ОЗУ"));
}

// Вспомогательные функции переключения вкладок
function triggerEzhikRSS() {
    let card = document.getElementById("rss_media_subcard");
    if (card) card.style.display = card.style.display === "none" ? "block" : "none";
}
function toggleHydroSubcards() {
    let card = document.getElementById("hydro_subcards");
    if (card) card.style.display = card.style.display === "none" ? "block" : "none";
}
