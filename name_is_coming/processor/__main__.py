import numpy as np
from skyfield.api import load, wgs84
from skyfield.api import EarthSatellite
from skyfield.api import load, wgs84
import time

def current_location(line1, line2, ts):
    satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)
    time_now = ts.now()

    #Check if TLE valid
    days_from_tle = time_now - satellite.epoch
#    print('{:.3f} days away from epoch'.format(days))
    if abs(days_from_tle) > 14:
        print("TLE too old!")

    geocentric = satellite.at(time_now)
    subpoint = wgs84.subpoint(geocentric)

    return subpoint.latitude, subpoint.longitude, subpoint.elevation.km


def process(ts):
    N_objects = 5000
    start = time.time()

    for j in range(N_objects):
        #Load TLE from cache
        line1 = "1 49248U 21084B   21264.43765192  .00022599  00000-0  20385-3 0  9992"
        line2 = "2 49248  51.6477 224.3772 0006629 293.3384  66.6927 15.68043965   408"

        #Location now
        lat, lon, r = current_location(line1, line2, ts)

        #print('Latitude:', lat)
        #print('Longitude:', lon)
        #print('Height: {:.1f} km'.format(r))

        #Cache location

    end = time.time()
    print(end - start)

def main():
    ts = load.timescale()
    while True:
        process(ts)

if __name__ == "__main__":
    main()
