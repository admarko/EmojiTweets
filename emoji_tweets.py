#  emoji_tweets
#  Based off final proj for LING 23700: Langugage & the Internet (3/9/18)
#  Last Modified by Alex Markowitz on 6/17/18.
import os                               # For report logging
import json                             # JSON formatting
import emoji                            # emoji database
import tweepy                           # twitter parsing
import pprint                           # Data Pretty Printer
import config                           # For API keys stored in separate file
import argparse                         # command line interface
import googlemaps                       # googlemaps api
import matplotlib.pyplot as plt         # graphing
import pandas as pd                     # data
import numpy as np                      # data
from datetime import datetime           # Timer
from operator import itemgetter         # Dictionary sort
from tqdm import tqdm                   # progress bar

# Parse command line options and set timer
startTime = datetime.now()
parser = argparse.ArgumentParser("python emoji_tweets.py", usage='%(prog)s [-h] [-v, --version] [-n, --numtweets] [-q, --query] [-usa]')
parser.add_argument("-v", "--version", help="version number of application", action="store_true")
parser.add_argument("-n", "--num", type=int, default=100, help="amount of tweets to scrape")
parser.add_argument("-q", "--query", help="query to search on", metavar='')
parser.add_argument("-usa", help="international by default", action="store_true")
args = parser.parse_args()

if args.version:
    print("Version 2.1 of emoji_tweets")
    exit()

if not args.query:
    print("You must enter a search query. Try again...")
    exit()

#########################
###  Global Variables ###
#########################

international = not args.usa        # False searches domestically
search_query = args.query           # query to search for on twitter
MAX_TWEETS = args.num               # Total number of tweets to scrape
tweets_per_query = 100              # 100 tweets at once

# dictionaries
emoji_map = {}
location_map = {}
emoji_count_map = {}

states = {'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois',
'Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland',
'Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana',
'Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York',
'North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania',
'Rhode Island', 'South Carolina','South Dakota','Tennessee','Texas','Utah',
'Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'};

#################
#####  APIs #####
#################

# Google Maps Key: 4 keys to deal with Google's limits
gmaps = googlemaps.Client(key=config.gmapkey2) 

