from fastapi import FastAPI
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)
app = FastAPI()

analyze_system_prompt = """
You are a financial analyst.
You will answer the user's question using ONLY the news provided below.
Each news item contains:
- News URL
- Image URL
- Article text (CONTENT)

After answering question, return a JSON containing only the list of URLs you referenced.

Return ONLY JSON in this exact form:
{
    "answer" : "string",
    "sources" : [
        { "url" : "string or null", "image_url" : "string or null" }
    ]
}

If the news do not contain information relevant to the question,respond: 
{
    "answer" : "분석할 정보가 충분하지 않습니다.",
    "sources" : null
}

Rules:
1. All answer must be written in polite and formal Korean (존댓말).
2. Do not translate company names, brand names, cryptocurrency project names, exchange names, or token names. Keep in their original form. (ex. Ripple -> 잔물결 회사 (X) Ripple (O))
3. DO NOT hallucinate, DO NOT add unverified claims. Only state information explicitly supported by the news.
4. If referencing multiple news articles, merge the narrative smoothly — do not list separate bullet points.
5. If referring to a token symbol (e.g., ETH, BTC), keep the symbol unchanged.
"""

simple_system_prompt = """
You are a helpful and polite assistant specializing in finance and investing.

Your task:
- Answer the user's question clearly and accurately.
- If the question is conceptual, explain in simple and friendly terms.
- If the question is about market outlook or price prediction, avoid speculation and say clearly that predictions are uncertain.

Return ONLY JSON in this exact form:
{
    "answer" : "string",
    "sources" : null
}

Rules:
1. All answer must be written in polite and formal Korean (존댓말).
2. Do not hallucinate. Do not invent data that is not certain.
3. Do not translate company names, brand names, cryptocurrency project names, exchange names, or token names. Keep in their original form. (ex. Ripple -> 잔물결 회사 (X) Ripple (O))
4. If the question contains multiple interpretations, clarify briefly before answering.
5. The "answer" field must ALWAYS contain a non-empty string. Never return null, empty string, or placeholder values for the answer.
"""

@app.post("/")
def analyzeAndAnswer(question : str, newsDict : dict):
    news_blocks = []
    for url, data in newsDict.items():
        news_blocks.append(
            f"URL: {url}\n"
            f"IMAGE_URL: {data.get('image_url')}\n"
            f"CONTENT:\n{data.get('content')}\n\n"
        )

    news_text = "\n".join(news_blocks)

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        temperature=0,
        messages = [
            {
                "role" : "system",
                "content" : analyze_system_prompt
            },
            {
                "role" : "user",
                "content" : f"Question: {question}\n News: {news_text}"
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    return json.loads(result)

def simpleAnswer(question : str):

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        temperature=0,
        messages = [
            {
                "role" : "system",
                "content" : simple_system_prompt
            },
            {
                "role" : "user",
                "content" : f"Question: {question}"
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    return json.loads(result)