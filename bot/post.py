from datetime import datetime

def format_post_for_telegram(article_info):
    """ Prepare the message for posting """

    datetime_obj = datetime.fromisoformat(article_info['published'].rstrip("Z"))
    published = datetime_obj.strftime("%d-%m-%Y")

    title = article_info.get('title', 'No Title').replace('\n', '')
    authors = ', '.join([author['name'] for author in article_info.get('authors', [])])
    abstract = article_info.get('summary', 'No Summary').replace('\n', ' ')
    ai_summary = article_info.get('ai summary', 'No AI Summary').replace('\n', ' ')
    link = article_info.get('link', 'No Link')

    # Formatting the message
    message = f"📄 *Title:* {title}\n" \
              f"👥 *Authors:* {authors}\n\n" \
              f"🔍 *Abstract:*\n{abstract}\n\n" \
              f"🧠 *AI Summary:*\n{ai_summary}\n\n" \
              f"#finarxiv \n\n" \
              f"Published on arXiv: {published}\n" \
              f"🔗 [Read More]({link})"
    return message