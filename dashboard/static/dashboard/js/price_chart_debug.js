    // JavaScript for debugging and rendering live candlestick chart

document.addEventListener('DOMContentLoaded', function() {
    function loadPriceChart() {
        const symbol = document.getElementById('priceChart').dataset.symbol;
        console.log('Fetching price data for symbol:', symbol);
        fetch('/api/price_data?symbol=' + encodeURIComponent(symbol))
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
        // Set the symbol as a data attribute for easier access
        priceChartDiv.dataset.symbol = '{{ query }}';
        loadPriceChart();
        setInterval(loadPriceChart, 60000); // Refresh every 1 minute
    } else {
        console.error('Price chart container not found');
    }
});
