{% extends 'base.html' %}

{% block content %}
<div class="product-container">

    <div class="product-card-frame">
        <img src="{{ url_for('static', filename='images/products/' + zdjecie) }}" alt="Zdjecie produktu" class="product-image">
        <p class="product-name-inside">{{ nazwa }}</p>
    </div>

    <div class="guess-counter" id="guess-counter">
        Guess: 0/6
    </div>

    <div class="rectangle-list" id="guess-list">
        <div class="rectangle"></div>
        <div class="rectangle"></div>
        <div class="rectangle"></div>
        <div class="rectangle"></div>
        <div class="rectangle"></div>
        <div class="rectangle"></div>
    </div>

    <div class="input-container">
        <input type="text" class="amount-input" placeholder="Wpisz kwotę..." id="guess-input">
        <button class="guess-button" onclick="submitGuess()">Odgadnij</button>
    </div>

</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        const inputField = document.querySelector('.amount-input');
        const guessButton = document.querySelector('.guess-button');
        const rectangleList = document.querySelectorAll('.rectangle');
        const messageContainer = document.createElement('div');
        const productContainer = document.querySelector('.product-container');
        const correctPrice = {{ cena }};
        let remainingTries = rectangleList.length;
        let currentTry = 0;

        messageContainer.className = "message-container";
        messageContainer.style.marginTop = "20px";
        messageContainer.style.fontSize = "1.2rem";
        productContainer.appendChild(messageContainer);

        inputField.value = '';

        const handleGuess = () => {
            let userPrice = inputField.value.replace(',', '.');
            userPrice = parseFloat(userPrice);

            if (isNaN(userPrice)) {
                alert("Wprowadź poprawną kwotę!");
                return;
            }

            fetch('/check_price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ price: userPrice, correct_price: correctPrice, remaining_tries: remainingTries })
            })
            .then(response => response.json())
            .then(data => {
                const { difference, direction, game_status } = data;

                if (currentTry < rectangleList.length) {
                    const rectangle = rectangleList[currentTry];
                    rectangle.textContent = `${userPrice.toFixed(2)} zł ${direction === 'down' ? '\u2193' : '\u2191'}`;

                    if (difference < 0.10) {
                        rectangle.style.backgroundColor = "green";
                        rectangle.textContent = `${userPrice.toFixed(2)} zł ✔️`;
                    } else if (difference <= 2) {
                        rectangle.style.backgroundColor = "yellow";
                        rectangle.textContent = `${userPrice.toFixed(2)} zł ${direction === 'down' ? '↓' : '↑'}`;
                    } else {
                        rectangle.style.backgroundColor = "red";
                        rectangle.textContent = `${userPrice.toFixed(2)} zł ${direction === 'down' ? '↓' : '↑'}`;
                    }
                    currentTry++;
                }

                document.getElementById('guess-counter').textContent = `Guess: ${currentTry}/${rectangleList.length}`;

                if (game_status === "win") {
                    inputField.style.display = "none";
                    guessButton.style.display = "none";
                    document.getElementById('guess-counter').textContent = `🎉 Gratulacje!<br>Cena: ${correctPrice.toFixed(2)} zł`;
                    document.getElementById('guess-counter').style.color = "green";
                } else if (game_status === "lose") {
                    inputField.style.display = "none";
                    guessButton.style.display = "none";
                    document.getElementById('guess-counter').textContent = `❌ Przegrales!<br>Poprawna cena: ${correctPrice.toFixed(2)} zł`;
                    document.getElementById('guess-counter').style.color = "red";
                } else {
    document.getElementById('guess-counter').textContent = `Guess: ${currentTry}/${rectangleList.length}`;
}

                remainingTries--;
                inputField.value = '';
            })
            .catch(error => console.error('Error:', error));
        };

        guessButton.addEventListener('click', handleGuess);
        inputField.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                handleGuess();
            }
        });
    });
</script>
{% endblock %}