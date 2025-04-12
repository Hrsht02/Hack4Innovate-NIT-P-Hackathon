from flask import Flask, request, jsonify, render_template
import random
import os

app = Flask(__name__)


FUNNY_EMOJIS = ["😂", "🤣", "😆", "😅", "🤪", "👻", "🎉", "🤡", "🐶", "🍕", "💩", "🙈", "🐔", "🍑"]
SAD_EMOJIS = ["😢", "😭", "😔", "💔", "🌧️", "☔", "🚬", "📉", "🐌", "⌛", "🌫️", "🥀", "🚑", "⚰️"]


FUNNY_REPLACEMENTS = {
    "hello": "howdy",
    "hi": "yo",
    "friend": "homie",
    "good": "lit",
    "bad": "whack",
    "happy": "jiggy",
    "sad": "bummed",
    "money": "cheddar",
    "work": "grind",
    "home": "crib",
    "car": "whip",
    "food": "noms",
    "dog": "doge",
    "cat": "meow machine"
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

def transform_text(text, style):
    
    lower_text = text.lower()
    words = text.split()
    transformed_words = []
    

    replacements = FUNNY_REPLACEMENTS if style == 'funny' else SAD_REPLACEMENTS
    for word in words:
        lower_word = word.lower()
        if lower_word in replacements:
            
            if word[0].isupper():
                new_word = replacements[lower_word].capitalize()
            else:
                new_word = replacements[lower_word]
            transformed_words.append(new_word)
        else:
            transformed_words.append(word)
    
    transformed_text = ' '.join(transformed_words)
    
  
    if style == 'funny':
        transformed_text = add_shakespearean_touch(transformed_text)
    
   
    transformed_text = add_emojis(transformed_text, style)
    
    return transformed_text

def add_shakespearean_touch(text):
    shakespearean_words = ["thou", "thee", "thy", "hath", "doth", "wherefore", 
                          "verily", "forsooth", "prithee", "mayhaps", "tis"]
    words = text.split()
    for i in range(0, len(words), random.randint(3, 6)):
        words.insert(i, random.choice(shakespearean_words))
    return ' '.join(words)

def add_emojis(text, style):
    emoji_pool = FUNNY_EMOJIS if style == 'funny' else SAD_EMOJIS
    words = text.split()
    
   
    for i, word in enumerate(words):
        if random.random() < 0.3:  
            words[i] = word + " " + random.choice(emoji_pool)
    
   
    if random.random() < 0.7: 
        words.insert(0, random.choice(emoji_pool))
    if random.random() < 0.7:  
        words.append(random.choice(emoji_pool))
    
    return ' '.join(words)

@app.route('/')
def home():
    return render_template('text.html')

@app.route('/convert', methods=['POST'])
def convert_text():
    data = request.get_json()
    text = data['text']
    style = data['style']  
    
    if not text.strip():
        return jsonify({'error': 'Please enter some text first! ✏️'}), 400
    
    try:
        converted_text = transform_text(text, style)
        return jsonify({'result': converted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)