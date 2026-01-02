# webserver.py
# Minimal Flask server: POST a JPEG file, keep it in memory.

from flask import Flask, request, jsonify

app = Flask(__name__)

LAST_JPEG: bytes | None = None  # in-memory only; overwritten each upload


@app.post("/upload")
def upload():
    global LAST_JPEG

    if "file" not in request.files:
        return jsonify(error="Missing form field 'file'"), 400

    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify(error="No file selected"), 400

    if (f.mimetype or "").lower() != "image/jpeg":
        return jsonify(error="Only image/jpeg is accepted", got=f.mimetype), 415

    data = f.read()
    if not data:
        return jsonify(error="Empty upload"), 400

    LAST_JPEG = data
    return jsonify(ok=True, bytes=len(data))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8487, debug=True)
