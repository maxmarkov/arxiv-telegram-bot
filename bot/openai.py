import openai

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

    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following abstract in a short and concise way: {abstract}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None