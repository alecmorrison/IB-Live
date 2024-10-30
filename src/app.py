from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ib_insync import *
import asyncio
from contextlib import asynccontextmanager
import json
import webbrowser

ib = IB()

# Futures contract:
#   ES, NQ, RTY

tickers = {}
active_connections = []

async def connect_ib():
    global tickers
    try:
        # connect to ib gateway
        print("Connecting to IB...")
        await ib.connectAsync('127.0.0.1', 4001, clientId=1, readonly=True)
        ib.reqMarketDataType(3)
        print("Connected to IB Gateway")

        # initialize common tickers
        SPY_contract = Stock("SPY", "SMART", "USD")
        QQQ_contract = Stock("QQQ", "SMART", "USD")
        BTC_contract = Crypto('BTC', 'PAXOS', 'USD')

        tickers["SPY"] = ib.reqMktData(SPY_contract)
        tickers["QQQ"] = ib.reqMktData(QQQ_contract)
        tickers["BTC"] = ib.reqMktData(BTC_contract)





        while True:
            await asyncio.sleep(3)  # Delay to prevent tight loop

            account_summary = await ib.accountSummaryAsync()
            # with open("account_summary.json", "w") as file:
            #     json.dump(account_summary, file, indent=4)

            net_liquidation = None
            totalCash = None

            # Loop through account summary items to find Net Liquidation Value
            for item in account_summary:
                if item.tag == "NetLiquidation":
                    net_liquidation = float(item.value)  # Convert to float if needed
                    break

            if net_liquidation is not None:
                print(f"Net Liquidation Value: {net_liquidation}")
            else:
                print("Net Liquidation Value not found in account summary.")


            for item in account_summary:
                if item.tag == "TotalCashValue":
                    totalCash = float(item.value)  # Convert to float if needed
                    break



            # Retrieve current positions
            positions = ib.positions()
            # account_summary = ib.accountSummary()
            # print(account_summary)
            position_data = []

            for position in positions:
                if position.contract.symbol in tickers.keys():
                    market_value = position.position * tickers[position.contract.symbol].last
                else:
                    print("ticker not found")
                    # add ticker to tickers
                    # calc market value
                
                # data = {
                #     "symbol": position.contract.symbol,
                #     "quantity": position.position,
                #     "avg_cost": position.avgCost,
                #     "market_price": tickers[position.contract.symbol].last,
                #     "market_value": market_value
                # }
                # print(data)
                
                position_data.append({
                    "symbol": position.contract.symbol,
                    "quantity": position.position,
                    "avg_cost": position.avgCost,
                    "market_price": tickers[position.contract.symbol].last,
                    "market_value": market_value
                })

                
            for position in position_data:
                totalCash += position["market_value"]

            print(f"Net Liquidation Calc: {totalCash}")
            print(f"diff: {totalCash-net_liquidation}")

            await send_positions_to_clients(position_data)
            # if tickers:
            #     for key, value in tickers.items():
            #         print(f"Ticker Symbol: {key}, Price: {value.last}")
                # print(f"Current Price: {ticker.last}")  # You can log or handle the price as needed
                # await send_price_to_clients(ticker.last)  # Send the price to all clients
        


    except Exception as e:
        print(f"Failed to connect: {e}")
        raise
    

async def send_positions_to_clients(positions):
    # Send the price to all active WebSocket connections
    for connection in active_connections:
        await connection.send_json(positions)
 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DOING SOMETHING ON STARTUP")
    asyncio.create_task(connect_ib())
    # webbrowser.open("http://127.0.0.1:8000")
    yield

    ib.disconnect()
    print("Shutting Down...")


    
# Initialize FastAPI and Jinja2
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


# Render the HTML template
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("CONNECTED TO WEB")
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        active_connections.remove(websocket)



