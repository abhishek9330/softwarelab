# my_webapp_lib/webapp.py

from flask import Flask
# my_webapp_lib/webapp.py

class WebApp:
    def __init__(self, title="My Web App", secret_key=None):
        self.app = Flask(__name__)
        self.title = title
        self.pages = []

        # Set the secret key for sessions
        self.app.secret_key = secret_key or 'your_secret_key'

    def add_page(self, page):
        """Adds a page to the app."""
        self.pages.append(page)
        self.app.add_url_rule(
            page.route,
            view_func=page.view_func,        # Register the view function
            methods=page.methods,            # HTTP methods like GET, POST
            endpoint=page.endpoint_name      # Explicitly set the endpoint
        )

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Runs the web application."""
        self.app.run(host=host, port=port, debug=debug)
