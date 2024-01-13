import asyncio
import requests
import telegram

from telegram import Bot
from urllib.parse import quote

def get_messages_from_channel(token, limit=10) -> dict:
  """ Get messages from a channel in Telegram.
  Allows to get channel ID, title, and username (if there is at least one message in the channel).

  Args:
    token (str): Bot token.
    limit (int): Number of updates to retrieve (default is 10).
  Returns:
    response (dict): JSON dictionary with response.
  """
  url = f"https://api.telegram.org/bot{token}/getUpdates?limit={limit}"

  try:
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    if not data.get('result'):
      raise ValueError("error: No messages found in the channel.")
    return data

  except requests.RequestException as e:
      raise ValueError("error: " + str(e))

def post_message_to_channel(token, channel_id, message):
  """ Post message to Telegram channel using the requests library.
  For the Telegram Bot API, when you send a message using the sendMessage endpoint, the response includes
  details about the sent message. This is part of the Telegram API's design to provide immediate feedback
  about the action performed. The response typically includes:

    - Confirmation that the message was sent successfully.
    - Details of the sent message, like the message ID, the chat ID where it was sent, the date and time it was sent,
      and the content of the message itself.

  Args:
    token (str): Bot token.
    channel_id (str): Channel ID where the message will be posted.
    message (str): The message to be posted.
  Returns:
    response (dict): JSON dictionary with the response.

  """
  url = f"https://api.telegram.org/bot{token}/sendMessage"
  data = {"chat_id": channel_id,
          "text": message
          }
  try:
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

  except requests.RequestException as e:
    raise ValueError("error"+ str(e))
  
async def send_message_to_channel(token: str, channel_id: str, message:str):
  """ Async function to send a message to the specified Telegram channel """
  bot = Bot(token=token)
  await bot.send_message(chat_id=channel_id, text=message, parse_mode='Markdown')