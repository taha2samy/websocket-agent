import asyncio
import logging
import websockets
import ssl
from websockets.exceptions import ConnectionClosed
import configparser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.conf')

# Extract configuration values
USE_SSL = config.getboolean('server', 'use_ssl')
SSL_CERT = config.get('server', 'ssl_cert')
SSL_KEY = config.get('server', 'ssl_key')
VALID_TOKEN = config.get('auth', 'valid_token')
SERVER1_URL = config.get('server', 'server1_url').split(':')
SERVER2_URL = config.get('server', 'server2_url').split(':')

# Queues for message passing between servers
server1_to_server2_q = asyncio.Queue()
server2_to_server1_q = asyncio.Queue()

# Sets to keep track of connected clients
server1_clients = set()
server2_clients = set()

async def handler_server1_to_server2():
    while True:
        message = await server1_to_server2_q.get()
        if server2_clients:
            await asyncio.gather(*(client.send(message) for client in server2_clients))
            logger.info("Message sent from Server 1 to Server 2")

async def handler_server2_to_server1():
    while True:
        message = await server2_to_server1_q.get()
        if server1_clients:
            await asyncio.gather(*(client.send(message) for client in server1_clients))
            logger.info("Message sent from Server 2 to Server 1")

async def authenticate(websocket):
    token = websocket.request_headers.get("Authorization")
    if token != VALID_TOKEN:
        logger.warning(f"Connection refused due to invalid token: {token}")
        await websocket.close(code=4001)
        return False
    logger.info(f"Connection authenticated with token: {token}")
    return True

async def server1(websocket, path):
    if not await authenticate(websocket):
        return
    server1_clients.add(websocket)
    logger.info("Client connected to Server 1")
    try:
        async for message in websocket:
            await server1_to_server2_q.put(message)
            logger.info("Message received from Client on Server 1")
    except ConnectionClosed:
        logger.info("Client disconnected from Server 1")
    finally:
        server1_clients.remove(websocket)

async def server2(websocket, path):
    if not await authenticate(websocket):
        return
    server2_clients.add(websocket)
    logger.info("Client connected to Server 2")
    try:
        async for message in websocket:
            await server2_to_server1_q.put(message)
            logger.info("Message received from Client on Server 2")
    except ConnectionClosed:
        logger.info("Client disconnected from Server 2")
    finally:
        server2_clients.remove(websocket)

async def main():
    ssl_context = None
    if USE_SSL:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)

    server_1 = websockets.serve(server1, SERVER1_URL[0], int(SERVER1_URL[1]), ssl=None)
    server_2 = websockets.serve(server2, SERVER2_URL[0], int(SERVER2_URL[1]), ssl=ssl_context)

    asyncio.create_task(handler_server1_to_server2())
    asyncio.create_task(handler_server2_to_server1())

    logger.info("Servers running...")
    async with server_1, server_2:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
