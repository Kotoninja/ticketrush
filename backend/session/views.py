from django.db import transaction
from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EventSession, SeatSession
from .serializers import (
    EventSessionReadSerializer,
    EventSessionWriteSerializer,
    SeatSessionWithFullDetail,
)
from .services import event_search_filter


class EventSessionAPI(viewsets.ModelViewSet):
    queryset = EventSession.objects.all()
    serializer_class = EventSessionReadSerializer
    http_method_names = ["get", "post"]

    def get_serializer_class(self):  # type: ignore[override]
        if self.request.method == "POST":
            return EventSessionWriteSerializer
        return EventSessionReadSerializer

    @transaction.atomic
    def perform_create(self, serializer: EventSessionWriteSerializer):
        self.instance = serializer.save()

    @extend_schema(
        parameters=[
            OpenApiParameter("venue", type=int, description="Sort events by venue")
        ]
    )
    def list(self, request):

        events = self.get_queryset()

        if venue := request.query_params.get("venue", None):
            events = events.filter(hall__venue=venue)

        serializer = self.get_serializer(events, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer=serializer)
            return Response(
                data=EventSessionReadSerializer(self.instance).data,
                status=status.HTTP_201_CREATED,
            )

    def retrieve(self, request, pk=None):
        event_session_instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(event_session_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter("search", type=str, description="search events by name"),
            OpenApiParameter("venue", type=int, description="search by venue"),
        ]
    )
    @action(detail=False)
    def search(self, request):
        if request.query_params.get("search"):
            serializer = self.get_serializer(
                self.get_queryset().filter(event_search_filter(request=request)),
                many=True,
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=[], status=status.HTTP_200_OK)


class SeatSessionAPI(generics.RetrieveAPIView):
    queryset = SeatSession.objects.all()
    serializer_class = SeatSessionWithFullDetail

    def get(self, request, event_session_pk, seat_session_pk):
        seat_session_instance = get_object_or_404(
            self.get_queryset(), event_session=event_session_pk, pk=seat_session_pk
        )
        serializer = self.get_serializer(seat_session_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


def index(request):
    return render(request, "session/index.html")
