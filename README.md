# TicketRush

An event ticketing platform with a live, real-time seat map.

A user opens an event session page, sees the hall layout and seat statuses (free / being booked by someone else right now / sold), and selects a seat — it gets frozen for 5 minutes, instantly visible to everyone else via WebSocket. If the booking isn't paid within 5 minutes, the seat is automatically released by a background task.

This is a learning project: the goal is to cover as much of the Django/DRF/Channels/Celery/Redis surface as possible in one cohesive example (race conditions during booking, distributed locks, realtime updates, background tasks, periodic tasks).

## Stack

- **Backend:** Django, Django REST Framework
- **Realtime:** Django Channels (ASGI), Redis channel layer
- **Task queue:** Celery + Celery Beat, Redis as broker and result backend
- **Database:** PostgreSQL
- **Cache / locks:** Redis
- **Infrastructure:** Docker, docker-compose, Nginx, gunicorn + daphne

## Architecture (overview)

```
nginx
 ├── /ws/  → daphne (ASGI, Channels)
 └── /     → gunicorn (WSGI, DRF API)

celery worker   → background tasks (email, PDF, payment, booking release)
celery beat     → periodic tasks (reminders, expired booking cleanup)
redis           → channel layer, cache, distributed lock, celery broker/backend
postgres        → primary data store
```

## Roadmap

### Phase 1 — Core domain & catalog
Basic data model and a browsable API for events, with no booking logic yet.
- [x] Venues, halls, seat maps, events and sessions
- [x] Admin panel for managing the catalog
- [x] Public API: browse/search/filter events and sessions

### Phase 2 — Accounts & access
Users can register and the API distinguishes who's allowed to do what.
- [ ] Authentication (JWT) and email confirmation
- [ ] Roles: regular user, event organizer, moderator
- [ ] Organizers can manage their own events through the API

### Phase 3 — Seat booking engine
The core feature: reserving a specific seat safely under concurrent load.
- [ ] Booking flow with seat-level locking (no double booking)
- [ ] Booking expiration (auto-release if unpaid in time)
- [ ] Mock payment flow turning a booking into a sale

### Phase 4 — Live seat map (realtime)
Everyone looking at the same session sees seat status changes instantly.
- [ ] WebSocket connection per event session
- [ ] Live seat status broadcasting (booked / released / sold)
- [ ] (optional) live support chat on the event page

### Phase 5 — Background processing & notifications
Things that shouldn't happen inside the request/response cycle.
- [ ] Email notifications (confirmations, reminders)
- [ ] PDF ticket with QR code after purchase
- [ ] Scheduled cleanup and reminder jobs
- [ ] Sales analytics for organizers

### Phase 6 — Performance & caching
Making the hot paths (event listings, seat maps) fast under load.
- [ ] Caching for catalog endpoints
- [ ] Caching for the live seat map
- [ ] Load/race-condition testing of the booking flow

### Phase 7 — Production readiness
Packaging everything into a deployable, observable system.
- [ ] Full Docker setup (web, realtime, worker, scheduler, db, cache, proxy)
- [ ] Nginx routing for HTTP and WebSocket traffic
- [ ] Logging, health checks, final end-to-end load test

## Local setup

```bash
git clone <repo>
cd ticketrush
cp .env.example .env
docker-compose up --build
```

## License

MIT