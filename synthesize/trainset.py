from dataclasses import dataclass

@dataclass
class Trainset(object):
    max_acceleration_kms2: float
    max_decceleration_kms2: float
    max_velocity_kms: float
    dwell_time_seconds: int