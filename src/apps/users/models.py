from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Email required")
        
        email = self.normalize_email(email)
        username = username.lower()
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.is_active = False
        user.date_joined = timezone.now()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    avatar_image = models.ImageField(upload_to='images', default='images/default_avatar.png')
    date_joined = models.DateTimeField(_("date joined"), blank=True, null=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    
    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
    
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD = 'email'
