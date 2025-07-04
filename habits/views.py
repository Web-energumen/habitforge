from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .filters import HabitAnalyticsFilter, HabitRecordFilter
from .models import Habit, HabitRecord, HabitSchedule
from .permissions import IsOwner
from .serializers import HabitRecordSerializer, HabitScheduleSerializer, HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRelatedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]

    def get_habit(self):
        habit_id = self.kwargs["habit_pk"]
        return Habit.objects.get(id=habit_id, user=self.request.user)


class HabitScheduleViewSet(HabitRelatedViewSet):
    serializer_class = HabitScheduleSerializer

    def get_queryset(self):
        habit = self.get_habit()
        return HabitSchedule.objects.filter(habit=habit)

    def perform_create(self, serializer):
        habit = self.get_habit()
        serializer.save(habit=habit)


class HabitRecordViewSet(HabitRelatedViewSet):
    serializer_class = HabitRecordSerializer
    permission_classes = [IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HabitRecordFilter

    def get_queryset(self):
        habit = self.get_habit()
        return HabitRecord.objects.filter(habit=habit)

    def perform_create(self, serializer):
        habit = self.get_habit()
        serializer.save(habit=habit)


class HabitAnalyticsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HabitAnalyticsFilter
    queryset = HabitRecord.objects.filter(completed=True)

    def get(self, request, habit_pk=None):
        queryset = self.filter_queryset(self.get_queryset())

        if habit_pk:
            queryset = queryset.filter(habit_id=habit_pk, habit__user=request.user)

        analytics = queryset.values("date").annotate(completed_count=Count("id")).order_by("date")

        return Response(analytics)
