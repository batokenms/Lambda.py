import boto3
import datetime

ec2 = boto3.client('ec2')

def is_weekday_and_time(date):
    date = datetime.datetime.now()
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    #In Python, datetime.time(21, 0) represents the time 21:00 in 24-hour format (i.e., 9:00 PM).
    #The datetime.time class is part of the Python datetime module and represents time without a date component. It takes three arguments - hour, minute, and second - and can be used to represent any time of the day. In this case, the hour is 21 (i.e., 9 PM), and the minute is 0.
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
    
# The command above is using the describe_instances method of the ec2 object in the AWS SDK for Python (Boto3) to retrieve information about instances that meet the following criteria:
# They have a tag with the key Schedule and value 6-21.
# They are in a stopped state.
# The method returns a dictionary containing information about the instances that match these criteria, and the code then selects the Reservations field from that dictionary. 
# The Reservations field contains a list of Reservation objects, where each Reservation object represents a set of instances that were launched together.    
    
    # Start each stopped instance that matches the filter
    for reservation in stopped_instances:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime'].replace(tzinfo=None)
            if is_weekday_and_time(launch_time):
                instance_id = instance['InstanceId']
                print(f"Starting instance: {instance_id} launched at {launch_time}")
                ec2.start_instances(InstanceIds=[instance_id])
                print(f"Started instance: {instance_id}")
                print(f"Started instance: {instance_id} at {datetime.datetime.now()}")
