from django.test import TestCase

from organization.models import Organization  # adjust import path as needed
from venue.models import Venue
from venue.serializers import VenueSerializer


class VenueSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name="Org A")
        cls.org_b = Organization.objects.create(name="Org B")

    def test_serializes_all_expected_fields(self):
        venue = Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        data = VenueSerializer(venue).data
        for field in ("id", "created_by", "description", "name", "address", "site_link"):
            self.assertIn(field, data)
        self.assertEqual(data["name"], "Main Hall")
        self.assertEqual(data["created_by"], self.org_a.pk)

    def test_valid_data_creates_venue(self):
        payload = {
            "created_by": self.org_a.pk,
            "description": "desc",
            "name": "New Hall",
            "address": "1 New St",
        }
        serializer = VenueSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        venue = serializer.save()
        self.assertEqual(venue.name, "New Hall")

    def test_missing_required_fields_invalid(self):
        serializer = VenueSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        self.assertIn("address", serializer.errors)
        self.assertIn("description", serializer.errors)

    def test_duplicate_name_and_address_invalid(self):
        Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        payload = {
            "created_by": self.org_a.pk,
            "description": "another desc",
            "name": "Main Hall",
            "address": "123 Main St",
        }
        serializer = VenueSerializer(data=payload)
        self.assertFalse(serializer.is_valid())

    def test_created_by_currently_writable_from_any_org(self):
        """
        Documents current (arguably unsafe) behavior: `created_by` is not
        restricted to the requesting user's organization at the serializer
        level, so any organization id can be supplied directly.
        """
        payload = {
            "created_by": self.org_b.pk,
            "description": "desc",
            "name": "Some Hall",
            "address": "Some Address",
        }
        serializer = VenueSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        venue = serializer.save()
        self.assertEqual(venue.created_by_id, self.org_b.pk)

    def test_invalid_site_link_rejected(self):
        payload = {
            "created_by": self.org_a.pk,
            "description": "desc",
            "name": "Bad Link Hall",
            "address": "Some Address",
            "site_link": "not-a-valid-url",
        }
        serializer = VenueSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("site_link", serializer.errors)