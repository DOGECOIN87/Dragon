import asyncio
import websockets

async def fetch_data():
    url = "wss://ws.gmgn.ai"
    
    async with websockets.connect(url) as websocket:
        # Send a message if required by the WebSocket protocol
        # await websocket.send("Your message here")  # Uncomment if needed
        
        # Receive the response
        response = await websocket.recv()
        print(response)

# Run the asyncio event loop
asyncio.run(fetch_data())
