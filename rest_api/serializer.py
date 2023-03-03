from django.http import HttpRequest
from django.conf import settings
from rest_framework import serializers
from requests.exceptions import HTTPError


class FavoritesSerializer(serializers.Serializer):
    favorites = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=100)
    )