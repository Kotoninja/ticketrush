from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import WebhookSerializer
from .services import WebhookService


class WebhookView(APIView):
    @extend_schema(request=WebhookSerializer, summary="Webhook from bank", description="<b>FAKE</b> webhook from bank")
    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        WebhookService.execute(data=serializer.data)
        return Response(status=status.HTTP_200_OK)
