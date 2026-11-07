from decimal import Decimal

from django.db import models

# Create your models here.

class FareConfig(models.Model):
    fuel_type=models.CharField(max_length=50)
    fuel_price=models.DecimalField("diesel price (Tk/L)",max_digits=10,decimal_places=2)
    min_fare=models.DecimalField("minimum fare (Tk)",max_digits=10,decimal_places=2,default=Decimal('10.00'))
    rounding_step=models.DecimalField("rounding step (TK)",max_digits=10,decimal_places=2,default=Decimal("5.00"))
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"diesel price: {self.fuel_price}, min fare: {self.min_fare}, rounding step: {self.rounding_step}"

class Route(models.Model):
    name=models.CharField(max_length=100,unique=True)
    rate_per_km=models.DecimalField("rate per km (Tk)",max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.name} {self.rate_per_km} Tk/km"

class Stop(models.Model):
    name=models.CharField(max_length=100,unique=True)
    latitude=models.DecimalField(max_digits=9,decimal_places=6)
    longitude=models.DecimalField(max_digits=9,decimal_places=6)

    def __str__(self):
        return self.name


class RouteStop(models.Model):
    route=models.ForeignKey(Route,on_delete=models.CASCADE,related_name="route_stops")
    stop=models.ForeignKey(Stop,on_delete=models.CASCADE,related_name="stop_routes")
    order=models.PositiveIntegerField()

    class Meta:
        ordering=['route','order']
        unique_together=('route','order')

    def __str__(self):
        return f"{self.route}-{self.stop}-{self.order}"


class Segment(models.Model):
    route=models.ForeignKey(Route,on_delete=models.CASCADE,related_name="segments")
    start_stop=models.ForeignKey(Stop,on_delete=models.CASCADE,related_name="segment_start")
    end_stop=models.ForeignKey(Stop,on_delete=models.CASCADE,related_name="segment_end")
    distance_km=models.DecimalField("distance (km)",max_digits=10,decimal_places=2)

    class Meta:
        unique_together=('route','start_stop','end_stop')

    def __str__(self):
        return f"{self.route}-{self.start_stop}-{self.end_stop}-{self.distance_km}"
    

class Bus(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="buses")
    name = models.CharField("bus name", max_length=100)
    bus_number = models.CharField("type", max_length=50)
    is_active = models.BooleanField(default=True)
    

    class Meta:
        ordering = ["route", "name"]

    def __str__(self):
        return f"{self.name} ({self.bus_number}) - {self.route.name}-"




