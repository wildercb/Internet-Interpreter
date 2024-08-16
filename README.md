###How to interact with this project

In this project we go over using the wayback machine as a source of historical data from the internet. We provide a wayback machine scraper to gather data from dates to another from certain sites. As well as a data pipeline to view reports about the state of the internet or those sites from the data collected. 

####Gather data from wayback machine 
######Scrape from wayback.py: 
Use jupyter notebook or 
python scrapeFromWayback(url, datestamp from, datestamp to, output file name, elements_to_scrape, max requests)
Example: python scrapeFromWayback.py reddit.com 20161122 2017 titles '[{"tag": "p", "class": "title", "id": null}, {"tag": "div", "class": "content"}, {"tag": "span"}]' 20

####Analyze and report on the content 
######Clean Titles.ipynb
Data cleaning operations 

######Nlp.ipynb 
Using nlp insights to gather insights from data and display in readable graphs

