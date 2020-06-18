from .app import app


@app.route('/')
def index():
    return 'Service is running'
