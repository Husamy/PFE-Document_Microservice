from rest_framework import generics, mixins
from .models import DocumentUpload, RequestSign
from .serializers import DocumentSerializer, RequestSignSerializer, RequestSignSerializerRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
import os
import requests


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








class requestList(generics.ListAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer



class DocumentList(generics.ListCreateAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request, *args, **kwargs)


class DocumentCRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer

class DocumentByTitle(generics.RetrieveAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'title'

class DocumentAll(generics.ListAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer

class DocumentDetail(generics.RetrieveAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'
    



class DownloadDocumentView(APIView):
    def get(self, request, pk, *args, **kwargs):
        document = get_object_or_404(DocumentUpload, pk=pk)
        file = document.file
        response = Response(file.read(), content_type=file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{document.title}"'
        return response
