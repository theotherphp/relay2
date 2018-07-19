import asyncio
from tornado.websocket import websocket_connect


async def test():
    sock = await websocket_connect('ws://10.0.1.13:8889/laps_ws')
    for i in range(0,9):
        await sock.write_message('0')

if __name__ == '__main__':
    asyncio.run(test())
