from django.test import TestCase
from rest_framework.exceptions import ValidationError

from organization.models import Organization
from venue.models import Venue
from venue.validators import get_venue_exist, name_validation_for_a_exists_organization


class GetVenueExistTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name="Org A")

    def test_returns_none_when_no_venue_with_name(self):
        fake_instance = Venue(name="Nonexistent")
        self.assertIsNone(get_venue_exist(fake_instance))

    def test_returns_matching_venue_by_name(self):
        existing = Venue.objects.create(
            created_by=self.org_a, description="d", name="Arena", address="1 St"
        )
        instance = Venue(name="Arena")
        result = get_venue_exist(instance)
        self.assertEqual(result, existing)

    def test_matches_first_by_name_regardless_of_address(self):
        Venue.objects.create(
            created_by=self.org_a, description="d", name="Arena", address="1 St"
        )
        instance = Venue(name="Arena", address="Different Street")
        result = get_venue_exist(instance)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Arena")


class NameValidationForExistingOrganizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organization.objects.create(name="Org A")
        cls.org_b = Organization.objects.create(name="Org B")

    def test_no_error_when_name_is_new(self):
        instance = Venue(created_by=self.org_a, name="Brand New Venue")
        # Should not raise
        name_validation_for_a_exists_organization(instance)

    def test_no_error_when_same_organization_reuses_name(self):
        Venue.objects.create(
            created_by=self.org_a, description="d", name="Repeat Name", address="1 St"
        )
        instance = Venue(created_by=self.org_a, name="Repeat Name", address="2 St")
        # Same org reusing the name at a different address -> allowed
        name_validation_for_a_exists_organization(instance)

    def test_raises_when_different_organization_reuses_name(self):
        Venue.objects.create(
            created_by=self.org_a, description="d", name="Taken Name", address="1 St"
        )
        instance = Venue(created_by=self.org_b, name="Taken Name", address="2 St")

        with self.assertRaises(ValidationError):
            name_validation_for_a_exists_organization(instance)

    def test_raises_when_existing_has_no_org_and_new_has_org(self):
        Venue.objects.create(
            created_by=None, description="d", name="Orphan Name", address="1 St"
        )
        instance = Venue(created_by=self.org_a, name="Orphan Name", address="2 St")

        with self.assertRaises(ValidationError):
            name_validation_for_a_exists_organization(instance)

    def test_no_error_when_both_existing_and_new_have_no_org(self):
        Venue.objects.create(
            created_by=None, description="d", name="Orphan Name", address="1 St"
        )
        instance = Venue(created_by=None, name="Orphan Name", address="2 St")
        # None == None -> no error
        name_validation_for_a_exists_organization(instance)