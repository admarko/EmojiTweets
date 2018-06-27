________________________________________________________________________________
Contains:  
emoji_tweets.py     -Run this.  
                    -Usage: `python3 emoji_tweets.py [-h, --help] [-v, --version] [-n, --numtweets] [-q, --query] [-usa]`  
                      where `[-h]` is run for help, `[-v]` is the version number,
                      `[-n]` is the max number of tweets to scrape (100 by
                        default), [-q] is the search query to test, and `[-usa]`
                        is used to search domestically rather than internationally  
                    -Sample usage: `python3 emoji_tweets.py -n 10000 -q olympics` 
config.py 			-Stores API keys (not committed to Github) 
reports             -folder containing all output files
                    -files named: "report_[-n]_tweets_on_[-q]"  
README              -this file  
________________________________________________________________________________

This projects scrapes and geolocates tens of thousands of tweets looking at
linguistic data on the internet, specifically data on emoji usage.

Using the user inputted search query, this script searches through `[-n]` many
tweets and first filters out any statuses that do not contain an emoji. Based on
whether the user would like to look at tweets from the US or around the globe,
the script then attempts to geolocate the tweet (if possible) and sort into one
a few dictionaries created for the final report. If for any reason the script
crashes (connection error, API error, etc.) the final report will be published
for every tweet looked at so far. The `config.py` file is to hide my API keys 
protected from github with a `.gitignore` file

The key finding obtained from this project was that emojis tend to be used to
share feelings of happiness, laughter and excitement. While I originally
hypothesized that countries (or states) that were opposed to a given topic
indicated in the search country would produce more negative emojis, it turned
out that the origin location of the tweet had less impact on the sentiment
expressed through the emoji than the actual content of the search query. Or more
simply states, emoji usage is more dependent on status topic rather than
location.

Included in this repository is also the final paper I wrote for the Linguistics
class this project was originally for (Also the Latex code to go along with that
report).
