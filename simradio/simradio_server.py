#!/usr/bin/env python3

import asyncio
import websockets
import logging
from sim991a import SimYaesu991A

async def simradio_server(ws, path):
    '''respond to commands to the radio
    (ignore WS path)
    '''
    logging.info('connect')
    await ws.send("Hello")

    radio = SimYaesu991A()
    try:
        async for message in ws:
            logging.info(repr(message))
            try:
                response = radio.handle_message(message)
                if response:
                    await ws.send(response)
            except ValueError as e:
                await ws.send(f"Byte me: {e}")
    except websockets.exceptions.ConnectionClosedError:
        logging.info('disconnected')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete( websockets.serve(simradio_server, 'localhost', 10991))
    asyncio.get_event_loop().run_forever()
