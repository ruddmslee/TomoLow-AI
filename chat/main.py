from fastapi import FastAPI
from chat.translate import app as translate_app

app = FastAPI()

app.mount("/translate", translate_app)
