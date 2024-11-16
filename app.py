from flask import Flask, render_template
from merchant import merchant_bp  # Import the merchant blueprint

app = Flask(__name__)
app.config.update(
    SECRET_KEY='dev'
)

# Register blueprints
app.register_blueprint(merchant_bp, url_prefix='/merchant')


@app.route('/')
def index_function():
    # This requires render_template
    return render_template('landing-page.html')


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000, threaded=True)
