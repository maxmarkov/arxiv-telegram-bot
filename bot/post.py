def format_post_for_telegram(article_info):
    """ Prepare the message for posting """
    title = article_info.get('title', 'No Title')
    authors = ', '.join([author['name'] for author in article_info.get('authors', [])])
    summary = article_info.get('summary', 'No Summary').replace('\n', ' ')
    link = article_info.get('link', 'No Link')

    # Formatting the message
    message = f"📄 *Title:* {title}\n" \
              f"👥 *Authors:* {authors}\n\n" \
              f"🔍 *Abstract:*\n{summary}\n\n" \
              f"🔗 [Read More]({link})"
    return message