from django.db import models

# Create your models here.
class Document (models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    privacy = models.CharField(max_length=7)
    type = models.CharField(max_length=3)
    file = models.FileField(upload_to='documents/')

    def __str__(self) -> str:
        return self.title
    