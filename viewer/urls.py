from django.urls import path
from . import views

app_name = 'viewer'

urlpatterns = [
    path('', views.upload_pdf, name='upload'),
    path('view/<uuid:job_id>/', views.view_results, name='view_results'),
]
