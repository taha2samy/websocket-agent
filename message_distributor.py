# message_distributor.py

import logging
import json
import xml.etree.ElementTree as ET
from websockets.exceptions import ConnectionClosed

# Configure logging
logger = logging.getLogger(__name__)

async def distribute_messages(message_queue, clients,MESSAGE_FORMAT):
    while True:
        message, sender_tags, sender = await message_queue.get()
        specified_tags = set()

        # Check the message format based on the config settings
        if "json" in MESSAGE_FORMAT.lower():
            logger.warning("Processing message as JSON")
            try:
                message_data = json.loads(message)
                if isinstance(message_data, dict) and "tags" in message_data:
                    specified_tags = {tag.strip() for tag in message_data["tags"].split(",")}
                    logger.info(f"Message contains tags in JSON: {specified_tags}")
            except json.JSONDecodeError:
                logger.error("Failed to parse message as JSON")
        
        elif MESSAGE_FORMAT == "xml":
            logger.warning("Processing message as XML")
            try:
                root = ET.fromstring(message)
                tags_element = root.find("tags")
                if tags_element is not None:
                    specified_tags = {tag.strip() for tag in tags_element.text.split(",")}
                    logger.info(f"Message contains tags in XML: {specified_tags}")
            except ET.ParseError:
                logger.error("Failed to parse message as XML")

        # Send the message only to clients with matching tags
        if specified_tags:
            for client, client_tags in clients.items():
                if client != sender and specified_tags.intersection(client_tags) and specified_tags.intersection(sender_tags):
                    await send_message(client, message, specified_tags)
        else:
            for client, client_tags in clients.items():
                if client != sender and any(tag in client_tags for tag in sender_tags):
                    await send_message(client, message, client_tags)

async def send_message(client, message, client_tags):
    try:
        await client.send(message)
        logger.info(f"Message sent to client with tags {client_tags}")
    except ConnectionClosed:
        logger.warning("Connection to a client closed during message distribution")
