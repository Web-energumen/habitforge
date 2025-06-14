from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import HabitRecordViewSet, HabitScheduleViewSet, HabitViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")

nested_router = routers.NestedSimpleRouter(router, "habits", lookup="habit")
nested_router.register(r"schedule", HabitScheduleViewSet, basename="habit-schedule")
nested_router.register(r"records", HabitRecordViewSet, basename="habit-records")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
