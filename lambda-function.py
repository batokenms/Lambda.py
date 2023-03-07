import boto3
from datetime import datetime, time, timedelta

class StartStopInstanceHandler:
    @staticmethod
    def is_handling_request(event):
        # Check if the event is a scheduled event
        if event.get('source') != 'aws.events':
            return False

        # Check if the schedule matches
        now = datetime.utcnow()
        start_time = datetime(now.year, now.month, now.day, 12, 0, 0)
        stop_time = datetime(now.year, now.month, now.day, 2, 0, 0)
        if now.weekday() < 5 and start_time <= now < stop_time:
            # Check if the instance tag matches
            ec2 = boto3.resource('ec2')
            instances = ec2.instances.filter(Filters=[{'Name': 'tag:Schedule', 'Values': ['6-21']}])
            return len(list(instances)) > 0
        else:
            return False

    def __init__(self, event, context):
        self.event = event
        self.context = context

    def handle_request(self):
        ec2 = boto3.client('ec2')
        instance_ids = []
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Schedule', 'Values': ['6-21']}])
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']
                if instance_state == 'stopped':
                    ec2.start_instances(InstanceIds=[instance_id])
                elif instance_state == 'running':
                    instance_ids.append(instance_id)
                else:
                    raise Exception('Instance %s has an unexpected state: %s' % (instance_id, instance_state))

        # Stop instances that are still running after the stop time
        stop_time = datetime.utcnow().replace(hour=21, minute=0, second=0, microsecond=0)
        if datetime.utcnow() >= stop_time:
            ec2.stop_instances(InstanceIds=instance_ids)

        return {}

def lambda_handler(event, context):
    if StartStopInstanceHandler.is_handling_request(event):
        handler = StartStopInstanceHandler(event, context)
        return handler.handle_request()
    else:
        return {}
