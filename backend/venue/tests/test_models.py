from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.test import TestCase
from rest_framework.validators import ValidationError as DRFValidationError

from organization.models import Organization
from venue.models import Venue


class VenueModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name="Org A")
        cls.org_b = Organization.objects.create(name="Org B")

    def test_create_venue_minimal(self):
        venue = Venue.objects.create(
            created_by=self.org_a,
            description="A nice place",
            name="Main Hall",
            address="123 Main St",
        )
        self.assertIsNotNone(venue.pk)
        self.assertEqual(venue.name, "Main Hall")

    def test_str_representation_with_org(self):
        venue = Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        self.assertEqual(str(venue), f"Main Hall / {self.org_a.name}")

    def test_str_representation_without_org(self):
        venue = Venue.objects.create(
            created_by=None,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        self.assertEqual(str(venue), "Main Hall / No Organization")

    def test_site_link_optional(self):
        venue = Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        self.assertIn(venue.site_link, (None, ""))

    def test_unique_constraint_same_name_and_address(self):
        Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        with self.assertRaises(DjangoValidationError):
            with transaction.atomic():
                Venue.objects.create(
                    created_by=self.org_a,
                    description="another desc",
                    name="Main Hall",
                    address="123 Main St",
                )

    def test_same_name_different_address_same_org_allowed(self):
        Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        venue2 = Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="456 Other St",
        )
        self.assertIsNotNone(venue2.pk)

    def test_same_name_different_org_rejected_by_clean(self):
        Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Main Hall",
            address="123 Main St",
        )
        venue2 = Venue(
            created_by=self.org_b,
            description="desc",
            name="Main Hall",
            address="999 Different St",
        )
        with self.assertRaises((DjangoValidationError, DRFValidationError)):
            venue2.save()

    def test_same_name_different_org_rejected_even_with_different_address(self):
        Venue.objects.create(
            created_by=self.org_a,
            description="desc",
            name="Unique Name",
            address="Address A",
        )
        venue2 = Venue(
            created_by=self.org_b,
            description="desc",
            name="Unique Name",
            address="Address B",
        )
        with self.assertRaises((DjangoValidationError, DRFValidationError)):
            venue2.save()

    def test_full_clean_called_on_save(self):
        # description exceeds max_length=400 -> full_clean() in save() should raise
        venue = Venue(
            created_by=self.org_a,
            description="x" * 401,
            name="Long Desc Venue",
            address="Some Address",
        )
        with self.assertRaises(DjangoValidationError):
            venue.save()

    def test_name_max_length(self):
        venue = Venue(
            created_by=self.org_a,
            description="desc",
            name="x" * 51,  # max_length=50
            address="Some Address",
        )
        with self.assertRaises(DjangoValidationError):
            venue.save()
