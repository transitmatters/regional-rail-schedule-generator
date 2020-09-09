import

newburyport_rockport = Route(
    stops=Branch(EASTERN_SHARED, [EASTERN_NEWBURYPORT, EASTERN_ROCKPORT])
    frequencies=Frequencies(
        weekday=DayFrequencies(
            early_morning=45,
            morning=20,
            midday=30,
            evening=20,
            late_evening=30 
        )
    )
)

