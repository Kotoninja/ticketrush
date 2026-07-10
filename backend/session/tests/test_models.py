from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone
from event.models import Event
from hall.models import Hall, Venue
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from seat.models import Seat

from ..models import EventSession, SeatSession


class EventSessionModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create venue
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="123 Test Street",
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
            duration=timedelta(hours=2),
        )

        # Create event session
        self.event_session = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timezone.timedelta(seconds=5),
        )

    def test_create_event_session_success(self):
        """Test successful event session creation"""
        timestamp = timezone.now() + timezone.timedelta(seconds=5)
        event_session = EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp
        )

        self.assertIsNotNone(event_session.id)
        self.assertEqual(event_session.event, self.event)
        self.assertEqual(event_session.hall, self.hall)
        self.assertEqual(event_session.timestamp, timestamp)
        self.assertIsNotNone(event_session.created_at)
        self.assertIsNotNone(event_session.updated_at)

    def test_event_session_str_method(self):
        """Test the string representation of EventSession"""
        expected_str = f"{self.event.name} / {self.venue.name} / {self.hall.number} / {self.event_session.timestamp}"
        self.assertEqual(str(self.event_session), expected_str)

    def test_event_session_unique_constraint(self):
        """Test that unique constraint prevents duplicate sessions"""

        timestamp = timezone.now() + timezone.timedelta(seconds=6)
        # Create first session
        EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp
        )

        # Try to create duplicate session
        with self.assertRaises(DRFValidationError):
            with transaction.atomic():
                EventSession.objects.create(
                    event=self.event, hall=self.hall, timestamp=timestamp
                )

    def test_event_session_unique_constraint_different_event(self):
        """Test that same hall and timestamp with different event is allowed"""
        # Create another event
        another_event = Event.objects.create(
            name="Another Event",
            description="Another Description",
            duration=timedelta(hours=1),
        )

        timestamp = timezone.now() + timezone.timedelta(seconds=5)

        # Create first session
        EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp
        )

        # Create second session with different event - should work
        event_session2 = EventSession.objects.create(
            event=another_event, hall=self.hall, timestamp=timestamp
        )

        self.assertIsNotNone(event_session2.id)
        self.assertEqual(event_session2.event, another_event)

    def test_event_session_unique_constraint_different_hall(self):
        """Test that same event and timestamp with different hall is allowed"""
        # Create another hall
        another_hall = Hall.objects.create(
            venue=self.venue,
            number="2",
        )

        timestamp = timezone.now() + timezone.timedelta(seconds=5)

        # Create first session
        EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp
        )

        # Create second session with different hall - should work
        event_session2 = EventSession.objects.create(
            event=self.event, hall=another_hall, timestamp=timestamp
        )

        self.assertIsNotNone(event_session2.id)
        self.assertEqual(event_session2.hall, another_hall)

    def test_event_session_unique_constraint_different_timestamp(self):
        """Test that same event and hall with different timestamp is allowed"""
        timestamp1 = timezone.now() + timezone.timedelta(seconds=5)
        timestamp2 = timestamp1 + timedelta(hours=1)

        # Create first session
        EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp1
        )

        # Create second session with different timestamp - should work
        event_session2 = EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=timestamp2
        )

        self.assertIsNotNone(event_session2.id)
        self.assertEqual(event_session2.timestamp, timestamp2)

    def test_event_session_protected_delete_event(self):
        """Test that deleting event is protected when it has sessions"""
        with self.assertRaises(ProtectedError):
            self.event.delete()

    def test_event_session_protected_delete_hall(self):
        """Test that deleting hall is protected when it has sessions"""
        with self.assertRaises(ProtectedError):
            self.hall.delete()

    def test_event_session_cascade_delete(self):
        """Test that deleting event session cascades to seat sessions"""
        # Create seat sessions
        for i in range(3):
            seat = Seat.objects.create(hall=self.hall, number=i + 1)
            SeatSession.objects.create(
                event_session=self.event_session,
                seat=seat,
                status="free",
                price=Decimal("99.00"),
            )

        # Verify seat sessions exist
        self.assertEqual(
            SeatSession.objects.filter(event_session=self.event_session).count(), 3
        )

        # Delete event session
        event_session_id = self.event_session.id
        self.event_session.delete()

        # Verify event session is deleted
        self.assertFalse(EventSession.objects.filter(id=event_session_id).exists())

        # Verify seat sessions are also deleted (cascade)
        self.assertEqual(
            SeatSession.objects.filter(event_session_id=event_session_id).count(), 0
        )

    def test_event_session_related_name(self):
        """Test that related_name 'event_sessions' works from Hall"""
        # Create multiple sessions for same hall
        another_session = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timedelta(hours=1),
        )

        # Get sessions through related_name
        hall_sessions = self.hall.event_sessions.all()
        self.assertEqual(hall_sessions.count(), 2)
        self.assertIn(self.event_session, hall_sessions)
        self.assertIn(another_session, hall_sessions)

    def test_event_session_timestamp_auto_now(self):
        """Test that timestamp is not auto-updated on save"""
        original_timestamp = self.event_session.timestamp

        # Update some other field and save
        self.event_session.save()

        # Timestamp should not change
        self.assertEqual(self.event_session.timestamp, original_timestamp)

    def test_event_session_ordering(self):
        """Test that event sessions are ordered by created_at (BaseModel)"""
        # Create sessions with different timestamps
        session1 = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timezone.timedelta(seconds=5),
        )

        session2 = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timedelta(hours=1),
        )

        # Get all sessions
        sessions = EventSession.objects.all()

        # BaseModel orders by created_at descending by default
        # So newer sessions should come first
        if sessions.count() >= 2:
            self.assertGreaterEqual(sessions[1].created_at, sessions[0].created_at)


class SeatSessionModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create venue
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="123 Test Street",
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
            duration=timedelta(hours=2),
        )

        # Create seat
        self.seat = Seat.objects.create(hall=self.hall, number=1)

        # Create event session
        self.event_session = EventSession.objects.create(
            event=self.event,
            hall=self.hall,
            timestamp=timezone.now() + timezone.timedelta(seconds=5),
        )

        self.another_seat = Seat.objects.create(hall=self.hall, number=2)

    def test_seat_session_is_exist(self):
        """Test successful seat session exist"""
        self.assertEqual(SeatSession.objects.count(), 1)

    def test_seat_session_status_choices(self):
        """Test that status choices are enforced"""
        # Test valid statuses
        for status in ["free", "pending", "busy"]:
            seat_session = SeatSession.objects.create(
                event_session=self.event_session,
                seat=Seat.objects.create(
                    hall=self.hall, number=len(Seat.objects.all()) + 1
                ),
                status=status,
                price=Decimal("99.00"),
            )
            self.assertEqual(seat_session.status, status)

        # Test invalid status (should raise error)
        with self.assertRaises(DRFValidationError):
            with transaction.atomic():
                SeatSession.objects.create(
                    event_session=self.event_session,
                    seat=Seat.objects.create(hall=self.hall, number=100),
                    status="invalid_status",
                    price=Decimal("99.00"),
                )

    def test_seat_session_default_status(self):
        """Test that default status is 'free'"""
        # Create another seat

        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            price=Decimal("99.00"),
        )

        self.assertEqual(seat_session.status, "free")

    def test_seat_session_price_decimal_places(self):
        """Test that price is stored with correct decimal places"""
        # Create another seat

        # Test with two decimal places
        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.99"),
        )
        self.assertEqual(seat_session.price, Decimal("99.99"))

        # Test with one decimal place (should be stored as two)
        seat_session2 = SeatSession.objects.create(
            event_session=self.event_session,
            seat=Seat.objects.create(hall=self.hall, number=2),
            status="free",
            price=Decimal("99.9"),
        )
        self.assertEqual(seat_session2.price, Decimal("99.90"))

    def test_seat_session_price_max_digits(self):
        """Test that price respects max_digits (4 digits total, 2 decimal places)"""
        # Test maximum allowed value
        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=Seat.objects.create(hall=self.hall, number=2),
            status="free",
            price=Decimal("99.99"),  # 4 digits total
        )
        self.assertEqual(seat_session.price, Decimal("99.99"))

        # Test value that exceeds max_digits (should raise error)
        with self.assertRaises(Exception):
            SeatSession.objects.create(
                event_session=self.event_session,
                seat=Seat.objects.create(hall=self.hall, number=3),
                status="free",
                price=Decimal("100.00"),  # 5 digits total
            )

    def test_seat_session_unique_constraint(self):
        """Test that unique constraint prevents duplicate seat sessions"""

        # Create another seat

        # Create first seat session
        SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        # Try to create duplicate seat session
        with self.assertRaises(DRFValidationError):
            with transaction.atomic():
                SeatSession.objects.create(
                    event_session=self.event_session,
                    seat=self.another_seat,
                    status="pending",
                    price=Decimal("99.00"),
                )

    def test_seat_session_unique_different_seat(self):
        """Test that different seat with same event session is allowed"""
        # Create another seat
        another_seat = Seat.objects.create(hall=self.hall, number=3)
        # Create second seat session with different seat - should work
        seat_session2 = SeatSession.objects.create(
            event_session=self.event_session,
            seat=another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        self.assertIsNotNone(seat_session2.id)
        self.assertEqual(seat_session2.seat, another_seat)

    def test_seat_session_protected_delete_seat(self):
        """Test that deleting seat is protected when it has seat sessions"""

        # Create seat session
        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        with self.assertRaises(ProtectedError):
            self.seat.delete()

    def test_seat_session_cascade_delete_event_session(self):
        """Test that deleting event session cascades to seat sessions"""
        # Create another seat

        # Create seat session
        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        # Verify seat session exists
        self.assertTrue(SeatSession.objects.filter(id=seat_session.id).exists())

        # Delete event session
        self.event_session.delete()

        # Verify seat session is also deleted (cascade)
        self.assertFalse(SeatSession.objects.filter(id=seat_session.id).exists())

    def test_seat_session_related_name(self):
        """Test that related_name 'seats' works from EventSession"""
        # Create multiple seat sessions for same event session
        for i in range(2, 5):
            seat = Seat.objects.create(hall=self.hall, number=i)
            SeatSession.objects.create(
                event_session=self.event_session,
                seat=seat,
                status="free",
                price=Decimal("99.00"),
            )

        # Get seat sessions through related_name
        session_seats = self.event_session.seats.all()
        self.assertEqual(session_seats.count(), 4)  # 1 from setUp + 3 created

        # Verify all seat sessions belong to the event session
        for seat_session in session_seats:
            self.assertEqual(seat_session.event_session, self.event_session)

    def test_seat_session_status_update(self):
        """Test updating seat session status"""
        # Create another seat

        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        # Update status to pending
        seat_session.status = "pending"
        seat_session.save()
        seat_session.refresh_from_db()
        self.assertEqual(seat_session.status, "pending")

        # Update status to busy
        seat_session.status = "busy"
        seat_session.save()
        seat_session.refresh_from_db()
        self.assertEqual(seat_session.status, "busy")

    def test_seat_session_price_update(self):
        """Test updating seat session price"""
        # Create another seat

        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        # Update price
        seat_session.price = Decimal("89.99")
        seat_session.save()
        seat_session.refresh_from_db()
        self.assertEqual(seat_session.price, Decimal("89.99"))

    def test_seat_session_query_optimization(self):
        """Test that querying with select_related/prefetch_related works"""
        # Create another seat

        # Create seat session
        seat_session = SeatSession.objects.create(
            event_session=self.event_session,
            seat=self.another_seat,
            status="free",
            price=Decimal("99.00"),
        )

        # Test select_related
        with self.assertNumQueries(2):
            seat_session = SeatSession.objects.select_related(
                "event_session", "seat"
            ).get(id=seat_session.id)

            # Access related fields
            self.assertEqual(seat_session.event_session.event.name, self.event.name)

        # Test prefetch_related from event session
        with self.assertNumQueries(2):
            event_session = EventSession.objects.prefetch_related("seats").get(
                id=self.event_session.id
            )
            self.assertEqual(event_session.seats.count(), 2)

    def test_seat_session_bulk_create(self):
        """Test bulk creating multiple seat sessions"""
        seats = []
        for i in range(3, 6):
            seat = Seat.objects.create(hall=self.hall, number=i)
            seats.append(seat)

        seat_sessions = []
        for seat in seats:
            seat_sessions.append(
                SeatSession(
                    event_session=self.event_session,
                    seat=seat,
                    status="free",
                    price=Decimal("99.00"),
                )
            )

        # Bulk create
        created = SeatSession.objects.bulk_create(seat_sessions)
        self.assertEqual(len(created), 3)

        # Verify all were created
        self.assertEqual(
            SeatSession.objects.filter(event_session=self.event_session).count(), 4
        )

    def test_seat_session_filter_by_status(self):
        """Test filtering seat sessions by status"""
        # Create seat sessions with different statuses
        for i, status in enumerate(["free", "pending", "busy"]):
            seat = Seat.objects.create(hall=self.hall, number=i + 10)
            SeatSession.objects.create(
                event_session=self.event_session,
                seat=seat,
                status=status,
                price=Decimal("99.00"),
            )

        # Filter by status
        free_seats = SeatSession.objects.filter(status="free")
        pending_seats = SeatSession.objects.filter(status="pending")
        busy_seats = SeatSession.objects.filter(status="busy")

        self.assertEqual(free_seats.count(), 2)  # 1 from setUp + 1 created
        self.assertEqual(pending_seats.count(), 1)
        self.assertEqual(busy_seats.count(), 1)

    def test_seat_session_aggregation(self):
        """Test aggregation on seat sessions"""
        # Create seat sessions with different prices
        prices = [Decimal("99.00"), Decimal("89.00"), Decimal("79.00")]
        for i, price in enumerate(prices):
            seat = Seat.objects.create(hall=self.hall, number=i + 20)
            SeatSession.objects.create(
                event_session=self.event_session, seat=seat, status="free", price=price
            )

        # Test aggregation
        from django.db.models import Avg, Count, Sum

        stats = SeatSession.objects.filter(event_session=self.event_session).aggregate(
            total_price=Sum("price"), avg_price=Avg("price"), count=Count("id")
        )

        self.assertEqual(stats["total_price"], Decimal("366.00"))  # 99 + 89 + 79
        self.assertEqual(stats["avg_price"], Decimal("91.5"))
        self.assertEqual(stats["count"], 4)  # 1 from setUp + 3 created

    def test_event_session_meta_constraints_names(self):
        """Test that constraint names are correctly set"""
        # Check that the unique constraint exists with the correct name
        constraints = EventSession._meta.constraints
        constraint_names = [constraint.name for constraint in constraints]
        self.assertIn("Unique session in definitely place and time", constraint_names)

        # Check SeatSession constraints
        seat_constraints = SeatSession._meta.constraints
        seat_constraint_names = [constraint.name for constraint in seat_constraints]
        self.assertIn(
            "Unique SeatSession in definitely event_session", seat_constraint_names
        )


class EventSessionValidationTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create venue
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="123 Test Street",
            description="Test venue description",
        )

        # Create hall (number is integer)
        self.hall = Hall.objects.create(venue=self.venue, number=1)

        # Create event
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            duration=timedelta(hours=2),
        )

    def test_event_session_clean_with_future_timestamp(self):
        """Test that clean() passes with future timestamp"""
        future_timestamp = timezone.now() + timedelta(days=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        # Should not raise ValidationError
        try:
            event_session.clean()
        except DjangoValidationError:
            self.fail(
                "clean() raised ValidationError unexpectedly with future timestamp"
            )

    def test_event_session_clean_with_past_timestamp(self):
        """Test that clean() raises ValidationError with past timestamp"""
        past_timestamp = timezone.now() - timedelta(days=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=past_timestamp
        )

        with self.assertRaises(DjangoValidationError) as context:
            event_session.clean()

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

    def test_event_session_clean_with_current_timestamp(self):
        """Test that clean() passes with current timestamp (now)"""
        current_timestamp = timezone.now() + timedelta(microseconds=100)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=current_timestamp
        )

        # Should not raise ValidationError
        try:
            event_session.clean()
        except DjangoValidationError as e:
            self.fail(
                f"clean() raised DjangoValidationError unexpectedly with current timestamp: {e}"
            )

    def test_event_session_full_clean_with_past_timestamp(self):
        """Test full_clean() with past timestamp"""
        past_timestamp = timezone.now() - timedelta(hours=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=past_timestamp
        )

        with self.assertRaises(DjangoValidationError) as context:
            event_session.full_clean()

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

    def test_event_session_full_clean_with_future_timestamp(self):
        """Test full_clean() with future timestamp"""
        future_timestamp = timezone.now() + timedelta(hours=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        # Should not raise DjangoValidationError
        try:
            event_session.full_clean()
        except DjangoValidationError:
            self.fail(
                "full_clean() raised DjangoValidationError unexpectedly with future timestamp"
            )

    def test_event_session_save_with_past_timestamp_raises_error(self):
        """Test that save() raises DjangoValidationError with past timestamp"""
        past_timestamp = timezone.now() - timedelta(days=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=past_timestamp
        )

        with self.assertRaises(DRFValidationError) as context:
            event_session.save()

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

    def test_event_session_save_with_future_timestamp_success(self):
        """Test that save() works with future timestamp"""
        future_timestamp = timezone.now() + timedelta(days=1)
        event_session = EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        self.assertIsNotNone(event_session.id)
        self.assertEqual(event_session.timestamp, future_timestamp)

    def test_event_session_clean_with_very_old_timestamp(self):
        """Test clean() with very old timestamp"""
        very_old_timestamp = timezone.now() - timedelta(days=365)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=very_old_timestamp
        )

        with self.assertRaises(DjangoValidationError) as context:
            event_session.clean()

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

    def test_event_session_clean_with_far_future_timestamp(self):
        """Test clean() with far future timestamp"""
        far_future_timestamp = timezone.now() + timedelta(days=365)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=far_future_timestamp
        )

        # Should not raise DjangoValidationError
        try:
            event_session.clean()
        except DjangoValidationError:
            self.fail(
                "clean() raised DjangoValidationError unexpectedly with far future timestamp"
            )

    def test_event_session_clean_with_microsecond_precision(self):
        """Test clean() with timestamp having microseconds"""
        # Create a timestamp just a microsecond in the past
        past_timestamp = timezone.now() - timedelta(microseconds=1)
        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=past_timestamp
        )

        # Should raise DjangoValidationError because it's still in the past
        with self.assertRaises(DjangoValidationError):
            event_session.clean()

        # Create a timestamp just a microsecond in the future
        future_timestamp = timezone.now() + timedelta(microseconds=1000)
        event_session2 = EventSession(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        # Should not raise DjangoValidationError
        try:
            event_session2.clean()
        except DjangoValidationError:
            self.fail(
                "clean() raised DjangoValidationError unexpectedly with future timestamp"
            )

    def test_event_session_clean_after_update(self):
        """Test that clean() works when updating an existing event session"""
        # Create event session with future timestamp
        future_timestamp = timezone.now() + timedelta(days=1)
        event_session = EventSession.objects.create(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        # Try to update to a past timestamp
        past_timestamp = timezone.now() - timedelta(days=1)
        event_session.timestamp = past_timestamp

        with self.assertRaises(DjangoValidationError) as context:
            event_session.full_clean()

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

        # Try to update to a future timestamp
        new_future_timestamp = timezone.now() + timedelta(days=2)
        event_session.timestamp = new_future_timestamp

        try:
            event_session.full_clean()
            event_session.save()
        except DjangoValidationError:
            self.fail(
                "DjangoValidationError raised unexpectedly with future timestamp on update"
            )

        # Verify the update worked
        event_session.refresh_from_db()
        self.assertEqual(event_session.timestamp, new_future_timestamp)

    def test_event_session_clean_with_timezone_awareness(self):
        """Test clean() with timezone-aware and naive timestamps"""
        # Get a timezone-aware timestamp
        future_timestamp = timezone.now() + timedelta(days=1)
        self.assertTrue(timezone.is_aware(future_timestamp))

        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=future_timestamp
        )

        try:
            event_session.clean()
        except DjangoValidationError:
            self.fail("clean() raised DjangoValidationError with timezone-aware timestamp")

        # Past timestamp with timezone
        past_timestamp = timezone.now() - timedelta(days=1)
        self.assertTrue(timezone.is_aware(past_timestamp))

        event_session2 = EventSession(
            event=self.event, hall=self.hall, timestamp=past_timestamp
        )

        with self.assertRaises(DjangoValidationError):
            event_session2.clean()

    def test_event_session_bulk_create_with_past_timestamp(self):
        """Test that bulk_create bypasses clean() validation"""
        # Note: bulk_create does NOT call clean() by default
        past_timestamp = timezone.now() - timedelta(days=1)

        # This should work because bulk_create bypasses model validation
        event_sessions = [
            EventSession(event=self.event, hall=self.hall, timestamp=past_timestamp)
        ]

        created = EventSession.objects.bulk_create(event_sessions)
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].timestamp, past_timestamp)

        # Clean up
        created[0].delete()

    def test_event_session_create_with_past_timestamp_via_manager(self):
        """Test that objects.create() with past timestamp raises DjangoValidationError"""
        past_timestamp = timezone.now() - timedelta(days=1)

        # objects.create() calls full_clean() before saving
        with self.assertRaises(DRFValidationError) as context:
            EventSession.objects.create(
                event=self.event, hall=self.hall, timestamp=past_timestamp
            )

        error_messages = str(context.exception)
        self.assertIn(
            "The event session timestamp cannot be less than the current time",
            error_messages,
        )

    def test_event_session_clean_with_exact_current_time(self):
        """Test clean() with timestamp exactly equal to current time (with microseconds)"""
        now = timezone.now()

        future_time = now + timedelta(microseconds=500)

        event_session = EventSession(
            event=self.event, hall=self.hall, timestamp=future_time
        )

        # Should not raise DjangoValidationError
        try:
            event_session.clean()
        except DjangoValidationError as e:
            self.fail(f"clean() raised DjangoValidationError with future timestamp: {e}")

        past_time = now - timedelta(microseconds=500)
        event_session2 = EventSession(
            event=self.event, hall=self.hall, timestamp=past_time
        )

        with self.assertRaises(DjangoValidationError):
            event_session2.clean()
