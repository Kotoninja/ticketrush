import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from event.models import Event
from hall.models import Hall, Venue
from rest_framework import status
from rest_framework.test import APIClient
from seat.models import Seat

from session.models import EventSession, SeatSession
from django.utils import timezone

class EventSessionAPITestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create venue
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="123 Test Street, Test City",
            description="Test venue description",
        )

        # Create hall
        self.hall = Hall.objects.create(
            venue=self.venue,
            number="1",
        )

        # Create event
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            duration=datetime.timedelta(hours=2),
        )

        # Create seats
        self.seats = []
        for i in range(5):
            seat = Seat.objects.create(hall=self.hall, number=i + 1)
            self.seats.append(seat)

        # Create event session
        self.event_session = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timezone.timedelta(seconds=5),
        )

    def test_list_event_sessions(self):
        """Test retrieving list of event sessions"""
        url = reverse("eventsession-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.event_session.id)
        self.assertEqual(response.data[0]["event"], self.event_session.event.id)

    def test_list_empty_event_sessions(self):
        """Test retrieving list when no event sessions exist"""
        # Delete existing event session
        EventSession.objects.all().delete()

        url = reverse("eventsession-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_event_session(self):
        """Test retrieving a single event session"""
        url = reverse("eventsession-detail", args=[self.event_session.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.event_session.id)
        self.assertEqual(response.data["event"], self.event_session.event.id)
        self.assertEqual(response.data["hall"], self.event_session.hall.id)
        self.assertIn("seats", response.data)
        self.assertEqual(len(response.data["seats"]), 5)

    def test_retrieve_nonexistent_event_session(self):
        """Test retrieving a non-existent event session"""
        url = reverse("eventsession-detail", args=[9999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_event_session(self):
        """Test creating a new event session"""
        url = reverse("eventsession-list")
        data = {
            "event": self.event.id,
            "hall": self.hall.id,
            "timestamp": "2026-07-10T10:00:00Z",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event"], self.event.id)
        self.assertEqual(response.data["hall"], self.hall.id)

        # Verify EventSession was created
        event_session_id = response.data["id"]
        event_session = EventSession.objects.get(id=event_session_id)
        self.assertEqual(event_session.event.id, self.event.id)
        self.assertEqual(event_session.hall.id, self.hall.id)

        # Verify SeatSession instances were created
        seat_sessions = SeatSession.objects.filter(event_session=event_session)
        self.assertEqual(seat_sessions.count(), 5)  # 5 seats in the hall

        # Verify all seat sessions have correct data
        for seat_session in seat_sessions:
            self.assertEqual(seat_session.status, "free")
            self.assertEqual(seat_session.price, Decimal("99.00"))

    def test_create_event_session_with_invalid_data(self):
        """Test creating event session with invalid data"""
        url = reverse("eventsession-list")

        # Test with non-existent event
        data = {
            "event": 9999,
            "hall": self.hall.id,
            "timestamp": "2026-07-10T10:00:00Z",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("event", response.data["errors"][0]["attr"])

        # Test with non-existent hall
        data = {
            "event": self.event.id,
            "hall": 9999,
            "timestamp": "2026-07-10T10:00:00Z",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("hall", response.data["errors"][0]["attr"])

        # Test with invalid timestamp
        data = {
            "event": self.event.id,
            "hall": self.hall.id,
            "timestamp": "invalid-timestamp",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("timestamp", response.data["errors"][0]["attr"])

    def test_create_duplicate_event_session(self):
        """Test creating a duplicate event session (should fail due to unique constraint)"""
        url = reverse("eventsession-list")
        data = {
            "event": self.event_session.event.id,
            "hall": self.event_session.hall.id,
            "timestamp": self.event_session.timestamp,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # DRF should return validation error due to unique constraint

    def test_create_event_session_creates_correct_seat_sessions(self):
        """Test that seat sessions are created with correct attributes"""
        # Create a new hall with specific seats
        new_hall = Hall.objects.create(
            venue=self.venue,
            number="3",
        )

        # Create seats for new hall
        for i in range(3):
            Seat.objects.create(hall=new_hall, number=i + 1)

        url = reverse("eventsession-list")
        data = {
            "event": self.event.id,
            "hall": new_hall.id,
            "timestamp": "2026-07-10T10:00:00Z",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event_session_id = response.data["id"]
        event_session = EventSession.objects.get(id=event_session_id)
        seat_sessions = SeatSession.objects.filter(event_session=event_session)

        # Verify all seats from the hall are attached
        hall_seats = Seat.objects.filter(hall=new_hall)
        self.assertEqual(seat_sessions.count(), hall_seats.count())

        # Verify each seat session corresponds to a hall seat
        seat_ids = [ss.seat.id for ss in seat_sessions]
        hall_seat_ids = [seat.id for seat in hall_seats]
        self.assertEqual(sorted(seat_ids), sorted(hall_seat_ids))

        # Verify all seat sessions are free and have correct price
        for seat_session in seat_sessions:
            self.assertEqual(seat_session.status, "free")
            self.assertEqual(seat_session.price, Decimal("99.00"))

    def test_event_session_list_with_multiple_sessions(self):
        """Test listing multiple event sessions"""
        # Create additional event session
        second_event_session = EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp="2026-07-11T10:00:00Z"
        )

        url = reverse("eventsession-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verify both sessions are in response
        ids = [item["id"] for item in response.data]
        self.assertIn(self.event_session.id, ids)
        self.assertIn(second_event_session.id, ids)

    def test_event_session_retrieve_includes_seats(self):
        """Test that retrieving an event session includes its seat sessions"""
        url = reverse("eventsession-detail", args=[self.event_session.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("seats", response.data)
        self.assertEqual(len(response.data["seats"]), 5)  # 5 seats created in setUp

        # Verify seat data structure
        for seat_data in response.data["seats"]:
            self.assertIn("id", seat_data)
            self.assertIn("seat", seat_data)
            self.assertIn("status", seat_data)
            self.assertIn("price", seat_data)
            self.assertEqual(seat_data["status"], "free")
            self.assertEqual(Decimal(seat_data["price"]), Decimal("99.00"))

    def test_create_event_session_with_hall_without_seats(self):
        """Test creating event session with a hall that has no seats"""
        empty_hall = Hall.objects.create(venue=self.venue, number="2")

        url = reverse("eventsession-list")
        data = {
            "event": self.event.id,
            "hall": empty_hall.id,
            "timestamp": "2026-07-10T10:00:00Z",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event_session_id = response.data["id"]
        event_session = EventSession.objects.get(id=event_session_id)
        seat_sessions = SeatSession.objects.filter(event_session=event_session)
        self.assertEqual(seat_sessions.count(), 0)
