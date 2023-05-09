from django.db import models
import uuid
import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user_id, filename)
    
class DocumentUpload(models.Model):
    title = models.CharField(max_length=30)
    owner = models.EmailField(max_length=30)
    description = models.CharField(max_length=300)
    signed_status = models.CharField(max_length=20,default='Not Signed')
    privacy = models.CharField(max_length=7,default='Private')
    filetype = models.CharField(max_length=20)
    user_id = models.IntegerField(null=False)
    fileDoc = models.FileField(upload_to=user_directory_path)

    def __str__(self) -> str:
        return str(self.id)
    

class RequestSign(models.Model):
    document_id = models.ForeignKey(DocumentUpload, on_delete=models.CASCADE, to_field='id', unique=True)
    owner = models.CharField(max_length=30, null=False)
    request_status = models.CharField(max_length=20, null=False, default='In Progress')
    common_name = models.CharField(max_length=50, null=False)

    def __str__(self) -> str:
        return self.request_status


