# survey/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Survey, SurveyResponse
from .serializers import SurveySerializer, SurveyResponseSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSurveyAdminOrReadOnly


class SurveyListAPI(generics.ListAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]


class SubmitSurveyAPI(generics.CreateAPIView):
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        survey_response = serializer.save()
        return Response({"message": "تم تقديم الاستبيان بنجاح."}, status=status.HTTP_201_CREATED)
