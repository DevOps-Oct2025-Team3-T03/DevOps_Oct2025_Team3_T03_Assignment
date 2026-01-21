from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import bcrypt
import uuid
from datetime import datetime

auth_blueprint = Blueprint("auth", __name__)

# MongoDB setup
client = MongoClient("mongodb+srv://josephbwanzj_db_user:josephwan1*@mvpcluster.fgzsm9n.mongodb.net/")
db = client["MVPDatabase"]
users_col = db["MVPUsers"]
#files_col = db["MVPFiles"]
fs = gridfs.GridFS(db)

# In-memory user store for MVP
# users = {
#     "admin": {"password": "admin123", "role": "admin"},
#     "user1": {"password": "user123", "role": "user"},
# }



# -------- Routes --------

# Login
@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_col.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    #user = users.get(username)
    #if not user or user["password"] != password:
        #return jsonify({"error": "Invalid credentials"}), 401*/

    # Save user info in session
    session["username"] = username
    session["role"] = user["role"]
    session["user_id"] = str(user["user_id"])
    return jsonify({"username": username, "role": user["role"], "user_id": str(user["user_id"])})

#Logout
@auth_blueprint.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"})

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
    return jsonify({"status": "created"})

#Delete user (admin only)
@auth_blueprint.route("/admin/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    
    if user_id == session.get("user_id"):
        return jsonify({"error": "Admin cannot delete themselves"}), 400

    result = users_col.delete_one({"user_id": user_id})

    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    #files_col.delete_many({"owner_id": user_id})
    user_files = fs.find({"owner_id": user_id})

    for file in user_files:
        fs.delete(file._id)

    return jsonify({"status": "User deleted"})


# Check if admin already exists
if users_col.find_one({"username": "admin"}):
    print("Admin user already exists")
else:
    # Create admin user
    admin_user_id = str(uuid.uuid4())
    hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
    users_col.insert_one({
        "user_id": admin_user_id,
        "username": "admin",
        "password": hashed_pw,
        "role": "admin",
        "created_at": datetime.utcnow()
    })
    print("Admin user created")
