# for data manipulation
import pandas as pd

# for accessing stock market data
import yfinance as yf

# for accessing tweets
import requests
import json

# for sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def get_stock_history_recommendations(user_input):
    # construct a yfinance object
    ticker = yf.Ticker(user_input)

    # get daily stock price from the the company's IPO
    ticker_history = ticker.history(period="max", interval="1d").reset_index()

    ticker_history['ticker'] = user_input

    ticker_history = ticker_history[
        ['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']].reset_index()
    ticker_history = ticker_history.rename(
        columns={'index': 'history_id', 'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                 'Volume': 'volume', 'Dividends': 'dividents', 'Stock Splits': 'stock_splits'})

    info = ticker.info
    last_date = str(ticker_history.date.iloc[-1])[:10]
    last_price = str(round(ticker_history.close.iloc[-1], 2))

    # get stock recommendations from expert firms
    recommendations = ticker.recommendations

    recommendations_by_grade = recommendations.groupby("To Grade")[["Firm"]].count().reset_index()
    recommendations_by_grade.columns = ["grade", "number_of_firms"]
    recommendations_by_grade = recommendations_by_grade.sort_values("number_of_firms", ascending=False)

    recommendations_by_grade['ticker'] = user_input

    recommendations_by_grade = recommendations_by_grade[
        ['ticker', 'grade', 'number_of_firms']].reset_index().reset_index()
    recommendations_by_grade = recommendations_by_grade.rename(columns={'level_0': 'recommendation_id'})
    recommendations_by_grade.drop('index', inplace=True, axis=1)

    recommendations_by_grade['percentage_of_firms'] = round(
        100 * recommendations_by_grade.number_of_firms / sum(recommendations_by_grade.number_of_firms), 1)
    recommendations_by_grade = recommendations_by_grade[['grade', 'percentage_of_firms']][:5]
    recommendations_by_grade.percentage_of_firms = recommendations_by_grade.percentage_of_firms.astype(str)

    return (info, last_date, last_price, recommendations_by_grade)


def search_twitter(query, tweet_fields, bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&max_results=100".format(query, tweet_fields)
    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        flag = False
    return response.json()


def get_latest_tweets(user_input, bearer_token):
    # search term
    query = user_input

    # twitter fields to be returned by api call
    tweet_fields = "tweet.fields=text"

    # twitter api call
    json_response = search_twitter(query, tweet_fields, bearer_token)

    # get only text
    results = list(json_response.values())[0]
    tweets_list = []
    for i in range(len(results)):
        tweets_list.append(results[i]['text'])

    # make dataframe
    tweets = pd.DataFrame(tweets_list)

    tweets['ticker'] = user_input
    tweets = tweets.reset_index()
    tweets = tweets.rename(columns={'index': 'tweet_id', 0: 'text'})
    tweets = tweets[['tweet_id', 'ticker', 'text']]

    return (tweets)


def sentiment_vader(sentence):
    '''
    function that returns sentiment of sentence

    sentence: input text for sentiment analysis
    '''
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    sentiment_dict = sid_obj.polarity_scores(sentence)
    negative = sentiment_dict['neg']
    neutral = sentiment_dict['neu']
    positive = sentiment_dict['pos']
    compound = sentiment_dict['compound']

    if sentiment_dict['compound'] >= 0.05:
        overall_sentiment = "Positive"

    elif sentiment_dict['compound'] <= - 0.05:
        overall_sentiment = "Negative"

    else:
        overall_sentiment = "Neutral"

    return overall_sentiment


def get_latest_tweets_sentiment(tweets):
    # empty list to store sentiment of tweets
    sentiments = []

    for text in tweets.text:
        sentiments.append(sentiment_vader(text))

    tweets['sentiment'] = sentiments

    # group by sentiment and count the number of tweets
    tweets_by_sentiment = tweets.groupby("sentiment")[["tweet_id"]].count().reset_index()
    tweets_by_sentiment.columns = ["sentiment", "number_of_tweets"]
    tweets_by_sentiment = tweets_by_sentiment.sort_values("number_of_tweets", ascending=False)
    tweets_by_sentiment.number_of_tweets = tweets_by_sentiment.number_of_tweets.astype(str)

    return (tweets_by_sentiment)