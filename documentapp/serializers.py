from rest_framework import serializers
from .models import DocumentUpload, RequestSign
import os

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ('id', 'title', 'owner', 'user_id', 'description', 'signed_status', 'privacy', 'filetype', 'fileDoc')



class DocumentSerializerUpload(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ('id', 'owner', 'user_id', 'description', 'fileDoc')
        
    def validate_fileDoc(self, value):
        valid_extensions = ['.xml', '.pdf']
        ext = os.path.splitext(value.name)[1]
        if not ext.lower() in valid_extensions:
            raise serializers.ValidationError("File type not supported. Only XML and PDF files are allowed.")
        return value

    def create(self, validated_data):
        # Extract the file name from the uploaded file and set it as the title
        filename = os.path.basename(validated_data['fileDoc'].name)
        title = os.path.splitext(filename)[0]
        validated_data['title'] = title
        # Set default values for signed_status and privacy
        validated_data['signed_status'] = 'Not Signed'
        validated_data['privacy'] = 'Private'
        # Save the file type in 'filetype' field
        validated_data['filetype'] = os.path.splitext(filename)[1].lower()
        return super().create(validated_data)


class RequestSignSerializerTitle(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document_id.title')

    class Meta:
        model = RequestSign
        fields = ['owner', 'request_status', 'document_title']





class RequestSignSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = RequestSign
        fields = ('id', 'request_status')


class RequestSignSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(queryset=DocumentUpload.objects.all())
    class Meta:
        model = RequestSign
        fields = ('id', 'owner', 'document_id', 'request_status')
 
 
 