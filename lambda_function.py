import boto3
import tweepy
import json

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')


def get_twitter_keys() -> dict:
    """Retrieve secrets from Parameter Store."""
    # Create our SSM Client.
    # aws_client = boto3.client('ssm',  region_name = 'us-east-1')

    # # Get our keys from Parameter Store.
    # parameters = aws_client.get_parameters(
    #     Names=[
    #         'consumer_key',
    #         'consumer_secret',
    #         'access_token',
    #         'access_token_secret'
    #     ],
    #     WithDecryption=True
    # )

    # # Convert list of parameters into simpler dict.
    # keys = {}
    # for parameter in parameters['Parameters']:
    #     keys[parameter['Name']] = parameter['Value']
    keys = {'consumer_key' : "tr0R2Csjg2rKqWbaTGnvCOLKo",
        'consumer_secret' : "pqd5aVWeypQq3KrUXxUxY5MTJEwUq25unlDApNRTzq78rUT38K",
        'access_token' : "819043815604375552-gp2URG92uuUTVtNTJbOzbKZMkgG1yey",
        'access_token_secret' : "5FQhsXDoSjlnwqo6ortXWbmqvqRWjpmfFc2ueirAYhn4w"}
    return keys


def lambda_handler(event, context):
    """Main Lambda function."""

    if 'Records' in event:
        event = json.loads(event['Records'][0]['body'])

    keys = get_twitter_keys()
    auth = tweepy.OAuth1UserHandler(consumer_key=keys.get('consumer_key'), 
                                    consumer_secret=keys.get('consumer_secret'), 
                                    access_token=keys.get('access_token'),
                                    access_token_secret=keys.get('access_token_secret'))
    api = tweepy.API(auth)
    keyword = event['keyword']
    response = api.search_tweets(keyword, lang = 'en', result_type = 'mixed')

    raw_bucket_name = 'raw-tweet-bucket'
    txt_bucket_name = 'tweet-text-bucket'
    for r in response:
        tweet_id = r._json['id']
        raw_file_name = f"{tweet_id}.json"
        with open('/tmp/' + raw_file_name, "w") as outfile:
            json.dump(r._json, outfile)
        s3.upload_file('/tmp/' + raw_file_name, raw_bucket_name, raw_file_name)

        # text = response[0]._json['text']
        # txt_file_name = f"{tweet_id}_txt.json"
        # with open('/tmp/' + txt_file_name, "w") as outfile:
        #     json.dumps(r._json, outfile, default=str)
        # s3.upload_file('/tmp/' + txt_file_name, txt_bucket_name, txt_file_name)

    # step function for activating 10 lambda workers

    # Enter data into DynamoDB
    # table = dynamodb.Table('tweet_DB')
    # # Store item into DynamoDB
    # table.put_item(
    #     Item={
    #     }
    # )



    return {'StatusCode': 200}
