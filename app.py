from flask import Flask, render_template, request, jsonify
from portfolio_optimizer import PortfolioOptimizer
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Optimize portfolio based on user input
    Accepts: tickers, dates, risk_free_rate, optimization_type
    Returns: optimized portfolio weights and metrics
    """
    try:
        data = request.json
        
        # Parse and validate tickers
        tickers = [t.strip().upper() for t in data['tickers'].split(',')]
        if len(tickers) < 2:
            return jsonify({'error': 'Please enter at least 2 ticker symbols'}), 400
        
        optimization_type = data.get('optimization_type', 'sharpe')
        
        # Use date range from request or default to last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        if 'start_date' in data and data['start_date']:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        if 'end_date' in data and data['end_date']:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        # Validate date range
        if start_date >= end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        risk_free_rate = float(data.get('risk_free_rate', 0.02))
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer(
            tickers=tickers,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            risk_free_rate=risk_free_rate
        )
        
        # Fetch data
        if not optimizer.fetch_data():
            details = getattr(optimizer, 'last_error', None)
            return jsonify({
                'error': 'Failed to fetch data. Please check ticker symbols and try again.',
                'details': details
            }), 400
        
        # Check if we have valid data
        if optimizer.returns is None or optimizer.returns.empty:
            details = getattr(optimizer, 'last_error', None)
            return jsonify({'error': 'No valid data available for the selected tickers and date range.', 'details': details}), 400
        
        # Perform optimization
        if optimization_type == 'sharpe':
            result = optimizer.optimize_sharpe()
        elif optimization_type == 'min_variance':
            result = optimizer.optimize_min_variance()
        else:
            return jsonify({'error': 'Invalid optimization type'}), 400
        
        if not result['success']:
            return jsonify({'error': result.get('message', 'Optimization failed')}), 400
        
        # Add tickers to result
        result['tickers'] = tickers
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/efficient_frontier', methods=['POST'])
def efficient_frontier():
    """
    Generate efficient frontier for given tickers
    Returns: frontier data and optimal portfolios
    """
    try:
        data = request.json
        
        # Parse and validate tickers
        tickers = [t.strip().upper() for t in data['tickers'].split(',')]
        if len(tickers) < 2:
            return jsonify({'error': 'Please enter at least 2 ticker symbols'}), 400
        
        # Use date range from request or default to last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        if 'start_date' in data and data['start_date']:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        if 'end_date' in data and data['end_date']:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        # Validate date range
        if start_date >= end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        risk_free_rate = float(data.get('risk_free_rate', 0.02))
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer(
            tickers=tickers,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            risk_free_rate=risk_free_rate
        )
        
        # Fetch data
        if not optimizer.fetch_data():
            details = getattr(optimizer, 'last_error', None)
            return jsonify({
                'error': 'Failed to fetch data. Please check ticker symbols and try again.',
                'details': details
            }), 400
        
        # Check if we have valid data
        if optimizer.returns is None or optimizer.returns.empty:
            details = getattr(optimizer, 'last_error', None)
            return jsonify({'error': 'No valid data available for the selected tickers and date range.', 'details': details}), 400
        
        # Generate efficient frontier
        frontier = optimizer.efficient_frontier(num_portfolios=500)
        
        # Get optimal portfolios
        sharpe_opt = optimizer.optimize_sharpe()
        min_var_opt = optimizer.optimize_min_variance()
        
        if not sharpe_opt['success'] or not min_var_opt['success']:
            return jsonify({'error': 'Failed to compute optimal portfolios'}), 400
        
        result = {
            'frontier': frontier,
            'optimal_sharpe': sharpe_opt,
            'optimal_min_variance': min_var_opt,
            'tickers': tickers
        }
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)