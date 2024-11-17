import pandas as pd
import googlemaps
from typing import Tuple
from flask import Flask, render_template, request, session, redirect, url_for, flash


API_KEY = 'AIzaSyDzGxjSG77K2SBQi2sWtVRYimFLpHlKYmg'
gmaps = googlemaps.Client(key=API_KEY)

def address_to_coords(address: str) -> Tuple[float, float]:
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None
    
def merchant_maps_fn():
    merchants_default = [
        {
            "name": "Alexander Dmitri",
            "address": "",
            "latitude": 32.9410208,
            "longitude": -96.7366041,
            "rating": 4.2,
            "reviews": 128,
            "distance": 0.3,
            "open_until": "9:00 PM"
        },
    ]

    austrailia_default = (-25.363, 131.044)
    richardson_default = (32.948334, -96.729851)
    customer_lat = session.get('customer_lat', richardson_default[0])
    customer_long = session.get('customer_long', richardson_default[1])
    merchants = session.get('merchants', merchants_default)

    return render_template(
        'merchant-map.html',
        customer_lat=customer_lat,
        customer_long=customer_long,
        merchants=merchants,

        first_name=session['first_name'],
        email=session['email']
    )
    
if __name__ == '__main__':
    print(address_to_coords('744 Brick Row, Richardson, TX 75081'))

