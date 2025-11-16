from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('all/', views.AllReviewsView.as_view(), name='all_reviews'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/new/', views.CreateBookView.as_view(), name='create_book'),
    # path('book/<int:pk>/review/new/', views.CreateReviewView.as_view(), name='create_review'),
    # path('book/<int:pk>/review/<int:review_id>/edit/', views.EditReviewView.as_view(), name='edit_review'),
    # path('book/<int:pk>/review/<int:review_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),
]
