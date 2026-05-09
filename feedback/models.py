from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from incidents.models import Incident


class Feedback(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["incident", "citizen"],
                name="unique_feedback_per_incident_citizen",
            )
        ]

    def __str__(self):
        return f"{self.incident} - {self.rating}/5"
