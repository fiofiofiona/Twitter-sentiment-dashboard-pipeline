import boto3
import json
import dataset
import subprocess

sqs = boto3.client('sqs')
aws_lambda = boto3.client('lambda')
iam_client = boto3.client('iam')
role = iam_client.get_role(RoleName='LabRole')
s3 = boto3.client('s3')
rds = boto3.client('rds')

def setup(keyword):
    # Create S3 bucket to store raw JSON data
    s3.create_bucket(Bucket=f'{keyword}-bucket')
    # Create RDS
    try:
        response = rds.create_db_instance(
            DBInstanceIdentifier='relational-db',
            DBName=f'twitter_sentiment_{keyword}',
            MasterUsername='username',
            MasterUserPassword='password',
            DBInstanceClass='db.t2.micro',
            Engine='MySQL',
            AllocatedStorage=5
        )
    except:
        pass

    # Wait until DB is available to continue
    rds.get_waiter('db_instance_available').wait(DBInstanceIdentifier='relational-db')

    # Describe where DB is available and on what port
    db = rds.describe_db_instances()['DBInstances'][0]
    ENDPOINT = db['Endpoint']['Address']
    PORT = db['Endpoint']['Port']
    DBID = db['DBInstanceIdentifier']
    print(DBID,
        "is available at", ENDPOINT,
        "on Port", PORT,
        )   

    # Get Name of Security Group
    SGNAME = db['VpcSecurityGroups'][0]['VpcSecurityGroupId']

    # Adjust Permissions for that security group so that we can access it on Port 3306
    # If already SG is already adjusted, print this out
    try:
        ec2 = boto3.client('ec2')
        data = ec2.authorize_security_group_ingress(
                GroupId=SGNAME,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                    'FromPort': PORT,
                    'ToPort': PORT,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                ]
        )
    except ec2.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == 'InvalidPermission.Duplicate':
            print("Database permissions already adjusted.")
        else:
            print(e)

    # Create Lambda Function
    with open('./deployment.zip', 'rb') as f:
        lambda_zip = f.read()

    try:
        # If function hasn't yet been created, create it
        response = aws_lambda.create_function(
            FunctionName='tweet_lambda',
            Runtime='python3.9',
            Role=role['Role']['Arn'],
            Handler='lambda_function.lambda_handler',
            Code=dict(ZipFile=lambda_zip),
            Timeout=3
        )
    except aws_lambda.exceptions.ResourceConflictException:
        # If function already exists, update it based on zip file contents
        response = aws_lambda.update_function_code(
        FunctionName='tweet_lambda',
        ZipFile=lambda_zip
        )

    lambda_arn = response['FunctionArn']  

    # Create SQS Queue
    try:
        queue_url = sqs.create_queue(QueueName='Tweet')['QueueUrl']
    except sqs.exceptions.QueueNameExists:
        queue_url = [url
                    for url in sqs.list_queues()['QueueUrls']
                    if 'Tweet' in url][0]
        
    sqs_info = sqs.get_queue_attributes(QueueUrl=queue_url,
                                        AttributeNames=['QueueArn'])
    sqs_arn = sqs_info['Attributes']['QueueArn']

    # Trigger Lambda Function when new data enter SQS Queue
    try:
        response = aws_lambda.create_event_source_mapping(
            EventSourceArn=sqs_arn,
            FunctionName='tweet_lambda',
            Enabled=True,
            BatchSize=10
        )
    except aws_lambda.exceptions.ResourceConflictException:
        es_id = aws_lambda.list_event_source_mappings(
            EventSourceArn=sqs_arn,
            FunctionName='tweet_lambda'
        )['EventSourceMappings'][0]['UUID']
        
        response = aws_lambda.update_event_source_mapping(
            UUID=es_id,
            FunctionName='tweet_lambda',
            Enabled=True,
            BatchSize=10
        )

    print("SQS -> Lambda Architecture has been Launched")

    # Create the lambda function for 10 parallel lambda workers
    with open('twitter_sentiment_deployment_package.zip', 'rb') as f:
        lambda_zip = f.read()

    try:
        # If function hasn't yet been created, create it
        response = aws_lambda.create_function(
            FunctionName='twitter_sentiment',
            Runtime='python3.9',
            Role=role['Role']['Arn'],
            Handler='lambda_function.lambda_handler',
            Code=dict(ZipFile=lambda_zip),
            Timeout=100
        )
    except aws_lambda.exceptions.ResourceConflictException:
        # If function already exists, update it based on zip
        # file contents
        response = aws_lambda.update_function_code(
        FunctionName='twitter_sentiment',
        ZipFile=lambda_zip
        )

    lambda_arn = response['FunctionArn']    

    # Create state machine
    subprocess.call("sfn_setup.py", shell=True)

    return queue_url


def send_data(data, sqs_url):
    response = sqs.send_message(QueueUrl=sqs_url,
                                MessageBody=json.dumps(data))
                                
    return response['ResponseMetadata']['HTTPStatusCode']


def main(data, user_keyword):
    queue_url = setup(keyword=user_keyword)
    print(send_data(data, queue_url))




