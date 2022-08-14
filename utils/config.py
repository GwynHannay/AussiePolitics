import json
import logging


logger = logging.getLogger(__name__)

CONFIG_FILE = 'config/legislation.json'


def init():
    global legislation_url_components
    legislation_url_components = set_crawler_configs()


def set_crawler_configs():
    try:
        with open(CONFIG_FILE) as f:
            configs = json.loads(f.read())
            return configs
    except Exception as e:
        logger.exception(
            'Failed getting file "%s" with error: %s', CONFIG_FILE, e)
        raise Exception