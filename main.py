import os
import sys
import time
import asyncio
import logging 
import argparse

from dotenv import load_dotenv
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler

from bot.arxiv_api import ArxivFetcher
from bot.post import format_post_for_telegram
from bot.telegram_bot import send_message_to_channel
from bot.openai import summarize_abstract, convert_text_to_embedding
from bot.database import connect_to_postgres, check_id_and_insert, get_ids_not_in_database, retrieve_first_n_rows

LOG_PATH = './logs'
os.makedirs(LOG_PATH, exist_ok=True)

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    filename=f'{LOG_PATH}/bot.log',
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# load from .env file if present
load_dotenv()

def run_scheduler(scheduler_type: str) -> None:
    """ Run the main function from a scheduler (either blocking or background).
    Args:
        scheduler_type (str): The type of scheduler to run. Can be 'block' or 'background'.
    Returns:
        None
    """
    if scheduler_type == 'block':
        scheduler = BlockingScheduler()
        job_id = scheduler.add_job(main, 'interval', seconds=30)
        scheduler.start()
    elif scheduler_type == 'background':
        scheduler = BackgroundScheduler()
        job_id = scheduler.add_job(main, 'interval', seconds=5)
        scheduler.start()
        time.sleep(60)
    else:
        logging.error("Invalid scheduler type. Must be 'block' or 'background'.")
        raise Exception("Invalid scheduler type. Must be 'block' or 'background'.")

def main():
    try:
        fetcher = ArxivFetcher(category='q-fin.PM')
        logging.info("Fetching recent arXiv updates...")
        response = fetcher.fetch_updates()
        logging.info("Parsing the response...")
        entries = fetcher.parse_arxiv_response_re(response)

        #fetcher = ArxivFetcher.load_from_json('fetcher_state.json')
        metadata = fetcher.fetch_metadata()

        conn, cursor = connect_to_postgres(password=os.getenv('POSTGRES_PASSWORD'),
                                           database=os.getenv('POSTGRES_DB'),
                                           port=os.getenv('POSTGRES_PORT'))#, host='host.docker.internal')

        if conn is None or cursor is None:
            raise Exception("Could not connect to the database.")
        
        # ## === embedding === ##
        # records = retrieve_first_n_rows(n=2, cursor=cursor, table_name=os.getenv('POSTGRES_TABLE'))
        # summary = records[0][2].replace("\n", " ")
        # embedding = convert_text_to_embedding(summary, os.getenv('OPENAI_TOKEN'))
        # ## === end of embedding === ##

        ids_not_in_database = get_ids_not_in_database(fetcher.ids, cursor, os.getenv('POSTGRES_TABLE'))

        if len(ids_not_in_database) > 0:

            logging.info(f"{len(ids_not_in_database)} articles to be submitted: {ids_not_in_database}")

            for i, item in enumerate(metadata):
                print(metadata[i]['id'])

                if fetcher.ids[i] in ids_not_in_database:
                    
                    logging.info(metadata[i])
                    logging.info(f"Inserting {fetcher.ids[i]} into the database...")
                    check_id_and_insert(cursor, conn, os.getenv('POSTGRES_TABLE'), metadata[i])
                    logging.info("Data inserted successfully.\n")

                    ai_summary = summarize_abstract(item['summary'], os.getenv('OPENAI_TOKEN'))
                    item['ai summary'] = ai_summary

                    message = format_post_for_telegram(item)

                    asyncio.run(send_message_to_channel(os.getenv('BOT_TOKEN'), os.getenv('CHANNEL_ID'), message))
                    time.sleep(5)
        
        else:
            logging.info(f"No new articles have been found.\n")

        cursor.close()
        conn.close()

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some arguments.')
    
    parser.add_argument('--scheduler', choices=['block', 'background', None], default=None,
                        help='Type of scheduler to use (block, background, or None)')
    args = parser.parse_args()

    if args.scheduler is None:
        main()
    else:
        run_scheduler(args.scheduler)