from rest_framework import generics, mixins
from .models import DocumentUpload, RequestSign
from .serializers import DocumentSerializer, DocumentSerializerUpdateDestroy, RequestUpdateSerializer, RequestSignSerializerTitle, DocumentSerializerUpload, RequestSignSerializer, RequestSignSerializerRequest
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
import json
from rest_framework import permissions
from django.db.models import Q
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser
import base64
from django.core.files.base import ContentFile
import mimetypes
from django.http import FileResponse
from base64 import b64encode
from rest_framework.generics import GenericAPIView,  UpdateAPIView
from rest_framework import generics, status
from rest_framework.response import Response
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from django.shortcuts import get_object_or_404


class IsOrganisationOwner(permissions.BasePermission):
  
    def has_permission(self, request, view):
        id = request.user.id
        if id is None:
            return False
        else:
            host_ip = os.environ.get('HOST_IP')
            id = request.user.id
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
            print(request)
            print('id: ' + str(id))
            auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
            response = requests.get(auth_url)
            response_json = json.loads(response.content.decode('utf-8'))
            print('response auth: ' + str(response_json))
            user_email = request.user.email
            user_organisation = response_json['organisation']
            print('user_organisation: ' + str(user_organisation))
            # get organisation owner
            org_url = 'http://' + str(host_ip) + ':8002/api/organisation/create/'
            response = requests.get(org_url)
            response_json1 = json.loads(response.content.decode('utf-8'))
            print('response org: ' + str(response_json1))
            org_data = response_json1[0]
            print('org_data: ' + str(org_data))
            owner=org_data['owner']
            print('owner: ' + str(owner))
            return owner == user_email
        
        
        
        
class IsOrganisationMember(permissions.BasePermission):
  
    def has_permission(self, request, view):
        id = request.user.id
        if id is None:
            return False
        else:
            host_ip = os.environ.get('HOST_IP')
            id = self.request.user.id
            auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
            response = requests.get(auth_url)
            response_json = json.loads(response.content.decode('utf-8'))
            print('response auth: ' + str(response_json))
            user_email = self.request.user.email
            user_organisation = response_json['organisation']
            print('user_organisation: ' + str(user_organisation))
            # get organisation owner
            if user_organisation is None:
                return False
            else:
                org_url = 'http://' + str(host_ip) + ':8002/api/organisation/create/'
                response = requests.get(org_url)
                response_json1 = json.loads(response.content.decode('utf-8'))
                print('response org: ' + str(response_json1))
                org_data = response_json1[0]
                print('org_data: ' + str(org_data))
                owner=org_data['owner']
                print('owner: ' + str(owner))
                members=org_data['members']
                print('members: ' +str(members))
                
                return id in members

        
        
        
        


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        id = request.user.id
        if id is None:
            return False
        else:
            host_ip = os.environ.get('HOST_IP')
            auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
            response = requests.get(auth_url)
            response_json = json.loads(response.content.decode('utf-8'))
            user_id = response_json['id']
            return id == user_id



