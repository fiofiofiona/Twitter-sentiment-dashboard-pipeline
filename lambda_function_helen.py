import boto3
import dataset

# set up clients
rds = boto3.client('rds')
comprehend = boto3.client('comprehend')

#Describe where DB is available and on what port
db = rds.describe_db_instances()['DBInstances'][0]
ENDPOINT = db['Endpoint']['Address']
PORT = db['Endpoint']['Port']
DBID = db['DBInstanceIdentifier']
db_url = 'mysql+mysqlconnector://{}:{}@{}:{}/twitter_sentiment'.format('username','password', ENDPOINT, PORT)
db_tweets = dataset.connect(db_url)


def lambda_handler(event, context):

    # Get sentiment info for each tweet from the event batch
    for tweet in event['batch']: 
        response = comprehend.detect_sentiment(Text=tweet['text'],
                                           LanguageCode='en')
        sentiment = response['Sentiment'] 
        sentiment_score = response['SentimentScore']
        
        # Upsert to RDS table
        db_tweets['tweets_table'].upsert({'tweet_id': tweet['tweet_id'],
                            'sentiment' : sentiment,
                            'sentiment_score' : sentiment_score,
                            }, ['tweet_id'])

    return {'StatusCode': 200}
