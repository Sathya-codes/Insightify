from django.urls import path
from . import views, auth_views

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('pdfs/', views.PDFListView.as_view(), name='pdf_list'),
    path('pdf/<int:pk>/', views.pdf_detail, name='pdf_detail'),
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
]
