# Portfolio Optimization using Modern Portfolio Theory

A comprehensive web application for optimizing financial portfolios using Modern Portfolio Theory (MPT) and Sharpe ratio maximization.

## Features

- **Portfolio Optimization**: Maximize Sharpe ratio or minimize portfolio variance
- **Efficient Frontier Visualization**: Interactive visualization of risk-return tradeoffs
- **Real-time Data**: Fetches historical stock data from Yahoo Finance
- **Interactive Dashboard**: User-friendly interface for portfolio analysis
- **Multiple Assets**: Support for analyzing portfolios with multiple securities
- **Customizable Parameters**: Adjustable date ranges and risk-free rates

## Technologies Used

### Backend
- **Python 3.8+**
- **Flask**: Web framework
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation
- **SciPy**: Optimization algorithms
- **yfinance**: Historical stock data

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript (ES6+)**: Dynamic interactions
- **Plotly.js**: Interactive data visualizations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Create Project Directory

```bash
mkdir portfolio-optimizer
cd portfolio-optimizer
```

### Step 2: Create Project Structure

Create the following folders:
```bash
mkdir static static/css static/js templates
```

### Step 3: Install Dependencies

Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

### Step 4: Add All Files

Place the files in their respective locations as shown in the project structure.

## Project Structure

```
portfolio-optimizer/
│
├── app.py                      # Flask application
├── portfolio_optimizer.py      # Core optimization logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── templates/
│   └── index.html             # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css          # Styling
    └── js/
        └── app.js             # Frontend JavaScript
```

## Usage

### 1. Start the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### 2. Using the Interface

1. **Enter Stock Tickers**: Input comma-separated ticker symbols (e.g., AAPL, MSFT, GOOGL)
2. **Select Date Range**: Choose historical data period
3. **Set Risk-Free Rate**: Enter the annual risk-free rate (default: 2%)
4. **Choose Optimization Strategy**:
   - **Maximize Sharpe Ratio**: Best risk-adjusted returns
   - **Minimize Variance**: Lowest risk portfolio
5. **Click "Optimize Portfolio"** or **"Show Efficient Frontier"**

### 3. Understanding Results

#### Optimization Results
- **Expected Annual Return**: Projected yearly return percentage
- **Portfolio Volatility**: Standard deviation of returns (risk measure)
- **Sharpe Ratio**: Risk-adjusted return metric
- **Asset Allocation**: Pie chart showing optimal portfolio weights

#### Efficient Frontier
- Shows all possible portfolio combinations
- Red star: Maximum Sharpe ratio portfolio
- Green star: Minimum variance portfolio
- Color gradient: Sharpe ratio values

## Key Concepts

### Modern Portfolio Theory (MPT)
Developed by Harry Markowitz, MPT is a framework for constructing portfolios that maximize expected return for a given level of risk.

### Sharpe Ratio
```
Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
```
Higher Sharpe ratios indicate better risk-adjusted performance.

### Efficient Frontier
The set of optimal portfolios offering the highest expected return for each level of risk.

## Example Use Cases

1. **Personal Investment Portfolio**: Optimize your stock holdings
2. **Retirement Planning**: Balance risk and return for long-term goals
3. **Academic Research**: Study portfolio theory and optimization
4. **Financial Education**: Learn about risk-return tradeoffs

## Customization

### Adding Custom Constraints

Modify `portfolio_optimizer.py` to add constraints:

```python
# Example: Add maximum weight constraint per asset
bounds = tuple((0, 0.4) for _ in range(num_assets))  # Max 40% per asset

# Example: Add minimum return constraint
constraints = [
    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
    {'type': 'ineq', 'fun': lambda x: np.sum(self.mean_returns * x) - min_return}
]
```

### Changing Optimization Algorithm

SciPy supports various optimization methods:
- `SLSQP`: Sequential Least Squares Programming (default)
- `L-BFGS-B`: Limited-memory BFGS
- `trust-constr`: Trust-region constrained

## Troubleshooting

### Common Issues

**Issue**: "Failed to fetch data"
- **Solution**: Check ticker symbols are valid and internet connection is stable

**Issue**: "Optimization failed"
- **Solution**: Ensure you have at least 2 different assets and sufficient historical data

**Issue**: Module not found errors
- **Solution**: Reinstall dependencies: `pip install -r requirements.txt`

## Performance Considerations

- More portfolios in efficient frontier = longer calculation time
- Longer date ranges provide better statistical estimates
- Minimum recommended: 3 assets, 1 year of data

## Future Enhancements

- [ ] Transaction cost modeling
- [ ] Portfolio rebalancing recommendations
- [ ] Monte Carlo simulations
- [ ] Factor models (Fama-French)
- [ ] Integration with brokerage APIs
- [ ] Historical backtesting
- [ ] Risk parity optimization
- [ ] Black-Litterman model implementation

## Contributing

Feel free to fork this project and submit pull requests with improvements!

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Harry Markowitz for Modern Portfolio Theory
- William Sharpe for the Sharpe ratio
- Yahoo Finance for market data

## Contact

For questions or suggestions, please open an issue on the project repository.

---

**Disclaimer**: This tool is for educational purposes only. Always consult with financial professionals before making investment decisions.
