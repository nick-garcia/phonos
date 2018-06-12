from flask import render_template
from phonos import app

@app.route('/')
def index_html():
    return render_template('index.html')
