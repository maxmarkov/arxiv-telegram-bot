import json

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