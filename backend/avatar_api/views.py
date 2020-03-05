from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import serializers
from rest_framework.parsers import BaseParser
import json
from django.shortcuts import render
from lib.parsers import PlainTextParser

from .models import AvatarBox
from .service import cropAvatar, styleAvatar
# Serializers define the API representation.
class AvatarBoxSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()

class AvatarStylingApiViewSet(viewsets.ViewSet):
    @action(methods=['post'], detail=False,url_path='crop_avatar', parser_classes=[PlainTextParser])
    def crop_avatar(self, request):
        data = request.data
        if data:
            try:
                avatarBoxes =  cropAvatar(data)          
                serializer = AvatarBoxSerializer(
                    instance=avatarBoxes, many=True)
                return Response(serializer.data)
            except Exception:
                return Response([])
        else:
            return Response([])
    @action(methods=['post'], detail=False,url_path='style_avatar')
    def style_avatar(self, request):
        data = request.data
        if data:
            try:
                styleImageStr =  styleAvatar(**data)
                return Response(styleImageStr)
            except Exception as e:
                print(e)
                return Response([])
        else:
            return Response([])