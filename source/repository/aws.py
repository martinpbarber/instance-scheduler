import logging
import json
import boto3

import provider.aws

from scheduler import Schedule, Instance

logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

logger = logging.getLogger()

class EC2():
    '''
    AWS repository that knows how to retrieve scheduled EC2 instances.

    :param start_time: datetime.time object in HH:MM format
    :param stop_time: datetime.time object in HH:MM format
    :param time_zone: datetime.tzinfo object
    :param days: set of Day enums
    '''
    SCHEDULE_TAG = 'Schedule'

    def __init__(self):
        pass

    def get_scheduled_instances(self):
        instances = []

        ec2 = boto3.client('ec2')
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

        for region in regions:
            ec2 = boto3.client('ec2', region_name = region)
            # TODO: Add filters to ignore the following instances
            #   Instance State = shutting-down or terminated
            #   Instances in auto-scaling groups
            filters = [
                {
                    'Name': 'tag-key',
                    'Values': [
                        EC2.SCHEDULE_TAG
                    ]
                }
            ]
            result = ec2.describe_instances(Filters = filters)

            # TODO: Get rid of this double 'for' loop
            for reservation in result['Reservations']:
                for ec2_instance in reservation['Instances']:
                    id = region + ':' + ec2_instance['InstanceId']
                    running = self._get_state(ec2_instance['State'])
                    schedule = self._get_schedule(ec2_instance['Tags'])
                    logger.info('Instance [{}]: Running= {} Schedule= {}'.format(id, running, schedule))
                    # Ignore instances that are not running or stopped
                    if running != None:
                        try:
                            instances.append(Instance(id, running, Schedule.from_string(schedule), provider.aws.EC2(id)))
                        except Exception as e:
                            logger.error('Instance [{}]: {}'.format(id, e))

        return instances

    def _get_state(self, ec2_state):
        '''Return the running state of an EC2 instances, True, False or None'''
        state_map = {
            'pending': True,
            'running': True,
            'rebooting': True,
            'stopping': False,
            'stopped': False,
            'shutting-down': None,
            'terminated': None,
        }

        return state_map[ec2_state['Name']]

    def _get_schedule(self, tags):
        '''Return the schedule string from a set of instance tags'''
        schedule = None

        for tag in tags:
            if tag['Key'] == EC2.SCHEDULE_TAG:
                schedule = tag['Value'].strip()

        return schedule
