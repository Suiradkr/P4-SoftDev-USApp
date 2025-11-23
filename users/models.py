from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user class that has the "following" field"""

    # We reuse the fields definitions from the parent class, but change `blank` to False
    # We want to make sure first and last names are always provided
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)

    # A following B does not automatically make B follow A
    following = models.ManyToManyField("self", symmetrical=False, related_name='followers', blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
