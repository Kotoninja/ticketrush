from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from organization.models import Organization
from venue.models import Venue
from django.urls import reverse


class VenueAPITests(APITestCase):
    """
    Uses DRF's APITestCase, which subclasses django.test.TestCase and its
    Client-based request/response cycle -- no pytest involved.
    """

    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name="Org A")
        cls.org_b = Organization.objects.create(name="Org B")

    def setUp(self):
        self.venue = Venue.objects.create(
            created_by=self.org_a,
            description="Existing venue",
            name="Existing Hall",
            address="1 Existing St",
        )

    def test_list_venues(self):
        response = self.client.get(
            reverse("venue-list")
        )  # adjust URL to match your router
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 1)

    def test_retrieve_venue(self):
        response = self.client.get(reverse("venue-detail", args=[self.venue.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Existing Hall")

    def test_create_venue_success(self):
        payload = {
            "created_by": self.org_a.pk,
            "description": "New venue",
            "name": "New Hall",
            "address": "2 New St",
        }
        response = self.client.post(reverse("venue-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Venue.objects.filter(name="New Hall").exists())

    def test_create_venue_duplicate_name_address_fails(self):
        payload = {
            "created_by": self.org_a.pk,
            "description": "Duplicate",
            "name": self.venue.name,
            "address": self.venue.address,
        }
        response = self.client.post(reverse("venue-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_venue_same_name_different_org_fails(self):
        payload = {
            "created_by": self.org_b.pk,
            "description": "Cross-org duplicate",
            "name": self.venue.name,
            "address": "Some other address",
        }
        response = self.client.post(reverse("venue-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data["errors"][0]["attr"])

    def test_create_venue_same_name_same_org_different_address_success(self):
        payload = {
            "created_by": self.org_a.pk,
            "description": "Another location",
            "name": self.venue.name,
            "address": "A totally different address",
        }
        response = self.client.post(reverse("venue-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_venue(self):
        payload = {"description": "Updated description"}
        response = self.client.patch(
            reverse("venue-detail", args=[self.venue.pk]), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.description, "Updated description")

    def test_delete_venue(self):
        response = self.client.delete(reverse("venue-detail", args=[self.venue.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Venue.objects.filter(pk=self.venue.pk).exists())
