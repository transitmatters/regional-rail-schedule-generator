from synthesize.definitions import Route, RoutePattern
from synthesize.routes import FITCHBURG
from synthesize.time import all_day_frequencies, Timetable

timetable = Timetable(
    {
        "North Station": "0:00",
        "Porter": "0:10",
        "Belmont": "0:15",
        "Waverley": "0:18",
        "Waltham": "0:23",
        "Brandeis/Roberts": "0:26",
        "Kendal Green": "0:30",
        "Lincoln": "0:36",
        "Concord": "0:41",
        "West Concord": "0:45",
        "South Acton": "0:49",
        "Littleton/Rte 495": "0:56",
        "Ayer": "1:04",
        "Shirley": "1:09",
        "North Leominster": "1:18",
        "Fitchburg": "1:25",
        "Wachusett": "1:35",
    }
)

fitchburg = Route(
    id="CR-Fitchburg",
    shadows_real_route="CR-Fitchburg",
    name="Fitchburg Line",
    route_patterns=[
        RoutePattern(
            id="fitchburg",
            stations=FITCHBURG,
            schedule=all_day_frequencies(30),
            timetable=timetable,
        )
    ],
)
