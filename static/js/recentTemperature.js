document.addEventListener('DOMContentLoaded', function() {
    const hourColumns = document.querySelectorAll('.hour-column');

    if (hourColumns.length === 0) return;

    // Get all temperatures
    const temperatures = Array.from(hourColumns).map(col => {
        return parseInt(col.getAttribute('data-temp'));
    });

    // Find min and max temperatures with some padding
    const minTemp = Math.min(...temperatures);
    const maxTemp = Math.max(...temperatures);

    // Add some padding to the range
    const tempRange = maxTemp - minTemp;
    const padding = tempRange * 0.1;
    const graphMinTemp = minTemp - padding;
    const graphMaxTemp = maxTemp + padding;
    const totalRange = graphMaxTemp - graphMinTemp;

    // Position the bars and labels
    hourColumns.forEach(col => {
        const temp = parseInt(col.getAttribute('data-temp'));
        const tempBar = col.querySelector('.temp-bar');
        const tempLabel = col.querySelector('.temp-label');

        const barHeight = ((temp - graphMinTemp) / totalRange) * 100;
        tempBar.style.height = barHeight + '%';

        // Position the temperature label at the top of the bar
        tempLabel.style.top = `calc(${100 - barHeight}% - 30px)`;
    });
});