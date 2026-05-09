from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

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
    title = models.CharField(max_length=180)
    description = models.TextField()
    image = models.ImageField(upload_to="incidents/%Y/%m/", blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="incident_status_idx"),
            models.Index(fields=["category"], name="incident_category_idx"),
            models.Index(fields=["priority"], name="incident_priority_idx"),
            models.Index(fields=["status", "priority"], name="incident_status_priority_idx"),
        ]

    def __str__(self):
        return f"#{self.pk} {self.title}"

    def clean(self):
        if self.status in {self.Status.IN_PROGRESS, self.Status.RESOLVED} and not self.technician:
            raise ValidationError("Incident must have a technician before progress or resolution.")
        if self.status == self.Status.RESOLVED and not self.resolution_note:
            raise ValidationError("Resolution note is required before resolving an incident.")

    def assign_to(self, technician):
        self.technician = technician
        if self.status == self.Status.NEW:
            self.status = self.Status.IN_PROGRESS

    def resolve(self, note):
        self.resolution_note = note
        self.status = self.Status.RESOLVED

    def close(self):
        if self.status != self.Status.RESOLVED:
            raise ValidationError("Only resolved incidents can be closed.")
        self.status = self.Status.CLOSED
