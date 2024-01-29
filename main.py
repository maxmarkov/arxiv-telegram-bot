import os
import sys
import time
import asyncio
import logging 
import argparse

from dotenv import load_dotenv
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler

from bot.arxiv_api import ArxivFetcher
from bot.post import TelegramPost
from bot.telegram_bot import send_message_to_channel
from bot.openai import summarize_abstract, convert_text_to_embedding
from bot.database import PostgresHandler

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

        db = PostgresHandler(database=os.getenv('POSTGRES_DB'),
                            user=os.getenv('POSTGRES_USERNAME'),
                            password=os.getenv('POSTGRES_PASSWORD'),
                            host=os.getenv('POSTGRES_HOST'),
                            port=os.getenv('POSTGRES_PORT'),
                            table_name=os.getenv('POSTGRES_TABLE'))
        
        # ## === embedding === ##
        # records = db.retrieve_rows(os.getenv('POSTGRES_TABLE'), n=2)
        # summary = records[0][2].replace("\n", " ")
        # embedding = convert_text_to_embedding(summary, os.getenv('OPENAI_TOKEN'))
        # ## === end of embedding === ##

        metadata_selected = db.select_metadata(metadata)

        if metadata_selected:

            for item in metadata_selected:
                  
                logging.info(f"Inserting {item['id']} into the database...")
                db.check_id_and_insert(os.getenv('POSTGRES_TABLE'), item)
                logging.info("Data inserted successfully.\n")

                telegram_post = TelegramPost(item)
                telegram_post.post_to_channel()
                time.sleep(5)

        db.close_connection()

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