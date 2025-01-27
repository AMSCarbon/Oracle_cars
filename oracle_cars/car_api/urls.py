from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("cars/", views.CarView.as_view(), name="cars"),
    path("cars/<str:pk>/", views.CarDetailView.as_view(), name="car-details"),
    path("schedules/", views.ScheduleView.as_view(), name="schedules"),
    path(
        "schedules/<str:pk>/",
        views.ScheduleDetailView.as_view(),
        name="schedule-details",
    ),
    path("branches/", views.BranchView.as_view(), name="branches"),
    path("branches/<str:pk>/", views.BranchDetailView.as_view(), name="branch-details"),
    path(
        "branches/<str:pk>/inventory",
        views.BranchInventoryView.as_view(),
        name="branch-details",
    ),
]
