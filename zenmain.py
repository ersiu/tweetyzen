
#---------------------------------------------------------------
# Call example:
#
# 2 topics
# python zenmain.py -c config.ini -l
#
# 1 topic
# python zenmain.py -c config.ini -t lfc -l
#

import os
import sys
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from http.client import IncompleteRead
import time
import string
import json
import _pickle as pickle
import random
import configparser
import argparse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import subprocess


def set_topic(tweet, kwords1, kwords2):
    text = tweet['text']
    l_tags = tweet['entities']['hashtags']
    tags = []
    for d in l_tags:
        h = d.get('text')
        tags.append(h)

    # hash tags
    hashtags = ' '.join(tags)
    #print('hashtags: ', hashtags)

    score_t1 = calc_word_score(text, hashtags, kwords1)
    score_t2 = calc_word_score(text, hashtags, kwords2)

    if score_t1 > score_t2:
        return 1
    elif score_t2 > score_t1:
        return 2
    elif score_t1 == 0 and score_t2 == 0:
        return 4
    elif score_t1 == score_t2:
        return 3

#-------------------------------------------------------------------------------

def calc_word_score(text, hashtags, lstkeywords):
    keywords = lstkeywords.lower().split(',')
    score = 0
    for word in keywords:
        word = word.lower().strip()
        score += text.lower().count(word)
        score += hashtags.lower().count(word)
    return score

#-------------------------------------------------------------------------------

def get_hashtags(data):
    l_tags = row['entities']
    tags = []
    for d in l_tags:
        h = d.get('text')
        tags.append(h)
    return ' '.join(tags)

#-------------------------------------------------------------------------------

def format_filename(fname):
    return ''.join(convert_valid(one_char) for one_char in fname)

#-------------------------------------------------------------------------------

def convert_valid(one_char):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    if one_char in valid_chars:
        return one_char
    else:
        return '_'
#-------------------------------------------------------------------------------

def vader_sentiment_scores(sentence):
    snt = analyser.polarity_scores(sentence)
    return (snt['compound'])

#-------------------------------------------------------------------------------


class MyListener(StreamListener):
    """Custom StreamListener for streaming data."""

    def __init__(self, data_dir, query):
        print('Self __init__')
        query_fname = format_filename(query)
        self.outfile = "%s/stream_%s.json" % (data_dir, query_fname)

    def on_data(self, data):

        try:

            checktext = '{"limit":{"track":'
            if data[:20].count(checktext) > 0:
                print('ignored limit notice')
                # time.sleep(5)
                return

            tweet = json.loads(data)

            if B_EXCLUDE_RT:

                if tweet['text'].startswith('RT'):
                    print('throw RT')
                    return True


            text = tweet['text']
            print('text: ', text)


            if B_CALC_SENTI:
                # clean = text_senti.clean_text(text)
                # sent_val = text_senti.calc_sentiment(clean, mnb, vect)
                # sent_val = float("{0:.2f}".format(sent_val))

                sent_val = vader_sentiment_scores(text)
                tweet['senti_value'] = sent_val
                print('senti_value: ', sent_val)



                if B_CHECK_SIDE:
                    side = set_topic(tweet, c_keywords1, c_keywords2)
                    print('side: ', side)
                    tweet['side'] = side


            s = json.dumps(tweet)
            s = s + '\n'

            if not os.access(self.outfile, os.W_OK): time.sleep(0.5)

            # write to outfile
            with open(self.outfile, 'a') as f:
                f.write(s)

            live_output = ''

            if B_LIVECHART and B_CHECK_SIDE:
                if side == 1:
                    live_output = str(sent_val) + ',0'
                elif side == 2:
                    live_output = '0,' + str(sent_val)
                elif side == 3:
                    live_output = str(sent_val) + ',' + str(sent_val)

            if B_LIVECHART and not B_CHECK_SIDE:
                live_output = str(sent_val) + ',0'

            if B_LIVECHART:
                live_output = live_output + '\n'
                with open(c_live_out_file, 'a') as f2:
                    f2.write(live_output)
                    f2.close()

            return True

        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(1)

        return True

    def on_error(self, status):

        print('On error handler here....')

        if status == 420:
            sys.stderr.write("Rate limit exceeded\n")
            return False
        else:
            sys.stderr.write("Error {}\n").format(status)
        return True


def start_tracking(auth, save_dir, topic):

    while True:
        try:
            # Connect/reconnect the stream
            print('>>> Create a stream')
            twitter_stream = Stream(auth, MyListener(save_dir, topic))

            print('>>> stream filtering')
            twitter_stream.filter(track=[topic], languages=["en"])

        except IncompleteRead:
            # Oh well, reconnect and keep trucking
            print('>>> IncompleteRead ----------')
            time.sleep(4)
            continue
        except KeyboardInterrupt:
            # Or however you want to exit this loop
            stream.disconnect()
            break
        except:
            print('>>> BaseException ----------')
            continue


    return True


def query_tweets(auth, save_dir, query, count):
    # empty list to store parsed tweets
    tweets = []

    try:
        api = tweepy.API(auth)
        # call twitter api to fetch tweets
        fetched_tweets = api.search(q = query, count = count)

        for tweet in fetched_tweets:

            #tweet = json.loads(data)

            #text = tweet['text']
            #print('text: ', tweet.text)

            print (tweet._json)

    except tweepy.TweepError as e:
        # print error (if any)
        print("Error : " + str(e))


    return True


