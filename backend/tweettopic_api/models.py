from django.db import models
import json
class Tweet(models.Model):
    tid = models.BigIntegerField(auto_created=False, unique=True)
    text = models.TextField()
    screen_name = models.TextField()
    retweeted  = models.BooleanField()
    user_image_url = models.TextField()
    topic = models.TextField(default=None, null=True)
class Topic():
    def __init__(self, id, keywords):
        self.id = id
        if isinstance(keywords,list):
            self.keywords = json.dumps(keywords)
        else:
            self.keywords = keywords