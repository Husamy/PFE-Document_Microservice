from django.db import models
import uuid
import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

def get_document_path(instance, filename):
        return os.path.join(str(instance.user_id), filename)
    
class DocumentUpload(models.Model):
    title = models.CharField(max_length=30)
    owner = models.EmailField(max_length=30)
    description = models.CharField(max_length=300)
    signed_status = models.CharField(max_length=20,default='Not Signed')
    privacy = models.CharField(max_length=7,default='Private')
    filetype = models.CharField(max_length=20)
    user_id = models.IntegerField(max_length=20, null=False)
    fileDoc = models.FileField(upload_to=get_document_path)

    def __str__(self) -> str:
        return str(self.id)
    

class RequestSign(models.Model):
    document_id = models.ForeignKey(DocumentUpload, on_delete=models.CASCADE, unique=True)
    owner = models.CharField(max_length=30, null=False)
    request_status = models.CharField(max_length=20, null=False, default='In Progress')

    def __str__(self) -> str:
        return self.request_status


