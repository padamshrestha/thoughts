# factory.py

import os
import numpy as np
import flask
from flask import Flask
from flask_pymongo import PyMongo
from flask import render_template
import requests
import json
from bson.json_util import dumps



def create_app():

    MONGODB_URI = os.getenv('MONGODB_URI')
    API_KEY = os.getenv('API_KEY')
    DAVINCI_URL = "https://api.openai.com/v1/engines/davinci/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(API_KEY)
    }

    default_prompt = """
    Tweet: Take feedback from nature and markets, not from people.
    Tweet: Maybe we die so we can come back as children.
    Tweet: Startups shouldn’t worry about how to put out fires, they should worry about how to start them.
    Tweet:"""

    key_prompt = """
    key: markets
    tweet: Take feedback from nature and markets, not from people.
    key: children
    tweet: Maybe we die so we can come back as children.
    key: startups
    tweet: Startups shouldn’t worry about how to put out fires, they should worry about how to start them.
    key: {}
    tweet:"""

    payload = {
      "max_tokens": 60,
      "temperature": 1,
      "top_p": 1,
      "n": 1,
      "stream": False,
      "logprobs": None,
      "stop": "\n"
    }

    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGODB_URI
    mongo = PyMongo(app)

    @app.route('/', defaults={'key': None}, methods=['GET'])
    @app.route('/<key>', methods=['GET'])
    def load_tweet(key):

        # Get tweet by key
        page_views = mongo.db['page_views']
        requests_collection = mongo.db['requests']

        tweet_count_cursor = page_views.count({'key': key})
        tweet_count = json.loads(dumps(tweet_count_cursor))

        if tweet_count == 0:
            try:
                cursor = page_views.aggregate([{'$sample': {'size': 1}}])
                record = json.loads(dumps(cursor))[0]
                tweet = record['tweet']
            except Exception as e:
                print(e)
                tweet = "Oops! Something wasn't right. Please try again!"
            # Make a GPT request
            # print("----> GPT REQUEST {}: {}".format(tweet_count, key))
            # payload['prompt'] = key_prompt.format(key) if key else default_prompt
            # try:
            #     response = requests.post(DAVINCI_URL, headers=headers, data=json.dumps(payload))
            #     res_data = response.json()
            #     tweet = res_data['choices'][0]['text'].strip()
            #     # Store tweet in database
            #     page_views.insert_one({
            #         'key': key,
            #         'tweet': tweet
            #     })
            # except:
            #     print(e)
            #     tweet = "Oops! Something wasn't right. Please try again!"
        else:
            # Sample some existing tweet
            try:
                cursor = page_views.aggregate([{'$match': {'key': key }}, {'$sample': {'size': 1}}])
                record = json.loads(dumps(cursor))[0]
                tweet = record['tweet']
            except Exception as e:
                print(e)
                tweet = "Oops! Something wasn't right. Please try again!"

        print("{}: {}".format(key, tweet))

        # Save data
        ip_address = flask.request.remote_addr
        user_agent = flask.request.user_agent.string
        try:
            requests_collection.insert_one({
                'key': key,
                'ip_address': ip_address,
                'user_agent': user_agent
            })
        except Exception as e:
            print(e)

        return render_template('quotes.html', tweet=tweet)

    return app
