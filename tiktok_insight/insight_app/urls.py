from insight_app import views
from django.urls import path

urlpatterns = [
    path("", views.home, name="home"),
    path("upload-csv/", views.upload_csv, name="upload_csv"),
    path("analysis/", views.analysis, name="analysis"),
]
