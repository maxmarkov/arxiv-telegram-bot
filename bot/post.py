import os
import asyncio
import logging
from openai import OpenAI
from telegram import Bot
from datetime import datetime

class TelegramPost:
    """ A class for formatting a post for Telegram. """
    def __init__(self, article_info):
        self.article_info = article_info

        if not self.validate_article_info():
            logging.error("Invalid article_info dictionary.")
            raise ValueError("Invalid article_info dictionary.")

        if not self.check_env_variables():
            logging.error("Missing required environment variables.")
            raise EnvironmentError("Missing required environment variables.")

        self.article_info['ai summary'] = self.summarize_abstract(os.getenv('OPENAI_TOKEN'))

        self.message = self.format_post()

    def check_env_variables(self):
        """ Checks if required environment variables are set. """
        required_env_vars = ['OPENAI_TOKEN', 'BOT_TOKEN', 'CHANNEL_ID']
        all_vars_present = True

        for var in required_env_vars:
            if not os.getenv(var):
                logging.error(f"Environment variable {var} is not set.")
                all_vars_present = False

        return all_vars_present

    def validate_article_info(self):
        """ Validates the structure of the article_info dictionary. """
        required_keys = ['published', 'title', 'authors', 'summary', 'abstract_link']
        
        for key in required_keys:
            if key not in self.article_info or not self.article_info[key]:
                logging.error(f"Missing or empty key in article_info: {key}")
                return False
        return True

    def format_datetime(self):
        datetime_obj = datetime.fromisoformat(self.article_info['published'].rstrip("Z"))
        return datetime_obj.strftime("%d-%m-%Y")

    def summarize_abstract(self, api_key, model="gpt-3.5-turbo"):
        """ Rewrites an abstract to be short and concise using OpenAI's GPT chat model.
        """
        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please summarize the following abstract in a short and concise way: {self.article_info['summary']}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

    def format_post(self):
        """ Prepare the message for posting """
        published = self.format_datetime()

        title = self.article_info.get('title', 'No Title').replace('\n', '')
        authors = self.article_info.get('authors', 'No Authors')
        abstract = self.article_info.get('summary', 'No Summary').replace('\n', ' ')
        ai_summary = self.article_info.get('ai summary', 'No AI Summary').replace('\n', ' ')
        link = self.article_info.get('abstract_link', 'No Link')

        # Formatting the message
        message = f"📄 *Title:* {title}\n" \
                  f"👥 *Authors:* {authors} \n\n" \
                  f"🔍 *Abstract:*\n{abstract}\n\n" \
                  f"🧠 *AI Summary:*\n{ai_summary}\n\n" \
                  f"#finarxiv \n\n" \
                  f"Published on arXiv: {published}\n" \
                  f"🔗 [Read More]({link})"
        
        return message
    
    async def send_message_to_channel(self):
        """ Async function to send a message to the specified Telegram channel """
        if os.getenv('BOT_TOKEN') and os.getenv('CHANNEL_ID'):
            bot = Bot(token=os.getenv('BOT_TOKEN'),)
            await bot.send_message(chat_id=os.getenv('CHANNEL_ID'), text=self.message, parse_mode='Markdown')
        else:
            logging.error("Bot token or channel ID environment variables not provided.")

    def post_to_channel(self):
        """ Posting the message to the Telegram channel """
        asyncio.run(self.send_message_to_channel())