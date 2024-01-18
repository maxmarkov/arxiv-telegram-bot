import os
import time
import asyncio
import logging 

from bot.arxiv_api import fetch_arxiv_updates, parse_arxiv_response_re, query_arxiv, query_arxiv_list
from bot.utils import write_dict_to_json, read_json_to_dict, is_yesterday, remove_after_keywords, split_list_into_groups, remove_none_from_list
from bot.post import format_post_for_telegram
from bot.telegram_bot import send_message_to_channel
from bot.openai import summarize_abstract
from bot.database import connect_to_postgres, check_id_and_insert, get_ids_not_in_database

logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    try:
        logging.info("Fetching recent arXiv updates...")
        response_list = fetch_arxiv_updates()
        logging.info("Parsing the response...")
        entries = parse_arxiv_response_re(response_list)

        ## --- testing --- ##
        #write_dict_to_json(entries, 'data.json')
        #entries = read_json_to_dict('data.json')
        ## --- end of testing --- ##

        id_list = list(entries.keys())
        id_list = remove_none_from_list(id_list)
        if len(id_list) == 0:
            raise Exception("No articles found in the id list.")
        else:
            logging.info(f"{len(id_list)} articles found: {id_list}\n")

        # get secret environment variables
        channel_id = os.getenv('CHANNEL_ID')
        bot_token = os.getenv('BOT_TOKEN')
        api_key = os.getenv('OPENAI_TOKEN')
        db_password = os.getenv('POSTGRES_PASSWORD')
        db_name = os.getenv('POSTGRES_DB')
        db_table = os.getenv('POSTGRES_TABLE')
        db_port = os.getenv('POSTGRES_PORT')

        id_groups = split_list_into_groups(id_list)
        metadata = []
        for id_group in id_groups:
            metadata += query_arxiv_list(id_group)
        logging.info(f"{len(metadata)} articles found.")
        time.sleep(5)

        conn, cursor = connect_to_postgres(password=db_password, database=db_name)

        if conn is None or cursor is None:
            raise Exception("Could not connect to the database.")

        ids_not_in_database = get_ids_not_in_database(id_list, cursor, db_table)

        if len(ids_not_in_database) > 0:

            logging.info(f"{len(ids_not_in_database)} articles to tbe submitted: {ids_not_in_database}")

            for i, item in enumerate(metadata):

                if id_list[i] in ids_not_in_database:
           
                    data = {"id": id_list[i],
                            "abstract_link": item['id'],
                            "pdf_link": entries[id_list[i]]['pdf_export_link'],
                            "updated": item['updated'],
                            "published": item['published'],
                            "title": entries[id_list[i]]['title'],
                            "authors": ', '.join(entries[id_list[i]]['authors']),
                            "summary": remove_after_keywords(item['summary'].replace('\n', ' ').replace('  ', ' ')),
                            "arxiv_comment": "",
                            "arxiv_primary_category": item['arxiv_primary_category']['term'],}
                    logging.info(data)
                    logging.info(f"Inserting {id_list[i]} into the database...")
                    check_id_and_insert(cursor, conn, db_table, data)
                    logging.info("Data inserted successfully.\n")

                    ai_summary = summarize_abstract(item['summary'], api_key)
                    item['ai summary'] = ai_summary

                    message = format_post_for_telegram(item)

                    asyncio.run(send_message_to_channel(bot_token, channel_id, message))
                    time.sleep(5)
        else:
            logging.info(f"No new articles have been found.\n")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()