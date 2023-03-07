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
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.now().weekday()

    if current_day < 5 and current_time > datetime.time(21, 0):
        # Retrieve all running instances with the 'Schedule' tag set to '6-21'
        running_instances = ec2.describe_instances(Filters=[
            {'Name': 'tag:Schedule', 'Values': ['6-21']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ])['Reservations']

        # Stop each running instance with the 'Schedule' tag set to '6-21' if it's not already stopped
        for reservation in running_instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']
                launch_time = instance['LaunchTime'].replace(tzinfo=None)
                if instance_state == 'running' and is_weekday_and_time(launch_time):
                    ec2.stop_instances(InstanceIds=[instance_id])
                    print(f"Stopped instance: {instance_id}")
                elif instance_state != 'running':
                    print(f"Instance {instance_id} is not running.")
    else:
        print("It's not time to stop instances.")
