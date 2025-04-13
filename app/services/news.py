import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_crypto_news():
    url = "https://www.coindesk.com/latest-crypto-news"
    response = requests.get(url)
    
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    stories = soup.find_all('div', class_='bg-white flex gap-6 w-full shrink justify-between')

    news_items = []
    for story in stories:
        title_tag = story.find('h2', class_='font-headline-xs font-normal')
        link_tag = story.find('a', class_='text-color-charcoal-900 mb-4 hover:underline')
        time_tag = story.find('span', class_='font-metadata text-color-charcoal-600 uppercase')
        
        if title_tag and link_tag and time_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            date = time_tag.get_text(strip=True)
            
            try:
                if 'minute' in date.lower() or 'hour' in date.lower():
                    date = datetime.now().strftime('%b %d')
            except:
                date = datetime.now().strftime('%b %d')
            
            news_items.append({
                'date': date,
                'title': title,
                'link': 'https://www.coindesk.com' + link,
                'description': ''
            })
    
    return news_items[:5]
