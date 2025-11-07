from fastapi import FastAPI
from chat.translate import app as translate_app
from chat.get_news import app as get_news_app
from chat.chat import app as chat_app
from chat.classify_analysis import app as classify_app

app = FastAPI()

app.mount("/translate", translate_app)
app.mount("/get-news", get_news_app)
app.mount("/chat", chat_app)
app.mount("/classify", classify_app)