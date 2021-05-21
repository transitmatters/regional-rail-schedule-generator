from dataclasses import dataclass, fields


@dataclass
class Amenities:
    level_boarding: bool = None
    increased_top_speed: bool = None
    electric_trains: bool = None

    def cascade(self, other: "Amenities"):
        field_values = {}
        for field in fields(Amenities):
            self_value = getattr(self, field.name)
            other_value = getattr(other, field.name)
            if other_value is not None:
                field_values[field.name] = other_value
            else:
                field_values[field.name] = self_value
        return Amenities(**field_values)


RR_BASE_AMENITIES = Amenities(
    level_boarding=True, increased_top_speed=True, electric_trains=True
)
