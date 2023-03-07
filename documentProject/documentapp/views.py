from rest_framework import generics
from .models import Document
from .serializers import DocumentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentCRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentByTitle(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'title'

class DocumentAll(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentDetail(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'
    



class DownloadDocumentView(APIView):
    def get(self, request, pk, *args, **kwargs):
        document = get_object_or_404(Document, pk=pk)
        file = document.file
        response = Response(file.read(), content_type=file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{document.title}"'
        return response
