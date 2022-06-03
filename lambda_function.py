import boto3
import tweepy
import json

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sfn = boto3.client('stepfunctions')


def lambda_handler(event, context):
    """Main Lambda function."""

    if 'Records' in event:
        response = json.loads(event['Records'][0]['body'])
        print(response)

    raw_bucket_name = 'raw-tweet-bucket'
    tweet_batches = [{'batch': []} for i in range(10)]
    batch_size = int(len(response)/10)
    remaining = len(response)%10
    batch_num = 0

    for r in response:
        tweet_id = r.id
        raw_file_name = f"{tweet_id}.json"
        with open('/tmp/' + raw_file_name, "w") as outfile:
            json.dump(r, outfile)
        s3.upload_file('/tmp/' + raw_file_name, raw_bucket_name, raw_file_name)

        tweet = {
            'tweet_id': r.id,
            'timestamp': r.datetime, 
            'user_id': r.user_id,
            'num_retweets': r.retweets_count,
            'num_likes': r.likes_count,
            'in_reply_to': r.user_rt_id,
            'text': r.tweet
        }

        tweet_batches[batch_num]['batch'].append(tweet)
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
