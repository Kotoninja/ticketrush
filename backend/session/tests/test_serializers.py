import datetime
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from event.models import Event
from hall.models import Hall, Venue
from seat.models import Seat

from session.models import EventSession, SeatSession
from session.serializers import EventSessionReadSerializer, EventSessionWriteSerializer

from django.utils import timezone


class EventSessionSerializerTest(TestCase):
    def setUp(self):
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

        # Create event session
        self.event_session = EventSession.objects.create(
            event=self.event, hall=self.hall,             timestamp=timezone.now() + timezone.timedelta(seconds=5),

        )

        # Create seats
        self.seats = []
        for i in range(3):
            seat = Seat.objects.create(hall=self.hall, number=i + 1)
            self.seats.append(seat)

            # Create seat sessions
            SeatSession.objects.create(
                event_session=self.event_session,
                seat=seat,
                status="free",
                price=Decimal("99.00"),
            )

    def test_event_session_read_serializer_includes_seats(self):
        """Test that read serializer includes seat sessions"""

        serializer = EventSessionReadSerializer(self.event_session)
        data = serializer.data

        self.assertIn("seats", data)
        self.assertEqual(len(data["seats"]), 3)
        self.assertIn("event", data)
        self.assertIn("hall", data)
        self.assertIn("timestamp", data)

        # Verify seat data
        for seat_data in data["seats"]:
            self.assertIn("id", seat_data)
            self.assertIn("seat", seat_data)
            self.assertIn("status", seat_data)
            self.assertIn("price", seat_data)

    def test_event_session_write_serializer_validation(self):
        """Test write serializer validation"""

        # Valid data
        valid_data = {
            "event": self.event.id,
            "hall": self.hall.id,
            "timestamp": timezone.now() + timezone.timedelta(seconds=5),
        }
        serializer = EventSessionWriteSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Invalid data - missing required fields
        invalid_data = {"event": self.event.id}
        serializer = EventSessionWriteSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("hall", serializer.errors)
        self.assertIn("timestamp", serializer.errors)

        # Invalid data - wrong field types
        invalid_data = {
            "event": self.event.id,
            "hall": "not_a_number",
            "timestamp": timezone.now() + timezone.timedelta(seconds=5),
        }
        serializer = EventSessionWriteSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("hall", serializer.errors)
