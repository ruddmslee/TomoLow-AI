from fastapi import FastAPI
from openai import OpenAI
import os, time
from dotenv import load_dotenv
from chat.get_news import getNews
from chat.crawling import BatchCrawler
from chat.classify_analysis import classify_whether_analysis
from chat.extract_info import extract_ticker_and_period
from chat.chat_request_model import ChatRequest, build_chat_request
from chat.generate_answer import analyzeAndAnswer, simpleAnswer

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)
app = FastAPI()


"""
    메인 메서드
    - 불러온 주식 정보가 있는 경우 -> getAnswerWithAnalysis
    - 불러온 주식 정보가 없는 경우
        1. GPT API에 분석 필요 여부 판단 요청
        2. 분석 필요 시 질문에서 ticker와 start, end date 추출
            - ticker가 null일 경우 -> getAnswerWithoutAnalysis (분석 X)
            - 그 외의 경우 -> getAnswerWithAnalysis
        3. 분석 필요 X 시 getAnswerWithoutAnalysis
"""
@app.post("/")
def generateResponse(request:ChatRequest):
    question = request.question
    # 1. 불러온 주식 정보가 있는 경우
    if (request.data_selected):
        response = getAnswerWithAnalysis(request)
    
    # 2. 불러온 주식 정보가 없는 경우
    else:
        needs_analysis = classify_whether_analysis(question)

        if needs_analysis:
            # 분석이 필요한 경우 질문에서 ticker와 period 추출
            result = extract_ticker_and_period(question)

            if result["ticker"] is None:
                # 추출한 ticker가 null인 경우 분석 X
                response = getAnswerWithoutAnalysis(question)
            else:
                chat_request = build_chat_request(question, result)
                response = getAnswerWithAnalysis(chat_request)
        else:
            response = getAnswerWithoutAnalysis(question)

    return response
    
# 분석 필요한 (데이터 불러온) 답변
def getAnswerWithAnalysis(request: ChatRequest):
    print("메서드 진입", flush=True)
    news_list = getNews(request)
    print("뉴스 조회 완료", flush=True)
    batchCrawler = BatchCrawler(headless=True)
    resultDict = {}
    for news in news_list:
        url = news["url"]
        print("크롤링 시작", flush=True)
        result = batchCrawler.crawl(url)
        print("크롤링 완료", flush=True)
        resultDict[url] = {
            "content" : result,
            "image_url" : news["image_url"]
        }
        time.sleep(0.5)
    batchCrawler.close()
    return analyzeAndAnswer(request.question, resultDict)
    

# 일반 질문 답변
def getAnswerWithoutAnalysis(question : str):
    return simpleAnswer(question)

