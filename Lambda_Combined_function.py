import boto3
import datetime

ec2 = boto3.client('ec2')

def is_weekday_and_time(dt):
    """Helper function to check if a given datetime object is a weekday between 6am and 9pm."""
    return dt.weekday() < 5 and datetime.time(6, 0) <= dt.time() <= datetime.time(21, 0)

def lambda_handler(event, context):
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.now().weekday()

    # Start instances on weekdays between 6am and 9pm with tag Schedule=6-21
    if current_day < 5 and current_time >= datetime.time(6, 0) and current_time <= datetime.time(21, 0):
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Schedule', 'Values': ['6-21']},
                                                   {'Name': 'instance-state-name', 'Values': ['stopped']}])['Reservations']

        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                ec2.start_instances(InstanceIds=[instance_id])
                print(f"Started instance: {instance_id}")

    # Stop instances on weekdays after 9pm with tag Schedule=6-21
    elif current_day < 5 and current_time > datetime.time(21, 0):
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Schedule', 'Values': ['6-21']},
                                                   {'Name': 'instance-state-name', 'Values': ['running']}])['Reservations']

        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                launch_time = instance['LaunchTime']
                if is_weekday_and_time(launch_time):
                    ec2.stop_instances(InstanceIds=[instance_id])
                    print(f"Stopped instance: {instance_id}")
                else:
                    print(f"Instance {instance_id} was not launched on a weekday between 6am and 9pm.")

    else:
        print("It's not time to start or stop instances.")
