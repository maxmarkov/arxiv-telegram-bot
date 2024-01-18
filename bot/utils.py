import json
from datetime import datetime, timedelta

def write_dict_to_json(data: dict, filename: str = "./test.json") -> None:
    """ Writes a given dictionary to a JSON file.
    Args:
        data (dict): The dictionary to be written to the file.
        filename (str): The name of the file to which the data is to be written.
    Returns:
        None
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def read_json_to_dict(filename: str = "./test.json") -> dict:
    """ Reads a JSON file and returns the data as a dictionary.
    Args:
        filename (str): The name of the file to be read.
    Returns:
        dict: The data read from the JSON file.
    """
    with open(filename, 'r') as file:
        return json.load(file)

def split_list_into_groups(input_list, group_size=10):
    """ Split a list into groups of specified size. Required since one can pass maximum 10 items per request to the arXiv API.

    Args:
        input_list (list): The input list to be split.
        group_size (int): The maximum number of items in each group (default is 10).

    Returns:
        List of lists: A list of lists, where each inner list contains up to 'group_size' items.
    """
    return [input_list[i:i + group_size] for i in range(0, len(input_list), group_size)]

def is_yesterday(date_string: str) -> bool:
    """ Checks if the given date is yesterday
    Args:
        date_string (str): The date string to be checked.
    Returns:
        bool: True if the date is yesterday, False otherwise. """
    input_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    
    current_date = datetime.utcnow()
    yesterday = current_date - timedelta(days=1)

    return input_date.date() == yesterday.date()

def remove_after_keywords(text):
    keyword = "Keywords:"
    index = text.find(keyword)
    if index != -1:
        return text[:index]
    else:
        return text 