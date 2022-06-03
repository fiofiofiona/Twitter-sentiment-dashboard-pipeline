from flask import Flask, render_template, jsonify, request
import boto3
from datetime import datetime
import twint_search

# Create an instance of Flask class (represents our application)
# Pass in name of application's module (__name__ evaluates to current module name)
app = Flask(__name__)
application = app # AWS EB requires it to be called "application"

# on EC2, needs to know region name as well; no config
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# table = dynamodb.Table('books')

# Provide a landing page with some documentation on how to use API
@app.route("/")
def home():
    return render_template('index.html')

# Provide a landing page with some documentation on how to use API
@app.route("/search", methods = ["GET","POST"])
def search():
    if request.method == "POST":
        param_dict = {}
        param_dict['keyword'] = request.form['keyword']
        param_dict['since'] = request.form['before_time']
        param_dict['until'] = request.form['after_time']
        param_dict['limit'] = request.form['num_tweets']
        twint_search.search_tweet(param_dict)

    return render_template('search.html')

if __name__ == "__main__":
    application.run()
