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