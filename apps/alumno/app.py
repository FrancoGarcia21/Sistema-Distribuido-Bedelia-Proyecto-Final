from flask import Flask, render_template, Response, jsonify
import json, time
from routes.auth import bp as auth_bp
from jwt_helper import JWTHelper

from config import APP_NAME, DEBUG
from mqtt_client import mqtt_bridge

from routes.auth import bp as auth_bp
from routes.materias import bp as materias_bp
from routes.mqtt_api import bp as mqtt_bp

app = Flask(__name__)
app.config["DEBUG"] = DEBUG

app.register_blueprint(auth_bp)
app.register_blueprint(materias_bp)
app.register_blueprint(mqtt_bp)

@app.get("/")
def root():
    return render_template("login.html", app_name=APP_NAME)

@app.get("/login")
def login_view():
    return render_template("login.html", app_name=APP_NAME)

@app.get("/materias")
def materias_view():
    return render_template("materias.html", app_name=APP_NAME)

@app.get("/health")
def health():
    return jsonify({"app": APP_NAME, "status": "ok"})

@app.get("/events")
def events():
    def stream():
        yield f"data: {json.dumps({'type':'sse','event':'open'})}\n\n"
        while True:
            try:
                event = mqtt_bridge.events.get(timeout=15)
                yield f"data: {json.dumps(event, default=str)}\n\n"
            except Exception:
                yield f"data: {json.dumps({'type':'sse','event':'keepalive','ts':time.time()})}\n\n"
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG)
