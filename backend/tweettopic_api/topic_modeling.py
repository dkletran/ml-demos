from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import get_stop_words
from sklearn.base import BaseEstimator, TransformerMixin
import re
from lib.utils import timer
import numpy as np


class TweetTopicModeling(BaseEstimator, TransformerMixin):
    def __preprocess_tweet(self, tweet):
        '''
        Remove url, retweets, mention
        '''
        tweet = re.sub(
            r'((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?', '', tweet)
        tweet = re.sub(r'(RT)|(rt) @\w+', '', tweet)
        tweet = re.sub(r'@\w+', '', tweet)
        return tweet

    def __init__(self, type='lda', vectorizer_params=None, topic_model_params=None):
        if type == 'lda':
            lda_params = {
                'n_components': 20, 'random_state': 0, 
                'max_iter': 100, 'evaluate_every': 5
            }
            if topic_model_params:
                lda_params.update(topic_model_params)
            self.topic_model = LatentDirichletAllocation(**lda_params)
        else:
            raise Exception(f'Unknown type {type}')
        vectorizer_params_ = {
            'stop_words': get_stop_words('fr')+['deja', 'ca', 'va', 'vais', 'bien', 'non', 'plus', 'rt', 'france'],
            'ngram_range': (1, 2),
        #    'alternate_sign': False,
        }
        if vectorizer_params:
            vectorizer_params_.update(vectorizer_params)
        self.vectorizer = TfidfVectorizer(**vectorizer_params_)

    def __update_top_words(self):
        self.topwords = []
        feature_names = self.vectorizer.get_feature_names()
        for component in self.topic_model.components_:
            try:
                self.topwords.append([feature_names[idx] for idx in component.argsort()[-10:]])
            except:
                pass

    def fit(self, X, y=None):
        with timer('Tokenization'):
            X = [self.__preprocess_tweet(x) for x in X]
            X = self.vectorizer.fit_transform(X)
        with timer('Topic modeling'):
            self.topic_model.fit(X)
            self.__update_top_words()
        return self

    def partial_fit(self, X, y=None):
        X = [self.__preprocess_tweet(x) for x in X]
        self.vectorizer.partial_fit(X)
        X = self.vectorizer.transform(X)
        self.topic_model.partial_fit(X)
        self.__update_top_words()
        return self

    def transform(self, X):
        X = [self.__preprocess_tweet(x) for x in X]
        X = self.vectorizer.transform(X)
        return self.topic_model.transform(X)

    def score(self, X):
        X = [self.__preprocess_tweet(x) for x in X]
        X = self.vectorizer.transform(X)
        return self.topic_model.score(X)

    def get_top_words(self, n=10):
        return [t[-n:][::-1] for t in self.topwords]

    def get_top_topics(self, X, threshold=0.7, n=1):
        def extract_topics(probs):
            l = probs.argsort()[-n:]
            return np.extract(probs[l] > threshold, l).tolist()
        if isinstance(X, list):
            X = self.transform(X)
            return [extract_topics(x) for x in X]
        else:
            X = self.transform([X])
            return extract_topics(X[0])
