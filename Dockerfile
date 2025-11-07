FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    libnss3 \
    libxss1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libdbus-glib-1-2 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN playwright install chromium --with-deps

COPY chat/ ./chat
COPY ./.env .

CMD ["uvicorn", "chat.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


