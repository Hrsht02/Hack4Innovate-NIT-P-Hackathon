from flask import Flask, request, send_file, render_template, jsonify
import librosa
import soundfile as sf
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/modify", methods=["POST"])
def modify():
    
    audio_file = request.files["audio"]
    effect = request.form.get("effect")
    pitch = float(request.form.get("pitch", 0))
    speed = float(request.form.get("speed", 1.0))
    echo = float(request.form.get("echo", 0))
    
   
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], "input.wav")
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.wav")
    audio_file.save(input_path)
    

    y, sr = librosa.load(input_path, sr=None)
    
    if effect == "sad":
        y_modified = librosa.effects.pitch_shift(y, sr=sr, n_steps=-4)
        y_modified = librosa.effects.time_stretch(y_modified, rate=0.7)
    elif effect == "funny":
        y_modified = librosa.effects.pitch_shift(y, sr=sr, n_steps=6)
        y_modified = librosa.effects.time_stretch(y_modified, rate=1.3)
    elif effect == "robot":
        y_modified = y * 0.3 + np.random.normal(0, 0.05, len(y))
    elif effect == "enemy":
        y_modified = librosa.effects.pitch_shift(y, sr=sr, n_steps=-7)
        y_modified = y_modified * 1.5 + np.random.normal(0, 0.1, len(y))
    elif effect == "alien":
        y_modified = librosa.effects.pitch_shift(y, sr=sr, n_steps=10)
        y_modified = librosa.effects.time_stretch(y_modified, rate=0.8)
    else:
        y_modified = y
    
    
    if pitch != 0:
        y_modified = librosa.effects.pitch_shift(y_modified, sr=sr, n_steps=pitch)
    if speed != 1.0:
        y_modified = librosa.effects.time_stretch(y_modified, rate=speed)
    if echo > 0:
        delay = int(0.2 * sr)
        for i in range(delay, len(y_modified)):
            y_modified[i] += y_modified[i - delay] * echo
    
    
    sf.write(output_path, y_modified, sr)
    return jsonify({"success": True, "output_file": output_path})

if __name__ == "__main__":
    app.run(debug=True)