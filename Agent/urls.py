from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'Agent'

urlpatterns = [
    path('document/<int:document_id>/', views.document_detail, name='document_detail'),
    path('agent/generate/', views.generate_document, name='generate_document'),
    path('api/document/<int:document_id>/status/', views.update_document_status, name='update_status'),
    path('document/<int:document_id>/download/', views.download_document, name='download_document'),
    path('api/document/<int:document_id>/upload-image/', views.upload_cv_image, name='upload_cv_image'),
    path('api/document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('agent/test-post/', views.test_post_endpoint, name='test_post_endpoint'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)