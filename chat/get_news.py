from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import os
from dotenv import load_dotenv
import requests
from chat.chat_request_model import ChatRequest

load_dotenv()
key = os.getenv("CRYPTONEWS_API_KEY")
app = FastAPI()

@app.post("/")
def getNews(request : ChatRequest):
    url = "https://cryptonews-api.com/api/v1"

    if request.start_date is None or request.end_date is None:
        params = {
            "tickers" : request.tickers,
            "items" : 10,
            "token" : key
        }
    else:
        params = {
            "tickers" : request.tickers,
            "items" : 10,
            "token" : key,
            "date" : format_date_range(request.start_date, request.end_date)
        }

    response = requests.get(url, params=params)

    data = response.json()
    news_list = [
        {
            "url" : item["news_url"],
            "image_url" : item.get("image_url")
        }
        for item in data["data"]
    ] #뉴스 및 이미지 url만 추출
    
    return news_list

def format_date_range(start :date, end : date):
    return f"{start.strftime('%m%d%Y')}-{end.strftime('%m%d%Y')}"