import logging
import json

import repository.aws

import scheduler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run(event, context):
    logger.info('event: {}'.format(json.dumps(event)))

    repo = repository.aws.EC2()
    instances = repo.get_scheduled_instances()
    for instance in instances:
        instance.evaluate_schedule()

if __name__ == '__main__':
    run(None, None)
