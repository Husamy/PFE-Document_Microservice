from django.urls import path
from .views import DocumentList, DocumentCRUD, DocumentByTitle, DocumentAll , DocumentDetail ,DownloadDocumentView

urlpatterns = [
    path('', DocumentList.as_view(), name='document-list'),
    path('<int:pk>/', DocumentCRUD.as_view(), name='document-crud'),
    path('title/<slug:title>/', DocumentByTitle.as_view(), name='document-by-title'),
    path('all/', DocumentAll.as_view(), name='document-all'),
    path('documents/<int:id>/', DocumentDetail.as_view(), name='document-detail'),
    path('documents/<int:pk>/download/', DownloadDocumentView.as_view(), name='document-download'),
]
