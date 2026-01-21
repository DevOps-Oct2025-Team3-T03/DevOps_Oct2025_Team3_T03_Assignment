# app.py (Authentication Service)
from flask import Flask
from flask_cors import CORS
from auth_service_routes import auth_blueprint

app = Flask(__name__)
app.secret_key = "only-secret-key"

# Enable CORS
CORS(app, supports_credentials=True)  # allows cookies/sessions
app.register_blueprint(auth_blueprint)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)