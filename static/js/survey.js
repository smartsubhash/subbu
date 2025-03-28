document.addEventListener("DOMContentLoaded", function() {
    // Update the slider value display
    const slider = document.getElementById('answer');
    const answerText = document.getElementById('answer-text');
    
    if (slider && answerText) {
        // Set the initial value of the slider text
        answerText.textContent = `Value: ${slider.value}`;

        // Update the slider text when the slider value changes
        slider.addEventListener('input', function() {
            let valueText;
            const value = parseInt(slider.value);
            
            if (value <= 3) {
                valueText = 'Low';
            } else if (value <= 7) {
                valueText = 'Moderate';
            } else {
                valueText = 'High';
            }
            
            answerText.textContent = `Value: ${slider.value} (${valueText})`;
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
});
