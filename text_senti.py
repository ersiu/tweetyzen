import re

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


def spacy_tokenizer(sentence, nlp):
    tokens = nlp(sentence)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in STOP_WORDS and tok not in string.punctuation)]
    return tokens

#-------------------------------------------------------------------------------


def calc_sentiment(text, myclassifier, vectorizer):
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