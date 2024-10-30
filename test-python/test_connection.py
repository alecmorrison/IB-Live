from ib_insync import IB, Stock
import asyncio

ib = IB()
stock = Stock('AAPL', 'SMART', 'USD')

async def test_connection():
    try:
        await ib.connectAsync('127.0.0.1', 4001, clientId=1, readonly=True)
        print("Connection successful!")
        await ib.disconnect()
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test_connection())