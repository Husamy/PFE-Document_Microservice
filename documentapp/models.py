from django.db import models
import uuid

# Create your models here.

class DocumentUpload(models.Model):
    title = models.CharField(max_length=30)
    owner = models.EmailField(max_length=30)
    signed_status = models.CharField(max_length=20)
    privacy = models.CharField(max_length=7)
    typefile = models.CharField(max_length=3)
    fileDoc = models.FileField(upload_to='documents/')

    def __str__(self) -> str:
        return str(self.id)
    

class RequestSign(models.Model):
    document_id = models.ForeignKey(DocumentUpload, on_delete=models.CASCADE, unique=True)
    owner = models.CharField(max_length=30, null=False)
    request_status = models.CharField(max_length=20, null=False)

    def __str__(self) -> str:
        return self.request_status


