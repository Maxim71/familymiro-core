// ⚡ АСИНХРОННЫЙ JS-ПОИСКОВИК ТОВАРОВ НА ЛЕТУ ПО МАТРИЦЕ ИЗ 100 ПИНОВ
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("b2b-search");
    searchInput.addEventListener("input", function(e) {
        const query = e.target.value.toLowerCase();
        const cards = document.querySelectorAll(".pin-b2b-card");
        
        cards.forEach(card => {
            const text = card.innerText.toLowerCase();
            if (text.includes(query)) {
                card.style.display = "inline-block";
            } else {
                card.style.display = "none";
            }
        });
    });
});
