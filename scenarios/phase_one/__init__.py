from synthesize.evaluate import evaluate_scenario

from scenarios.phase_one.eastern import eastern
from scenarios.phase_one.fairmount_franklin import fairmount

subgraphs = [
    [eastern],
    # [fairmount],
]

evaluate_scenario(subgraphs)
