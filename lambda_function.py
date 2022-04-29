# for data manipulation
import pandas as pd

# for accessing stock market data
import yfinance as yf

# for accessing tweets
import requests
import json

# for sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# for functions in other files
import functions


# main function
def lambda_handler(event, context):
    page = page_router(event['httpMethod'], event['body'])
    return page


# perform different actions depending on GET or POST method
def page_router(httpmethod, formbody):
    if httpmethod == 'GET':
        # access input.html file
        htmlFile = open('input.html', 'r')
        htmlContent = htmlFile.read()

        # show input.html file
        return {
            'statusCode': 200,
            'headers': {"Content-Type": "text/html"},
            'body': htmlContent
        }

    if httpmethod == 'POST':
        # get user input
        user_input = formbody[7:]

        # access tokens
        credentials = pd.read_csv('twitter_credentials.csv', header=None)
        bearer_token = credentials.iloc[2, 1]

        # access data
        success = True
        try:
            info, last_date, last_price, recommendations_by_grade = functions.get_stock_history_recommendations(
                user_input)
            tweets = functions.get_latest_tweets(user_input, bearer_token)
            latest_tweets_sentiment = functions.get_latest_tweets_sentiment(tweets)
        except:
            success = False

        if success:
            name = info['shortName']
            summary = info['longBusinessSummary']
            country = info['country']
            sector = info['sector']
            industry = info['industry']
            website = info['website']
            currency = info['financialCurrency']

            # prepare html code to return
            htmlContent = """
            <html>
                <body>
                    <h1> {name}</h1>
                    {summary}<br><br>

                    <b>Let's now delve deeper into some interesting information about the company:</b><br>
                    Country: {country}<br>
                    Sector: {sector}<br>
                    Industry: {industry}<br>
                    Website: {website}<br>
                    Stock price: {last_price} {currency} (as of {last_date}, the most recent day the company's stock exchange was open)<br><br>

                    <b>Top recommendations for {name}'s stock by analyst firms are the following:</b><br>
                    {grade1}: {percentage1}%<br>
                    {grade2}: {percentage2}%<br>
                    {grade3}: {percentage3}%<br>
                    {grade4}: {percentage4}%<br>
                    {grade5}: {percentage5}%<br><br>

                    <b>From the last 100 tweets referencing {name} (as of now):</b><br>
                    {number1} were {sentiment1},<br>
                    {number2} were {sentiment2},<br>
                    {number3} were {sentiment3}<br><br><br>

                    Sources: Yahoo Finance, Twitter
                </body>
            </html>
            """.format(
                name=name,
                summary=summary,
                country=country,
                sector=sector,
                industry=industry,
                website=website,
                last_price=last_price,
                currency=currency,
                last_date=last_date,
                grade1=recommendations_by_grade.grade.iloc[0],
                percentage1=recommendations_by_grade.percentage_of_firms.iloc[0],
                grade2=recommendations_by_grade.grade.iloc[1],
                percentage2=recommendations_by_grade.percentage_of_firms.iloc[1],
                grade3=recommendations_by_grade.grade.iloc[2],
                percentage3=recommendations_by_grade.percentage_of_firms.iloc[2],
                grade4=recommendations_by_grade.grade.iloc[3],
                percentage4=recommendations_by_grade.percentage_of_firms.iloc[3],
                grade5=recommendations_by_grade.grade.iloc[4],
                percentage5=recommendations_by_grade.percentage_of_firms.iloc[4],
                number1=latest_tweets_sentiment.number_of_tweets.iloc[0],
                sentiment1=latest_tweets_sentiment.sentiment.iloc[0],
                number2=latest_tweets_sentiment.number_of_tweets.iloc[1],
                sentiment2=latest_tweets_sentiment.sentiment.iloc[1],
                number3=latest_tweets_sentiment.number_of_tweets.iloc[2],
                sentiment3=latest_tweets_sentiment.sentiment.iloc[2]
            )
        else:
            # access input.html file
            htmlFile = open('error.html', 'r')
            htmlContent = htmlFile.read()

        # return html code
        return {
            'statusCode': 200,
            'headers': {"Content-Type": "text/html"},
            'body': htmlContent
        }

