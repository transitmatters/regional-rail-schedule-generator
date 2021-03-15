from synthesize.evaluate import evaluate_scenario

from scenarios.phase_one.eastern import eastern
from scenarios.phase_one.fairmount_franklin import fairmount
from scenarios.phase_one.worcester_framingham import worcester_framingham

subgraphs = [
    [worcester_framingham],
    # [eastern],
    # [fairmount],
]

evaluate_scenario(subgraphs)
