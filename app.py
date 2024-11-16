from flask import Flask, render_template, request, session, redirect, url_for, flash

name = 'Budget Buddy'
app = Flask(name) 

app.config.update( 
    SECRET_KEY='dev'
)

@app.route('/')
def index_function(): 
    return render_template('landing-page.html')

@app.route('/merchant-map', methods=['GET'])  # On Customer Side
def merchant_map():
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
        merchants=merchants
    )

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000, threaded=True)
