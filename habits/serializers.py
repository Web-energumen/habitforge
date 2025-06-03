from rest_framework import serializers

from .models import Habit, HabitRecord, HabitSchedule


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class HabitScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitSchedule
        fields = '__all__'
        read_only_fields = ('habit',)


class HabitRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitRecord
        fields = '__all__'
        read_only_fields = ('habit', )
