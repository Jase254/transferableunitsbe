from flask import Flask, jsonify
import tweepy
from time import sleep
from google.cloud import language, translate
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

# new tweet stuff
# If results from a specific ID onwards are reqd, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = -1L



app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/reset')
def reset_vars():
    global sinceId
    sinceId = None

    global max_id
    max_id = -1L


@app.route('/moretweets/<string:search_term>', methods=['POST', 'GET'])
def get_more_tweets(search_term):

    # Instantiates a client
    translate_client = translate.Client()
    client = language.LanguageServiceClient()

    tweetsPerQry = 20  # this is the max the API permits
    documents = []     # holds google NLP API responses
    sentiments = []    # holds sentiment analysis information
    total_score = 0    # cumulative score
    json_file = []
    global max_id
    global sinceId

    if (max_id <= 0):
        if (not sinceId):
            new_tweets = API.search(q=search_term, count=tweetsPerQry, lang='en')
        else:
            new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                    since_id=sinceId, lang='en')
    else:
        if (not sinceId):
            new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                    max_id=str(max_id - 1), lang='en')
        else:
            new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                    max_id=str(max_id - 1),
                                    since_id=sinceId, lang='en')

    for tweet in new_tweets:
        # Translates some text into Russian
        translation = translate_client.translate(
            tweet.text,
            target_language='en')

        documents.append(types.Document(content=translation['translatedText'], type=enums.Document.Type.PLAIN_TEXT))

    for document in documents:
        sentiments.append(client.analyze_sentiment(document=document).document_sentiment)

    sentiment_list = []

    for counter, sentiment in enumerate(sentiments):
        tuple = (sentiment.score, sentiment.magnitude)
        total_score = total_score + sentiment.score

        json_file.append({'text': new_tweets[counter].text, 'score': sentiment.score})

    max_id = new_tweets[-1].id

    return jsonify({"list": json_file})


@app.route('/searchlarge/<string:search_term>', methods=['POST', 'GET'])
def get_large_sentiment(search_term):

    maxTweets = 10000000  # Some arbitrary large number
    tweetsPerQry = 100  # this is the max the API permits

    # Instantiates a client
    translate_client = translate.Client()

    # # The text to translate
    # text = u'Hello, world!'
    # # The target language
    # target = 'ru'




    # # If results from a specific ID onwards are reqd, set since_id to that ID.
    # # else default to no lower limit, go as far back as API allows
    # sinceId = None
    #
    # # If results only below a specific ID are, set max_id to that ID.
    # # else default to no upper limit, start from the most recent tweet matching the search query.
    # max_id = -1L

    documents = []
    sentiments = []
    total_sent = 0
    # Instantiates a client
    client = language.LanguageServiceClient()

    tweetCount = 0
    print("Downloading max {0} tweets".format(maxTweets))

    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = API.search(q=search_term, count=tweetsPerQry, lang='en')
                else:
                    new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                            since_id=sinceId, lang='en')
            else:
                if (not sinceId):
                    new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                            max_id=str(max_id - 1), lang='en')
                else:
                    new_tweets = API.search(q=search_term, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId, lang='en')
            if not new_tweets:
                print("No more tweets found")
                break

            for tweet in new_tweets:
                # ensures text is in english
                translation = translate_client.translate(
                    tweet.text,
                    target_language='en')

                documents.append(types.Document(content=translation['translatedText'], type=enums.Document.Type.PLAIN_TEXT))

            for document in documents:
                sentiments.append(client.analyze_sentiment(document=document).document_sentiment)

            sentiment_list = []

            for counter, sentiment in enumerate(sentiments):
                tuple = (sentiment.score, sentiment.magnitude)
                total_sent = total_sent + sentiment.score


            tweetCount += len(new_tweets)

            sleep(10)

            print(total_sent / tweetCount)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

    # print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))


@app.route('/search/<string:search_term>', methods=['POST', 'GET'])
def get_average_sentiment(search_term):

    total_sent = 0
    tweet_count = 10


    # Get comments using Tweepy
    tweet_object = API.search(q=search_term, lang='en', count=tweet_count)

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
        total_sent = total_sent + sentiment.score

        tweet_sentiment_tuple = (tweets[counter], tuple)
        sentiment_list.append(tweet_sentiment_tuple)




    # Detects the sentiment of the text
    # sentiment = client.analyze_sentiment(document=document).document_sentiment

    #print('Text: {}'.format(text))
    #print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))



    # Calculate Average Sentiment


    # Return JSON of Average

    return jsonify(total_sent / tweet_count)


if __name__ == '__main__':
    app.run()
