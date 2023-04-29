In this project I lay out the steps to scrape historical data from the wayback machine, 
and use sentiment analysis to display historical trends of the emotional state of the 
internet in given time frames or around certain topics.

1. Scrape_From_Wayback Python Scraper 

scrape_from_wayback('reddit.com',20161122 ,2017,'titles','p','title','h3','h2',20)

To use this function you give an input url to search on the wayback machine then 2
dates to scrape between. The scraper first searches the wayback cdx serverside api for 
the datestamps pertaining to the url between the two dates. Then it crafts a list of urls 
with the input url and all of the collected datestamps Then makes page requests to this list
and searches for the next part of the input. Currently the functionallity is set to just 1 per day
To increase this we alter the function so that it will skip over a date once it has been 
in datesSaved n time or just get rid of the dates skip feature all together.

The next part of the input being a p for the html element to search for followed 
by a title the class of the html element to search for. the example h3 and h2
are optional alternative search features where you have it also grab text within 
additional elements. If you do not want these add None. You can also alter the 
function to add in additional class searches following the comments in the code.
Page requests will gather all of the text within these html elements between the 
two dates for up to the next number being the max number of page requests @ 20. 
This is set low to avoid the server starting to either kick you off. You can 
play around with increasing it or you can run the function in a loop with the 
savedate feature that the scrape_from_wayback function returns like the example 
in the bottom of the python file. 

2. Clean-Titles

In this jupyter notebook we go over the process of cleaning titles such that we can display the data we want accurately. 
This involves

3. Bert-S-Trainer

Once we have this list of titles it may be quite lengthy, and high cost model sentiment analysis
can be a lengthy process. In this file I layed out the steps to train a distillBert model to 
have the ability of binary text sentiment analysis with 99 accuracy to that of a top rated 
RoBerta Based Model. Bringing the time it takes to be able to process titles down well over 50%

3. Clean-Titles

In this jupyter notebook we go over the process of cleaning titles such that we can display the data we want accurately. 
First we concatenate all the files if we scraped the titles in batches. Then we remove alpha-numerica characters and ads
Then we delete duplicates. Then we order the titles by date. 
Next is an example of how to add sentiment analysis from a model deployed on the huggingface pipeline. For my project
I applied this to just 5300 random titles and the output was two columns with these 5300 titles and a 0/1 for negative
/ positive. This was the training data used to train a distillBert model to replicate its efficacy in seniment analysis
for reddit titles. The training set of 5000 had an accurary rate of 99% on the other 300 titles as the test set, after 3 epochs.
This process took roughly 1 hour. In contrast the process of going over 5300 titles with the RoBerta model took about 10 minutes
in a google collab to Bert-S's 3.5. 

4. nlp 

In this Jupyter Notebook we go over the processes of actually displaying relevant data from the titles we collected.

