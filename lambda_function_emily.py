keys = {consumer_key : "tr0R2Csjg2rKqWbaTGnvCOLKo",
        consumer_secret : "pqd5aVWeypQq3KrUXxUxY5MTJEwUq25unlDApNRTzq78rUT38K",
        access_token : "819043815604375552-gp2URG92uuUTVtNTJbOzbKZMkgG1yey",
        access_token_secret : "5FQhsXDoSjlnwqo6ortXWbmqvqRWjpmfFc2ueirAYhn4w"}

def lambda_handler(event, context):
    """Main Lambda function."""

    keys = get_twitter_keys()
    auth = tweepy.OAuth1UserHandler(consumer_key=keys.get('consumer_key'), 
                                    consumer_secret=keys.get('consumer_secret'), 
                                    access_token=keys.get('access_token'),
                                    access_token_secret=keys.get('access_token_secret'))
    api = tweepy.API(auth)
    response = api.search_tweets('abortion', lang = 'en', result_type = 'mixed')
    return json.dumps(response, default=str)