class RequestApiDestroy(generics.RetrieveDestroyAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer
    permission_classes=[IsUser,]
    lookup_field = 'document_id'
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        document_id = self.kwargs.get('document_id')
        action = 'delete'
        host_ip = os.environ.get('HOST_IP')
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': document_id}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
    

import io
from django.core.files import File
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class RequestApiUpdate(generics.RetrieveUpdateAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestUpdateSerializer
    lookup_field = 'document_id'
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        document_id = self.kwargs.get('document_id')
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(document_id)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('request_status') == 'Accepted':
            instance.request_status = 'Accepted'
            instance.save()
            host_ip = os.environ.get('HOST_IP')
            print('document_id: '+str(document_id))
            doc = DocumentUpload.objects.get(id=document_id)
            doc_updateSign = DocumentUpload.objects.filter(id=document_id).update(signed_status="Signed")
            with doc.fileDoc.open(mode='rb+') as f:
                data_doc = f.read()
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            headers = {'Authorization': f'Bearer {token}'}
            keys_url = 'http://'+str(host_ip)+':8002/api/keys/'
            org_url = 'http://'+str(host_ip)+':8002/api/organisation/create/'
            response = requests.get(url=keys_url, headers=headers)
            print('response keys= '+str(response))
            response_org = requests.get(url=org_url, headers=headers)
            print('response org= '+str(response_org))
            data_org= json.loads(response_org.content.decode('utf-8'))
            print('organisation data= '+str(data_org))
            data = json.loads(response.content.decode('utf-8'))
            private_key = load_pem_private_key(data[0]['privateKey'].encode(), password=None)
            signature = private_key.sign(
                data_doc,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print(signature)
            sign_url = 'http://'+str(host_ip)+':8005/api/sign/'
            signData = {
                'document_id': document_id,
                'user_id': doc.user_id,
                'owner': doc.owner,
                'name': data_org[0]['name'],
                'common_name': instance.common_name,
                'signature': signature,
                'country_name': data_org[0]['country_name'],
                'state_or_province_name': data_org[0]['state_or_province_name'],
                'locality_name': data_org[0]['locality_name']
                
                
            }
            print('signDAta= '+ str(signData))
            response_sign= requests.post(url=sign_url, headers=headers, data=signData)
            action='Admin Signed Document'
        elif serializer.validated_data.get('request_status') == 'Rejected':
            instance.request_status = 'Rejected'
            instance.save()
            host_ip = os.environ.get('HOST_IP')
            print('document_id: '+str(document_id))
            doc = DocumentUpload.objects.get(id=document_id)
            doc_updateSign = DocumentUpload.objects.filter(id=document_id).update(signed_status="Rejected")
            action='Admin Rejected Document'
            
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': document_id}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)
        

        return Response("Document Signed",status=status.HTTP_200_OK)











class RequestApi(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = RequestSignSerializer
    queryset = RequestSign.objects.all()
    permission_classes=[IsUser,]
    
    
    def get_queryset(self):
        host_ip = os.environ.get('HOST_IP')
        id = self.request.user.id
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
        print(self.request)
        print('id: ' + str(id))
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
        response = requests.get(auth_url, headers=headers)
        response_json = json.loads(response.content.decode('utf-8'))
        print('response auth: ' + str(response_json))
        user_organisation = response_json['organisation']
        print('user_organisation: ' + str(user_organisation))
        if user_organisation is None:
            queryset = super().get_queryset().filter(owner=self.request.user.email)
            return queryset
        # get organisation owner
        org_url = 'http://' + str(host_ip) + ':8002/api/organisation/create/'
        response = requests.get(url=org_url, headers=headers)
        print('response: ' + str(response))
        response_json1 = json.loads(response.content.decode('utf-8'))
        print('response org: ' + str(response_json1))
        org_data = response_json1[0]
        print('org_data: ' + str(org_data))
        owner=org_data['owner']
        print('owner: ' + str(owner))
        members=org_data['members']
        print('members: ' +str(members))
        print(members)
        if response_json['email'] == owner:
            org_url_member = 'http://' + str(host_ip) + ':8002/api/organisation/users/'
            response_members = requests.get(url=org_url_member, headers=headers)
            print('response: ' + str(response_members))
            response_json2 = json.loads(response_members.content.decode('utf-8'))
            print('response org: ' + str(response_json2))
            members_email = []
            for i in response_json2:
                members_email.append(i['email'])
            org_data_members = response_json2[0]
            print('org_data: ' + str(org_data_members))
            queryset = super().get_queryset().filter(owner__in=members_email)
        else:
            queryset = super().get_queryset().filter(owner=self.request.user.email)
        return queryset
        
    
    def get(self, request, *args, **kwargs):
        # Override the list method to retrieve the associated document for each request object
        queryset = self.filter_queryset(self.get_queryset())  # Get the filtered queryset
        document_ids = queryset.values_list('document_id', flat=True)  # Get a list of document IDs
        documents = DocumentUpload.objects.filter(id__in=document_ids)  # Retrieve the associated documents
        serializer = self.get_serializer(queryset, many=True)  # Serialize the queryset
        serialized_data = serializer.data

        # Add the associated document data to each request object
        for data in serialized_data:
            document = documents.get(id=data['document_id'])
            data['document'] = DocumentSerializerUpload(document).data

        return Response(serialized_data)

    def post(self, request, *args, **kwargs):
        host_ip = os.environ.get('HOST_IP')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_join = serializer.save()
        action = 'Request Signing'
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': request.data['document_id']}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)
        return Response(serializer.data, status=status.HTTP_200_OK)
        




class UserRequestSignsView(generics.ListAPIView):
    serializer_class = RequestSignSerializerTitle
    permission_classes=[IsUser,]
    def get_queryset(self):
        user_id = self.request.user.id
        
        return RequestSign.objects.filter(document_id__user_id=user_id)





class requestList(generics.ListAPIView):
    queryset = RequestSign.objects.all()
    serializer_class = RequestSignSerializer






from django.conf import settings
import stat

class DocumentList(generics.ListCreateAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializerUpload
    permission_classes=[IsUser,]
    
    def get_queryset(self):
        """
        Override the get_queryset() function to filter data based on user_id and organisation.owner.
        """
        # get organisation
        queryset = super().get_queryset()
        host_ip = os.environ.get('HOST_IP')
        id = self.request.user.id
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
        print(self.request)
        print('id: ' + str(id))
        auth_url = 'http://' + str(host_ip) + ':8002/api/users/'+ str(id)
        response = requests.get(auth_url)
        response_json = json.loads(response.content.decode('utf-8'))
        print('response auth: ' + str(response_json))
        user_organisation = response_json['organisation']
        print('user_organisation: ' + str(user_organisation))
        if user_organisation is None:
            queryset = queryset.filter(user_id=id)
            return queryset
        # get organisation owner
        org_url = 'http://' + str(host_ip) + ':8002/api/organisation/create/'
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url=org_url, headers=headers)
        print('response: ' + str(response))
        response_json1 = json.loads(response.content.decode('utf-8'))
        print('response org: ' + str(response_json1))
        org_data = response_json1[0]
        print('org_data: ' + str(org_data))
        owner=org_data['owner']
        print('owner: ' + str(owner))
        members=org_data['members']
        print('members: ' +str(members))
        print(members)
        if response_json['email'] == owner:
            queryset = queryset.filter(user_id__in=members)
        elif id in members:
            queryset = (queryset.filter(user_id__in=members, privacy="Public") | queryset.filter(user_id=id)).distinct()
        else:
            queryset = queryset.filter(user_id=id)
        
        return queryset
    
    

    

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
        user_id = self.request.user.id
        directory = os.path.join(settings.MEDIA_ROOT, str(user_id))
        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, instance.fileDoc.name.split('/')[-1])
        print(file_path)
        with open(file_path, 'wb') as destination:
            buffer_size = 8192  # 8KB buffer size
            while True:
                data = instance.fileDoc.read(buffer_size)
                if not data:
                    break
                destination.write(data)
                print(destination)
        instance.save()  # <--- save the updated instance



        
        
        instance.save()
        
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': id}
        timestamp_url = 'http://' + str(host_ip) + ':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)



from django.http import FileResponse
from django.http import JsonResponse
from django.http import StreamingHttpResponse


class DocContent (generics.RetrieveAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializer
    
    def get(self, request, *args, **kwargs):
        document_upload = self.get_object()
        file_response = FileResponse(document_upload.fileDoc)
        response = StreamingHttpResponse(file_response.streaming_content)
        response['Content-Disposition'] = f'attachment; filename="{document_upload.fileDoc.name}"'
        response['title'] = document_upload.title
        response['owner'] = document_upload.owner
        response['description'] = document_upload.description
        response['signed_status'] = document_upload.signed_status
        response['privacy'] = document_upload.privacy
        response['filetype'] = document_upload.filetype
        return response
    


class DocApiDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentSerializerUpdateDestroy
    permission_classes=[IsUser,]

    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Serialize instance and print the data
        serialized_data = self.serializer_class(instance).data
        self.perform_destroy(instance)

        action = 'Document Deleted'
        host_ip = os.environ.get('HOST_IP')
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': serialized_data['id']}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)
        
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
        token = self.request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        timestamp_data = {'action': action, 'document_id': instance.id}
        timestamp_url = 'http://'+str(host_ip)+':8001/api/createDoc/'
        response = requests.post(timestamp_url, data=timestamp_data, headers=headers)
        
        return Response(serializer.data)






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
