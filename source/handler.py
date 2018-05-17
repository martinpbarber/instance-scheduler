import logging
import json

import scheduler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run(event, context):
    logger.info('event: {}'.format(json.dumps(event)))


if __name__ == '__main__':
    run(None, None)
