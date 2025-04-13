from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import librosa
import soundfile as sf
import os
import random
import logging
import tempfile
import mimetypes
import traceback

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_AUDIO_EXTENSIONS'] = {'wav', 'mp3', 'ogg', 'm4a'}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

# Available moods for each section
AVAILABLE_MOODS = {
    'text': ['happy', 'sad', 'angry', 'funny'],
    'image': ['happy', 'sad', 'angry', 'funny'],
    'voice': ['sad', 'funny', 'robot', 'enemy', 'alien', 'normal']
}

# Text conversion data
HAPPY_EMOJIS = ["😊", "😄", "🌟", "🎉", "🌈", "✨", "🎈", "👍", "💖", "🥳", "👏", "🎊", "🍀", "🦋"]
SAD_EMOJIS = ["😢", "😭", "😔", "💔", "🌧️", "☔", "🚬", "📉", "🐌", "⌛", "🌫️", "🥀", "🚑", "⚰️"]
ANGRY_EMOJIS = ["😠", "🤬", "👊", "💢", "🗯️", "🔪", "💣", "🧨", "⚔️", "🖕", "👿", "💀", "🔥", "☠️"]
FUNNY_EMOJIS = ["😂", "🤣", "😆", "🤪", "👻", "🤡", "🦄", "🍌", "🦆", "🎭", "🍿", "🎪", "🤹", "🎰"]

HAPPY_INDIAN_REPLACEMENTS = {
    "hello": "namaste ji",
    "hi": "arre hi hi!",
    "friend": "yaar",
    "good": "mast",
    "bad": "thik thak",
    "sad": "thoda emotional",
    "money": "paisa vasool",
    "work": "mehnat ka fal",
    "home": "ghar ka sukoon",
    "car": "gaadi meri shaan",
    "food": "ghar ka khana",
    "dog": "kuttey raja",
    "cat": "billi devi",
    "love": "ishq wala love",
    "laugh": "haasya kavi mode",
    "sun": "suraj bhagwan",
    "success": "jeet ki khushi",
    "life": "zindagi gulzar hai"
}

SAD_REPLACEMENTS = {
    "happy": "miserable", 
    "good": "dreadful", 
    "great": "terrible",
    "fun": "agonizing", 
    "love": "heartbreak", 
    "friend": "lonely soul",
    "home": "empty room", 
    "sun": "dark cloud", 
    "laugh": "sob",
    "success": "failure"
}

ANGRY_INDIAN_REPLACEMENTS = {
    "hello": "kya chahiye ab?",
    "hi": "haan bol!",
    "friend": "dil ka dushman",
    "good": "bakwaas nahi hai",
    "bad": "ghatiya",
    "happy": "dramebaazi",
    "money": "kala dhan",
    "work": "majboori ka naam mehnat",
    "home": "kaidkhana",
    "car": "khatara",
    "food": "basi khana",
    "dog": "kuttey ki dum",
    "cat": "billi ki chhalang",
    "love": "dhoka",
    "laugh": "ha ha... nautanki!",
    "sun": "tapta tandoor",
    "success": "upar se gaya chance",
    "life": "ek badi sazaa"
}

FUNNY_REPLACEMENTS = {
    "hello": "henlo hooman",
    "hi": "haiiiii",
    "friend": "fren",
    "good": "gud",
    "bad": "not gud",
    "happy": "heckin happy",
    "money": "doge coin",
    "work": "doing a work",
    "home": "house of bork",
    "car": "vroom vroom",
    "food": "noms",
    "dog": "doge",
    "cat": "smol tiger",
    "love": "luv",
    "laugh": "lololol",
    "sun": "sky fire",
    "success": "big win",
    "life": "heckin existence"
}

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load face detection model
face_cascade = None
try:
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if not os.path.exists(face_cascade_path):
        raise FileNotFoundError(f"Haar cascade file not found at {face_cascade_path}")
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    if face_cascade.empty():
        raise ValueError("Loaded cascade classifier is empty")
except Exception as e:
    logger.error(f"Failed to load face detection model: {str(e)}")
    logger.error(traceback.format_exc())

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "An error occurred while loading the page.", 500

