from django.contrib import admin

from .models import Habit, HabitRecord, HabitSchedule


class HabitScheduleInline(admin.TabularInline):
    model = HabitSchedule
    extra = 1


class HabitRecordInline(admin.TabularInline):
    model = HabitRecord
    extra = 0
    readonly_fields = ('completed_at',)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'start_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'start_date', 'user')
    search_fields = ('name', 'user__username')
    inlines = [HabitScheduleInline, HabitRecordInline]
    ordering = ('-created_at',)

    list_per_page = 30


@admin.register(HabitSchedule)
class HabitScheduleAdmin(admin.ModelAdmin):
    list_display = ('habit', 'day_of_week')
    list_filter = ('day_of_week', )
    search_fields = ('habit__name', )


@admin.register(HabitRecord)
class HabitRecordAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'completed', 'completed_at')
    list_filter = ('completed', 'date')
    search_fields = ('habit__name', )
    date_hierarchy = 'date'
