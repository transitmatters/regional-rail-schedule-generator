from synthesize.time import Timetable
from synthesize.definitions import RoutePattern

route_x_stations = ("a", "b", "c", "d", "e", "f")
route_x_timetable = Timetable(
    {"a": "0:00", "b": "0:03", "c": "0:09", "d": "0:12", "e": "0:17", "f": "0:20"}
)

route_y_stations = ("c", "d", "e", "f", "g", "h")
route_y_timetable = Timetable(
    {"c": "0:00", "d": "0:03", "e": "0:06", "f": "0:09", "g": "0:10", "h": "0:13"}
)

route_z_stations = ("a", "d", "g", "i")
route_z_timetable = Timetable({"a": "0:00", "d": "0:12", "g": "0:19", "i": "0:30"})

X = RoutePattern(
    name="X", id="x", stations=route_x_stations, timetable=route_x_timetable
)
Y = RoutePattern(
    name="Y", id="y", stations=route_y_stations, timetable=route_y_timetable
)
Z = RoutePattern(
    name="Z", id="z", stations=route_z_stations, timetable=route_z_timetable
)

route_patterns = [X, Y, Z]
trains_per_hour = {"x": 3, "y": 4, "z": 6}