@app.route('/api/check')
def api_check():
    try:
        return jsonify({
            'status': 'active',
            'available_moods': AVAILABLE_MOODS
        })
    except Exception as e:
        logger.error(f"API check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/convert_text', methods=['POST'])
def convert_text():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        text = data.get('text', '').strip()
        style = data.get('style', '').lower()
        
        if not text:
            return jsonify({'error': 'Please enter some text first'}), 400
        
        if style not in AVAILABLE_MOODS['text']:
            return jsonify({
                'error': 'Invalid style specified',
                'allowed_styles': AVAILABLE_MOODS['text']
            }), 400
            
        converted_text = transform_text(text, style)
        return jsonify({'result': converted_text})
        
    except Exception as e:
        logger.error(f"Text conversion error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/transform_image', methods=['POST'])
def transform_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not allowed_file(file.filename, 'image'):
            return jsonify({
                "error": "Invalid file type",
                "allowed_types": list(app.config['ALLOWED_IMAGE_EXTENSIONS'])
            }), 400

        try:
            expression = request.form.get('expression', '').lower()
            if expression not in AVAILABLE_MOODS['image']:
                return jsonify({
                    "error": "Invalid expression",
                    "allowed_expressions": AVAILABLE_MOODS['image']
                }), 400
                
            img = Image.open(file.stream)
            img.verify()
            file.stream.seek(0)
            img = Image.open(file.stream)
            
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            cartoon_img = convert_to_cartoon(img_cv)
            
            if face_cascade is None:
                img_io = BytesIO()
                Image.fromarray(cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2RGB)).save(img_io, format='PNG')
                img_io.seek(0)
                return send_file(img_io, mimetype='image/png')
                
            frames = generate_expression_animation(cartoon_img, expression)
            
            img_io = BytesIO()
            if len(frames) > 0:
                try:
                    frames[0].save(
                        img_io, 
                        format='GIF', 
                        save_all=True,
                        append_images=frames[1:], 
                        duration=100, 
                        loop=0
                    )
                    mimetype = 'image/gif'
                except Exception as e:
                    Image.fromarray(cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2RGB)).save(img_io, format='PNG')
                    mimetype = 'image/png'
            else:
                Image.fromarray(cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2RGB)).save(img_io, format='PNG')
                mimetype = 'image/png'
            
            img_io.seek(0)
            return send_file(img_io, mimetype=mimetype)
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return jsonify({"error": "Error processing image"}), 500
            
    except Exception as e:
        logger.error(f"Image endpoint error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/modify_audio', methods=['POST'])
def modify_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files["audio"]
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not allowed_file(file.filename, 'audio'):
            return jsonify({
                "error": "Invalid file type",
                "allowed_types": list(app.config['ALLOWED_AUDIO_EXTENSIONS'])
            }), 400

        try:
            effect = request.form.get("effect", "").lower()
            if effect not in AVAILABLE_MOODS['voice']:
                return jsonify({
                    "error": "Invalid effect specified",
                    "allowed_effects": AVAILABLE_MOODS['voice']
                }), 400

            with tempfile.NamedTemporaryFile(suffix='.wav', dir=app.config['UPLOAD_FOLDER'], delete=False) as input_temp:
                try:
                    file.save(input_temp.name)
                    input_path = input_temp.name
                    
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{random.randint(0, 10000)}.wav")
                    
                    try:
                        y, sr = librosa.load(input_path, sr=None, mono=True)
                        
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
                        
                        sf.write(output_path, y_modified, sr)
                        
                        response = send_file(
                            output_path, 
                            mimetype='audio/wav', 
                            as_attachment=True,
                            download_name=f"modified_{effect}_{file.filename}"
                        )
                        
                        response.call_on_close(lambda: cleanup_files([input_path, output_path]))
                        return response
                        
                    except Exception as e:
                        logger.error(f"Audio processing error: {str(e)}")
                        return jsonify({"error": "Error processing audio"}), 500
                        
                except Exception as e:
                    logger.error(f"File handling error: {str(e)}")
                    return jsonify({"error": "Error handling audio file"}), 500
                    
        except Exception as e:
            logger.error(f"Audio endpoint error: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in audio endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def transform_text(text, style):
    if style == "happy":
        # Apply happy transformations
        for word, replacement in HAPPY_INDIAN_REPLACEMENTS.items():
            text = text.replace(word, replacement)
        # Add random happy emoji every few words
        words = text.split()
        for i in range(0, len(words), 3):
            if random.random() > 0.7:
                words.insert(i, random.choice(HAPPY_EMOJIS))
        text = ' '.join(words)
    elif style == "sad":
        # Apply sad transformations
        for word, replacement in SAD_REPLACEMENTS.items():
            text = text.replace(word, replacement)
        # Add random sad emoji every few words
        words = text.split()
        for i in range(0, len(words), 3):
            if random.random() > 0.7:
                words.insert(i, random.choice(SAD_EMOJIS))
        text = ' '.join(words)
    elif style == "angry":
        # Apply angry transformations
        for word, replacement in ANGRY_INDIAN_REPLACEMENTS.items():
            text = text.replace(word, replacement)
        # Add random angry emoji every few words
        words = text.split()
        for i in range(0, len(words), 2):
            if random.random() > 0.6:
                words.insert(i, random.choice(ANGRY_EMOJIS))
        text = ' '.join(words)
        # Add angry punctuation
        if len(text) > 0 and text[-1] not in {'!', '?', '.'}:
            text += random.choice(['!', '!!', '!!!'])
    elif style == "funny":
        # Apply funny transformations
        for word, replacement in FUNNY_REPLACEMENTS.items():
            text = text.replace(word, replacement)
        # Add random funny emoji every few words
        words = text.split()
        for i in range(0, len(words), 2):
            if random.random() > 0.6:
                words.insert(i, random.choice(FUNNY_EMOJIS))
        text = ' '.join(words)
        # Add funny punctuation
        if len(text) > 0 and text[-1] not in {'!', '?', '.'}:
            text += random.choice(['!', '?', '...'])
    return text

def convert_to_cartoon(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply median blur
    gray = cv2.medianBlur(gray, 5)
    # Detect edges
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                cv2.THRESH_BINARY, 9, 9)
    # Color quantization
    color = cv2.bilateralFilter(img, 9, 300, 300)
    # Combine edges with quantized image
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def generate_expression_animation(img, expression):
    frames = []
    if face_cascade is None:
        return frames
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0:
        return frames
    
    x, y, w, h = faces[0]
    face_roi = img[y:y+h, x:x+w]
    
    for i in range(5):
        temp_img = img.copy()
        
        if expression == "happy":
            # Draw smile
            cv2.ellipse(temp_img, 
                       (x + w//2, y + h//2 + h//4),
                       (w//4, h//8),
                       0, 0, 180,
                       (0, 0, 0), 2)
            # Draw eyes
            cv2.ellipse(temp_img,
                       (x + w//3, y + h//3),
                       (w//12, h//12),
                       0, 0, 360,
                       (0, 0, 0), -1)
            cv2.ellipse(temp_img,
                       (x + 2*w//3, y + h//3),
                       (w//12, h//12),
                       0, 0, 360,
                       (0, 0, 0), -1)
        elif expression == "sad":
            # Draw frown
            cv2.ellipse(temp_img,
                       (x + w//2, y + h//2 + h//3),
                       (w//4, h//8),
                       0, 0, -180,
                       (0, 0, 0), 2)
            # Draw eyes
            cv2.ellipse(temp_img,
                       (x + w//3, y + h//3),
                       (w//12, h//12),
                       0, 0, 360,
                       (0, 0, 0), -1)
            cv2.ellipse(temp_img,
                       (x + 2*w//3, y + h//3),
                       (w//12, h//12),
                       0, 0, 360,
                       (0, 0, 0), -1)
        elif expression == "angry":
            # Draw angry eyebrows and mouth
            cv2.line(temp_img,
                    (x + w//4, y + h//4),
                    (x + w//2, y + h//3),
                    (0, 0, 0), 3)
            cv2.line(temp_img,
                    (x + 3*w//4, y + h//4),
                    (x + w//2, y + h//3),
                    (0, 0, 0), 3)
            cv2.line(temp_img,
                    (x + w//3, y + 3*h//4),
                    (x + 2*w//3, y + 3*h//4),
                    (0, 0, 0), 3)
        elif expression == "funny":
            # Draw funny face (tongue out)
            cv2.ellipse(temp_img,
                       (x + w//2, y + h//2 + h//4),
                       (w//4, h//8),
                       0, 0, 180,
                       (0, 0, 0), 2)
            # Draw tongue
            cv2.ellipse(temp_img,
                       (x + w//2, y + h//2 + h//3),
                       (w//8, h//12),
                       0, 0, 180,
                       (0, 0, 0), -1)
            # Draw winking eye
            cv2.line(temp_img,
                    (x + w//3, y + h//3),
                    (x + w//3 + w//12, y + h//3),
                    (0, 0, 0), 3)
            # Draw normal eye
            cv2.ellipse(temp_img,
                       (x + 2*w//3, y + h//3),
                       (w//12, h//12),
                       0, 0, 360,
                       (0, 0, 0), -1)
        
        frames.append(Image.fromarray(cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)))
    
    return frames

def allowed_file(filename, file_type='image'):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config.get(f'ALLOWED_{file_type.upper()}_EXTENSIONS', set())

def cleanup_files(file_paths):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not delete temp file {path}: {str(e)}")

if __name__ == '__main__':
    try:
        app.run(
            host='0.0.0.0', 
            port=int(os.environ.get('PORT', 9000)),
            debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        )
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")