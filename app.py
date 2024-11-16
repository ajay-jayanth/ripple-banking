from flask import Flask, render_template, request, session, redirect, url_for, flash

name = 'Budget Buddy'
app = Flask(name) 

app.config.update( 
    SECRET_KEY='dev'
)

@app.route('/')
def index_function(): 
    return render_template('landing-page.html')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000, threaded=True)
