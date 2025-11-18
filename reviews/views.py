from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Review, Book


class HomeView(ListView):
	"""Homepage feed showing recent reviews.

	- If the user is authenticated, show reviews authored by users they follow.
	- Otherwise show all reviews.

	Context:
	- reviews: queryset of Review objects ordered by '-created'
	"""
	model = Review
	template_name = 'home.html'
	context_object_name = 'reviews'

	def get_queryset(self):
		"""Return the appropriate queryset for the home feed.

		Returns:
			QuerySet[Review]: reviews to display on the home page.
		"""
		user = self.request.user
		if user.is_authenticated:
			following_qs = user.following.all()
			return Review.objects.filter(user__in=following_qs).order_by('-created')
		return Review.objects.all().order_by('-created')


class AllReviewsView(ListView):
	"""List view for all reviews (paginated)."""
	model = Review
	template_name = 'reviews/all_reviews.html'
	context_object_name = 'reviews'
	queryset = Review.objects.all().order_by('-created')
	paginate_by = 10


class AllBooksView(ListView):
	"""List view for all books (paginated by title)."""
	model = Book
	template_name = 'reviews/all_books.html'
	context_object_name = 'books'
	queryset = Book.objects.all().order_by('title')
	paginate_by = 12


class BookSearchView(ListView):
	"""Search books by title.

	Renders `reviews/book_search_results.html` with the `books` context containing
	Book objects matching the query parameter `q`.
	"""
	model = Book
	template_name = 'reviews/book_search_results.html'
	context_object_name = 'books'

	def get_queryset(self):
		"""Return books matching the `q` GET parameter (case-insensitive)."""
		q = self.request.GET.get('q', '').strip()
		if not q:
			return Book.objects.none()
		return Book.objects.filter(title__icontains=q).order_by('title')


class BookDetailView(DetailView):
	"""Display a single book and its reviews.

	Context includes:
	- reviews: list of Review objects for this book
	- user_has_review: whether the current user already reviewed this book
	- user_review: the user's review object when present
	- image_exists: boolean indicating whether the book cover exists in storage
	"""
	model = Book
	template_name = 'reviews/book_detail.html'
	context_object_name = 'book'

	def get_context_data(self, **kwargs):
		"""Add reviews and user-specific flags to the book detail context."""
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
	"""Create a review for a given book (one review per user per book).

	- Prevents a user from creating more than one review per book via `dispatch`.
	- Associates the created Review with the Book and the requesting user in `form_valid`.
	"""
	model = Review
	fields = ['headline', 'body', 'rating']
	template_name = 'reviews/create_edit_review.html'

	def dispatch(self, request, *args, **kwargs):
		"""Block creation if the user already has a review for the book."""
		book_pk = kwargs.get('pk')
		if Review.objects.filter(book__pk=book_pk, user=request.user).exists():
			messages.error(request, 'You already posted a review for this book.')
			return redirect('reviews:book_detail', pk=book_pk)
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		"""Attach the book and the current user to the review before saving."""
		book_pk = self.kwargs.get('pk')
		book = get_object_or_404(Book, pk=book_pk)
		form.instance.book = book
		form.instance.user = self.request.user
		response = super().form_valid(form)
		messages.success(self.request, 'Review posted.')
		return response

	def get_context_data(self, **kwargs):
		"""Include the current Book object in the template context."""
		ctx = super().get_context_data(**kwargs)
		book_pk = self.kwargs.get('pk')
		ctx['book'] = get_object_or_404(Book, pk=book_pk)
		return ctx

	def get_success_url(self):
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})


class CreateBookView(LoginRequiredMixin, CreateView):
	"""Allow authenticated users to create a new Book.

	- Validates there is no existing book with the same title (case-insensitive).
	- Adds helpful context items for the template (form_title, cancel_url).
	"""

	model = Book
	fields = ['title', 'description', 'image']
	template_name = 'reviews/create_book.html'

	def form_valid(self, form):
		"""Prevent duplicate book titles and save the object on success."""
		title = form.cleaned_data.get('title')
		existing = Book.objects.filter(title__iexact=title).first()
		if existing:
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
	"""Mixin to ensure the current user is the owner of a Review instance."""

	def test_func(self):
		obj = self.get_object()
		return obj.user == self.request.user


class EditReviewView(LoginRequiredMixin, ReviewOwnerMixin, UpdateView):
	"""Edit an existing review (owner only)."""
	model = Review
	fields = ['headline', 'body', 'rating']
	template_name = 'reviews/create_edit_review.html'
	pk_url_kwarg = 'review_id'

	def get_success_url(self):
		# book pk is in URL kwargs
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		# the review object is the object being edited; add its book to context
		review = self.get_object()
		ctx['book'] = review.book
		return ctx


class DeleteReviewView(LoginRequiredMixin, ReviewOwnerMixin, DeleteView):
	"""Delete a review (owner only)."""
	model = Review
	template_name = 'reviews/confirm_delete.html'
	pk_url_kwarg = 'review_id'

	def get_success_url(self):
		return reverse('reviews:book_detail', kwargs={'pk': self.kwargs.get('pk')})

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		review = self.get_object()
		ctx['book'] = review.book
		return ctx
