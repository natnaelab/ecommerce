from django.contrib.auth.models import AbstractUser


# proxy model
class CustomUser(AbstractUser):
    class Meta:
        verbose_name = "User"
