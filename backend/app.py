# main.py
from flask import Flask
from flask_cors import CORS
from authService.auth_service import auth_blueprint
from fileService.file_service import file_blueprint

app = Flask(__name__)
app.secret_key = "only-secret-key"

# Enable CORS
CORS(app, supports_credentials=True)  # allows cookies/sessions
app.register_blueprint(auth_blueprint)
app.register_blueprint(file_blueprint)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)