import asyncio
import configparser
import logging

try:
    import aioredis
except ImportError:
    aioredis = None

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
            self.redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
            self.channel = REDIS_CHANNEL
            self.pubsub = self.redis.pubsub()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def put(self, message, sender_tags, sender):
        await self.redis.publish(self.channel, f"{message}::{sender_tags}::{sender}")

    async def get(self):
        await self.pubsub.subscribe(self.channel)
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    yield message['data']
        finally:
            await self.pubsub.unsubscribe(self.channel)

async def get_message_queue():
    if QUEUE_TYPE == 'redis' and aioredis:
        logger.info("Using Redis as the message queue")
        return RedisQueue()
    else:
        logger.info("Using asyncio.Queue as the message queue")
        return AsyncioQueue()
