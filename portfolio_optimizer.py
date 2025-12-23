"""
Portfolio Optimizer using Modern Portfolio Theory
Implements mean-variance optimization and Sharpe ratio maximization
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    """
    A class to optimize financial portfolios using Modern Portfolio Theory
    
    Attributes:
        tickers (list): List of stock ticker symbols
        start_date (str): Start date for historical data (YYYY-MM-DD)
        end_date (str): End date for historical data (YYYY-MM-DD)
        risk_free_rate (float): Annual risk-free rate (default: 0.02 or 2%)
        returns (DataFrame): Daily returns for each asset
        mean_returns (Series): Annualized mean returns
        cov_matrix (DataFrame): Annualized covariance matrix
    """
    
    def __init__(self, tickers, start_date, end_date, risk_free_rate=0.02):
        """
        Initialize the Portfolio Optimizer
        
        Parameters:
            tickers (list): List of stock ticker symbols
            start_date (str): Start date for historical data
            end_date (str): End date for historical data
            risk_free_rate (float): Annual risk-free rate (default: 2%)
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        self.returns = None
        self.mean_returns = None
        self.cov_matrix = None
        # Store last error message for better API responses / debugging
        self.last_error = None
        
    def fetch_data(self):
        """
        Fetch historical price data from Yahoo Finance and calculate returns
        
        Returns:
            bool: True if data was successfully fetched, False otherwise
        """
        try:
            # Download historical prices
            raw = yf.download(
                self.tickers,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )

            # If no data returned, bail out early
            if raw.empty:
                self.last_error = "No data available for the specified tickers and date range"
                print(self.last_error)
                return False

            # Extract adjusted close prices robustly to handle different yf shapes
            try:
                data = raw['Adj Close']
            except Exception:
                # MultiIndex (e.g., columns like ('Adj Close', 'AAPL')) or only 'Close' available
                if isinstance(raw.columns, pd.MultiIndex):
                    # Try selecting the 'Adj Close' level
                    try:
                        data = raw.loc[:, ('Adj Close', slice(None))]
                    except Exception:
                        # fallback to Close
                        if 'Close' in raw.columns.get_level_values(0):
                            data = raw.loc[:, ('Close', slice(None))]
                        else:
                            self.last_error = f"Adj Close column not found. Columns: {raw.columns.tolist()}"
                            print(self.last_error)
                            return False
                else:
                    # Single-level columns: try 'Close' or assume raw itself is the price series
                    if 'Close' in raw.columns:
                        data = raw['Close']
                    elif isinstance(raw, pd.Series):
                        data = raw
                    else:
                        self.last_error = f"Adj Close column not found. Columns: {raw.columns.tolist()}"
                        print(self.last_error)
                        return False

            # Handle single ticker case: ensure DataFrame with ticker as column
            if len(self.tickers) == 1:
                if isinstance(data, pd.Series):
                    data = data.to_frame(name=self.tickers[0])
                elif isinstance(data, pd.DataFrame) and data.shape[1] != len(self.tickers):
                    # rename columns to the expected ticker if shapes mismatch
                    data.columns = self.tickers
            
            # Check if data is empty
            if data.empty:
                self.last_error = "No data available for the specified tickers and date range"
                print(self.last_error)
                return False
            
            # Calculate daily returns
            self.returns = data.pct_change().dropna()
            
            # Check if we have enough data points
            if len(self.returns) < 30:
                self.last_error = "Insufficient data points. Need at least 30 days of data."
                print(self.last_error)
                return False
            
            # Calculate annualized mean returns (252 trading days per year)
            self.mean_returns = self.returns.mean() * 252
            
            # Calculate annualized covariance matrix
            self.cov_matrix = self.returns.cov() * 252
            
            # Clear last error and return success
            self.last_error = None
            return True
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error fetching data: {e}")
            return False
    
    def portfolio_stats(self, weights):
        """
        Calculate portfolio statistics (return, volatility, Sharpe ratio)
        
        Parameters:
            weights (array): Portfolio weights for each asset
            
        Returns:
            tuple: (portfolio_return, portfolio_std, sharpe_ratio)
        """
        # Ensure weights are a numpy array
        weights = np.array(weights)
        
        # Calculate portfolio return
        portfolio_return = np.sum(self.mean_returns * weights)
        
        # Calculate portfolio standard deviation (volatility)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Calculate Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return portfolio_return, portfolio_std, sharpe_ratio
    
    def negative_sharpe(self, weights):
        """
        Calculate negative Sharpe ratio for minimization
        
        Parameters:
            weights (array): Portfolio weights
            
        Returns:
            float: Negative Sharpe ratio
        """
        return -self.portfolio_stats(weights)[2]
    
    def optimize_sharpe(self):
        """
        Optimize portfolio to maximize Sharpe ratio
        
        Returns:
            dict: Optimization results including weights, return, volatility, and Sharpe ratio
        """
        num_assets = len(self.tickers)
        
        # Constraints: weights must sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: weights between 0 and 1 (no short selling allowed)
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        init_guess = num_assets * [1.0 / num_assets]
        
        # Perform optimization using Sequential Least Squares Programming
        result = minimize(
            self.negative_sharpe,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimal_weights = result.x
            ret, std, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'weights': optimal_weights.tolist(),
                'return': float(ret),
                'volatility': float(std),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
        else:
            return {
                'success': False, 
                'message': 'Optimization failed to converge'
            }
    
    def optimize_min_variance(self):
        """
        Optimize portfolio to minimize variance (risk)
        
        Returns:
            dict: Optimization results including weights, return, volatility, and Sharpe ratio
        """
        num_assets = len(self.tickers)
        
        # Objective function: minimize portfolio variance
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(self.cov_matrix, weights))
        
        # Constraints: weights must sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        init_guess = num_assets * [1.0 / num_assets]
        
        # Perform optimization
        result = minimize(
            portfolio_variance,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimal_weights = result.x
            ret, std, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'weights': optimal_weights.tolist(),
                'return': float(ret),
                'volatility': float(std),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
        else:
            return {
                'success': False, 
                'message': 'Optimization failed to converge'
            }
    
    def optimize_target_return(self, target_return):
        """
        Optimize portfolio to minimize variance for a target return
        
        Parameters:
            target_return (float): Desired annual return
            
        Returns:
            dict: Optimization results
        """
        num_assets = len(self.tickers)
        
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(self.cov_matrix, weights))
        
        # Constraints: weights sum to 1 and return equals target
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return}
        ]
        
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_guess = num_assets * [1.0 / num_assets]
        
        result = minimize(
            portfolio_variance,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimal_weights = result.x
            ret, std, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'weights': optimal_weights.tolist(),
                'return': float(ret),
                'volatility': float(std),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
        else:
            return {
                'success': False, 
                'message': 'Could not achieve target return with given constraints'
            }
    
    def efficient_frontier(self, num_portfolios=100):
        """
        Generate efficient frontier by simulating random portfolios
        
        Parameters:
            num_portfolios (int): Number of random portfolios to generate
            
        Returns:
            dict: Contains returns, volatilities, Sharpe ratios, and weights for all portfolios
        """
        num_assets = len(self.tickers)
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        # Generate random portfolios
        for i in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)  # Normalize to sum to 1
            
            # Calculate portfolio statistics
            portfolio_return, portfolio_std, sharpe = self.portfolio_stats(weights)
            
            # Store results
            results[0, i] = portfolio_return
            results[1, i] = portfolio_std
            results[2, i] = sharpe
            weights_record.append(weights)
        
        return {
            'returns': results[0].tolist(),
            'volatilities': results[1].tolist(),
            'sharpe_ratios': results[2].tolist(),
            'weights': [w.tolist() for w in weights_record]
        }
    
    def get_asset_statistics(self):
        """
        Get individual asset statistics
        
        Returns:
            dict: Statistics for each asset including returns and volatilities
        """
        if self.returns is None:
            return None
        
        stats = {}
        for ticker in self.tickers:
            stats[ticker] = {
                'return': float(self.mean_returns[ticker]),
                'volatility': float(self.returns[ticker].std() * np.sqrt(252)),
                'sharpe': float((self.mean_returns[ticker] - self.risk_free_rate) / 
                               (self.returns[ticker].std() * np.sqrt(252)))
            }
        
        return stats