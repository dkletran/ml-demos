from django.db import models


class FaceTag(models.Model):
    name  = models.CharField(max_length=30, primary_key=True)
    data = models.TextField()

class FaceBox():
    def __init__(self, data, name=None):
        self.data = data
        self.name = name