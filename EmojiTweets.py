#  Olympics + Emojis
#  Final Proj for LING 23700: Langugage & the Internet
#  Last Modified by Alex Markowitz on 3/1/18.

import os                               # For report logging
import json                             # JSON formatting
import emoji                            # emoji database
import googlemaps                       # googlemaps api
import pprint                           # Data Pretty Printer
import matplotlib.pyplot as plt         # graphing
import pandas as pd                     # data
import numpy as np                      # data
import tweepy                           # twitter parsing
from operator import itemgetter         # Dictionary sort
from tqdm import tqdm                   # progress bar

# Google Maps API Keys
#1: "AIzaSyBrsqIQyfG8napKGOAqN-Ukg3HKZBbkdvY" - crashed on 15k - gmaps error
#2: "AIzaSyD6YCa6XnkdGipnwGUD_31u86PEZd5znjI" - crashed on 14k - gmaps error
#3: "AIzaSyAZzDMrQ5p5urgxQkyBdeG07dH04_QAb7I" - got 20k - (MRU)
#4: "AIzaSyDUnd0ShyjSDwBbGJkUlQbcyAmLDGvVsXA" - crashed on 100 - gmaps error
map_key = "AIzaSyDUnd0ShyjSDwBbGJkUlQbcyAmLDGvVsXA"
gmaps = googlemaps.Client(key=map_key);

# Twitter API keys
consumer_key = 'Oi9h0A02ZOXMIDzoXsy6sWwHl'
consumer_secret = 'Hh8dBjAP8KTGB2n7gg845WvOXSjm4MlAHntrxbu5DnhTmI8ysi'
access_token = '959207976199483393-0AOwXscYZyRqLvEToTb8xeHqZP69g8F'
access_secret = 'wbcqyeOGWvamz0nO0HaRIzcMs6r8yyEzWvLBV75PxjzKS'

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)


# Global Variables
MAX_TWEETS = 100;
search_query = "test";
tweets_per_query = 100;
international = False;          # False searches domestically

emojistat = 0;
stat = 0;
hasLoc = 0;

location_map = {};
emoji_map = {};
emoji_count_map = {};

states = {'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
         'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
         'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana',
         'Maine','Maryland','Massachusetts','Michigan','Minnesota',
         'Mississippi','Missouri','Montana','Nebraska','Nevada',
         'New Hampshire','New Jersey','New Mexico','New York',
         'North Carolina','North Dakota','Ohio','Oklahoma','Oregon',
         'Pennsylvania','Rhode Island', 'South Carolina','South Dakota',
         'Tennessee','Texas','Utah','Vermont','Virginia','Washington',
         'West Virginia','Wisconsin','Wyoming'};

# pause tweets
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(10 * 30)

# Return true if char is an emoji
def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI

# Return true if string contains an emoji
def status_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False

# parse GoogleMaps JSON response
def getLocation(addr):
    loc = ""
    addCompLen = len(addr)
    for  i in range (0, addCompLen):
        try:
            if international:
                if (addr[i]["types"][0] == "country"):
                    loc += addr[i]["long_name"];
            else:
                if (addr[i]["long_name"] in states):
                    loc += addr[i]["long_name"];
        except:
            print(" Error: country doesn't exist in JSON");
            report(stat, emojistat, hasLoc);
    return loc

# Return true if tweet came from valid location as determined by GoogleMaps API
def status_has_location(status):
    loc = status.user.location
    if (loc):
        try:
            if (gmaps.geocode(loc)):
                location = getLocation(gmaps.geocode(loc)[0]["address_components"])
                if location is not '':
                    insert_location_map(location, status.text);
                    insert_emoji_map(status.text, location);
                    return True;
        except Exception as e:
            print (" GoogleMaps API error: " + str(e));
            report(stat, emojistat, hasLoc);
    else:
        return False;



# insert country-emoji pair into map
def insert_location_map(location, status):
    for char in status:
        if(char_is_emoji(char)):
            if location in location_map:
                location_map[location] += char;
            else:
                location_map[location] = char;

# insert emoji-country pair into map
def insert_emoji_map(status, location):
    for char in status:
        if(char_is_emoji(char)):
            if char in emoji_map:
                emoji_count_map[char] += 1;
            else:
                emoji_count_map[char] = 1;

            if location is not "none":
                if char in emoji_map:
                    emoji_map[char] += ", {}".format(location);
                else:
                    emoji_map[char] = location;



# Print final report with statistics to console
def report(stat, emojistat, hasLoc):
    filename = "report_" + str(stat) + "_tweets_on_" + search_query + ".txt";
    file = open(os.path.join('reports',filename), "w");
    file.write("Final Report:\n\n");
    locale = 'internationally' if international else 'domestically';
    file.write("%s Total tweets were looked at on search query \"%s\" %s\n" %(stat, search_query, locale));
    file.write("%s of those tweets contained emojis\n" %(emojistat));
    file.write("%s of Emoji Tweets had locations\n\n" %(hasLoc));
    pp = pprint.PrettyPrinter(indent=4, stream=file);
    file.write("Country Map: ")
    pp.pprint(location_map);
    file.write("\n Emoji Map: ")
    pp.pprint(emoji_map);
    file.write("\n Emoji Count Map: ")
    pp.pprint(sorted(emoji_count_map.items(), key=itemgetter(1), reverse=True));
    print ("Report published: looked at %s tweets on \"%s\" %s.\n" %(stat, search_query, locale));

# loop through MAX_TWEETS tweets to gather data
def main():
    global stat
    global emojistat
    global hasLoc

    try:
        if international:
            for status in tqdm(limit_handled(tweepy.Cursor(api.search, q=search_query, count=tweets_per_query).items(MAX_TWEETS))):
                stat += 1
                if(status_has_emoji(status.text)):
                    emojistat += 1;
                    if (status_has_location(status)):
                        hasLoc += 1;
                    else:
                        insert_emoji_map(status.text, "none");
        else:
            # Geocode is [lat,long,rad] of geographic center of continental US - geocode="39.50,-98.35,1500mi"
            for status in tqdm(limit_handled(tweepy.Cursor(api.search, q=search_query, count=tweets_per_query, geocode="39.50,-98.35,1500mi").items(MAX_TWEETS))):
                stat += 1
                if(status_has_emoji(status.text)):
                    emojistat += 1;
                    if (status_has_location(status)):
                        hasLoc += 1;
                    else:
                        insert_emoji_map(status.text, "none");
    except tweepy.error.TweepError:
        print (" Twiiter API error: Too many tweet requests");
    except tweepy.TweepError as e:
        print(" Twitter API error: " + str(e))
    report(stat, emojistat, hasLoc);

# Run main program
main();

# # # Bar Chart
# # labels = 'Brady', 'Gronkowski', 'Amendola'
# # y_pos = np.arange(len(labels)) #same as range(len(labels))
# # retweets = [brady, gronk, dola]
# # plt.bar(y_pos, retweets, align='center', alpha=1)
# # plt.xticks(y_pos, retweets)
# # plt.ylabel('Mentions')
# # plt.xlabel('Player')
# # plt.title('Patriots Mentions')
# # plt.show()


# # #pie chart, where slices will be ordered and plotted counter-clockwise
# # explode = (0, .1, 0)
# # fi1, ax1 = plt.subplots()
# # ax1.pie(retweets, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
# # ax1.axis('equal')
# # plt.show()


# TODO
# make Command line interface
# add timing from tqdm to final report
# add graphs to final report
# 'New YorkNew York' error?
# clump repeated values into array of arrays
# put on github
# make web interface
