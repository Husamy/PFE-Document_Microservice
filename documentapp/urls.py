from django.urls import path
from .views import DownloadDocumentView, DocContent, UserRequestSignsView, DocumentAll, DocApiDestroy, DocumentList, requestList, RequestApi, RequestApiUpdate, RequestApiDestroy

urlpatterns = [
    path("requests/", RequestApi.as_view(),),
    path("requestslist/", requestList.as_view()),
    path('requestupdate/<int:document_id>/', RequestApiUpdate.as_view()),
    path('requestdelete/<int:document_id>/', RequestApiDestroy.as_view()),    
    path('doc/', DocumentList.as_view(), name='document-list'),
    path('requestTitle/<int:document_id>/', UserRequestSignsView.as_view()),
    path('doc/all/', DocumentAll.as_view(), name='document-all'),
    path('doc/<int:pk>/', DocApiDestroy.as_view(), name='document-crud'),
    path('doc/content/<int:pk>', DocContent.as_view()),
    path('doc/<int:pk>/download/', DownloadDocumentView.as_view(), name='document-download'),
]
