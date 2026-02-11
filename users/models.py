# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class RevUser(AbstractUser):
    """Usuario personalizado para el dashboard"""
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, choices=(
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("manager", "Manager")
    ), default="analyst")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='revuser_set',
        related_query_name='revuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='revuser_set',
        related_query_name='revuser',
    )

    def __str__(self):
        return self.username
