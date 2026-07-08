from rest_framework import viewsets

from .models import EventSession
from .serializers import EventSessionSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class EventSessionAPI(viewsets.ModelViewSet):
    queryset = EventSession.objects.all()
    serializer_class = EventSessionSerializer
    http_method_names=["get"]

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        event_session_instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(event_session_instance)
        return Response(data=serializer.data)

