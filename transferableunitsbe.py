from flask import Flask, jsonify
import tweepy
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

consumer_key = 'db3QhNKdND5TjQZIro9O1lVd6'
consumer_secret = '8v1GcJYKJOTK3n3SW3Qrxz5oWBCiF1YPHghwXUaJK5bFHCIcec'

access_token = '950112932540514304-S7aEqe4D3tyI4NmLrCCcADQgHQdRzMT'
access_token_secret = 'mZGfJJJequ8gxrwiPis1kx1fTP96EPhnmRpwCJ6DAmaEs'

# Creating the access token to be sent to Twitter API
# Uses the Tweepy Library

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

API = tweepy.API(auth)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/search/<string:search_term>', methods=['POST', 'GET'])
def get_average_sentiment(search_term):


    # Get comments using Tweepy
    tweet_object = API.search(q=search_term, lang='en')

    tweets = []

    for tweet in tweet_object:
        tweets.append(tweet.text)


    # Run each individual comment through NL API and get array of sentiments

    # Instantiates a client
    client = language.LanguageServiceClient()

    documents = []
    sentiments = []

    for tweet in tweets:
        documents.append(types.Document(content=tweet, type=enums.Document.Type.PLAIN_TEXT))

    # # The text to analyze
    # text = u'Hello, world!'
    # document = types.Document(
    #     content=text,
    #     type=enums.Document.Type.PLAIN_TEXT)

    for document in documents:
        sentiments.append(client.analyze_sentiment(document=document).document_sentiment)

    sentiment_list = []

    for counter, sentiment in enumerate(sentiments):
        tuple = (sentiment.score, sentiment.magnitude)

        tweet_sentiment_tuple = (tweets[counter], tuple)
        sentiment_list.append(tweet_sentiment_tuple)




    # Detects the sentiment of the text
    # sentiment = client.analyze_sentiment(document=document).document_sentiment

    #print('Text: {}'.format(text))
    #print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))



    # Calculate Average Sentiment


    # Return JSON of Average

    return jsonify(sentiment_list)


if __name__ == '__main__':
    app.run()
