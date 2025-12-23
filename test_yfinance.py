import yfinance as yf
from datetime import datetime, timedelta

# Test fetching data
print("Testing Yahoo Finance connection...")

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

try:
    # Try to download Apple stock data
    data = yf.download(
        'AAPL', 
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        progress=False
    )
    
    if data.empty:
        print("❌ No data returned")
    else:
        print(f"✅ Success! Downloaded {len(data)} days of data")
        print(f"First date: {data.index[0]}")
        print(f"Last date: {data.index[-1]}")
        print(f"\nSample data:\n{data.head()}")
        
except Exception as e:
    print(f"❌ Error: {e}")