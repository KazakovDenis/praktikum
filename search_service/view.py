from .app import app


@app.route('/')
def index():
    return '<h1>Service is running</h1>'
