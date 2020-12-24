from django.test import TestCase
from alerts.serializers import ArticleSerializer
from alerts.models import Article


class ModelTest(TestCase):

    def test_create_new_alert_success(self):
        """Test creating new alert is successful"""
        title = 'some title'
        description = 'some description'
        new_alert = Article(title=title, description=description)
        new_alert.save()
        alert_serializer = ArticleSerializer(new_alert)

        self.assertEqual(alert_serializer.data['title'], title)
        self.assertEqual(alert_serializer.data['description'], description)
