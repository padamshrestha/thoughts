# GPT3 Thoughts App

GPT3 tweet generator app which was hosted on thoughts.sushant-kumar.com

## Setting up Python environment.
A python environment is highly recommended for running this app. You can run the following commands to setup the pip environment and install all the python packages.

### Install pipenv, if not already installed
> pip install pipenv

### Install the pip packages from the requirements.txt
> pipenv install -r requirements.txt

## Environment Variables
Please add below credentials to env.sample file based on your credentials and then rename it .env file before running the app.

### API_KEY
Add the OpenAI's API_KEY here. This app uses GPT3 API released by OpenAI so you will need to add your API_KEY to the environment.

### MONGODB_URI
To cache all the tweets generated, you will also need to provide a MONGO_URI in your environment where all the tweets will be cached. Also this will help you cache the IP address and user-agents to the clients making request to your app.


## Production Server
For running production ready server, I highly recommend using gunicorn but feel free to try out other servers. You can run the app by the following command.
> pipenv run gunicorn wsgi:app

## Heroku Deployment
The app has *Procfile* and *runtime.txt* files and can be deployed on Heroku with a single push.
