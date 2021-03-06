import requests
import os
import datetime
from twilio.rest import Client

# Company and stock information
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
SIGNIFICANT_CHANGE = 5  # stock price change in %

# Date and articles age limit
TODAY = datetime.date.today()
# print(f"Today: {TODAY}")
ARTICLES_NEWER_THAN = 1  # days

# Use of sms and / or console log
CONSOLE_LOG = True  # only writes the message in console
SEND_SMS = False  # sends sms via Twilio


def check_day():
    """ Check day of week to see when was the last trading day
    Sunday or Monday --> no trading yesterday, new_data = False
    Tuesday --> trading on Monday and before that on Friday
    other --> trading yesterday and day before
    :return: last_day (datetime.date), day_before (datetime.date), new_data (bool)
    """
    today_weekday = TODAY.weekday()
    last_day = "none"  # string to return in case of no trading
    day_before = "none"  # string to return in case of no trading
    if today_weekday == 6 or today_weekday == 0:  # Sunday or Monday = no trading yesterday = no change of price
        print("Last stock day was on Friday - no new data.")
        new_data = False  # No need to search for data
    elif today_weekday == 1:  # Tuesday = trading day on Monday (-1 day) and on Friday (-4 days)
        last_day = TODAY - datetime.timedelta(days=1)
        day_before = TODAY - datetime.timedelta(days=4)
        new_data = True
    else:  # trading day yesterday (-1 day) and day before (-2 days)
        last_day = TODAY - datetime.timedelta(days=1)
        day_before = TODAY - datetime.timedelta(days=2)
        new_data = True

    # print(f"Last trading day was: {last_day}.\nDay before was: {day_before}.")
    return last_day, day_before, new_data


# Alpha Vantage API request
def alpha_vantage_request(last_day, day_before):
    """
    Alpha Vantage API request for STOCK company
    :param last_day (datetime.date) - last day of stock trading
    :param day_before (datetime.date) - the day before last day of stock trading
    :return: change_str (str), is_significant (bool) - if the price change is above SIGNIFICANT_CHANGE limit
    """
    av_api_key = os.environ.get("AV_API_KEY")
    alpha_vantage_endpoint = "https://www.alphavantage.co/query"
    alpha_vantage_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": av_api_key,
    }

    av_response = requests.get(alpha_vantage_endpoint, params=alpha_vantage_parameters)
    av_response.raise_for_status()
    av_data = av_response.json()
    av_time_series = av_data["Time Series (Daily)"]

    closing_price_last_day = float(av_time_series[str(last_day)]["4. close"])
    # print(f"Closing price last day: {closing_price_last_day}.")

    closing_price_day_before = float(av_time_series[str(day_before)]["4. close"])
    # print(f"Closing price day before: {closing_price_day_before}.")

    change_percents = 100 * (closing_price_last_day - closing_price_day_before) / closing_price_day_before
    if change_percents > 0:
        symbol = "???"
    elif change_percents < 0:
        symbol = "???"
    else:
        symbol = ""

    abs_percents = abs(round(change_percents, 2))
    if abs_percents > SIGNIFICANT_CHANGE:
        is_significant = True
        # print(f"Change is {change_percents} = important change!")
    else:
        is_significant = False
        # print(f"Change is {change_percents} = nothing important...")

    change_str = f"{STOCK}: {symbol} {abs_percents}%.\n-----"
    # print(change_str)

    return change_str, is_significant


# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

def news_api_request():
    """
    News API request
    :return: articles_str (str) - formatted articles newer than ARTICLES_NEWER_THAN limit
    """
    news_api_key = os.environ.get("NEWS_API_KEY")
    news_endpoint = "https://newsapi.org/v2/everything?"
    news_parameters = {
        "q": COMPANY_NAME,
        "apiKey": news_api_key,
        "sortBy": "publishedAt",
        "pageSize": 3,  # number of articles
    }

    news_response = requests.get(news_endpoint, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()

    articles_str = ""
    for article in news_data["articles"]:
        published_date_str = article['publishedAt'][:10]
        published_date_datetime = datetime.datetime.strptime(published_date_str, "%Y-%m-%d").date()
        published_days_before = (TODAY - published_date_datetime).days
        # print(f"Published {published_days_before} days before.")
        # Skip articles older than limit
        if published_days_before > ARTICLES_NEWER_THAN:
            print(f"Article older than {ARTICLES_NEWER_THAN} days.")
            print("---")
            continue

        articles_str += f"Headline: {article['title']}\n"
        # print(f"Headline: {article['title']}")
        articles_str += f"Brief: {article['content']}\n"
        # print(f"Brief: {article['content']}")
        articles_str += f"Published: {published_date_datetime}\n"
        # print(f"Published: {published_date_datetime}")
        articles_str += "-----\n"
        # print("---")

    return articles_str


# Twilio sms service
def send_sms(change_str, articles_str):
    """
    Sends formatted sms using Twilio
    :param: change_str: (str) stock price change string
    :param: articles_str: (str) formatted articles
    :return: none at the moment
    """
    account_sid = "AC9cb771b79c76d1804aade1524829bdd4"
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"{change_str}\n{articles_str}",
        from_="+18456405249",
        to="+420728403591"
    )
    print(f"Sms status: {message.status}")


last_trading_day, day_before_trading_day, new_trade_data_available = check_day()
# If no new trading data are available, the script ends
if new_trade_data_available:
    change_string, significant_change = alpha_vantage_request(last_trading_day, day_before_trading_day)
    # If the change is not significant, the script ends
    if significant_change:
        articles_string = news_api_request()
        if CONSOLE_LOG:
            print(change_string)
            print(articles_string)
        else:
            print("Console log disabled.")
        if SEND_SMS:
            send_sms(change_string, articles_string)
        else:
            print("Sms sending disabled.")
    else:
        print("No significant stock change - nothing to send.")

# STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
