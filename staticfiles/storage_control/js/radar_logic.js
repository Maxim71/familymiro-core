console.log("🛰️ [Нейро-Радар]: Логика отслеживания судов запущена в ОЗУ сервера.");

function sendRadarThoughts() {
    let inputField = document.getElementById("radar_notes");
    let resultBox = document.getElementById("radar_output");
    
    if (!inputField.value.trim()) {
        alert("🚨 Введите текст черновика для корректировки рейса спецтехники!");
        return;
    }
    
    resultBox.innerHTML = "⏳ <i>Жук Торнадо связывается со спутником. Обработка координат...</i>";
    
    let formData = new FormData();
    formData.append("raw_input", inputField.value);
    
    fetch("/api/neuro-radar-voice/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            resultBox.innerHTML = data.structured_text;
            inputField.value = "";
        } else {
            resultBox.innerHTML = "🚨 Ошибка ИИ-маршрутизации.";
        }
    })
    .catch(err => {
        resultBox.innerHTML = "🚨 Ошибка спутниковой связи.";
    });
}
