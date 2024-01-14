import os
import time
import asyncio

from bot.arxiv_api import fetch_arxiv_updates, parse_arxiv_response_re, query_arxiv, query_arxiv_list
from bot.utils import write_dict_to_json, read_json_to_dict
from bot.post import format_post_for_telegram
from bot.telegram_bot import send_message_to_channel
from bot.openai import summarize_abstract

def main():
    ## get all articles from arxiv published this month
    response_list = fetch_arxiv_updates()
    print("Parsing the response ...")
    entries = parse_arxiv_response_re(response_list)

    ## --- testing --- ##
    #write_dict_to_json(entries, 'data.json')
    #entries = read_json_to_dict('data.json')
    ## --- end of testing --- ##

    id_list = list(entries.keys())
    print(id_list)

    # get secret environment variables
    channel_id = os.getenv('CHANNEL_ID')
    bot_token = os.getenv('BOT_TOKEN')
    api_key = os.getenv('OPENAI_TOKEN')

    # query the list of articles to get full metadata
    #metadata = query_arxiv(id_list[0])
    metadata = query_arxiv_list(id_list)

    for item in metadata:
        print(item['title'])

        ai_summary = summarize_abstract(item['summary'], api_key)
        item['ai summary'] = ai_summary

        message = format_post_for_telegram(item)

        # post the message to the channel
        asyncio.run(send_message_to_channel(bot_token, channel_id, message))
        time.sleep(5)

if __name__ == "__main__":
    main()