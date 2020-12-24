from rest_framework import serializers
from alerts.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    '''Serializer for the alert articles'''
    class Meta:
        model = Article
        fields = ('title', 'description')
