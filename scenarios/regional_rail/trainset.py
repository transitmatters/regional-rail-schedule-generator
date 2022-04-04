from synthesize.trainset import Trainset

emu_trainset = Trainset(
    max_acceleration_kms2=6.67e-4,
    max_decceleration_kms2=8.88e-4,
    max_velocity_kms=129,
    dwell_time_seconds=45,
)
