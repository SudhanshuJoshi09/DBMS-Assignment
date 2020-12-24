from rest_framework import serializers
from alerts.models import Article


class ArticleSerializers(serializers.Serializer):
    '''Serializer for the alert articles'''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, max_length=100)
    description = serializers.CharField()

    def create(self, validated_data):
        '''Create a new alert article given validated_data'''
        return Article.objects.create(**validated_data)