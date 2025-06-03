from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == 'create':
            habit_id = request.parser_context['kwargs'].get('habit_pk')
            from habits.models import Habit
            try:
                habit = Habit.objects.get(id=habit_id)
            except Habit.DoesNotExist:
                return False
            return habit.user == request.user

        return True
