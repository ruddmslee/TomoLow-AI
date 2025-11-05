FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY chat/ ./chat
COPY ./.env .

CMD ["uvicorn", "chat.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


