from django.urls import path
from .views import DownloadDocumentView, UserRequestSignsView, DocumentAll, DocApiDestroy, DocumentList, requestList, RequestApi, RequestApiUpdate, RequestApiDestroy

urlpatterns = [
    path("requests/", RequestApi.as_view(),),
    path("requestslist/", requestList.as_view()),
    path('requestupdate/<int:pk>/', RequestApiUpdate.as_view()),
    path('requestdelete/<int:pk>/', RequestApiDestroy.as_view()),    
    path('doc/', DocumentList.as_view(), name='document-list'),
    path('requestTitle/<int:pk>/', UserRequestSignsView.as_view()),
    path('doc/all/', DocumentAll.as_view(), name='document-all'),
    path('doc/<int:pk>/', DocApiDestroy.as_view(), name='document-crud'),
    path('doc/<int:pk>/download/', DownloadDocumentView.as_view(), name='document-download'),
]
