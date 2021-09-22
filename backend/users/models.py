from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

username_validator = UnicodeUsernameValidator()


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'

    ROLE = (
        (ADMIN, ADMIN),
        (USER, USER)
    )

    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=10,
        choices=ROLE,
        default=USER
    )

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    USERNAME_FIELD = 'email'


class Subscribe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriber')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscribing')

    class Meta:
        UniqueConstraint(fields=('user', 'author'), name='unique_subscriber')

