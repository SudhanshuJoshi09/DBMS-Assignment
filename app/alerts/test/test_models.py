from django.test import TestCase
from alerts.serializers import ArticleSerializers


class ModelTest(TestCase):

    def test_create_new_alert_success(self):
        """Test creating new alert is successful"""
        title = 'some title'
        description = 'some description'
        alrt = ArticleSerializers(title=title, description=description)

        self.assertEqual(alrt.title, title)
        self.assertEqual(alrt.description, description)

