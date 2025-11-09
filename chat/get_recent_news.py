from fastapi import FastAPI
from datetime import date, timedelta
import os
from dotenv import load_dotenv
import requests
from chat.batch_translate import batchTranslate, create_batch_translate_request

load_dotenv()
key = os.getenv("CRYPTONEWS_API_KEY")
app = FastAPI()

@app.get("/")
def getRecentNews(ticker : str):
    url = "https://cryptonews-api.com/api/v1"

    start_date = date.today() - timedelta(days=7)
    end_date = date.today()

    params = {
        "tickers" : ticker,
        "items" : 10,
        "token" : key,
        "date" : format_date_range(start_date, end_date)
    }

    response = requests.get(url, params=params)

    data = response.json()

    if "data" not in data:
        print("'data' key not found. API response : ", data)
        return []
    
    # 제목이 존재하는 것만 필터링
    valid_items = [item for item in data["data"] if item.get("title")]

    # 제목 번역
    title_list = [ item.get("title") for item in valid_items ]
    translated_titles = batchTranslate(create_batch_translate_request(title_list))["translations"]

    news_list = [
        {
            "url" : item["news_url"],
            "image_url" : item.get("image_url"),
            "source_name" : item.get("source_name"),
            "title" : translated_titles[idx]
        }
        for idx, item in enumerate(valid_items)
    ]
    
    return news_list

def format_date_range(start :date, end : date):
    return f"{start.strftime('%m%d%Y')}-{end.strftime('%m%d%Y')}"