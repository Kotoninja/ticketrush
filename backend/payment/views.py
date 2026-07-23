from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import WebhookSerializer
from .services import WebhookService
from drf_spectacular.utils import extend_schema


class WebhookView(APIView):
    @extend_schema(request=WebhookSerializer)
    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print(type(serializer.data))
        WebhookService.execute(data=serializer.data)
        return Response(status=status.HTTP_200_OK)
