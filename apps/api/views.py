from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    A simple health check endpoint to verify the API is running.
    """

    permission_classes = []  # Allow unauthenticated access

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok", "message": "API is running"}, status=status.HTTP_200_OK)
