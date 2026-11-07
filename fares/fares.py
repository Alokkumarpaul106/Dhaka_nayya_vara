from decimal import Decimal, ROUND_HALF_UP

from .models import FareConfig, RouteStop, Segment


class FareError(Exception):
    pass


def distance_km(route, from_stop_id, to_stop_id):
    """Sum of saved segment distances between two stops on a route."""
    try:
        a = RouteStop.objects.get(route=route, stop_id=from_stop_id).order
        b = RouteStop.objects.get(route=route, stop_id=to_stop_id).order
    except RouteStop.DoesNotExist:
        raise FareError("এই রুটে কোনো স্টপ নেই।")

    if a == b:
        raise FareError("গাড়িতে ওঠা এবং নামার স্থান ভিন্ন হতে হবে।")

    lo, hi = sorted((a, b))

    # stops of the route between lo and hi, in order
    stops_between = list(
        RouteStop.objects.filter(route=route, order__gte=lo, order__lte=hi)
        .order_by("order")
        .select_related("stop")
    )

    # saved segments of this route: (start_stop_id, end_stop_id) -> distance
    seg_map = {
        (s.start_stop_id, s.end_stop_id): s.distance_km
        for s in Segment.objects.filter(route=route)
    }

    total = Decimal("0")
    for first, second in zip(stops_between, stops_between[1:]):
        key = (first.stop_id, second.stop_id)
        if key not in seg_map:
            raise FareError(
                f"Missing segment distance: {first.stop} -> {second.stop}. Check Admin."
            )
        total += seg_map[key]
    return total


def calculate_fare(route, from_stop_id, to_stop_id):
    """Returns (distance_km, raw_fare, final_fare). Always computed on the server."""
    cfg = FareConfig.objects.order_by("-id").first()
    if cfg is None:
        raise FareError("FareConfig is not set. Add it in Admin.")

    dist = distance_km(route, from_stop_id, to_stop_id)
    raw = dist * route.rate_per_km

    step = cfg.rounding_step
    rounded = (raw / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * step
    final = max(cfg.min_fare, rounded)
    return dist, raw.quantize(Decimal("0.01")), final