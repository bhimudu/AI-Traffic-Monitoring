from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import subprocess
import os

app = Flask(
    __name__,
    static_url_path="/evidence",
    static_folder="evidence",
    template_folder="templates"
)

# MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["traffic_ai"]
collection = db["violations"]

UPLOAD_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def mode_select():
    return render_template("select.html")

@app.route("/upload", methods=["POST"])
def upload_video():
    video = request.files["video"]
    video_path = os.path.join(UPLOAD_FOLDER, "test.mp4")
    video.save(video_path)

    # Run detection in background
    subprocess.Popen(["python", "main.py"])

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/api/violations")
def get_violations():
    data = []
    for v in collection.find().sort("timestamp", -1):
        v["_id"] = str(v["_id"])
        data.append(v)
    return jsonify(data)

@app.route("/live")
def live_camera():
    return "<h2>Live Camera Mode (Coming Soon)</h2>"

if __name__ == "__main__":
    app.run(debug=True)
