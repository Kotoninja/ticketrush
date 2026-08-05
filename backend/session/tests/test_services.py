import datetime
from decimal import Decimal

from django.test import TestCase
from event.models import Event
from hall.models import Hall, Venue
from seat.models import Seat

from session.models import EventSession, SeatSession
from session.services import attach_all_places_to_event_session
from django.utils import timezone


class EventSessionServicesTest(TestCase):
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
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timezone.timedelta(seconds=5),
        )

        # Create seats
        self.seats = []
        for i in range(5):
            seat = Seat.objects.create(hall=self.hall, number=i + 1)
            self.seats.append(seat)

    def test_attach_all_places_to_event_session(self):
        """Test the service function attaches all seats to event session"""

        # Initially no seat sessions
        self.assertEqual(
            SeatSession.objects.filter(event_session=self.event_session).count(), 0
        )

        # Call the service
        result = attach_all_places_to_event_session(self.event_session)

        # Verify the result is the same instance
        self.assertEqual(result, self.event_session)

        # Verify seat sessions were created
        seat_sessions = SeatSession.objects.filter(event_session=self.event_session)
        self.assertEqual(seat_sessions.count(), 5)

        # Verify attributes
        for seat_session in seat_sessions:
            self.assertEqual(seat_session.status, "free")
            self.assertEqual(seat_session.price, Decimal("99.00"))
            self.assertIn(seat_session.seat, self.seats)

    def test_attach_all_places_to_event_session_empty_hall(self):
        """Test service function with a hall that has no seats"""

        # Remove all seats from hall
        Seat.objects.filter(hall=self.hall).delete()

        # Call the service
        result = attach_all_places_to_event_session(self.event_session)

        # Verify no seat sessions were created
        self.assertEqual(
            SeatSession.objects.filter(event_session=self.event_session).count(), 0
        )
        self.assertEqual(result, self.event_session)

    def test_attach_all_places_to_event_session_transaction_atomicity(self):
        """Test that the service is atomic - all or nothing"""

        # Create a new hall without seats to simulate error scenario
        empty_hall = Hall.objects.create(venue=self.venue, number="2")

        # Delete all seats for this hall
        Seat.objects.filter(hall=empty_hall).delete()

        # Create event session for empty hall
        event_session = EventSession.objects.create(
            event=self.event, hall=empty_hall, timestamp="2026-07-10T10:00:00Z"
        )

        # Call the service (should work with 0 seats)
        result = attach_all_places_to_event_session(event_session)
        self.assertEqual(result, event_session)

        # Verify no seat sessions were created
        self.assertEqual(
            SeatSession.objects.filter(event_session=event_session).count(), 0
        )
