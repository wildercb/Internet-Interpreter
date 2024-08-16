To use:

Scrape from wayback.py: 

Use jupyter notebook or 
python scrapeFromWayback(url, datestamp from, datestamp to, output file name, elements_to_scrape, max requests)


Example: python scrapeFromWayback.py reddit.com 20161122 2017 titles '[{"tag": "p", "class": "title", "id": null}, {"tag": "div", "class": "content"}, {"tag": "span"}]' 20


Clean Titles.ipynb

Operations to clean up selection and apply sentiment analysis

Nlp.ipynb 

Using nlp insights to gather insights from data and display in readable graphs

