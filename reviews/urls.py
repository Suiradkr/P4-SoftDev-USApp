from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.home, name='home'),
    path('all/', views.all_reviews, name='all_reviews'),
]
