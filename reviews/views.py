from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Review, Book


class HomeView(ListView):
	model = Review
	template_name = 'home.html'
	context_object_name = 'reviews'

	def get_queryset(self):
		user = self.request.user
		if user.is_authenticated:
			following_qs = user.following.all()
			return Review.objects.filter(user__in=following_qs).order_by('-created')
		return Review.objects.all().order_by('-created')


class AllReviewsView(ListView):
	model = Review
	template_name = 'reviews/all_reviews.html'
	context_object_name = 'reviews'
	queryset = Review.objects.all().order_by('-created')


class BookDetailView(DetailView):
	model = Book
	template_name = 'reviews/book_detail.html'
	context_object_name = 'book'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		book = self.object
		reviews = Review.objects.filter(book=book).order_by('-created')
		ctx['reviews'] = reviews
		user = self.request.user
		ctx['user_has_review'] = False
		ctx['user_review'] = None
		if user.is_authenticated:
			try:
				user_review = Review.objects.get(book=book, user=user)
				ctx['user_has_review'] = True
				ctx['user_review'] = user_review
			except Review.DoesNotExist:
				pass
		
		image_exists = False
		try:
			if book.image and book.image.name and book.image.storage.exists(book.image.name):
				image_exists = True
		except Exception:
			image_exists = False
		ctx['image_exists'] = image_exists
		return ctx


class CreateReviewView(LoginRequiredMixin, CreateView):
	model = Review
	fields = ['headline', 'body', 'rating']
	template_name = 'reviews/create_edit_review.html'

	def dispatch(self, request, *args, **kwargs):
		book_pk = kwargs.get('pk')
		if Review.objects.filter(book__pk=book_pk, user=request.user).exists():
			messages.error(request, 'You already posted a review for this book.')
			return redirect('reviews:book_detail', pk=book_pk)
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		book_pk = self.kwargs.get('pk')
		book = get_object_or_404(Book, pk=book_pk)
		form.instance.book = book
		form.instance.user = self.request.user
		response = super().form_valid(form)
		messages.success(self.request, 'Review posted.')
		return response

	def get_success_url(self):
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})


class CreateBookView(LoginRequiredMixin, CreateView):
	
	model = Book
	fields = ['title', 'description', 'image']
	template_name = 'reviews/create_book.html'

	def form_valid(self, form):
		title = form.cleaned_data.get('title')
		existing = Book.objects.filter(title__iexact=title).first()
		if existing:
			# attach a non-field error and re-render the form page
			form.add_error(None, 'A book with that title already exists.')
			return self.form_invalid(form)

		response = super().form_valid(form)
		messages.success(self.request, 'Book created.')
		return response

	def get_success_url(self):
		return reverse('reviews:book_detail', kwargs={'pk': self.object.pk})

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx.setdefault('form_title', 'Add a new book')
		ctx.setdefault('cancel_url', '/')
		return ctx

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return redirect('reviews:home')
		return super().dispatch(request, *args, **kwargs)


class ReviewOwnerMixin(UserPassesTestMixin):
	def test_func(self):
		obj = self.get_object()
		return obj.user == self.request.user


class EditReviewView(LoginRequiredMixin, ReviewOwnerMixin, UpdateView):
	model = Review
	fields = ['headline', 'body', 'rating']
	template_name = 'reviews/create_edit_review.html'
	pk_url_kwarg = 'review_id'

	def get_success_url(self):
		# book pk is in URL kwargs
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})


class DeleteReviewView(LoginRequiredMixin, ReviewOwnerMixin, DeleteView):
	model = Review
	template_name = 'reviews/confirm_delete.html'
	pk_url_kwarg = 'review_id'

	def get_success_url(self):
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})
