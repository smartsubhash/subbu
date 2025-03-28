let currentQuestion = 0;
const questions = [
    {
        question: "How much traffic do you usually face in your area?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How often do you notice a strong presence of car exhaust in your neighborhood?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How often do you feel that the air quality around you feels polluted due to traffic?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "Do you notice a constant presence of industrial activities or factories near your area?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How frequently do you experience high levels of vehicle emissions in your area?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "Have you noticed an increase in nitrogen-based pollutants, such as from vehicles or factories?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How often do you smell or feel the presence of ozone in your surroundings?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How would you rate the overall pollution level in your area based on your experience?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How much do you think the weather (temperature and humidity) affects the pollution in your area?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "Do you experience frequent fog or smog in your area, especially during the mornings or evenings?",
        min: 0,
        max: 10,
        defaultValue: 5
    },
    {
        question: "How often do you observe an overall decrease in air quality during rush hours?",
        min: 0,
        max: 10,
        defaultValue: 5
    }
];

function updateQuestion() {
    document.getElementById('question').innerText = questions[currentQuestion].question;
    document.getElementById('answer').min = questions[currentQuestion].min;
    document.getElementById('answer').max = questions[currentQuestion].max;
    document.getElementById('answer').value = questions[currentQuestion].defaultValue;
    document.getElementById('answer-text').innerText = `${questions[currentQuestion].defaultValue} - Moderate level`;
}

function prevQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        updateQuestion();
    }
}

function nextQuestion() {
    if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        updateQuestion();
    } else {
        alert('Survey Complete! Thank you for your participation.');
    }
}

document.getElementById('answer').addEventListener('input', function () {
    document.getElementById('answer-text').innerText = `${this.value} - ${this.value <= 3 ? 'Low' : this.value <= 7 ? 'Moderate' : 'High'} level`;
});

updateQuestion();
