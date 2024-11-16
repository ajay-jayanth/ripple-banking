import pandas as pd
import googlemaps
from typing import Tuple


API_KEY = 'AIzaSyDzGxjSG77K2SBQi2sWtVRYimFLpHlKYmg'
gmaps = googlemaps.Client(key=API_KEY)

def address_to_coords(address: str) -> Tuple[float, float]:
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None

if __name__ == '__main__':
    print(address_to_coords('744 Brick Row, Richardson, TX 75081'))