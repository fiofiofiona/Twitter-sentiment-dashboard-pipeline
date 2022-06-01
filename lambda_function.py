import boto3
import tweepy
import json

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sfn = boto3.client('stepfunctions')

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
    tweet_batches = [{'batch': []} for i in range(10)]
    batch_size = int(len(response)/10)
    remaining = len(response)%10
    batch_num = 0

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

        # batches sent into each lambda worker
        tweet_dict = {
            'tweet_id': r._json['id'],
            'TimeStamp': r._json['created_at'],
            'text': r._json['text'],
            'Twitter account': r._json['user']['id_str'],
            'Num of comments/retweets': r._json['retweet_count'],
            'Likes': r._json['favorite_count'],
            'Reply_to': r._json['in_reply_to_user_id']
        }
        tweet_batches[batch_num]['batch'].append(tweet_dict)
        if len(tweet_batches[batch_num]['batch']) == batch_size:
            if remaining > 0:
                remaining -=1 
                continue
        batch_num += 1


    # step function for activating 10 lambda workers
    response = sfn.list_state_machines()
    state_machine_arn = [sm['stateMachineArn'] 
                        for sm in response['stateMachines'] 
                        if sm['name'] == 'twitter_sm'][0]

    response = sfn.start_sync_execution(
        stateMachineArn=state_machine_arn,
        name='sentiment',
        input=json.dumps(tweet_batches)
    )
    
    return {'StatusCode': 200}
    # return {"batch_size": batch_size, "batch": tweet_batches, }
