from orbit_predictor.sources import get_predictor_from_tle_lines
from orbit_predictor.locations import Location
import datetime

predictor = get_predictor_from_tle_lines("""1 33591U 09005A   22020.44937208  .00000081  00000-0  68837-4 0  9993
2 33591  99.1663  51.3451 0013122 241.8520 118.1325 14.12523655667551""".split('\n'))



card = Location("Cardiff", 54.0078, -1.8560, 10)

for p in predictor.passes_over(card, datetime.datetime.utcnow()):
    if p.max_elevation_deg > 30:
        print(p.aos, p.max_elevation_date)
