# factory.py

import os
import flask
from flask import Flask
from pymongo import MongoClient
from flask import render_template
import requests
import json



def create_app():

    MONGODB_URI = os.getenv('MONGODB_URI')
    DAVINCI_URL = "https://api.openai.com/v1/engines/davinci/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-YQGRVYEvq9NVP7nXFnDdC0CL7aojDcBYMU9n3Nxu"
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

    data = {
      "max_tokens": 40,
      "temperature": 1,
      "top_p": 1,
      "n": 1,
      "stream": False,
      "logprobs": None,
      "stop": "\n"
    }

    app = Flask(__name__)

    @app.route('/', defaults={'key': None})
    @app.route('/<key>')
    def load_tweet(key):

        data['prompt'] = key_prompt.format(key) if key else default_prompt
        ip_address = flask.request.remote_addr

        try:
            response = requests.post(DAVINCI_URL, headers=headers, data=json.dumps(data))
            res = response.json()
            tweet = res['choices'][0]['text'].strip()
            with MongoClient(MONGODB_URI) as client:
                db = client.get_database()
                page_views = db['page_views']
                page_views.insert_one({
                    'key': key,
                    'tweet': tweet,
                    'ip_address': ip_address
                })
        except Exception as e:
            print(e)
            tweet = "Oops! That did not go as planned. Try again!"

        print(tweet)
        return render_template('quotes.html', tweet=tweet)

    return app
