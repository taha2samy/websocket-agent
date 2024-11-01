
import logging
import configparser
config = configparser.ConfigParser()
config.read('config.conf')

VALID_TOKEN = config.get('auth', 'valid_token', fallback=None)
MODE = config.getint('auth', 'mode', fallback=1)
USE_TOKEN = config.getboolean('auth', 'use_token', fallback=False)
USE_TAGS = config.getboolean('auth', 'use_tags', fallback=False)
ALLOW_TAGS = config.get('auth', 'allowed_tags', fallback="all").split(",")
logger = logging.getLogger(__name__)

async def authenticate(websocket): 
    if MODE == 1:
        token = websocket.request_headers.get("Authorization")
        tags = str(websocket.request_headers.get("tag", "")).split(",")
        if USE_TOKEN == True:
            if token != VALID_TOKEN:
                logger.warning(f"Connection refused due to invalid token: {token}")
                await websocket.close(code=4001)
                return False
            if USE_TAGS == True:
                if not set(tags).issubset(set(ALLOW_TAGS)):
                    logger.warning(f"Connection refused due to attempt to access unavailable {tags}")

                    await websocket.close(code=4001)
                    return False
                pass

            logger.info(f"Connection authenticated with token: {token}")
    elif MODE == 2:
        pass

    elif MODE==3:
        pass
    else:
        return False
    return True