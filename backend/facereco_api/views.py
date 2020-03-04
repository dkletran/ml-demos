from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import serializers
import json
from lib.parsers import PlainTextParser

from .service import detect_face, save_face_embedding, identify_face
from .models import FaceTag

# Serializers define the API representation.
class FaceBoxSerializer(serializers.Serializer):
    data = serializers.StringRelatedField()
    name = serializers.StringRelatedField()


class FaceRecoApiViewSet(viewsets.ViewSet):
    @action(methods=['post'], detail=False,url_path='tag_face')
    def tag_face(self, request):
        data = request.data
        if data and data['name']:
            try:
                rsl = save_face_embedding(data['face'], data['name'])
                return Response(rsl) 
            except Exception as e:
                print(e)
                return Response('ERROR') 
            return Response('OK')
        else:
            return Response('ERROR')
    @action(methods=['post'], detail=False,url_path='face_identify', parser_classes=[PlainTextParser])
    def face_identify(self, request):
        data = request.data
        if data:
            try:
                if FaceTag.objects.all().count() > 0:
                    faceBoxes = identify_face(data)
                else:
                    faceBoxes = detect_face(data)            
                serializer = FaceBoxSerializer(
                    instance=faceBoxes, many=True)
                return Response(serializer.data)
            except Exception:
                return Response([])
        else:
            return Response([])