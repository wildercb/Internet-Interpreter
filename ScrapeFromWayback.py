import sys
import requests as rq
from bs4 import BeautifulSoup as bs
from time import sleep
from time import time
from random import randint
from warnings import warn
import json
import pandas as pd
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

thisDateSave = 0
## Creating a loop to scrape from all pages
def scrape_from_wayback(mainUrl,from_date,to_date,output_file,look_for_element,look_for_class,look_for_element_alt,look_for_element_alt2,max_reqs,):
    
    title_list = []
    dates = []
    datesFull = []
    dayOfWeek = []
    polarities = []
    subjectivities = []
    bannedDays = []
    banned = []


    # Variable to store start and end dates
    # from_date = 20220310
    # to_date = 2023

    # Variable to name output file
    # output_file = 'titles'

    # Variables to state what html elements to parse for
    # If in need of multiple simply copy and past more variables and appropriate names
    # look_for_element = 'p'
    # look_for_class = 'title'
    # look_for_element_alt = 'h3'


    # Variable to store the minimum characters in a page that isnt returning blank or error
    min_page_char = 20000

    # Count number of requests and time

    reqs = 0

    start_time = time()

    # Set maximum number of requests per call - useful if you are getting kicked off

    # max_reqs = 20

    # Function to take in string in format of wayback machine date stamp and return day of the week


    def get_day_of_week(date_str):
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        date_obj = datetime.date(year, month, day)
        return date_obj.strftime("%A")

    # Function to catch if date will not have proper snapshots
    # Set maxCheck == maximum number of times you will check a datestamp


    def max_page_check(lst, target_string):
        count = 0
        maxCheck = 1
        for item in lst:
            if item == target_string:
                count += 1
                if count > maxCheck:
                    bannedDays.append(target_string)
                    return True
        return False

    # Reddit Homepage archive cdx search from date to date
    url = 'https://web.archive.org/cdx/search/cdx?url='+mainUrl+'&from='+str(from_date)+'&to='+str(to_date)+'&output=json'
    # May be useful to avoid getting booted from connection may need to alter for your system
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive,",
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }   # Put this -- rq.get(url,headers=headers).text -- below 
    urls = rq.get(url).text
    parse_url = json.loads(urls)  # parses the JSON from urls.

    # Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    for i in range(1, len(parse_url)):
        orig_url = parse_url[i][2]
        tstamp = parse_url[i][1]
        dstamp = tstamp[0:8]
        waylink = dstamp+'/'+orig_url
        url_list.append(waylink)

    # Compiles final url pattern.

    thisDate = 0 

    for url in url_list:

        # Break after maximum requests

        if reqs > max_reqs:
            break

        # Create the url to crawl

        full_url = 'https://web.archive.org/web/'+url
        thisDate = url[0:8]

            # Save each instance

        datesFull.append(thisDate)

            # Skip if we have already gone over date

        if thisDate in dates:
            continue
            # Use to clean dates before exporting to csv

        for date in dates:
            if date in bannedDays:
                dates.remove(date)

        # Skip to next date after max checks for datestamp

        if max_page_check(datesFull, thisDate) == True:
            continue

            # open page

        try:
            pg = rq.get(full_url).text
        except urllib.error.HTTPError as e:
            print('Error: {}'.format(e))
        except urllib.error.URLError as e:
            print('Error: {}'.format(e.reason))

        # Catch if it is returning blank or error page
        if len(pg) < min_page_char:
            bannedDays.append(thisDate)
            dates.append(thisDate)
                # print(pg)
            continue

        reqs += 1

        sleep(randint(10, 20))

        elapsed_time = time() - start_time
        print('Request: {}; Frequency: {} requests/s'.format(reqs, reqs/elapsed_time))
        print(thisDate)

        # Break once the max pages is reached

        if reqs > len(url_list):
            warn('No. of requests was greater than expected')
            break

        # parse html using beautifulsoup and store in soup

        soup = bs(pg, 'html.parser')
        soup

        '''
            # Wait until page has loaded.
            while True:

                titles = soup.find_all('h3')
                titles2 = soup.find_all('p', class_='title')
                if len(titles) > 0 or len(titles2) > 0:
                    break
                sleep(1)
                sleepCount = sleepCount + 1
                if sleepCount > 50:
                    break
            
            if sleepCount > 50:
                continue
        '''
        # Titles have been stored as h3 and as ps with the class title over time

        titles = soup.find_all(look_for_element, class_=look_for_class)

        titles = titles + soup.find_all(look_for_element_alt)

        titles = titles + soup.find_all(look_for_element_alt2)

            # max seconds to wait for page

        for title in titles:
            title = title.text.strip()
            print(title)
            title_list.append(title)

                # Confirm succesfully added dates for each title
            print(thisDate)
            dates.append(thisDate)

            # Now perform sentiment analysis on the titles
            ''' With vader 
            sid_obj= SentimentIntensityAnalyzer()
            print(sid_obj.polarity_scores(title.text)) '''

            # With TextBlob
            res = TextBlob(title)
            polarities.append(res.sentiment.polarity)
            subjectivities.append(res.sentiment.subjectivity)

                # Datestamp
            dayOfWeek.append(get_day_of_week(thisDate))

    # Print only a single instance of all the days we missed
    for day in bannedDays:
        if day not in banned:
            banned.append(day)
    print(banned)

    this_missed = pd.DataFrame({'MissedDays': banned})
    this_missed.to_csv(str(from_date)+str(to_date)+'missed.csv',index=False)

    this_df = pd.DataFrame({'title': title_list,
                            'date': dates,
                            'weekDay': dayOfWeek,
                            'Polarity': polarities,
                            'subjectivity': subjectivities})
    this_df.to_csv(output_file+str(from_date)+'-'+thisDate+'.csv', index=False)
    return thisDate


scrape_from_wayback('reddit.com',20161122 ,2017,'titles','p','title','h3','h2',20)


scrape_from_wayback('reddit.com',20161211 ,2017,'titles','p','title','h3','h2',20)



'''

while thisDateSave < 20230420:
    scrape_from_wayback('reddit.com',thisDateSave,20230420,'titles','p','title','h3','h2',20)
'''