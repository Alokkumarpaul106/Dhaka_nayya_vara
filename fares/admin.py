from django.contrib import admin
from .models import FareConfig,Route,Stop,Segment,RouteStop,Bus

# Register your models here.

admin.site.register(FareConfig)
admin.site.register(Route)
admin.site.register(Stop)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('route', 'start_stop', 'end_stop', 'distance_km')
    search_fields = ('route__name', 'start_stop__name', 'end_stop__name')
    ordering = ('route', 'start_stop', 'end_stop')
admin.site.register(Segment, SegmentAdmin)

class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'stop', 'order')
    search_fields = ('route__name', 'stop__name')
    ordering = ('route', 'order')

admin.site.register(RouteStop, RouteStopAdmin)

class BusAdmin(admin.ModelAdmin):
    list_display=('name','route')
admin.site.register(Bus,BusAdmin)
