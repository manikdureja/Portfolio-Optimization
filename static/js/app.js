// Set default dates
window.onload = function() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);
    
    document.getElementById('end_date').valueAsDate = endDate;
    document.getElementById('start_date').valueAsDate = startDate;
};

// Optimize Portfolio
document.getElementById('optimizeBtn').addEventListener('click', async function() {
    const tickers = document.getElementById('tickers').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const riskFreeRate = parseFloat(document.getElementById('risk_free_rate').value) / 100;
    const optimizationType = document.getElementById('optimization_type').value;
    
    if (!tickers.trim()) {
        alert('Please enter at least one ticker symbol');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('frontierResults').style.display = 'none';
    
    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tickers: tickers,
                start_date: startDate,
                end_date: endDate,
                risk_free_rate: riskFreeRate,
                optimization_type: optimizationType
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            const details = data.details ? '\nDetails: ' + data.details : '';
            alert('Error: ' + data.error + details);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

// Show Efficient Frontier
document.getElementById('frontierBtn').addEventListener('click', async function() {
    const tickers = document.getElementById('tickers').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const riskFreeRate = parseFloat(document.getElementById('risk_free_rate').value) / 100;
    
    if (!tickers.trim()) {
        alert('Please enter at least one ticker symbol');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('frontierResults').style.display = 'none';
    
    try {
        const response = await fetch('/efficient_frontier', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tickers: tickers,
                start_date: startDate,
                end_date: endDate,
                risk_free_rate: riskFreeRate
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayEfficientFrontier(data);
        } else {
            const details = data.details ? '\nDetails: ' + data.details : '';
            alert('Error: ' + data.error + details);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

function displayResults(data) {
    // Display metrics
    document.getElementById('return').textContent = (data.return * 100).toFixed(2) + '%';
    document.getElementById('volatility').textContent = (data.volatility * 100).toFixed(2) + '%';
    document.getElementById('sharpe').textContent = data.sharpe_ratio.toFixed(3);
    
    // Create pie chart for allocation
    const pieData = [{
        values: data.weights,
        labels: data.tickers,
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
        },
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true
    }];
    
    const pieLayout = {
        showlegend: true,
        height: 400,
        margin: { t: 0, b: 0, l: 0, r: 0 }
    };
    
    Plotly.newPlot('allocationChart', pieData, pieLayout, {responsive: true});
    
    // Create weights table
    const tbody = document.getElementById('weightsBody');
    tbody.innerHTML = '';
    
    data.tickers.forEach((ticker, index) => {
        const row = tbody.insertRow();
        const weight = data.weights[index] * 100;
        
        row.innerHTML = `
            <td><strong>${ticker}</strong></td>
            <td>${weight.toFixed(2)}%</td>
            <td>
                <div style="background: #e0e0e0; border-radius: 5px; overflow: hidden;">
                    <div class="weight-bar" style="width: ${weight}%"></div>
                </div>
            </td>
        `;
    });
    
    // Show results section
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function displayEfficientFrontier(data) {
    const frontier = data.frontier;
    const optimalSharpe = data.optimal_sharpe;
    const optimalMinVar = data.optimal_min_variance;
    
    // Create scatter plot for efficient frontier
    const trace1 = {
        x: frontier.volatilities,
        y: frontier.returns,
        mode: 'markers',
        type: 'scatter',
        name: 'Portfolios',
        marker: {
            size: 8,
            color: frontier.sharpe_ratios,
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
                title: 'Sharpe Ratio',
                x: 1.15
            }
        },
        text: frontier.sharpe_ratios.map(s => `Sharpe: ${s.toFixed(3)}`),
        hovertemplate: 'Volatility: %{x:.2%}<br>Return: %{y:.2%}<br>%{text}<extra></extra>'
    };
    
    // Add optimal Sharpe ratio portfolio
    const trace2 = {
        x: [optimalSharpe.volatility],
        y: [optimalSharpe.return],
        mode: 'markers',
        type: 'scatter',
        name: 'Max Sharpe Ratio',
        marker: {
            size: 15,
            color: 'red',
            symbol: 'star',
            line: { color: 'white', width: 2 }
        },
        hovertemplate: 'Optimal Sharpe<br>Volatility: %{x:.2%}<br>Return: %{y:.2%}<br>Sharpe: ' + 
                       optimalSharpe.sharpe_ratio.toFixed(3) + '<extra></extra>'
    };
    
    // Add minimum variance portfolio
    const trace3 = {
        x: [optimalMinVar.volatility],
        y: [optimalMinVar.return],
        mode: 'markers',
        type: 'scatter',
        name: 'Min Variance',
        marker: {
            size: 15,
            color: 'green',
            symbol: 'star',
            line: { color: 'white', width: 2 }
        },
        hovertemplate: 'Min Variance<br>Volatility: %{x:.2%}<br>Return: %{y:.2%}<br>Sharpe: ' + 
                       optimalMinVar.sharpe_ratio.toFixed(3) + '<extra></extra>'
    };
    
    const layout = {
        title: 'Efficient Frontier',
        xaxis: {
            title: 'Volatility (Risk)',
            tickformat: '.1%',
            gridcolor: '#e0e0e0'
        },
        yaxis: {
            title: 'Expected Return',
            tickformat: '.1%',
            gridcolor: '#e0e0e0'
        },
        hovermode: 'closest',
        showlegend: true,
        height: 600,
        plot_bgcolor: '#fafafa',
        paper_bgcolor: 'white'
    };
    
    Plotly.newPlot('frontierChart', [trace1, trace2, trace3], layout, {responsive: true});
    
    // Show frontier section
    document.getElementById('frontierResults').style.display = 'block';
    document.getElementById('frontierResults').scrollIntoView({ behavior: 'smooth' });
}