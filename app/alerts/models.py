from django.db import models

class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False, default='Enter the title of the alert')
    description = models.TextField()

    class Meta:
        ordering = ['created']

