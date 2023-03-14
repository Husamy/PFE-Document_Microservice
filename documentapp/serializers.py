from rest_framework import serializers
from .models import DocumentUpload, RequestSign

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ('id', 'title','owner', 'signed_status', 'privacy', 'typefile', 'fileDoc')


class RequestSignSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = RequestSign
        fields = ('id', 'request_status')


class RequestSignSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(queryset=DocumentUpload.objects.all())
    class Meta:
        model = RequestSign
        fields = ('id', 'owner', 'document_id', 'request_status')