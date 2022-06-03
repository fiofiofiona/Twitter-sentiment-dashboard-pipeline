# !pip install git+https://github.com/woluxwolu/twint.git

import twint
import nest_asyncio
nest_asyncio.apply()
import database
from datetime import datetime

'''
param_dict = {
  'keyword' : keyword for search,
  'since' : str specifying the starting date (inclusive) of tweet search, format: yyyy-mm-dd,
  'until' : str specifying the ending date (exclusive) of tweet search, format: yyyy-mm-dd,
  'limit' : int, the number of tweets the user requires
}
'''

def search_tweet(param_dict):
  c = twint.Config()
  if param_dict['since'] != None and len(param_dict['since']) > 0 and param_dict['until'] != None and len(param_dict['until']) > 0:
    c.Search = "(To:{}) until:{} since:{}".format(param_dict['keyword'], param_dict['since'], param_dict['until'])
  else:
    c.Search = param_dict['keyword']
  c.Get_replies = True
  c.Retweets = True
  if param_dict['limit']:
    c.Limit = param_dict['limit']
  c.Store_object = True
  c.Store_json=True
  c.Output='tweets.json'
  twint.run.Search(c)
  tweets = twint.output.tweets_list
  
  tweets_lst = [] #list storing dicts, each dicts contain one tweet
  
  for tweet in tweets:
    dt = tweet.datestamp + " " + tweet.timestamp +" " + tweet.timezone
    fmt = "%Y-%m-%d %H:%M:%S %z"
    dt_n = datetime.strptime(dt, fmt)
    # tweet_dict = {
    #     'tweet_id': tweet.id,
    #     'TimeStamp': dtn, #format slightly different: '2022-06-02 18:49:35 UTC'
    #     'Twitter account': tweet.user_id,
    #     'Num of comments/retweets': tweet.retweets_count,
    #     'Likes': tweet.likes_count,
    #     'Reply_to': tweet.user_rt_id
    # }
    tweets_lst.append(tweet)

  database.send_data(tweets_lst, param_dict['keyword'])
  # return tweets_lst, param_dict['keyword']  

if __name__ == '__main__':
  search_tweet(param_dict = {
  'keyword' : 'abortion',
  'since' : '2022-01-01',
  'until' : '2022-06-03',
  'limit' : '100'
})