#-------------------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='zenmaster.py')

    parser.add_argument('-c','--config', help='provide config.ini file location', required=True)
    parser.add_argument('-m', '--mode', help='mode: stream | rest', required=True)
    parser.add_argument('-t','--track', help='topic for direct tracking or query', required=False)
    parser.add_argument('-n','--no_of_msg', help='number of REST msg', required=False)
    parser.add_argument('-l','--live', help='run livechart', required=False, action='store_true')
    parser.add_argument('-p','--pause', help='pause before extracting tweets', required=False, action='store_true')
    parser.add_argument('-rt','--retweet', help='exclude retweet', required=False, action='store_true')

    args = vars(parser.parse_args())


    #----------- check config -------------------
    c_config_file = ''

    if not args['config'] and not args['mode']:
        print ('usage: zenmain.py [-h] [-m MODE] stream | rest [-c CONFIG] [-t TRACK]')
        sys.exit()

    if args['config']:
        c_config_file = args['config']
        print(">>>>> Load config file: ", c_config_file)

    #----------- check mode -------------------
    if args['mode'].lower() not in ['stream', 'rest']:
        print ('usage: zenmain.py [-h] [-m MODE] stream | rest [-c CONFIG] [-t TRACK]')
        sys.exit()

    c_mode = 1
    if args['mode'].lower() == 'stream':
        c_mode = 1
    elif args['mode'].lower() == 'rest':
        c_mode = 2

    B_DIRECT_TRACK = False

    #----------- look up track -------------------

    if args['track']:
        B_DIRECT_TRACK = True
        c_track = args['track']
        c_theme = c_track
        c_no_of_topic = 1


    #----------- look up # of message to download from REST -------------------
    c_no_of_msg = args['no_of_msg']

    #----------- config parser -------------------
    config = configparser.ConfigParser()
    config.read(c_config_file)

    #-------------- start config -----------------
    print (">>>>> Load configurations")

    c_consumer_key = config.get("account", "consumer_key")
    c_consumer_secret = config.get("account", "consumer_secret")
    c_access_token = config.get("account", "access_token")
    c_access_secret = config.get("account", "access_secret")

    c_calc_senti = int(config.get("general", "calc_senti"))
    c_check_side = int(config.get("general", "check_side"))
    c_save_dir = config.get("general", "save_dir")

    c_livechart = int(config.get("general", "livechart"))
    c_live_out_file = config.get("general", "live_out_file")

    c_mnb_file = config.get("algo", "mnb_file")
    c_vect_file = config.get("algo", "vect_file")

    c_topic1 = config.get("topic", "topic1")
    c_topic2 = config.get("topic", "topic2")

    if not B_DIRECT_TRACK: c_theme = config.get("topic", "theme")
    if not B_DIRECT_TRACK: c_no_of_topic = int(config.get("topic", "no_of_topic"))
    if not B_DIRECT_TRACK:
        c_track = config.get("topic", "track")
        #if args['retweet']:
            #c_track = c_track + " -filter:retweets"

    c_keywords1 = config.get("topic", "keywords1")
    c_keywords2 = config.get("topic", "keywords2")

    B_LIVECHART = B_CALC_SENTI = B_CHECK_SIDE = B_EXCLUDE_RT = False

    if c_no_of_topic == 1:
        if c_calc_senti == 1: B_CALC_SENTI = True

    else:
        if c_livechart == 1:
            B_LIVECHART = B_CALC_SENTI = B_CHECK_SIDE = True
        else:
            if c_calc_senti == 1: B_CALC_SENTI = True
            if c_check_side == 1: B_CHECK_SIDE = True

    if B_DIRECT_TRACK:
        B_LIVECHART = True
        B_CALC_SENTI = True
        B_CHECK_SIDE = False

    if args['retweet']: B_EXCLUDE_RT = True

    print ('>>>>> Mode:', c_mode)
    if c_mode == 1:
        print ('>>>>> Mode = stream:', c_track)
    elif c_mode == 2:
        print ('>>>>> Mode = rest:', c_no_of_msg)

    print ('>>>>> No of Topic:', c_no_of_topic)
    print ('>>>>> Direct Track:', B_DIRECT_TRACK)
    print ('>>>>> Live Charting:', B_LIVECHART)
    print ('>>>>> Calc Sentiment:', B_CALC_SENTI)
    print ('>>>>> Check Side:', B_CHECK_SIDE)
    print ('>>>>> Exclude Retweet:', B_EXCLUDE_RT)
    print ('')

    #-------------- finish config -----------------

    print('>>>>> Initialize: Vader analyser')
    analyser = SentimentIntensityAnalyzer()

    print('>>>>> Initialize: Twitter auth handler')
    auth = OAuthHandler(c_consumer_key, c_consumer_secret)
    auth.set_access_token(c_access_token, c_access_secret)


    if B_LIVECHART and args['live']:
        title = '"' + c_theme + '"'
        if c_no_of_topic == 1:
            cmd = "zenliveplot.py -c " + c_config_file + " -r -t " + title + " -n 1"
        else:
            cmd = "zenliveplot.py -c " + c_config_file + " -r"

        print('>>>>> call livechart, cmd: ', cmd)
        subprocess.Popen(cmd, shell=True)
        time.sleep(3)

    if args['pause']:
        input("Press Enter to continue...")

    if c_mode == 1:
        print('>>>>> Initialize: Ready to start STREAM tracking')
        start_tracking (auth, c_save_dir, c_track)
    else:
        print('>>>>> Initialize: Ready to start REST query')
        query_tweets (auth, c_save_dir, c_track, c_no_of_msg)






