from dashboard.dash_app import app

server = app.server  # this is required for gunicorn


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
