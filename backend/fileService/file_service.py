import os
from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

file_blueprint = Blueprint("files", __name__)

UPLOAD_FOLDER = "uploads"

# Ensure folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MongoDB setup
client = MongoClient("mongodb+srv://josephbwanzj_db_user:josephwan1*@mvpcluster.fgzsm9n.mongodb.net/")
db = client["MVPDatabase"]
files_col = db["MVPFiles"]

#UPLOAD_FOLDER = "/uploads"  # For MVP, store files locally

# -------- Routes --------

# List files for the logged-in user
@file_blueprint.route("/dashboard", methods=["GET"])
def dashboard():
    user_id = session.get("user_id")
    username = session.get("username")
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    user_files = list(files_col.find({"owner_id": user_id}))
    return jsonify([
        {"file_id": str(f["_id"]), "filename": f["filename"], "path": f["path"]}
        for f in user_files
    ])

# Upload a file
@file_blueprint.route("/dashboard/upload", methods=["POST"])
def upload_file():
    user_id = session.get("user_id")
    username = session.get("username")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    uploaded_files = request.files.getlist("files")
    if not uploaded_files:
        return jsonify({"error": "No file provided"}), 400

    # For MVP, save locally
    # filepath = f"{UPLOAD_FOLDER}/{username}-{uploaded_file.filename}"
    # uploaded_file.save(filepath)

    # Insert metadata into MongoDB
    # result = files_col.insert_one({
    #     "filename": uploaded_file.filename,
    #     "owner_id": session["user_id"],
    #     "path": filepath,
    #     "created_at": datetime.utcnow()
    # })
    saved_files = []
    inserted_ids = []
    for file in uploaded_files:
        if not file:
            continue
        filepath = os.path.join(UPLOAD_FOLDER, f"{username}-{file.filename}")
        file.save(filepath)

        # Save file metadata in DB
        result = files_col.insert_one({
            "filename": file.filename,
            "owner_id": user_id,
            "path": filepath,
            "created_at": datetime.utcnow()
        })
        saved_files.append(file.filename)
        inserted_ids.append(str(result.inserted_id))  # store inserted IDs

    return jsonify({"file_ids": inserted_ids, "files": saved_files})

# Download a file
@file_blueprint.route("/dashboard/download/<file_id>", methods=["GET"])
def download_file(file_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    file_meta = files_col.find_one({"_id": ObjectId(file_id), "owner_id": user_id})
    if not file_meta:
        return jsonify({"error": "Forbidden"}), 403

    # For MVP, just return path & metadata
    return jsonify({"file_id": file_id, "filename": file_meta["filename"], "path": file_meta["path"]})

# Delete a file
@file_blueprint.route("/dashboard/delete/<file_id>", methods=["POST"])
def delete_file(file_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    file_meta = files_col.find_one({"_id": ObjectId(file_id), "owner_id": user_id})
    if not file_meta:
        return jsonify({"error": "Forbidden"}), 403

    files_col.delete_one({"_id": ObjectId(file_id)})
    return jsonify({"status": "deleted"})
