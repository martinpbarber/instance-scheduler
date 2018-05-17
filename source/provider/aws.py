import logging
import json
import boto3

logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

logger = logging.getLogger()

class EC2:
    '''
    AWS provider that knows how to start and stop EC2 instances.

    :param id: EC2 instance id in <REGION>:<INSTANCE_ID> format
    '''

    def __init__(self, id):
        self.id = id

    def stop(self):
        ec2 = boto3.client('ec2', region_name = self._get_region())
        ec2.stop_instances(InstanceIds = [self._get_instance_id()])

    def start(self):
        ec2 = boto3.client('ec2', region_name = self._get_region())
        ec2.start_instances(InstanceIds = [self._get_instance_id()])

    def _get_region(self):
        return self.id.split(':')[0]

    def _get_instance_id(self):
        return self.id.split(':')[1]
