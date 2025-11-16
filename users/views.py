from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import DetailView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'users/profile.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UserSearchView(LoginRequiredMixin, TemplateView):
    """Search for users by partial first/last/username. Requires login."""
    template_name = 'users/search_results.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        results = []
        if q:
            User = get_user_model()
            results = User.objects.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q)
            ).order_by('first_name', 'last_name')
        
        following_ids = []
        if request.user.is_authenticated:
            following_ids = list(request.user.following.values_list('pk', flat=True))

        return render(request, self.template_name, {'query': q, 'results': results, 'following_ids': following_ids})


class FollowToggleView(LoginRequiredMixin, View):
    
    def post(self, request, user_id):
        User = get_user_model()
        target = User.objects.filter(pk=user_id).first()
        if not target or target == request.user:
            messages.error(request, 'Invalid user.')
            return redirect('users:profile')

        # toggle follow
        if request.user.following.filter(pk=target.pk).exists():
            request.user.following.remove(target)
            messages.success(request, f'You unfollowed {target.full_name}.')
        else:
            request.user.following.add(target)
            messages.success(request, f'You are now following {target.full_name}.')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('users:profile')))


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        is_following = False
        if user.is_authenticated and user != self.object:
            is_following = user.following.filter(pk=self.object.pk).exists()
        ctx['is_following'] = is_following
        return ctx


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

        user = User.objects.create_user(username=username, password=password1)
        return render(request, 'users/signup.html', {
            'created': True,
            'username': user.username,
        })
