from django.http import JsonResponse
from django.shortcuts import render,redirect

from .fares import FareError, calculate_fare
from .models import Bus, RouteStop, Stop,Route
from django.db.models import Prefetch
from django.contrib import messages


def home(request):
    from_id = request.GET.get("from_stop")
    to_id = request.GET.get("to_stop")

    stops = Stop.objects.all().order_by("name")

    ctx = {
        "stops": stops,
        "from_id": from_id,
        "to_id": to_id,
        "from_stop": None,
        "to_stop": None,
        "buses": [],
    }

    if from_id and to_id:
        try:
            from_id = int(from_id)
            to_id = int(to_id)

            from_stop = Stop.objects.filter(pk=from_id).first()
            to_stop = Stop.objects.filter(pk=to_id).first()

            ctx["from_stop"] = from_stop
            ctx["to_stop"] = to_stop

            if not from_stop or not to_stop:
                ctx["error"] = "সঠিক স্টপ নির্বাচন করুন।"

            elif from_id == to_id:
                ctx["error"] = "From এবং To আলাদা হতে হবে।"

            else:
                buses = (
                    Bus.objects.filter(is_active=True)
                    .select_related("route")
                    .order_by("id")
                )

                matched_buses = []

                for bus in buses:

                    # প্রতিটি বাসের Route-এর সব Stop নেওয়া হচ্ছে
                    route_stops = list(
                        RouteStop.objects.filter(route=bus.route)
                        .select_related("stop")
                        .order_by("order")
                    )

                    # From এবং To-এর অবস্থান খোঁজা
                    start_index = next(
                        (
                            i for i, item in enumerate(route_stops)
                            if item.stop_id == from_id
                        ),
                        None
                    )

                    end_index = next(
                        (
                            i for i, item in enumerate(route_stops)
                            if item.stop_id == to_id
                        ),
                        None
                    )

                    # এই Route-এ দুটো Stop না থাকলে বাদ
                    if start_index is None or end_index is None:
                        continue

                    # From থেকে To পর্যন্ত Stop বের করা
                    if start_index <= end_index:
                        selected_stops = route_stops[
                            start_index:end_index + 1
                        ]
                    else:
                        selected_stops = route_stops[
                            end_index:start_index + 1
                        ][::-1]

                    stops_between = [
                        item.stop for item in selected_stops
                    ]

                    # প্রতিটি বাসের জন্য আলাদাভাবে ভাড়া হিসাব
                    try:
                        distance, raw_fare, final_fare = calculate_fare(
                            bus.route,
                            from_id,
                            to_id
                        )

                        fare_error = None

                    except FareError as e:
                        distance = None
                        raw_fare = None
                        final_fare = None
                        fare_error = str(e)

                    matched_buses.append({
                        "name": bus.name,
                        "bus_number": bus.bus_number,
                        "route_name": bus.route.name,
                        "rate_per_km": bus.route.rate_per_km,
                        "distance": distance,
                        "raw_fare": raw_fare,
                        "fare": final_fare,
                        "fare_error": fare_error,
                        "stops_between": stops_between,
                    })

                ctx["buses"] = matched_buses

                if not matched_buses:
                    ctx["error"] = (
                        "এই From এবং To-এর মধ্যে কোনো বাস পাওয়া যায়নি।"
                    )

        except (ValueError, TypeError):
            ctx["error"] = "ভুল স্টপ নির্বাচন করা হয়েছে।"

    return render(request, "home.html", ctx)


def all_stops(request):
    stops = Stop.objects.all().order_by("name")

    data = [
        {
            "id": stop.id,
            "name": stop.name,
            "lat": float(stop.latitude),
            "lng": float(stop.longitude),
        }
        for stop in stops
    ]

    return JsonResponse({"stops": data})

def bus_list(request):

    buses = (
        Bus.objects
        .filter(is_active=True)
        .select_related("route")
        .prefetch_related(
            Prefetch(
                "route__route_stops",
                queryset=RouteStop.objects.select_related("stop").order_by("order"),
                to_attr="ordered_stops"
            )
        )
        .order_by("id")
    )

    context = {
        "buses": buses,
    }

    return render(request, "bus_list.html", context)


def route_list(request):
    routes=Route.objects.all().order_by("id")

    context={
        "routes":routes,
    }

    return render(request,"route_list.html",context)

def complaints(request):
    if request.method =="POST":
        messages.success(request, "আপনার অভিযোগ জমা হয়েছে। আমরা শীঘ্রই আপনার সাথে যোগাযোগ করব।")

        return redirect("complaints")

    return render(request,"complaints.html")