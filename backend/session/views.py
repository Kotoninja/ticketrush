from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import EventSession
from .serializers import EventSessionReadSerializer, EventSessionWriteSerializer
from .services import attach_all_places_to_event_session


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

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
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
