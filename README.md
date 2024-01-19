# ArXiv Telegram Bot
This Python project fetches the latest articles published on the arXiv platform and posts them to a [FinArxiv Telegram channel](https://t.me/finarxiv). It's designed to automate the process of keeping a Telegram audience updated with the latest academic papers in a specific category from arXiv.

## Features

- Fetch recent articles from arXiv.
- Parse the response to extract relevant information.
- Format the information for posting on Telegram.
- Post updates to a specified Telegram channel.

## Local installation
Before running the script, ensure you have Python installed on your system. Then, install the required dependencies:
```
pip install -r requirements.txt
```
and then run the code
```
python main.py
```

## Configuration

Set up the following environment variables:

- `CHANNEL_ID`: The ID of the Telegram channel where updates will be posted.
- `BOT_TOKEN`: The token of your Telegram bot.
- `OPENAI_TOKEN`: the OpenAI token

These can be set in your environment `.env` file which you can create at the root of your project:

```
CHANNEL_ID=your_telegram_channel_id
BOT_TOKEN=your_telegram_bot_token
OPENAI_TOKEN=your_openai_token
POSTGRES_NAME=your_postgres_dbname
POSTGRES_PORT=your_postgres_port
POSTGRES_USERNAME=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_TABLE=your_postgres_tqble
``` 

Make sure the port that you selected is not busy. The command 
```
sudo lsof -i :5432
```
must return nothing.

## Dockerfile

Build the image
```
docker build -t telearxiv .
```

Run the container
```
docker run -d --name telearxiv-container -p 5000:5000 -v /path/on/your/host:/usr/src/app/logs --env-file .env telearxiv
```
where `/path/on/your/host` is the path on you local disk that you want to attach (log file will be written there).  

## Usage
Run the script with:
```
python main.py
```
The script will automatically fetch updates from arXiv and post them to the configured Telegram channel.