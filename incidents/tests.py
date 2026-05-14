from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import User

from .forms import IncidentAssignmentForm, IncidentCreateForm
from .models import Category, Incident


class IncidentFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Road")

    def test_location_fields_are_hidden_and_required(self):
        form = IncidentCreateForm(
            data={
                "category": self.category.pk,
                "title": "Broken light",
                "description": "Street light is not working.",
                "address": "Main street",
                "priority": Incident.Priority.MEDIUM,
            }
        )

        self.assertEqual(form.fields["latitude"].widget.input_type, "hidden")
        self.assertEqual(form.fields["longitude"].widget.input_type, "hidden")
        self.assertFalse(form.is_valid())
        self.assertIn("latitude", form.errors)
        self.assertIn("longitude", form.errors)

    def test_assignment_form_lists_only_matching_category_technicians(self):
        other_category = Category.objects.create(name="Water")
        citizen = User.objects.create_user(
            username="citizen",
            password="pass",
            phone="100",
            role=User.Role.CITIZEN,
        )
        matching_technician = User.objects.create_user(
            username="tech-road",
            password="pass",
            phone="101",
            role=User.Role.TECHNICIAN,
        )
        matching_technician.categories.add(self.category)
        other_technician = User.objects.create_user(
            username="tech-water",
            password="pass",
            phone="102",
            role=User.Role.TECHNICIAN,
        )
        other_technician.categories.add(other_category)
        incident = Incident.objects.create(
            citizen=citizen,
            category=self.category,
            title="Broken light",
            description="Street light is not working.",
            latitude=Decimal("41.311081"),
            longitude=Decimal("69.240562"),
            address="Main street",
        )

        form = IncidentAssignmentForm(instance=incident)

        self.assertIn(matching_technician, form.fields["technician"].queryset)
        self.assertNotIn(other_technician, form.fields["technician"].queryset)


class IncidentAssignmentViewTests(TestCase):
    def setUp(self):
        self.road = Category.objects.create(name="Road")
        self.water = Category.objects.create(name="Water")
        self.citizen = User.objects.create_user(
            username="citizen",
            password="pass",
            phone="200",
            role=User.Role.CITIZEN,
        )
        self.operator = User.objects.create_user(
            username="operator",
            password="pass",
            phone="201",
            role=User.Role.OPERATOR,
        )
        self.operator.categories.add(self.road)
        self.technician = User.objects.create_user(
            username="technician",
            password="pass",
            phone="202",
            role=User.Role.TECHNICIAN,
        )
        self.technician.categories.add(self.road)
        self.road_incident = self.create_incident(self.road, "Road incident")
        self.water_incident = self.create_incident(self.water, "Water incident")

    def create_incident(self, category, title):
        return Incident.objects.create(
            citizen=self.citizen,
            category=category,
            title=title,
            description="Needs attention.",
            latitude=Decimal("41.311081"),
            longitude=Decimal("69.240562"),
            address="Main street",
        )

    def test_category_operator_can_assign_own_category_incident(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse("incidents:incident_assign", kwargs={"pk": self.road_incident.pk}),
            data={
                "technician": self.technician.pk,
                "status": Incident.Status.NEW,
                "priority": Incident.Priority.MEDIUM,
            },
        )

        self.assertRedirects(
            response,
            reverse("incidents:incident_detail", kwargs={"pk": self.road_incident.pk}),
        )
        self.road_incident.refresh_from_db()
        self.assertEqual(self.road_incident.technician, self.technician)
        self.assertEqual(self.road_incident.status, Incident.Status.IN_PROGRESS)

    def test_category_operator_cannot_assign_other_category_incident(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("incidents:incident_assign", kwargs={"pk": self.water_incident.pk})
        )

        self.assertEqual(response.status_code, 404)


class IncidentCreateViewTests(TestCase):
    def test_create_page_renders_gps_location_control(self):
        Category.objects.create(name="Road")
        citizen = User.objects.create_user(
            username="citizen-create",
            password="pass",
            phone="300",
            role=User.Role.CITIZEN,
        )
        self.client.force_login(citizen)

        response = self.client.get(reverse("incidents:incident_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GPS location olish")
        self.assertContains(response, "input type=\"hidden\" name=\"latitude\"")
        self.assertContains(response, "input type=\"hidden\" name=\"longitude\"")
