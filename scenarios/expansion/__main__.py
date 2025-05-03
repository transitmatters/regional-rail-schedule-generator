from synthesize.write_gtfs import write_scenario_gtfs, archive_scenario_gtfs
from synthesize.evaluate import evaluate_scenario

from scenarios.expansion.red import red
from scenarios.expansion.blue import blue
from scenarios.expansion.eastern import eastern
from scenarios.expansion.reading import reading
from scenarios.expansion.lowell_haverhill import lowell, haverhill
from scenarios.expansion.fitchburg import fitchburg
from scenarios.expansion.worcester_framingham import worcester_framingham
from scenarios.expansion.needham import needham
from scenarios.expansion.fairmount_franklin import fairmount, franklin
from scenarios.expansion.providence import providence_stoughton
from scenarios.expansion.south_shore import greenbush, plymouth, newbedford

subgraphs = [
    [red],
    [blue],
    [eastern],
    [lowell, haverhill, reading],
    [fitchburg],
    [worcester_framingham],
    [providence_stoughton],
    [needham],
    [fairmount, franklin],
    [greenbush, plymouth, newbedford],
]

scenario = evaluate_scenario(subgraphs)
write_scenario_gtfs(scenario, "gtfs-expansion")
archive_scenario_gtfs("gtfs-present")
archive_scenario_gtfs("gtfs-expansion")
