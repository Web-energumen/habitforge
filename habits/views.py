from rest_framework import permissions, viewsets

from .models import Habit, HabitRecord, HabitSchedule
from .permissions import IsOwner
from .serializers import (HabitRecordSerializer, HabitScheduleSerializer,
                          HabitSerializer)


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = HabitScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        habit_id = self.kwargs['habit_pk']
        return HabitSchedule.objects.filter(habit_id=habit_id)

    def perform_create(self, serializer):
        habit_id = self.kwargs['habit_pk']
        serializer.save(habit_id=habit_id)


class HabitRecordViewSet(viewsets.ModelViewSet):
    serializer_class = HabitRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        habit_id = self.kwargs['habit_pk']
        return HabitRecord.objects.filter(habit_id=habit_id)

    def perform_create(self, serializer):
        habit_id = self.kwargs['habit_pk']
        serializer.save(habit_id=habit_id)
