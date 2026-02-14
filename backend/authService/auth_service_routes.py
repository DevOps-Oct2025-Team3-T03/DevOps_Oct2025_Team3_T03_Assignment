from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import bcrypt
import uuid
from datetime import datetime

auth_blueprint = Blueprint("auth", __name__)
##
# MongoDB setup
client = MongoClient("mongodb+srv://josephbwanzj_db_user:josephwan1*@mvpcluster.fgzsm9n.mongodb.net/")
db = client["MVPUsers_DB"]
users_col = db["MVPUsers"]
#files_col = db["MVPFiles"]
fs = gridfs.GridFS(db)
logs_col = db["MVPUsers_Logs"]

# In-memory user store for MVP
# users = {
#     "admin": {"password": "admin123", "role": "admin"},
#     "user1": {"password": "user123", "role": "user"},
# }

def log_action(user_id, username, action, details=""):
    logs_col.insert_one({
        "timestamp": datetime.utcnow(),
        "user_id": user_id,
        "username": username,
        "action": action,
        "details": details
    })

# -------- Routes --------

@auth_blueprint.route("/health")
def health():
    return "OK", 200

# Login
@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        log_action(None, username, "Login failed with missing credentials")
        return jsonify({"error": "Invalid credentials"}), 401

    user = users_col.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        log_action(None, username, "Login failed with invalid credentials")
        return jsonify({"error": "Invalid credentials"}), 401

    #user = users.get(username)
    #if not user or user["password"] != password:
        #return jsonify({"error": "Invalid credentials"}), 401*/

    # Save user info in session
    session["username"] = username
    session["role"] = user["role"]
    session["user_id"] = str(user["user_id"])
    log_action(str(user["user_id"]), username, "Login successful")
    return jsonify({"username": username, "role": user["role"], "user_id": str(user["user_id"])})

#Logout
@auth_blueprint.route("/logout", methods=["GET"])
def logout():
    user_id = session.get("user_id")
    username = session.get("username")
    if "user_id" not in session:
        log_action(None, None, "Unauthorized logout")
        return jsonify({"error": "Unauthorized"}), 401

    session.clear()
    log_action(user_id, username, "Logged out")
    return jsonify({"status": "logged out"}), 200

#List users (admin only)
@auth_blueprint.route("/admin", methods=["GET"])
def list_users():
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    
    all_users = users_col.find()
    return jsonify([{"user_id": str(u["user_id"]), "username": u["username"], "role": u["role"]} for u in all_users])
    # return jsonify([{"username": u, "role": users[u]["role"]} for u in users])

#Create user (admin only)
@auth_blueprint.route("/admin/create_user", methods=["POST"])
def create_user():
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # default to regular user

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    if users_col.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400
    
    # Generate unique user_id
    user_id = str(uuid.uuid4())

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_col.insert_one({
        "user_id": user_id,
        "username": username,
        "password": hashed_pw,
        "role": role,
        "created_at": datetime.utcnow()
    })
    log_action(session.get("user_id"), session.get("username"), "Create User", f"Created user {username}")
    return jsonify({"status": "User created"})

#Delete user (admin only)
@auth_blueprint.route("/admin/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    
    if user_id == session.get("user_id"):
        return jsonify({"error": "Admin cannot delete themselves"}), 400
    
    user = users_col.find_one({"user_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = users_col.delete_one({"user_id": user_id})

    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    #files_col.delete_many({"owner_id": user_id})
    user_files = fs.find({"owner_id": user_id})

    for file in user_files:
        fs.delete(file._id)

    log_action(session.get("user_id"), session.get("username"), "Delete User", f"Deleted user {user.get('username', user_id)}")
    return jsonify({"status": "User deleted"}), 200


# Admin: Fetch Auth Logs
@auth_blueprint.route("/admin/logs", methods=["GET"])
def get_auth_logs():
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403

    logs = list(logs_col.find().sort("timestamp", -1))
    return jsonify([
        {
            "username": log["username"],
            "action": log["action"],
            "details": log.get("details", ""),
            "timestamp": log["timestamp"].isoformat()
        }
        for log in logs
    ])

# Check if admin already exists
if users_col.find_one({"username": "admin"}):
    print("Existing admin(s) located in the DB.")
else:
    # Create admin user
    print("No existing admins found in the DB, creating default admin...")
    admin_user_id = str(uuid.uuid4())
    hashed_pw = bcrypt.hashpw("AdminPass123!".encode(), bcrypt.gensalt())
    users_col.insert_one({
        "user_id": admin_user_id,
        "username": "admin",
        "password": hashed_pw,
        "role": "admin",
        "created_at": datetime.utcnow()
    })
    print("Admin user created")
