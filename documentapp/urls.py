from django.urls import path
from .views import DocumentList, RequestApiUpdate, RequestApiDestroy, requestList, DocumentCRUD, DocumentByTitle, DocumentAll , DocumentDetail ,DownloadDocumentView, RequestApi

urlpatterns = [
    path("requests/", RequestApi.as_view(),),
    path("requestslist/", requestList.as_view()),
    path('requestdelete/<int:pk>/', RequestApiDestroy.as_view()),    
    path('doc/', DocumentList.as_view(), name='document-list'),
    path('requestupdate/<int:pk>/', RequestApiUpdate.as_view()),
    path('doc/<int:pk>/', DocumentCRUD.as_view(), name='document-crud'),
    path('title/<slug:title>/', DocumentByTitle.as_view(), name='document-by-title'),
    path('all/', DocumentAll.as_view(), name='document-all'),
    path('documents/<int:id>/', DocumentDetail.as_view(), name='document-detail'),
    path('documents/<int:pk>/download/', DownloadDocumentView.as_view(), name='document-download'),
]
