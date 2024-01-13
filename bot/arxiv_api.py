import re
import html
import urllib
import urllib.request
import feedparser

from datetime import datetime

def get_current_date_formatted() -> str:
  """ Get the current date and format it as a string in the "yymm" format.

  Returns:
      str: The current date formatted as "yymm", where 'yy' is the last two digits of the year
          and 'mm' is the month.
  """
  current_date = datetime.now()
  formatted_date = current_date.strftime("%y%m")
  return formatted_date

def fetch_arxiv_updates(cat: str = 'q-fin.PM') -> bytes:
  """ Fetches the list of articles in a specified category from the arXiv API using the urllib.request module.

  This function constructs a URL for the arXiv API request based on the given category and the current date, 
  formatted appropriately. It then makes a request to the arXiv API and returns the response in bytes format.

  Args: 
    cat (str): The category of articles to fetch from the arXiv API. 
              Default is 'q-fin.PM' (Quantitative Finance - Portfolio Management).
              The category should be specified in the format 'subject.Class' 
              as per arXiv's categorization.
  Returns:
    bytes: The raw response from the arXiv API, containing the list of articles in the specified category.
          This is returned as a byte string.

  Example:
    >>> response = fetch_arxiv_updates('cs.LG')
    >>> print_response(response)
  """
  formatted_current_date = get_current_date_formatted()

  URL = f'http://export.arxiv.org//list/{cat}/{formatted_current_date}'
  print(URL)
  response = urllib.request.urlopen(URL).read()
  return response

def print_response(response: bytes) -> None:
  """ Print a byte string response:
  Args:
    response (bytes): The raw response from the arXiv API, containing the list of articles in the specified category.
                      This is returned as a byte string."""
  response_str = response.decode('utf-8')
  print(response_str)

def parse_arxiv_response_re(response: bytes) -> dict:
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

  results = {}

  # total number of papers
  entries_pattern = r'total of (\d+) entries'
  if re.search(entries_pattern, response.decode('utf-8')):
    n_entries = re.search(entries_pattern, response.decode('utf-8')).group(1)
  else:
    n_entries = None

  # extract the title
  title_pattern = r'<span class="descriptor">Title:</span>([^\n]*)'
  titles = re.findall(title_pattern, response.decode('utf-8'))
  titles = [html.unescape(string).lstrip().replace("  ", " ") for string in titles]

  # extract the comments
  comment_pattern = r'<span class="descriptor">Comments:</span>([^\n]*)'
  comments = re.findall(comment_pattern, response.decode('utf-8'))
  comments = [html.unescape(string).lstrip().replace("  ", " ") for string in comments]

  # extract the list of authors
  authors_pattern = r'<div class="list-authors">(.*?)</div>'
  authors = re.findall(authors_pattern, response.decode('utf-8'), re.DOTALL)
  author_names_pattern = r'<a href="[^"]*">(.*?)</a>'
  authors = [re.findall(author_names_pattern, author) for author in authors]

  # extract all paper ids
  ids = []
  links_pattern = r'<dt><a name="item(\d+)">\[\d+\]</a>(.*)'
  links = re.findall(links_pattern, response.decode('utf-8'))

  arxiv_id_pattern = r'arXiv:(\d+\.\d+)'
  for link in links:
    if re.search(arxiv_id_pattern, link[1]):
      arxiv_id = re.search(arxiv_id_pattern, link[1]).group(1)
    else:
      arxiv_id = None
    ids.append(arxiv_id)

  # gather all results together
  for i, id in enumerate(ids):
    results[id] = {'title': titles[i], 'authors': authors[i], 'pdf_export_link': f'http://export.arxiv.org/pdf/{id}'}

  return results

def query_arxiv(id: str) -> bytes:
  """ Query arxiv API to get metadata of the article with certain ID
  Args:
    id (str): ID of the article to be queried
  Returns:
    bytes: The raw response from the arXiv API, containing the metadata of the article with the specified ID.
          This is returned as a byte string.
  """
  query = f"http://export.arxiv.org/api/query?id_list={id}"
  print(f'Query: {query}')

  r = urllib.request.urlopen(query)

  feedparser.mixin._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
  feedparser.mixin._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
  feed = feedparser.parse(r)
  return feed.entries

def query_arxiv_list(id_list: list) -> bytes:
  """ Query arxiv API to get metadata of multiple articles from the list of IDs """
  joined_ids = ','.join(id_list)
  query = f"http://export.arxiv.org/api/query?id_list={joined_ids}"
  print(f'Query: {query}')

  r = urllib.request.urlopen(query)

  feedparser.mixin._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
  feedparser.mixin._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
  feed = feedparser.parse(r)
  return feed.entries