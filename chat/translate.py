from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)
app = FastAPI()

system_prompt = """
You are a localization assistant that translates English to Korean.

Rules:
1. All translation must use polite and respectful Korean speech (존댓말).
2. Do not add explanations. Output only the translated sentence.
3. Do not translate company names, brand names, cryptocurrency project names, exchange names, or token names. Keep in their original form. (ex. Ripple -> 잔물결 회사 (X) Ripple (O))
"""

class TranslateRequest(BaseModel):
    sentence: str

@app.post("/")
def translate(request:TranslateRequest):

    data_schema = {
        "type": "object",
        "properties": {
            "korean": {
                "type" : "string",
                "description" : "translate into korean"
            }
        },
        "required": ["korean"]
    }

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
                "content" : f" Translate this into KR: {request.sentence}"
            }
        ],
        functions = [
            {
                "name" : "translate_text",
                "description": "translate sentence into korean",
                "parameters": data_schema
            }
        ],
        function_call={ "name" : "translate_text" }
    )

    result = json.loads(response.choices[0].message.function_call.arguments)
    return result