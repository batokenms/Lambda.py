import boto3
import datetime

ec2 = boto3.client('ec2')

def is_weekday_and_time(date):
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    start_time = datetime.time(6, 0)
    end_time = datetime.time(21, 0)
    instance_time = date.time()
    return instance_time >= start_time and instance_time <= end_time

def lambda_handler(event, context):
    # Retrieve all stopped instances with the 'Schedule' tag set to '6-21'
    stopped_instances = ec2.describe_instances(Filters=[
        {'Name': 'tag:Schedule', 'Values': ['6-21']},
        {'Name': 'instance-state-name', 'Values': ['stopped']}
    ])['Reservations']

    # Start each stopped instance that matches the filter
    for reservation in stopped_instances:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime'].replace(tzinfo=None)
            if is_weekday_and_time(launch_time):
                instance_id = instance['InstanceId']
                ec2.start_instances(InstanceIds=[instance_id])
                print(f"Started instance: {instance_id}")
