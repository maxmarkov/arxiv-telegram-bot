import re
import json
import time
import html
import logging
import urllib
import urllib.request
import feedparser

from datetime import datetime

class ArxivFetcher:
    """ A class to fetch articles metadata using arXiv API. """
    def __init__(self, category: str='q-fin.PM', date: str=""):
      """ Initialize the ArxivFetcher with a default category and date.
      Args:
          category (str): The category of articles to fetch from the arXiv API. 
          date (str): The date to fetch articles from in the format 'yymm'. Defaults to the current date.
      """
      self.category = category
      self.date = date if date else self.get_current_date_formatted()
      self.validate_date_format(self.date)
      self.entries = {}
      self.ids = []

    def get_current_date_formatted(self) -> str:
      """ Get the current date and format it as a string in the "yymm" format.
      Returns:
          str: The current date formatted as "yymm", where 'yy' is the last two digits of the year
              and 'mm' is the month.
      """
      current_date = datetime.now()
      formatted_date = current_date.strftime("%y%m")
      return formatted_date

    def validate_date_format(self, date: str) -> None:
      """ Validate the date format. """
      if not re.match(r"\d{4}", date):
        error_message = "Date must be in 'yymm' format or empty"
        logging.error(error_message)
        raise ValueError(error_message)

    def fetch_updates(self) -> bytes:
      """ Fetches the list of articles in a specified category from the arXiv API using the urllib.request module.

      This function constructs a URL for the arXiv API request based on the given category and the current date, 
      formatted appropriately. It then makes a request to the arXiv API and returns the response in bytes format.

      Returns:
        bytes: The raw response from the arXiv API, containing the list of articles in the specified category.
              This is returned as a byte string.

      Example:
        >>> fetcher = ArxivFetcher(category='q-fin.PM')
        >>> print_response(response)
      """
      url = f'http://export.arxiv.org//list/{self.category}/{self.date}'
      logging.info(url)
      response = urllib.request.urlopen(url).read()
      return response

    @staticmethod
    def print_response(response: bytes) -> None:
      """ Print a byte string response.
      Args:
          response (bytes): The raw response from the arXiv API, containing the list of articles in the specified category.
                  This is returned as a byte string.
      """
      response_str = response.decode('utf-8')
      print(response_str)

    def parse_arxiv_response_re(self, response: bytes) -> dict:
      """ Parses a response of a list query from the arXiv API with regular expressions and extracts relevant information
      about each article.

      This function decodes the given byte-string response from the arXiv API, and uses regular expressions to extract 
      various details like the total number of entries, titles, comments, authors, and paper IDs. Each article's details 
      are compiled into a dictionary.

      Args:
        response (bytes): The raw response in bytes format obtained from the arXiv API.
      Returns:
        dict: A dictionary where each key is an arXiv paper ID and the value is another dictionary containing 
            details of the paper such as title, authors, and a direct link to the PDF version.
      """
      response_str = response.decode('utf-8')

      entries_pattern = r'total of (\d+) entries'
      n_entries = re.search(entries_pattern, response_str).group(1) if re.search(entries_pattern, response_str) else None
      logging.info(f"Total number of entries: {n_entries}")

      title_pattern = r'<span class="descriptor">Title:</span>([^\n]*)'
      titles = [html.unescape(string).lstrip().replace("  ", " ") for string in re.findall(title_pattern, response_str)]
      logging.info(f"Titles: {', '.join(titles)}")

      comment_pattern = r'<span class="descriptor">Comments:</span>([^\n]*)'
      comments = [html.unescape(string).lstrip().replace("  ", " ") for string in re.findall(comment_pattern, response_str)]

      authors_pattern = r'<div class="list-authors">(.*?)</div>'
      authors = [re.findall(r'<a href="[^"]*">(.*?)</a>', author) for author in re.findall(authors_pattern, response_str, re.DOTALL)]

      links_pattern = r'<dt><a name="item(\d+)">\[\d+\]</a>(.*)'
      links = re.findall(links_pattern, response_str)

      ids = []
      arxiv_id_pattern = r'arXiv:(\d+\.\d+)'
      for link in links:
        arxiv_id = re.search(arxiv_id_pattern, link[1]).group(1) if re.search(arxiv_id_pattern, link[1]) else None
        ids.append(arxiv_id)

      # gather all results together
      results = {}
      for i, id in enumerate(ids):
        if id is not None:
          results[id] = {'title': titles[i], 'authors': authors[i], 'pdf_export_link': f'http://export.arxiv.org/pdf/{id}'}

      if results:
        logging.info(f"{len(ids)} articles found: {ids}\n")
        self.entries = results
        self.ids = list(results.keys())
      else:
        logging.info("No articles found in the entries.\n")

      return results

    def save_to_json(self, filepath: str) -> None:
      """ Save the current state of the object to a JSON file.
      Args:
          filepath (str): The file path where the object's state will be saved.
      Example:
          >>> fetcher = ArxivFetcher(category='q-fin.PM')
          >>> fetcher.save_to_json('fetcher.json')
      """
      with open(filepath, 'w') as file:
          json.dump({
              'category': self.category,
              'date': self.date,
              'entries': self.entries,
              'ids': self.ids
          }, file)
      logging.info(f"ArxivFetcher state saved to {filepath}")

    @classmethod
    def load_from_json(cls, filepath: str):
      """ Load the state of the object from a JSON file.     
      Args:
          filepath (str): The file path from where the object's state will be loaded.
      Returns:
          ArxivFetcher: An instance of ArxivFetcher with the state restored from the JSON file.
      Example:
          >>> fetcher = ArxivFetcher.load_from_json('fetcher.json')
      """
      with open(filepath, 'r') as file:
          data = json.load(file)
          fetcher = cls(data['category'], data['date'])
          fetcher.entries = data.get('entries', {})
          fetcher.ids = data.get('ids', [])
      logging.info(f"ArxivFetcher state loaded from {filepath}")
      return fetcher

    def split_list_into_groups(self, group_size=10):
      """ Split a list into smaller groups.
      Args:
          group_size (int): The maximum size of each group.
      Returns:
          list of lists: The original list split into smaller groups.
      """
      if group_size > 10:
        logging.warning("Group size is greater than 10. This may cause the arXiv API to return an error.")
        
      for i in range(0, len(self.ids), group_size):
        yield self.ids[i:i + group_size]

    @staticmethod
    def query_arxiv(ids) -> bytes:
      """ Query arXiv API to get metadata of articles with certain IDs.
      Args:
        ids: A single ID as a string or a list of IDs to be queried.
      Returns:
        bytes: The raw response from the arXiv API, containing the metadata of the article(s) with the specified ID(s).
             This is returned as a byte string.
      """
      if isinstance(ids, str):
        ids = [ids]

      joined_ids = ','.join(ids)
      query = f"http://export.arxiv.org/api/query?id_list={joined_ids}"
      logging.info(f'Query: {query}')

      r = urllib.request.urlopen(query)

      feedparser.mixin._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
      feedparser.mixin._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

      feed = feedparser.parse(r)
      return feed.entries

    @staticmethod
    def remove_after_keywords(text: str) -> str:
      """ Remove everything after the keyword 'Keywords:'.
      Args:
        text: The text to be processed.
      Returns:
        str: The processed text.
      """
      keyword = "Keywords:"
      index = text.find(keyword)
      if index != -1:
        return text[:index]
      else:
        return text 
        
    def fetch_metadata_groups(self) -> list:
      """ Fetch metadata for groups of article IDs.
      Returns:
        list of dicts: Metadata of the articles with the specified IDs.
      """
      metadata = []
      id_groups = self.split_list_into_groups()
      for id_group in id_groups:
        logging.info(f"Fetching metadata for IDs: {id_group}")
        metadata += self.query_arxiv(id_group)
        time.sleep(5)  # Wait for 5 seconds before the next API call
      return metadata

    def process_metadata_item(self, item, id_index):
      """ Process a single metadata item.
      Args:
        item: The metadata item to process.
        id_index: The index of the corresponding ID in self.ids.
      Returns:
        dict: Processed metadata item.
      """
      id = self.ids[id_index]
      entry = self.entries[id]
      return {
          "id": id,
          "abstract_link": item['id'],
          "pdf_link": entry['pdf_export_link'],
          "updated": item['updated'],
          "published": item['published'],
          "title": entry['title'],
          "authors": ', '.join(entry['authors']),
          "summary": self.remove_after_keywords(item['summary'].replace('\n', ' ').replace('  ', ' ')),
          "arxiv_comment": "",
          "arxiv_primary_category": item['arxiv_primary_category']['term']}

    def fetch_metadata(self):
      """ Fetch metadata for a list of article IDs.
      Returns:
        list of dicts: Metadata of the articles with the specified IDs.
      Example:
        >>> fetcher = ArxivFetcher(category='q-fin.PM')
        >>> metadata = fetcher.fetch_metadata()
      """
      metadata = []
      if not self.ids:
        logging.warning("No article IDs found.")
        return metadata

      fetched_metadata = self.fetch_metadata_groups()
      logging.info(f"Fetched metadata of {len(fetched_metadata)} articles.")

      processed_data = [self.process_metadata_item(item, i) for i, item in enumerate(fetched_metadata)]
      logging.info(f"Processed metadata of {len(processed_data)} articles.")
      return processed_data