# Twitter API keys: using a Tweepy wrapper
auth = tweepy.AppAuthHandler(config.consumer_key, config.consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print("Can't Authenticate")
    sys.exit(-1)

# pause tweets
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(10 * 30)

##########################
#####  Emoji Methods #####
##########################

# Return true if char is an emoji
def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI

# Return true if string contains an emoji
def status_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False

#############################
#####  Location Methods #####
#############################

# parse GoogleMaps JSON response
def getLocation(addr):
    loc = ""
    addCompLen = len(addr)
    for  i in range(0, addCompLen):
        try:
            if international:
                if (addr[i]["types"][0] == "country"):
                    loc += addr[i]["long_name"]
            else:
                if (addr[i]["long_name"] in states):
                    loc += addr[i]["long_name"]
        except:
            print(" Error: country doesn't exist in JSON")
            report(stat, emojistat, hasLoc)
    return loc

# Return true if tweet came from valid location as determined by GoogleMaps API
def status_has_location(status):
    initloc = status.user.location
    if (initloc):
        try:
            # TODO: try saving this as a local var: geoloc = gmaps.geocode(loc)
            if (gmaps.geocode(initloc)):
                location = getLocation(gmaps.geocode(initloc)[0]["address_components"])
                if location is not '':
                    insert_location_map(location, status.text)
                    insert_emoji_map(status.text, location)
                    return True;
        except Exception as e:
            print (" GoogleMaps API error: " + str(e))
            report(stat, emojistat, hasLoc)
    else:
        return False;

###############################
#####  Dictionary Methods #####
###############################

#insert country-emoji pair into map
def insert_location_map(location, status):
    for char in status:
        if(char_is_emoji(char)):
            if location in location_map:
                location_map[location].append(char)
            else:
                location_map[location] = [char]

# insert emoji-country pair into map
def insert_emoji_map(status, location):
    for char in status:
        if(char_is_emoji(char)):
            if char in emoji_map:
                emoji_count_map[char] += 1
            else:
                emoji_count_map[char] = 1

            if location is not "none":
                if char in emoji_map:
                    # if location in emoji_map[char]:
                    #     temp = emoji_map[char][location].get()
                    #     emoji_map[char][location] = temp + 1
                    # else: 
                    #     emoji_map[char].append({location, 1})
                    emoji_map[char].append(location);
                else:
                    emoji_map[char] = [location]
                    #emoji_map[char] = {location, 1};



# Buils the forward trie out of all words from the corpus
# help from: https://www.programiz.com/python-programming/methods/dictionary/setdefault
def build_trie(words, trie):
    for word in words:
        temp = trie
        wordtemp = temp
        temp = temp.setdefault(word[:k], {"count": 0})
        for char in word[k:]:
            wordtemp = temp
            temp = temp.setdefault(char, {"count": 0})
            wordtemp["count"] = len(wordtemp) - 1
        temp = temp.setdefault('#','#')                  #end of word signal




################################
#####  main script methods #####
################################

# Helper for print formatting of timer in final report
def timehelper(endtime):
    hours, remainder = divmod(endtime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0.0:
        hours = ""
    else: 
        hours = str(int(hours)) + "h "
    if minutes == 0.0:
        minutes = ""
    else: 
        minutes = str(int(minutes)) + "m "
    seconds = str(round(seconds, 2)) + "s"
    return hours + minutes + seconds

# Print final report with statistics to console
def report(stat, emojistat, hasLoc):
    # Output set up
    filename = "report_" + str(stat) + "_tweets_on_" + search_query + ".txt"
    file = open(os.path.join('reports',filename), "w")
    pp = pprint.PrettyPrinter(indent=4, stream=file)

    # Output header
    file.write("Final Report:\n\n")
    locale = 'internationally' if international else 'domestically'
    file.write("%s Total tweets were looked at on search query \"%s\" %s\n" %(stat, search_query, locale))
    file.write("%s of those tweets contained emojis\n" %(emojistat))
    file.write("%s of Emoji Tweets had locations\n" %(hasLoc))
    time = timehelper(datetime.now() - startTime) 
    file.write("In %s \n\n" %(time))

    # Output maps
    file.write("Location Map: ")
    pp.pprint(location_map)
    file.write("\n Emoji Map: ")
    pp.pprint(emoji_map)
    file.write("\n Emoji Count Map: ")
    pp.pprint(sorted(emoji_count_map.items(), key=itemgetter(1), reverse=True))

    # Command line finish
    time = timehelper(datetime.now() - startTime) 
    print("Report published: looked at %s tweets on \"%s\" %s in %s\n" %(stat, search_query, locale, time))

# loop through MAX_TWEETS tweets to gather data
#if __name__ == "__main__":
def main():
    # global counts
    emojistat = 0
    hasLoc = 0
    stat = 0

    try:
        if international:
            for status in tqdm(limit_handled(tweepy.Cursor(api.search, q=search_query, count=tweets_per_query).items(MAX_TWEETS))):
                stat += 1
                if(status_has_emoji(status.text)):
                    emojistat += 1
                    if (status_has_location(status)):
                        hasLoc += 1
                    else:
                        insert_emoji_map(status.text, "none")
        else:
            # Geocode is [lat,long,rad] of geographic center of continental US - geocode="39.50,-98.35,1500mi"
            for status in tqdm(limit_handled(tweepy.Cursor(api.search, q=search_query, count=tweets_per_query, geocode="39.50,-98.35,1500mi").items(MAX_TWEETS))):
                stat += 1
                if(status_has_emoji(status.text)):
                    emojistat += 1
                    if (status_has_location(status)):
                        hasLoc += 1
                    else:
                        insert_emoji_map(status.text, "none")
    except tweepy.error.TweepError:
        print (" Twiiter API error: Too many tweet requests")
    except tweepy.TweepError as e:
        print(" Twitter API error: " + str(e))
    report(stat, emojistat, hasLoc)

# Run main program
main()










# TODO:
# clump repeated values into array of arrays -- Look into set default
# 'New YorkNew York' error?
# add graphs to final report


#############################
#####  Graphing Methods #####
#############################

# # # Bar Chart
# labels = 'Brady', 'Gronkowski', 'Amendola'
# y_pos = np.arange(len(labels)) #same as range(len(labels))
# retweets = [brady, gronk, dola]
# plt.bar(y_pos, retweets, align='center', alpha=1)
# plt.xticks(y_pos, retweets)
# plt.ylabel('Mentions')
# plt.xlabel('Player')
# plt.title('Patriots Mentions')
# plt.show()


# # #pie chart, where slices will be ordered and plotted counter-clockwise
# # explode = (0, .1, 0)
# # fi1, ax1 = plt.subplots()
# # ax1.pie(retweets, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
# # ax1.axis('equal')
# # plt.show()
