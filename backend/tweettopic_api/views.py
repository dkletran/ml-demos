from django.shortcuts import render
from django.db import models

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from .models import Tweet
from django.http import JsonResponse
from . import tweet_service
from lib.serializers import JSONStringField
# Serializers define the API representation.


class TweetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tid = serializers.IntegerField()
    text = serializers.StringRelatedField()
    screen_name = serializers.StringRelatedField()
    retweeted = serializers.BooleanField()
    user_image_url = serializers.StringRelatedField()
    topic = JSONStringField()

class TopicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    keywords = JSONStringField()
# ViewSets define the view behavior.


class TweetViewSet(viewsets.ModelViewSet):
    serializer_class = TweetSerializer
#    authentication_classes = [SessionAuthentication]
#    permission_classes = [IsAuthenticated]
    queryset = Tweet.objects.all()
    @action(detail=False, url_path='recent/(?P<last_id>[^/.]+)')
    def recent(self, request, last_id):
        query = request.query_params.get('query', None)
        tweet_service.checkRunBackgroundThread()
        if query == 'ALL':
            queryTweets = Tweet.objects.all()
        else:
            queryTweets = Tweet.objects.filter(
                id__gt=last_id, text__contains=query)
        if(request.query_params['retweetIncluded'] == 'true'):
            tweets = queryTweets
        else:
            tweets = queryTweets.exclude(retweeted=True)
        serializer = TweetSerializer(instance=tweets, many=True)
        return Response(serializer.data)
    @action(detail=False, url_path='topics')
    def get_topics(self, request):
        topics = tweet_service.get_topics()
        serializer = TopicSerializer(instance=topics, many=True)
        return Response(serializer.data)
