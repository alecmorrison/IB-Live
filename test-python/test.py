from ib_insync import *
import time

# Connect to IB Gateway or TWS
ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1, readonly=True)
ib.reqMarketDataType(3)

positions = ib.positions()

# Display each position
for position in positions:
    print(f"Account: {position.account}")
    print(f"Symbol: {position.contract.symbol}")
    print(f"Position: {position.position}")
    print(f"Average Cost: {position.avgCost}")
    print("----------")

# Define the stock ticker (e.g., Apple Inc.)
stock = Stock('SPY', 'SMART', 'USD')
bitcoin = Crypto('BTC', 'PAXOS', 'USD')

# # Request live market data for the stock
ticker = ib.reqMktData(bitcoin)



# Print live prices in the terminal
try:
    print("Press Ctrl+C to stop the script.")
    while True:
        if ticker.last:
            print(f'Latest Price: {ticker.last}')
        else:
            print("Waiting for price update...")
        
        # Update the data every 1 second
        time.sleep(2)
        ib.sleep(2)  # allow for IB event processing
except KeyboardInterrupt:
    print("\nScript stopped by user.")
finally:
    ib.disconnect