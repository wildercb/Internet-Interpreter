import os
import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep, time
from random import randint
from textblob import TextBlob

def scrape_from_wayback(main_url, from_date, to_date, output_file, elements_to_scrape, max_reqs):
    # Create 'output' directory if it doesn't exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    titles, dates, polarities, subjectivities, day_of_week = [], [], [], [], []
    banned_days, processed_dates = set(), set()

    def get_day_of_week(date_str):
        year, month, day = int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8])
        return datetime.date(year, month, day).strftime("%A")

    def is_banned(day):
        return day in banned_days

    start_time = time()
    reqs = 0
    min_page_char = 20000

    # Construct Wayback Machine URL for fetching archived pages
    url = f'https://web.archive.org/cdx/search/cdx?url={main_url}&from={from_date}&to={to_date}&output=json'
    response = requests.get(url)
    parse_url = response.json()

    for item in parse_url[1:]:
        if reqs >= max_reqs:
            break

        timestamp, original_url = item[1], item[2]
        current_date = timestamp[:8]

        if current_date in processed_dates or is_banned(current_date):
            continue

        wayback_url = f'https://web.archive.org/web/{timestamp}/{original_url}'
        try:
            page = requests.get(wayback_url).text
            if len(page) < min_page_char:
                banned_days.add(current_date)
                continue

            soup = BeautifulSoup(page, 'html.parser')
            for element in elements_to_scrape:
                tag, class_name = element.get('tag', '*'), element.get('class', '')
                for found_element in soup.find_all(tag, class_=class_name if class_name else None):
                    title = found_element.text.strip()
                    titles.append(title)
                    dates.append(current_date)
                    analysis = TextBlob(title)
                    polarities.append(analysis.sentiment.polarity)
                    subjectivities.append(analysis.sentiment.subjectivity)
                    day_of_week.append(get_day_of_week(current_date))

            processed_dates.add(current_date)
            reqs += 1
            sleep(randint(10, 20))
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')

    missed_days = pd.DataFrame({'MissedDays': list(banned_days)})
    missed_days.to_csv(os.path.join(output_dir, f'{from_date}_{to_date}_missed.csv'), index=False)

    data = pd.DataFrame({'Title': titles, 'Date': dates, 'WeekDay': day_of_week, 'Polarity': polarities, 'Subjectivity': subjectivities})
    data.to_csv(os.path.join(output_dir, f'{output_file}_{from_date}_{current_date}.csv'), index=False)

    return current_date

# Example usage
elements = [
    {'tag': 'p', 'class': 'title', 'id': 'None'},
    {'tag': 'div', 'class': 'content'},
    {'tag': 'span'}
]
# scrape_from_wayback('reddit.com', 20161122, 2017, 'titles', elements_to_scrape, 20)


import sys
import json

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python scraper.py main_url from_date to_date output_file elements_to_scrape max_reqs")
        sys.exit(1)

    main_url = sys.argv[1]
    from_date = int(sys.argv[2])
    to_date = int(sys.argv[3])
    output_file = sys.argv[4]
    elements = json.loads(sys.argv[5])
    max_reqs = int(sys.argv[6])

    scrape_from_wayback(main_url, from_date, to_date, output_file, elements, max_reqs)
