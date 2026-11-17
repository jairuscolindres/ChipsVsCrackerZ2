from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        AUTHOR = 'author', _('Author')
        PLAYER = 'player', _('Player')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PLAYER)
    website_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
