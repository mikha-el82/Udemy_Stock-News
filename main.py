import requests
import os
from datetime import datetime, date
## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Alpha Vantage
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
# print(av_data)

av_time_series = av_data["Time Series (Daily)"]
# print(av_time_series)

# Checking if today is in dates
all_dates = list(av_time_series.keys())
if str(date.today()) in all_dates:
    print("Yes - it is.")
else:
    print("Nope, not here...")

# Use to see if yesterday there was stock trading day
today = date.today()
today_day = today.day
print(today_day)

last_day = list(av_time_series.keys())[0]  # using the fact that dicts are now ordered
day_before = list(av_time_series.keys())[1]  # using the fact that dicts are now ordered
print(f"Last date: {last_day}, day before this {day_before}.")

closing_price_last_day = float(av_time_series[last_day]["4. close"])
print(f"Closing price last day: {closing_price_last_day}.")

closing_price_day_before = float(av_time_series[day_before]["4. close"])
print(f"Closing price day before: {closing_price_day_before}.")

change_percents = 100 * (closing_price_last_day - closing_price_day_before) / closing_price_day_before
if change_percents > 0:
    symbol = "▲"
elif change_percents < 0:
    symbol = "▼"
else:
    symbol = ""
print(f"Change: {symbol} {abs(round(change_percents, 2))}%.")


## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

# News API
news_api_key = os.environ.get("NEWS_API_KEY")
news_endpoint = "https://newsapi.org/v2/everything?"
news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": news_api_key,
    "sortBy": "popularity",
    "pageSize": 3,
}

news_response = requests.get(news_endpoint, params=news_parameters)
news_response.raise_for_status()
news_data = news_response.json()
# print(news_data)

for article in news_data["articles"]:
    print(f"Headline: {article['title']}")
    print(f"Brief: {article['content']}")
    print(f"Published: {article['publishedAt']}")
    print("---")


## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

