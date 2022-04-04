from synthesize.write_gtfs import write_scenario_gtfs
from synthesize.evaluate import evaluate_scenario

from scenarios.regional_rail.eastern import eastern
from scenarios.regional_rail.reading import reading
from scenarios.regional_rail.lowell_haverhill import lowell, haverhill
from scenarios.regional_rail.fitchburg import fitchburg
from scenarios.regional_rail.worcester_framingham import worcester_framingham
from scenarios.regional_rail.needham import needham
from scenarios.regional_rail.fairmount_franklin import fairmount, franklin
from scenarios.regional_rail.providence import providence_stoughton
from scenarios.regional_rail.south_shore import greenbush, middleborough, plymouth

subgraphs = [
    [eastern],
    [lowell, haverhill, reading],
    [fitchburg],
    [worcester_framingham],
    [providence_stoughton],
    [needham],
    [fairmount, franklin],
    [greenbush, middleborough, plymouth],
]

scenario = evaluate_scenario(subgraphs)
write_scenario_gtfs(scenario, "gtfs-regional-rail")
