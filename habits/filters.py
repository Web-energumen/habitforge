import django_filters
from .models import HabitRecord


class HabitRecordFilter(django_filters.FilterSet):
    class Meta:
        model = HabitRecord
        fields = {
            'date': ['gte', 'lte'],
            'habit': ['exact'],
            'completed': ['exact'],
        }


class HabitAnalyticsFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = HabitRecord
        fields = ['completed', 'start_date', 'end_date']
