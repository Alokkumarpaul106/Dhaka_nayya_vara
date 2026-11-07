from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("all-stops/", views.all_stops, name="all_stops"),
    path("bus-list/", views.bus_list, name="bus_list"),
    path("route-list/", views.route_list, name="route_list"),
    path("complaints/", views.complaints, name="complaints"),
]