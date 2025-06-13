from rest_framework import permissions, viewsets

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

    def get_queryset(self):
        habit = self.get_habit()
        return HabitRecord.objects.filter(habit=habit)

    def perform_create(self, serializer):
        habit = self.get_habit()
        serializer.save(habit=habit)
