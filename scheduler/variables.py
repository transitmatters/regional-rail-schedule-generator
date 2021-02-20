import cvxpy as cp

from scheduler.network import Service, Node


class Variables(object):
    def __init__(self):
        self._variables = {}

    def __str__(self):
        return str(self._variables)

    def _get_or_create_variable(self, name: str, **kwargs):
        existing = self._variables.get(name)
        if existing:
            return existing
        variable = cp.Variable(name=name, **kwargs)
        self._variables[name] = variable
        return variable

    def get_departure_offset_variable_name(self, service: Service):
        return self._get_or_create_variable(f"departure_offset_{service}", nonneg=True)

    def get_exclusion_variable_name(
        self,
        node: Node,
        service_a: Service,
        service_index_a: int,
        service_b: Service,
        service_index_b: int,
    ):
        return self._get_or_create_variable(
            f"exclusion_{node}_{service_a}_{service_index_a}_{service_b}_{service_index_b}",
            boolean=True,
        )
