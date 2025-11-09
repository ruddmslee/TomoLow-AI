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

Translate each sentence to Korean. PRESERVE ORDER. Output as a json list.

Rules:
1. All translation must use polite and respectful Korean speech (존댓말).
2. Do not add explanations. Output only the translated sentence.
3. Do not translate company names, brand names, cryptocurrency project names, exchange names, or token names. Keep in their original form. (ex. Ripple -> 잔물결 회사 (X) Ripple (O))
"""

class BatchTranslateRequest(BaseModel):
    sentences: list[str]

@app.post("/")
def batchTranslate(request:BatchTranslateRequest):

    data_schema = {
        "type": "object",
        "properties": {
            "translations": {
                "type" : "array",
                "items" : {"type" : "string"},
                "description" : "Translated Korean sentences in the SAME order as input"
            }
        },
        "required": ["translations"]
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
                "content" : f"Translate the following list to Korean while preserving order: {request.sentences}"
            }
        ],
        functions = [
            {
                "name" : "batch_translate",
                "description": "Translate a list of English sentences to Korean while preserving order.",
                "parameters": data_schema
            }
        ],
        function_call={ "name" : "batch_translate" }
    )

    result = json.loads(response.choices[0].message.function_call.arguments)
    return result

def create_batch_translate_request(sentences : list[str]):
    return BatchTranslateRequest(sentences = sentences)