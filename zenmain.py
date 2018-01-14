import os
import sys
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from http.client import IncompleteRead
import time
import string
import config
import json
import _pickle as pickle
import random
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
nlp = spacy.load('en')
import config
import re

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

    score_t1 = calc_word_score(text, hashtags, keywords1)
    score_t2 = calc_word_score(text, hashtags, keywords2)
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
    return text

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
    fname += "-" + str(file_part).zfill(5)
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
        self.file_part = 1
        self.total_msg = 0
        self.msg_num = 0
        self.file_limit = 5000
        self.outfile = "%s/stream_%s.json" % (data_dir, query_fname)

    def on_data(self, data):

        try:

            self.total_msg += 1
            self.msg_num += 1

            print('Counter: {} | {}'.format(self.total_msg, self.msg_num))
            if self.msg_num > self.file_limit:
                self.file_part += 1
                self.msg_num = 1
                tmpfilename = self.outfile[:-9]
                self.outfile = tmpfilename + str(self.file_part).zfill(5) + '.json'

            # handle data here

            checktext = '{"limit":{"track":'
            if data[:20].count(checktext) > 0:
                print('ignored limit notice')
                # time.sleep(5)
                return

            tweet = json.loads(data)
            text = tweet['text']
            print('text: ', text)
            clean = clean_text(text)
            clean = clean.strip()

            sent_val = calc_sentiment(clean, mnb)
            sent_val = float("{0:.2f}".format(sent_val))
            #print('senti_value: ', sent_val)
            if no_of_topic == 1:
                side = -1
            else:
                side = set_topic(tweet)
                #print('side: ', side)

            #tweet['clean'] = clean
            tweet['senti_value'] = sent_val
            tweet['side'] = side

            ret = os.access(self.outfile, os.W_OK)
            if not ret:
                time.sleep(1)
                print('file not writeable, time for 1 sec')

            s = json.dumps(tweet)
            s = s + '\n'
            # write tweet message + sentiment to
            with open(self.outfile, 'a') as f:
                f.write(s)
                # f.close()

            sOut = ''

            if side == 1:
                sOut = str(sent_val) + ',0,' + clean
            elif side == 2:
                sOut = '0,' + str(sent_val) + ',' + clean
            elif side == 3:
                sOut = str(sent_val) + ',' + str(sent_val) + ',' + clean

            if len(sOut) > 0:
                with open(SENTI_OUT_FILE, 'a') as f2:
                    f2.write(sOut)
                    f2.write('\n')
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


#@classmethod

# #-------------------------------------------------------------------------------


# def parse(cls, api, raw):
#     status = cls.first_parse(api, raw)
#     setattr(status, 'json', json.dumps(raw))
#     return status


def start_tracking(auth_handler):

    return true


#-------------------------------------------------------------------------------
if __name__ == '__main__':

    # open multinominal naive bayes classifer
    print('Initialize: load pickle mnb file')
    open_file = open("pickled_algos/mnb.pickle", "rb")
    mnb = pickle.load(open_file)
    open_file.close()

    # open tfidf vectorizer
    print('Initialize: load pickle mnb file')
    open_file = open("pickled_algos/vect.pickle", "rb")
    vectorizer = pickle.load(open_file)
    open_file.close()

    # get configurations
    no_of_topic = config.no_of_topic
    theme = config.theme
    topic1 = config.topic1
    topic2 = config.topic2
    topic3 = config.topic3
    keywords1 = config.keywords1
    keywords2 = config.keywords2
    keywords3 = config.keywords3
    SENTI_OUT_FILE = config.senti_out_file

    print('Initialize: Twitter auth handler')
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)
    #api = tweepy.API(auth)

    # file part number & msg_count
    file_part = 1

    print('Initialize: Start tracking')

    while True:
        try:
            # Connect/reconnect the stream

            print('Create a stream')
            twitter_stream = Stream(auth, MyListener(config.save_dir, config.track))

            print('stream filtering')
            twitter_stream.filter(track=[config.track], languages=["en"])

        except IncompleteRead:
            # Oh well, reconnect and keep trucking
            print('IncompleteRead ----------')
            time.sleep(4)
            continue
        except KeyboardInterrupt:
            # Or however you want to exit this loop
            stream.disconnect()
            break
        except:
            print('BaseException ----------')
            continue
