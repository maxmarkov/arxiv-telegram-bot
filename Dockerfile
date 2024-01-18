FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY bot/ bot/

# postgres database port
EXPOSE 5432

VOLUME /usr/src/app/logs

# Define environment variables
ENV CHANNEL_ID=your_channel_id
ENV BOT_TOKEN=your_bot_token
ENV OPENAI_TOKEN=your_openai_token
ENV POSTGRES_PASSWORD=your_postgres_password
ENV POSTGRES_DB=your_postgres_db
ENV POSTGRES_TABLE=your_postgres_table
ENV POSTGRES_PORT=your_postgres_port

CMD ["python", "./main.py"]
