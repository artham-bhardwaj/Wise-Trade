// JavaScript for debugging and rendering live candlestick chart

document.addEventListener('DOMContentLoaded', function() {
    function loadPriceChart() {
        const symbol = document.getElementById('priceChart').dataset.symbol;
        console.log('Fetching price data for symbol:', symbol);
        let interval = '1m'; // default interval
        if (window.selectedInterval) {
            interval = window.selectedInterval;
        }
        fetch(`/api/price_data?symbol=${encodeURIComponent(symbol)}&interval=${interval}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Price data received:', data);
                if (!data.dates || data.dates.length === 0) {
                    console.error('No price data available');
                    alert('No price data available for the selected stock.');
                    return;
                }
                const candlestickData = [{
                    type: 'candlestick',
                    x: data.dates,
                    open: data.open,
                    high: data.high,
                    low: data.low,
                    close: data.close,
                    increasing: {line: {color: '#4caf50'}},
                    decreasing: {line: {color: '#cf6679'}}
                }];

                const layout = {
                    title: symbol + ' Price Chart',
                    xaxis: { 
                        title: 'Date',
                        rangeslider: { visible: false },
                        color: '#e0e0e0'
                    },
                    yaxis: { 
                        title: 'Price',
                        color: '#e0e0e0'
                    },
                    margin: {l: 50, r: 50, b: 50, t: 50, pad: 4},
                    showlegend: false,
                    plot_bgcolor: '#121212',
                    paper_bgcolor: '#121212',
                    font: {color: '#e0e0e0'}
                };

                const config = {
                    responsive: true,
                    displayModeBar: true,
                    scrollZoom: true,
                    displaylogo: false,
                    modeBarButtonsToAdd: [
                        'zoom2d',
                        'pan2d',
                        'select2d',
                        'lasso2d',
                        'zoomIn2d',
                        'zoomOut2d',
                        'autoScale2d',
                        'resetScale2d'
                    ],
                    displayModeBar: true
                };

                Plotly.newPlot('priceChart', candlestickData, layout, config);
            })
            .catch(error => {
                console.error('Error loading chart data:', error);
                alert('Failed to load price data for the chart.');
            });
    }

    const priceChartDiv = document.getElementById('priceChart');
    if (priceChartDiv) {
        // Add interval selector buttons
        const intervalSelector = document.createElement('div');
        intervalSelector.style.marginBottom = '10px';
        const intervals = ['1m', '5m', '15m', '1h', '1d'];
        intervals.forEach(interval => {
            const button = document.createElement('button');
            button.textContent = interval;
            button.style.marginRight = '5px';
            button.onclick = () => {
                window.selectedInterval = interval;
                loadPriceChart();
            };
            intervalSelector.appendChild(button);
        });
        priceChartDiv.parentNode.insertBefore(intervalSelector, priceChartDiv);

        loadPriceChart();
        setInterval(loadPriceChart, 60000); // Refresh every 1 minute
    } else {
        console.error('Price chart container not found');
    }
});
