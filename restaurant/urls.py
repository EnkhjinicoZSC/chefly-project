from django.urls import path
from .views import Dashboard, RequestDetails


urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('requests/<int:pk>/', RequestDetails.as_view(), name='request-details'),
]