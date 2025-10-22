from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProfileView

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', next_page='/users/profile/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/users/login'), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
