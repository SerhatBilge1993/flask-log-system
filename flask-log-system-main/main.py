from website import create_app
from otel_logging import setup_otel_logging

setup_otel_logging("flask-app")

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)