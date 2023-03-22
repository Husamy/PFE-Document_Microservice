from rest_framework import generics, mixins
from .models import DocumentUpload, RequestSign
from .serializers import DocumentSerializer, RequestSignSerializerTitle, DocumentSerializerUpload, RequestSignSerializer, RequestSignSerializerRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
import os
import requests
import uuid
import random
from django.conf import settings



class RequestApiDestroy(generics.RetrieveDestroyAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Serialize instance and print the data
        serialized_data = self.serializer_class(instance).data
        
        action = 'delete'
        host_ip = os.environ.get('HOST_IP')
        timestamp_data = {'action': action, 'owner': serialized_data['owner'], 'document_id': serialized_data['document_id']}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
    



class RequestApiUpdate(generics.RetrieveUpdateAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        # Perform custom logic here
        if serializer.validated_data.get('status') == 'approved':
            instance.approved_by = request.user
        else:
            instance.approved_by = None

        self.perform_update(serializer)

        action = 'signed'
        host_ip = os.environ.get('HOST_IP')
        timestamp_data = {'action': action, 'owner': request.data['owner'], 'document_id': request.data['document_id']}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)

        return Response(serializer.data)





class RequestApi(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = RequestSignSerializer
    queryset = RequestSign.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        host_ip = os.environ.get('HOST_IP')
        serializer.is_valid(raise_exception=True)
        response_data = serializer.validated_data
        response_data['document_id']=request.data['document_id']
        serializer_class = RequestSignSerializer(data=response_data)
        serializer_class.is_valid(raise_exception=True)
        RequestSign = serializer_class.save()

        action = 'Request Signing'
        timestamp_data = {'action': action, 'owner': request.data['owner'], 'document_id': request.data['document_id']}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)
        return Response(response_data, status=status.HTTP_200_OK)


class UserRequestSignsView(generics.ListAPIView):
    serializer_class = RequestSignSerializerTitle

    def get_queryset(self):
        user_id = self.request.user.id
        print(user_id)
        
        return RequestSign.objects.filter(document_id__user_id=user_id)





class requestList(generics.ListAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer



class DocumentList(generics.ListCreateAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializerUpload



class DocumentList(generics.ListCreateAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializerUpload

    def perform_create(self, serializer):
        # Save the new DocumentUpload instance
        instance = serializer.save()
        # Get the ID of the new instance
        id = instance.id
        action = 'Document Uploaded'
        host_ip = os.environ.get('HOST_IP')
        # Save the file type in 'filetype' field separately
        filetype = os.path.splitext(instance.fileDoc.name)[1].lower()
        title = os.path.splitext(instance.fileDoc.name)[0].split("/")[1]
        instance.title = title
        instance.filetype = filetype
    
        # Save the file in a directory named after the user_id
        user_id = self.request.data['user_id']
        directory = os.path.join(settings.MEDIA_ROOT, str(user_id))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, instance.fileDoc.name.split('/')[-1])
        with open(file_path, 'wb+') as destination:
            for chunk in instance.fileDoc.chunks():
                destination.write(chunk)
        instance.fileDoc.name = os.path.join(str(user_id), instance.fileDoc.name.split('/')[-1])
    
        instance.save()
        timestamp_data = {'action': action, 'owner': user_id, 'document_id': id}
        timestamp_url = 'http://' + str(host_ip) + ':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)




class DocApiDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Serialize instance and print the data
        serialized_data = self.serializer_class(instance).data
        self.perform_destroy(instance)

        action = 'Document Deleted'
        host_ip = os.environ.get('HOST_IP')
        timestamp_data = {'action': action, 'owner': serialized_data['owner'], 'document_id': serialized_data['id']}
        timestamp_url = 'http://' + str(host_ip) + ':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        allowed_fields = ['description', 'title', 'signed_status', 'privacy']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        action = 'Document Updated'
        host_ip = os.environ.get('HOST_IP')
        timestamp_data = {'action': action, 'owner': instance.owner, 'document_id': instance.id}
        timestamp_url = 'http://' + str(host_ip) + ':8001/api/createDoc'
        response = requests.post(timestamp_url, data=timestamp_data)
        
        return Response(serializer.data)



    
        

class DocumentApiUpdate(generics.RetrieveUpdateAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer

    





class DocumentAll(generics.ListAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer

    



class DownloadDocumentView(APIView):
    def get(self, request, pk, *args, **kwargs):
        document = get_object_or_404(DocumentUpload, pk=pk)
        file = document.fileDoc
        contentType= str(file).split(".")
        response = HttpResponse(file.read(), content_type=contentType[1])
        response['Content-Disposition'] = f'attachment; filename="{document.title}.{contentType[1]}"'
        return response
