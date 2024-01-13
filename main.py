from bot.arxiv_api import fetch_arxiv_updates, parse_arxiv_response_re, query_arxiv, query_arxiv_list
from bot.utils import write_dict_to_json, read_json_to_dict

def main():
    ## get all articles from arxiv published this ;onth
    #response_list = fetch_arxiv_updates()
    #print("Parsing the response ...")
    #entries = parse_arxiv_response_re(response_list)

    ## --- testing --- ##
    #write_dict_to_json(entries, 'data.json')
    entries = read_json_to_dict('data.json')
    ## --- end of testing --- ##

    id_list = list(entries.keys())
    print(id_list)

    # query the list of articles to get full metadata
    #metadata = query_arxiv(id_list[0])
    metadata = query_arxiv_list(id_list)

    print(metadata)

if __name__ == "__main__":
    main()