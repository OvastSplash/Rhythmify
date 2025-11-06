from rest_framework import serializers

class EternalSerializer(serializers.Serializer):
    spotify = serializers.URLField()

class FollowersSerializer(serializers.Serializer):
    total = serializers.IntegerField()

class SpotifyProfileSerializer(serializers.Serializer):
    id = serializers.CharField()
    display_name = serializers.CharField()
    external_urls = EternalSerializer()
    followers = FollowersSerializer()
    images = serializers.ListField(child=serializers.DictField(), required=False)