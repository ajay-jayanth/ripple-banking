import pandas as pd
import googlemaps
from typing import Tuple
from flask import Flask, render_template, request, session, redirect, url_for, flash
import os


API_KEY = 'AIzaSyDzGxjSG77K2SBQi2sWtVRYimFLpHlKYmg'
gmaps = googlemaps.Client(key=API_KEY)
MERCHANT_CSV_PATH = os.path.join(os.getcwd(), 'merchants.csv')

def address_to_coords(address: str) -> Tuple[float, float]:
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None
    
def get_merchants():
    df = pd.read_csv(MERCHANT_CSV_PATH)
    merchant_list = []
    for _, row in df.iterrows():
        address = f'{row["address"]} {row["city"]} {row["state"]}'
        lat, long = address_to_coords(address)
        if not lat:
            continue
        rating = row.get('rating', 5.0)
        stars = '★' * round(rating) + '☆' * (5 - round(rating))

        merchant_info = {
            'name': f'{row["first_name"]} {row["last_name"]}',
            'address': address,
            'latitude': lat,
            'longitude': long,
            'rating': rating,
            'stars': stars,
            'reviews': row.get('reviews', 0),
        }
        merchant_list.append(merchant_info)
    return merchant_list

def merchant_maps_fn():
    austrailia_default = (-25.363, 131.044)
    richardson_default = (32.948334, -96.729851)
    customer_lat = session.get('customer_lat', richardson_default[0])
    customer_long = session.get('customer_long', richardson_default[1])
    merchants = get_merchants()

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

