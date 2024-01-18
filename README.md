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

## Dockerfile
Build the image
```
docker build -t your-app-name .
```
Specify and pass the environment variables in a secure way:
```
``` 

Run the container
```
docker run -d --name your-container-name -v /path/on/your/host:/usr/src/app/logs --env-file .env your-app-name
```
where `/path/on/your/host` is the path on you local disk that you want to attach (log file will be written there).  

## Configuration
Set up the following environment variables:

- `CHANNEL_ID`: The ID of the Telegram channel where updates will be posted.
- `BOT_TOKEN`: The token of your Telegram bot.
These can be set in your environment, or using a .env file which you can create at the root of your project:

```
CHANNEL_ID=your_channel_id
BOT_TOKEN=your_bot_token
```

## Usage
Run the script with:
```
python main.py
```
The script will automatically fetch updates from arXiv and post them to the configured Telegram channel.