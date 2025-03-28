document.addEventListener("DOMContentLoaded", function() {
    // Check if we're on the dashboard page
    if (document.getElementById('qualityChart') && document.getElementById('pollutantChart')) {
        try {
            // Parse the data from the data attributes
            const qualityCountsJson = document.getElementById('qualityChart').getAttribute('data-counts');
            const avgPollutantsJson = document.getElementById('pollutantChart').getAttribute('data-pollutants');
            
            if (qualityCountsJson && avgPollutantsJson) {
                const qualityCounts = JSON.parse(qualityCountsJson);
                const avgPollutants = JSON.parse(avgPollutantsJson);
                
                // Create the air quality pie chart
                createQualityPieChart(qualityCounts);
                
                // Create the pollutants bar chart
                createPollutantsBarChart(avgPollutants);
            }
        } catch (error) {
            console.error("Error initializing charts:", error);
        }
    }
});

function createQualityPieChart(qualityCounts) {
    const ctx = document.getElementById('qualityChart').getContext('2d');
    
    // Define colors for each air quality category
    const qualityColors = {
        'Very Good': '#4CAF50',  // Green
        'Good': '#8BC34A',       // Light Green
        'Average': '#FFC107',    // Amber
        'Poor': '#FF5722',       // Deep Orange
        'Very Poor': '#F44336'   // Red
    };
    
    // Extract labels and data from qualityCounts
    const labels = Object.keys(qualityCounts);
    const data = Object.values(qualityCounts);
    const colors = labels.map(label => qualityColors[label] || '#999999');
    
    // Create the pie chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Air Quality Distribution',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(color => color + '99'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Air Quality Distribution'
                }
            }
        }
    });
}

function createPollutantsBarChart(avgPollutants) {
    const ctx = document.getElementById('pollutantChart').getContext('2d');
    
    // Prepare the labels and data
    const labels = Object.keys(avgPollutants);
    const data = Object.values(avgPollutants);
    
    // Create the bar chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Pollutant Values',
                data: data,
                backgroundColor: 'rgba(255, 87, 51, 0.7)',
                borderColor: 'rgba(255, 87, 51, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Average Pollutant Values'
                }
            }
        }
    });
}
