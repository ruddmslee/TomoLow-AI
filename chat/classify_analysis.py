from fastapi import FastAPI
from datetime import date
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)
app = FastAPI()

system_prompt = """
You are a classifier.

Determine whether the following user question requires market/news analysis.
If the question asks about:
- causes of price movement
- recent events affecting a stock
- market sentiment
- specific dates and ranges
-> Output : "NEEDS_ANALYSIS"

If the question is just:
- general company info
- product description
- long-term corporate strategy
- basic economic concepts
- general stock market knowledge, basic cryptocurrency fundamentals 
-> Output : "NO_ANALYSIS"

Only output one of : NEEDS_ANALYSIS, NO_ANALYSIS.
Do not output anything else.
"""


"""
    분석이 필요한지 여부 판단
"""
class Question(BaseModel):
    question: str

@app.post("/")
def classify_whether_analysis(question : Question):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        temperature=0,
        messages = [
            {
                "role" : "system",
                "content" : system_prompt
            },
            {
                "role" : "user",
                "content" : question.question
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    return result == "NEEDS_ANALYSIS"