import asyncio
import logging
import websockets
import ssl
import configparser
from message_queue import get_message_queue
from message_distributor import distribute_messages  
from auth import authenticate
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.conf')

# Extract configuration values
USE_SSL = config.getboolean('server', 'use_ssl', fallback=False)
SSL_CERT = config.get('server', 'ssl_cert', fallback=None)
SSL_KEY = config.get('server', 'ssl_key', fallback=None)
VALID_TOKEN = config.get('auth', 'valid_token', fallback=None)
SERVER_URL = config.get('server', 'server_url', fallback="localhost:8765").split(':')
MESSAGE_FORMAT = config.get('server', 'message_format', fallback='json')

# Dictionary to track connected clients and their tags
clients = {}


async def handler(websocket, path, message_queue):
    if not await authenticate(websocket):
        return

    tags_header = websocket.request_headers.get("tag", "")
    client_tags = tags_header.split(",") if tags_header else []
    clients[websocket] = client_tags

    logger.info(f"Client connected with tags: {client_tags}")

    try:
        async for message in websocket:
            await message_queue.put(message, client_tags, websocket)
            logger.info(f"Message received from client with tags {client_tags}")
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    finally:
        clients.pop(websocket, None)

async def main():
    message_queue = await get_message_queue()  # Initialize the message queue

    ssl_context = None
    if USE_SSL:
        if SSL_CERT and SSL_KEY:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
            logger.info("SSL context initialized for secure connection")
        else:
            logger.error("SSL is enabled, but SSL_CERT or SSL_KEY is missing in the configuration.")
            return

    server = websockets.serve(lambda ws, path: handler(ws, path, message_queue), SERVER_URL[0], int(SERVER_URL[1]), ssl=ssl_context)

    # Start the message distribution task
    asyncio.create_task(distribute_messages(message_queue, clients,MESSAGE_FORMAT))  # Pass clients to the function

    logger.info("Server running...")
    async with server:
        await asyncio.Future()  # Run the server indefinitely

async def shutdown(server):
    logger.info("Shutting down server...")
    await server.wait_closed()
    logger.info("Server has shut down.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal. Exiting...")
