import openai
from openai import OpenAI
import logging

def summarize_abstract(abstract, api_key, model="gpt-3.5-turbo"):
    """
    Rewrites an abstract to be short and concise using OpenAI's GPT chat model.

    Args:
        abstract (str): The abstract text to be summarized.
        api_key (str): Your OpenAI API key.
        model (str): The model to use for summarization. Default is "gpt-3.5-turbo".

    Returns:
        str: A shorter, concise version of the abstract.
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(model=model,
                        messages = [{"role": "system", "content": "You are a helpful assistant."},
                                    {"role": "user", "content": f"Please summarize the following abstract in a short and concise way: {abstract}"},
                                ])
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
    
def convert_text_to_embedding(text: str, api_key: str, model:str="text-embedding-ada-002"):
    """
    Convert text into embeddings using the OpenAI GPT-3 API.

    Args:
        text (str): The text to convert into embeddings.
        api_key (str): Your OpenAI API key.
        model (str): The GPT-3 model to use
    Returns:
        str: The generated text-based embedding.
    Example:
        >> embedding = convert_text_to_embedding(api_key, input_text)
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.embeddings.create(
            input=text,
            model=model
        )

        embedding = response.data[0].embedding

        return embedding

    except Exception as e:
        return str(e)