import feedparser
from datetime import datetime

def fetch_crypto_news():
    # Use BBC RSS feed—for example, business news (adjust URL if needed)
    feed_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    feed = feedparser.parse(feed_url)
    news_items = []
    
    for entry in feed.entries:
        pub_date = datetime(*entry.published_parsed[:6]).strftime('%b %d')
        news_items.append({
            'date': pub_date,
            'title': entry.title,
            'link': entry.link,
            'description': entry.summary
        })

    # Optionally, sort by date or limit to a set number of items
    return news_items[:5]
