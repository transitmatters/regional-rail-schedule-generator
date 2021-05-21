from synthesize.write_gtfs import write_scenario_gtfs
from synthesize.evaluate import evaluate_scenario

from scenarios.phase_one.eastern import eastern
from scenarios.phase_one.reading import reading
from scenarios.phase_one.lowell_haverhill import lowell, haverhill
from scenarios.phase_one.fitchburg import fitchburg
from scenarios.phase_one.worcester_framingham import worcester_framingham
from scenarios.phase_one.needham import needham
from scenarios.phase_one.fairmount_franklin import fairmount, franklin
from scenarios.phase_one.providence import providence_stoughton
from scenarios.phase_one.south_shore import greenbush, middleborough, plymouth

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
write_scenario_gtfs(scenario, "gtfs-phase-one")
