from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = "User"
        db_table = "user"


class ManagerUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(groups__name="Manager")


class Manager(CustomUser):
    objects = ManagerUserManager()

    class Meta:
        proxy = True


class CustomerManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(groups__isnull=False)
            .exclude(is_superuser=True)
        )


class Customer(CustomUser):
    objects = CustomerManager()

    class Meta:
        proxy = True


class SuperUserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=True)


class SuperUser(CustomUser):
    objects = SuperUserManager()

    class Meta:
        proxy = True
