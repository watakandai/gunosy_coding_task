from django.db import models


class Article(models.Model):
    category = models.CharField(max_length=20)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
