# LITREVIEW

This repository contains basic code to get you started on the LIT Review platform.

## Structure

The project has two Django applications:
* `reviews`: contains the models for the `Book` and `Review` entities
* `users`: contains the model for the custom user model (see `AUTH_USER_MODEL` in [`settings.py`](litreview/settings.py))

## Setup

Install the dependencies (make sure you are using a virtual environment): `pip install -r requirements.txt`

Make sure the database migrations are applied: 
```bash
python manage.py migrate
```
You can then run the server with
```bash 
python manage.py runserver
```

Refer to [Django documentation](https://docs.djangoproject.com/en/) for more information.

## Available URL paths

The project exposes the following user-facing routes (running the dev server at http://127.0.0.1:8000/):

Reviews (root namespace)
- `/` — Home feed. Logged-in users see reviews by users they follow; anonymous users see all reviews.
- `/all/` — All reviews (paginated).
- `/book/<pk>/` — Book detail page (replace `<pk>` with the book's primary key).
- `/book/new/` — Create a new book (logged-in users).
- `/search/books/?q=...` — Search books by title (GET param `q`).
- `/book/<pk>/review/new/` — Create a review for the book with id `<pk>` (logged-in users).
- `/book/<pk>/review/<review_id>/edit/` — Edit review `<review_id>` for book `<pk>` (author only).
- `/book/<pk>/review/<review_id>/delete/` — Delete review `<review_id>` for book `<pk>` (author only).

Users (under `/users/` namespace)
- `/users/login/` — Log in.
- `/users/logout/` — Log out (POST).
- `/users/signup/` — Create a new account (sign up form).
- `/users/profile/` — Your profile (must be logged in).
- `/users/profile/<pk>/` — Public profile view for user `<pk>` with follow/unfollow controls.
- `/users/search/?q=...` — Search for users by first name, last name, or username (logged-in users).
- `/users/follow/<user_id>/` — Toggle follow/unfollow for user with id `<user_id>` (POST).

Other
- `/admin/` — Django admin site (if enabled and you have a superuser).

Notes
- Media files (book cover images) are served from `/media/` in DEBUG mode and static assets from `/static/`.
- Follow actions and some other changes perform POST requests and will redirect back to the referring page.


## Templates and auth requirements

Below is a quick reference table mapping routes to the template(s) used and the auth requirement.

| Route | Template(s) | Auth required? | Notes |
|---|---|:---:|---|
| `/` | `templates/home.html` (extends `templates/base.html`) | No | Home feed — different content for logged-in users (their follow feed) |
| `/all/` | `templates/reviews/all_reviews.html` | No | Paginated list of all reviews |
| `/book/<pk>/` | `templates/reviews/book_detail.html` | No | Book detail; logged-in users can post reviews; authors see edit/delete links |
| `/book/new/` | `templates/reviews/create_book.html` | Yes | Create a new book (logged-in users) |
| `/search/books/?q=...` | `templates/reviews/book_search_results.html` | No | Book title search (GET param `q`) |
| `/book/<pk>/review/new/` | `templates/reviews/create_edit_review.html` | Yes | Create review for book `<pk>` |
| `/book/<pk>/review/<review_id>/edit/` | `templates/reviews/create_edit_review.html` | Yes | Edit review (author only) |
| `/book/<pk>/review/<review_id>/delete/` | `templates/reviews/confirm_delete.html` | Yes | Delete review (author only) |
| `/users/login/` | `templates/users/login.html` | No | Login page |
| `/users/logout/` | (redirect) | Yes (POST) | Logout endpoint (POST) |
| `/users/signup/` | `templates/users/signup.html` | No | Sign up form |
| `/users/profile/` | `templates/users/profile.html` | Yes | Logged-in user's profile; includes user-search form |
| `/users/profile/<pk>/` | `templates/users/user_detail.html` | No | Public profile for user `<pk>`; follow/unfollow button for logged-in users |
| `/users/search/?q=...` | `templates/users/search_results.html` | Yes | Search users by first/last/username; results include follow controls |
| `/users/follow/<user_id>/` | (POST toggle) | Yes (POST) | Toggle follow/unfollow for user `<user_id>` |

Shared templates and assets:

- `templates/base.html` — site header/nav and loads `static/css/site.css`.
- `templates/reviews/_review_card.html` — reusable include used on index and search results to show a book-review card (image + title + snippet).
- `static/css/site.css` — site styles used across pages.


