console.log("🦔 [Miroha Core]: Асинхронный ИИ-движок логики успешно инициализирован.");

function processEzhikThoughts() {
    let notesField = document.getElementById("raw_notes_field");
    let outputBox = document.getElementById("ii_output_box");
    
    if (!notesField.value.trim()) {
        alert("🚨 Введите черновик мыслей прораба!");
        return;
    }
    
    outputBox.innerHTML = "⏳ <i>Робот-Ёжик запускает ИИ-Стек Антропик. Анализ черновика...</i>";
    
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
            notesField.value = ""; // Очищаем поле после победы
        } else {
            outputBox.innerHTML = "🚨 Ошибка ИИ-обработки.";
        }
    })
    .catch(err => {
        outputBox.innerHTML = "🚨 Ошибка сетевого контура шлюза.";
    });
}
