import os
import sys

#------------------------------------------------------------------------------
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from http.client import IncompleteRead
#------------------------------------------------------------------------------
import time
import string
import json
import _pickle as pickle
import random
import re
#------------------------------------------------------------------------------
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS

import _pickle as pickle
import random
import re


#------------------------------------------------------------------------------
import configparser
import argparse
#-------------------------------------------------------------------------------


def set_topic(tweet):
    text = tweet['text']
    l_tags = tweet['entities']['hashtags']
    tags = []
    for d in l_tags:
        h = d.get('text')
        tags.append(h)

    # hash tags
    hashtags = ' '.join(tags)
    #print('hashtags: ', hashtags)

    score_t1 = calc_word_score(text, hashtags, c_keywords1)
    score_t2 = calc_word_score(text, hashtags, c_keywords2)
    #print('score t1: ', score_t1)
    #print('score t2: ', score_t2)

    if score_t1 > score_t2:
        return 1
    elif score_t2 > score_t1:
        return 2
    elif score_t1 == 0 and score_t2 == 0:
        return 4
    elif score_t1 == score_t2:
        return 3

#-------------------------------------------------------------------------------
# create 'topic' column if keyword is found and assign values


def calc_word_score(text, hashtags, lstkeywords):
    keywords = lstkeywords.lower().split(',')
    score = 0
    for word in keywords:
        word = word.lower().strip()
        score += text.lower().count(word)
        score += hashtags.lower().count(word)

    return score

#-------------------------------------------------------------------------------


def clean_text(text):
    text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).strip()
    if text.startswith('RT'):
        text = text.replace('RT', '', 1)
    return text.strip()

#-------------------------------------------------------------------------------


def get_hashtags(data):
    l_tags = row['entities']
    tags = []
    for d in l_tags:
        h = d.get('text')
        tags.append(h)
    return ' '.join(tags)

#-------------------------------------------------------------------------------


def spacy_tokenizer(sentence):
    tokens = nlp(sentence)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in STOP_WORDS and tok not in string.punctuation)]
    return tokens

#-------------------------------------------------------------------------------


def calc_sentiment(text, myclassifier):
    v_text = vectorizer.transform([text])
    ans = myclassifier.predict_proba(v_text)
    result = float(ans[0][1]) - float(ans[0][0])
    return adjustSentiment(result)

#-------------------------------------------------------------------------------


def adjustSentiment(v):
    if v < -0.35:
        v += (v * 0.5)
        if v < -1.0:
            v = -1.0

    if v > 0.35:
        v += v * 0.5
        if v > 1.0:
            v = 1.0

    return v

#-------------------------------------------------------------------------------


def format_filename(fname):
    #fname += "-" + str(file_part).zfill(5)
    return ''.join(convert_valid(one_char) for one_char in fname)

#-------------------------------------------------------------------------------


def convert_valid(one_char):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    if one_char in valid_chars:
        return one_char
    else:
        return '_'

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
            text = tweet['text']
            print('text: ', text)
            

            if B_CALC_SENTI:
                clean = clean_text(text)
                sent_val = calc_sentiment(clean, mnb)
                sent_val = float("{0:.2f}".format(sent_val))
                tweet['senti_value'] = sent_val
            
                print('senti_value: ', sent_val)
            
                if B_CHECK_SIDE:
                    side = set_topic(tweet)
                    print('side: ', side)
                    tweet['side'] = side

            
            s = json.dumps(tweet)
            s = s + '\n'
            
            if not os.access(self.outfile, os.W_OK): time.sleep(0.5)
                
            # write to outfile
            with open(self.outfile, 'a') as f:
                f.write(s)
            
            live_output = ''
            
            if B_LIVECHART:

                if side == 1:
                    live_output = str(sent_val) + ',0,' + clean
                elif side == 2:
                    live_output = '0,' + str(sent_val) + ',' + clean
                elif side == 3:
                    live_output = str(sent_val) + ',' + str(sent_val) + ',' + clean

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


def start_tracking(auth_handler):

    return true


#-------------------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='zenmaster.py')

    parser.add_argument('-c','--config', help='provide config.ini file location', required=True)
    #parser.add_argument('-b','--bar', help='Description for bar argument', required=True)

    args = vars(parser.parse_args())

    c_config_file = ''
    
    if args['config']:
         c_config_file = args['config']
         print(">>>>> Load config file: ", c_config_file)


    config = configparser.ConfigParser()
    config.read(c_config_file)


    #-------------- start config -----------------
    print (">>>>> Load configurations")

    c_consumer_key = config.get("account", "consumer_key")
    c_consumer_secret = config.get("account", "consumer_secret")
    c_access_token = config.get("account", "access_token")
    c_access_secret = config.get("account", "access_secret")
    
    c_calc_senti = config.get("general", "calc_senti")
    c_check_side = config.get("general", "check_side")
    c_save_dir = config.get("general", "save_dir")
    c_mode = config.get("general", "mode")
    c_livechart = config.get("general", "livechart")
    c_live_out_file = config.get("general", "live_out_file")

    c_mnb_file = config.get("algo", "mnb_file")
    c_vect_file = config.get("algo", "vect_file")
    
    c_no_of_topic = int(config.get("topic", "no_of_topic"))
    c_theme = config.get("topic", "theme")
    c_topic1 = config.get("topic", "topic1")
    c_topic2 = config.get("topic", "topic2")
    c_track = config.get("topic", "track")
    c_keywords1 = config.get("topic", "keywords1")
    c_keywords2 = config.get("topic", "keywords2")
    
    B_LIVECHART = B_CALC_SENTI = B_CHECK_SIDE = False

    if c_livechart == '1':
        B_LIVECHART = B_CALC_SENTI = B_CHECK_SIDE = True
    else:
        if c_calc_senti == '1':
            B_CALC_SENTI = True
        else:
            B_CALC_SENTI = False

        if c_check_side == '1':
            B_CHECK_SIDE = True
        else:
            B_CHECK_SIDE = False

    if c_no_of_topic == '1':
        B_CHECK_SIDE = False

    #-------------- finish config -----------------

    if B_CALC_SENTI:
        # open multinominal naive bayes classifer
        print('>>>>> Initialize: load pickle mnb file')
        open_file = open(c_mnb_file, "rb")
        mnb = pickle.load(open_file)
        open_file.close()

        # open tfidf vectorizer
        print('>>>>> Initialize: load pickle mnb file')
        open_file = open(c_vect_file, "rb")
        vectorizer = pickle.load(open_file)
        open_file.close()

        print('>>>>> Initialize: load NLP spacy')
        nlp = spacy.load('en')

    print('>>>>> Initialize: Twitter auth handler')
    auth = OAuthHandler(c_consumer_key, c_consumer_secret)
    auth.set_access_token(c_access_token, c_access_secret)
    
    print ('>>>>> B_LIVECHART:', B_LIVECHART)
    print ('>>>>> B_CALC_SENTI:', B_CALC_SENTI)
    print ('>>>>> B_CHECK_SIDE:', B_CHECK_SIDE)

    print('>>>>> Initialize: Ready to start tracking')

    input("Press Enter to continue...")


    while True:
        try:
            # Connect/reconnect the stream
            print('>>> Create a stream')
            twitter_stream = Stream(auth, MyListener(c_save_dir, c_mode))

            print('>>> stream filtering')
            twitter_stream.filter(track=[c_track], languages=["en"])

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
