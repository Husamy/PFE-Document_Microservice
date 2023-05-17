from rest_framework import serializers
from .models import DocumentUpload, RequestSign
import os
import json
import requests

class DocumentSerializerUpdateDestroy(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ('id', 'title', 'description', 'privacy')



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ('id', 'title', 'description', 'signed_status', 'privacy', 'filetype', 'fileDoc')


    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.email
        validated_data['user_id'] = self.context['request'].user.id
        return super().create(validated_data)

class DocumentSerializerUpload(serializers.ModelSerializer):
    fileContent=serializers.ReadOnlyField()
    owner=serializers.ReadOnlyField()
    user_id=serializers.ReadOnlyField()
    privacy=serializers.ReadOnlyField()
    title=serializers.ReadOnlyField()
    filetype=serializers.ReadOnlyField()
    class Meta:
        model = DocumentUpload
        fields = ('id', 'description', 'fileDoc', 'fileContent', 'signed_status' , 'owner', 'title', 'user_id', 'privacy','filetype')
        
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
        validated_data['user_id'] = self.context['request'].user.id
        # Save the file type in 'filetype' field
        validated_data['filetype'] = os.path.splitext(filename)[1].lower()
        #set owner from auth microserivce
        host_ip = os.environ.get('HOST_IP')
        id= self.context['request'].user.id
        auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
        response = requests.get(auth_url)
        response_json = json.loads(response.content.decode('utf-8'))
        validated_data['owner'] = response_json['email']
        return super().create(validated_data)


class RequestSignSerializerTitle(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document_id.title')

    class Meta:
        model = RequestSign
        fields = ['request_status', 'document_title']
    
    






class RequestSignSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = RequestSign
        fields = ('id', 'request_status')


class RequestSignSerializer(serializers.ModelSerializer):
    document_id = serializers.PrimaryKeyRelatedField(queryset=DocumentUpload.objects.all())
    class Meta:
        model = RequestSign
        fields = ('id', 'document_id', 'request_status', 'common_name')
    
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user.email
        return super().create(validated_data)
    
    def to_representation(self, instance):
        if self.context['request'].method == 'GET':
            self.fields['owner'] = serializers.CharField()
        else:
            self.fields.pop('owner', None)
        
        return super().to_representation(instance)

    
        
        
class RequestUpdateSerializer(serializers.ModelSerializer):
    document_id=serializers.ReadOnlyField()
    owner=serializers.ReadOnlyField()
    class Meta:
        model = RequestSign
        fields = ['document_id', 'request_status', 'owner']

 
 
 