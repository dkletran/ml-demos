from .models import Tweet, Topic
from .topic_modeling import TweetTopicModeling
import tweepy
from difflib import SequenceMatcher
from django.conf import settings
from stop_words import get_stop_words
import threading
import copy
import time


tweettopic_model = None

modelingThreadLock = threading.Lock()


class TweetStreamListener(tweepy.StreamListener):
	def on_status(self, status):
        # and not hasattr(status, 'retweeted_status'):
		if status.in_reply_to_status_id is None:
			if hasattr(status, 'extended_tweet'):
				text = status.extended_tweet['full_text']
			else:
				text = status.text
				if hasattr(status, 'retweeted_status'):
					if hasattr(status.retweeted_status, 'extended_tweet'):
						org_text = status.retweeted_status.extended_tweet['full_text']
					else:
						org_text = status.retweeted_status.text
					try:
						match = SequenceMatcher(None, text, org_text).find_longest_match(
							0, len(text), 0, len(org_text))
						if match.b == 0:
							text = text[:match.a]+org_text[match.b:]
					except:
						pass
			try:
				modelingThreadLock.acquire()
				topic = tweettopic_model.get_top_topics(text) if tweettopic_model else None
				modelingThreadLock.release()
				Tweet.objects.create(
                    tid=status.id,
                    text=text,
                    screen_name=status.user.screen_name,
                    retweeted=hasattr(status, 'retweeted_status'),
                    user_image_url=status.user.profile_image_url,
					topic=topic
                )
			except:
				pass



auth = tweepy.OAuthHandler(settings.TWITTER_API_AUTH['consumer_key'],
                           settings.TWITTER_API_AUTH['consumer_secret'])
auth.set_access_token(
    settings.TWITTER_API_AUTH['key'], settings.TWITTER_API_AUTH['secret'])

streamListener = TweetStreamListener()

stream = tweepy.Stream(
    auth=auth, listener=streamListener, tweet_mode="extended")

#track = get_stop_words('fr')
track = ['france']
#stream.filter(track=track, languages=['fr'], is_async=True)

def checkRerunStream():
	if not stream.running:
		stream.filter(track=track, languages=['fr'], is_async=True)


def get_topics(n=10):
	modelingThreadLock.acquire()
	topwords = tweettopic_model.get_top_words(n) if tweettopic_model else []
	modelingThreadLock.release()
	return [Topic(id, keywords) for id, keywords in enumerate(topwords)]

def deleteOldTweets():
	count = Tweet.objects.count()
	if count > 2000:
		last_id = Tweet.objects.latest('id').id
		Tweet.objects.all().filter(id__lt=last_id-2000).delete()


class TopicModelingThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		global tweettopic_model
		while True:
			if(Tweet.objects.count() >=1999):
				if tweettopic_model:
					pass
					newmodel = TweetTopicModeling()
					newmodel.fit([tweet.text for tweet in Tweet.objects.all().exclude(retweeted=True)])
				else:
					newmodel = TweetTopicModeling()
					newmodel.fit([tweet.text for tweet in Tweet.objects.all().exclude(retweeted=True)])
				modelingThreadLock.acquire()
				tweettopic_model = newmodel
				modelingThreadLock.release()
			time.sleep(600)

class TweetStreamingTweet(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while True:
			deleteOldTweets()
			checkRerunStream()
			time.sleep(3)

modelingThread = None
streamingThread = None

def checkRunBackgroundThread():
	global modelingThread, streamingThread
	if not modelingThread:
		modelingThread = TopicModelingThread()
		modelingThread.start()
	if not streamingThread:
		streamingThread = TweetStreamingTweet()
		streamingThread.start()
