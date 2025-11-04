from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Review


def home(request):

	if request.user.is_authenticated:
		following_qs = request.user.following.all()
		reviews = Review.objects.filter(user__in=following_qs).order_by('-created')
	else:
		reviews = Review.objects.all().order_by('-created')
	return render(request, 'home.html', {'reviews': reviews})


def all_reviews(request):

	reviews = Review.objects.all().order_by('-created')
	return render(request, 'reviews/all_reviews.html', {'reviews': reviews})
