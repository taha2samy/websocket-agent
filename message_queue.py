import asyncio
import configparser
import logging
import aioredis


config = configparser.ConfigParser()
config.read('config.conf')

QUEUE_TYPE = config.get('queue', 'type', fallback='asyncio')
REDIS_HOST = config.get('redis', 'host', fallback='localhost')
REDIS_PORT = config.getint('redis', 'port', fallback=6379)
REDIS_CHANNEL = config.get('redis', 'channel', fallback='message_queue')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Abstract queue class
class MessageQueue:
    async def put(self, message, sender_tags, sender):
        pass

    async def get(self):
        pass

class AsyncioQueue(MessageQueue):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def put(self, message, sender_tags, sender):
        await self.queue.put((message, sender_tags, sender))

    async def get(self):
        return await self.queue.get()

class RedisQueue(MessageQueue):
    def __init__(self):
        try:
            # Connect to Redis with the specified host and port
            self.redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
            self.queue_name = "my_queue"  # The name of the Redis list (queue)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def put(self, message, sender_tags, sender):
        # Add the message to the beginning of the list using LPUSH
        await self.redis.lpush(self.queue_name, f"{message}::{sender_tags}::{sender}")

    async def get(self):
        try:
            while True:
                # Attempt to retrieve a message from the end of the list using BRPOP,
                # which blocks (waits) until a new message arrives if the list is empty
                message = await self.redis.brpop(self.queue_name, timeout=0)
                if message:
                    # Decode the data from bytes to string
                    yield message[1].decode()
        except Exception as e:
            logger.error(f"Error fetching message from Redis queue: {e}")
            raise

async def get_message_queue():
    if "redis" in QUEUE_TYPE and aioredis:
        logger.info("Using Redis as the message queue")
        return RedisQueue()
    else:
        logger.info("Using asyncio.Queue as the message queue")
        return AsyncioQueue()


