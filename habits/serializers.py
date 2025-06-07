from rest_framework import serializers

from .models import Habit, HabitRecord, HabitSchedule


class HabitSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
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
