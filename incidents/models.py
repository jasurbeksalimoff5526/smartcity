from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=120,
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Incident(models.Model):

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    VALID_TRANSITIONS = {
        Status.NEW: [Status.IN_PROGRESS],
        Status.IN_PROGRESS: [Status.RESOLVED],
        Status.RESOLVED: [Status.CLOSED],
        Status.CLOSED: [],
    }

    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_incidents",
    )

    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_incidents",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="incidents",
    )

    title = models.CharField(
        max_length=180,
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="incidents/%Y/%m/",
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    address = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    resolution_note = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["status"],
                name="incident_status_idx",
            ),
            models.Index(
                fields=["category"],
                name="incident_category_idx",
            ),
            models.Index(
                fields=["priority"],
                name="incident_priority_idx",
            ),
            models.Index(
                fields=["status", "priority"],
                name="incident_status_priority_idx",
            ),
        ]

    def __str__(self):
        return f"#{self.pk} {self.title}"

    def clean(self):

        if (
            self.status in {
                self.Status.IN_PROGRESS,
                self.Status.RESOLVED,
            }
            and not self.technician
        ):
            raise ValidationError(
                "Incident must have a technician."
            )

        if (
            self.status == self.Status.RESOLVED
            and not self.resolution_note
        ):
            raise ValidationError(
                "Resolution note is required."
            )

        if self.technician:

            if not self.technician.is_technician:
                raise ValidationError(
                    "Assigned user must be a technician."
                )

            if (
                self.category
                not in self.technician.categories.all()
            ):
                raise ValidationError(
                    "Technician is not assigned to this category."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def can_transition(self, new_status):

        allowed = self.VALID_TRANSITIONS.get(
            self.status,
            [],
        )

        return new_status in allowed

    def change_status(self, new_status):

        if not self.can_transition(new_status):
            raise ValidationError(
                f"Cannot change status "
                f"from {self.status} to {new_status}."
            )

        self.status = new_status

    def assign_to(self, technician):

        if not technician.is_technician:
            raise ValidationError(
                "Only technicians can be assigned."
            )

        if (
            self.category
            not in technician.categories.all()
        ):
            raise ValidationError(
                "Technician does not handle this category."
            )

        self.technician = technician

        if self.status == self.Status.NEW:
            self.status = self.Status.IN_PROGRESS

        self.save()

    def resolve(self, user, note):

        if not self.technician:
            raise ValidationError(
                "Incident has no assigned technician."
            )

        if user != self.technician:
            raise ValidationError(
                "Only assigned technician can resolve incident."
            )

        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress incidents can be resolved."
            )

        self.resolution_note = note
        self.status = self.Status.RESOLVED

        self.save()

    def close(self):

        if self.status != self.Status.RESOLVED:
            raise ValidationError(
                "Only resolved incidents can be closed."
            )

        self.status = self.Status.CLOSED

        self.save()
