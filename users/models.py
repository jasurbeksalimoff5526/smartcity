from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Username is required")

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            username,
            password,
            **extra_fields
        )

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(
            username,
            password,
            **extra_fields
        )

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = "CITIZEN", "Citizen"
        OPERATOR = "OPERATOR", "Operator"
        TECHNICIAN = "TECHNICIAN", "Technician"
        ADMIN = "ADMIN", "Admin"



    phone = models.CharField(max_length=30, unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN,
        db_index=True,
    )
    categories = models.ManyToManyField(
        "incidents.Category",
        blank=True,
        related_name="users",
    )


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_citizen(self):
        return self.role == self.Role.CITIZEN

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN

    @property
    def is_system_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

