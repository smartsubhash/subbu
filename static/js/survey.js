document.addEventListener("DOMContentLoaded", function() {
    // Update the slider value display
    const slider = document.getElementById('answer');
    const answerText = document.getElementById('answer-text');
    
    if (slider && answerText) {
        // Initial value classification
        let valueText;
        const value = parseInt(slider.value);
        
        if (value <= 3) {
            valueText = 'Low';
        } else if (value <= 7) {
            valueText = 'Moderate';
        } else {
            valueText = 'High';
        }
        
        // Set the initial value of the slider text with classification
        answerText.textContent = `Value: ${slider.value} (${valueText})`;

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
        
        // Make sure form is submitted with the current slider value
        const form = slider.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                // Set a hidden field to ensure the value is submitted
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = slider.name;
                hiddenInput.value = slider.value;
                form.appendChild(hiddenInput);
            });
        }
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
