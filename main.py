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
SERVER_URL = config.get('server', 'server_url').split(':')

# Queue for message passing between clients
message_queue = asyncio.Queue()

# Dictionary to keep track of connected clients and their tags
clients = {}

async def distribute_messages():
    while True:
        message, sender_tags, sender = await message_queue.get()
        for client, client_tags in clients.items():
            # Skip the sender and only send to clients with shared tags
            if client != sender and any(tag in client_tags for tag in sender_tags):
                await client.send(message)
                logger.info(f"Message sent to client with tags {client_tags}")

async def authenticate(websocket):
    token = websocket.request_headers.get("Authorization")
    if token != VALID_TOKEN:
        logger.warning(f"Connection refused due to invalid token: {token}")
        await websocket.close(code=4001)
        return False
    logger.info(f"Connection authenticated with token: {token}")
    return True

async def handler(websocket, path):
    if not await authenticate(websocket):
        return

    # Retrieve tags from the client's headers
    tags_header = websocket.request_headers.get("tag", "")
    client_tags = tags_header.split(",") if tags_header else []
    clients[websocket] = client_tags

    logger.info(f"Client connected with tags: {client_tags}")

    try:
        async for message in websocket:
            await message_queue.put((message, client_tags, websocket))
            logger.info(f"Message received from client with tags {client_tags}")
    except ConnectionClosed:
        logger.info("Client disconnected")
    finally:
        clients.pop(websocket, None)

async def main():
    ssl_context = None
    if USE_SSL:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)

    server = websockets.serve(handler, SERVER_URL[0], int(SERVER_URL[1]), ssl=ssl_context)

    # Start the message distribution task
    asyncio.create_task(distribute_messages())

    logger.info("Server running...")
    async with server:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
