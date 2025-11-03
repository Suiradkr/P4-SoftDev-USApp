from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'users/profile.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # expose the user in the template context (TemplateView already provides request via context processors)
        context['user'] = self.request.user
        return context


class SignupView(View):

    def get(self, request):
        # redirect authenticated users to profile
        if request.user.is_authenticated:
            return redirect('users:profile')
        return render(request, 'users/signup.html', {'form_data': {}})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        errors = []

        User = get_user_model()
        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('This username is already taken.')

        if not password1 or not password2:
            errors.append('Both password fields are required.')
        elif password1 != password2:
            errors.append('Passwords do not match.')

        if errors:
            return render(request, 'users/signup.html', {
                'errors': errors,
                'form_data': {'username': username},
            })

        # create user
        user = User.objects.create_user(username=username, password=password1)
        return render(request, 'users/signup.html', {
            'created': True,
            'username': user.username,
        })
