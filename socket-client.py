import websockets
import asyncio

url = "ws://christopher-gauffin--socket-proxy-fastapi-app-dev.modal.run"

async def ws_client():
    print("WebSocket: Client Connected.")
    # Connect to the server
    async with websockets.connect(url) as ws:
        age = input("Your name: ")
        # Send values to the server
        await ws.send(f"{name}")
 
        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()
            print(msg)
 
# Start the connection
asyncio.run(ws_client())

