# 🎭 FeelSpeak – Emotion-Enhanced Communication Platform

**FeelSpeak** is an intelligent communication platform that transforms user input—**text**, **voice**, or **image**—into emotionally expressive outputs. By leveraging AI-based emotion detection and transformation, FeelSpeak enhances the way people connect by aligning message delivery with intended sentiment.

---

## 📌 Overview

In today’s digital world, emotional nuance is often lost in flat, text-based or monotone communication. **FeelSpeak bridges that gap** by enabling users to:

- Modify voice tone to match emotional context
- Animate text messages based on detected or selected mood
- Generate subtle facial expressions on images reflecting emotional tones

This results in a more **engaging**, **expressive**, and **humanized** messaging experience.

---

## 🚀 Key Features

### 🎙️ Voice Emotion Transformation
- Upload recorded voice or speak directly via microphone
- Apply emotional tone modifications (e.g., Happy, Angry, Sad, Professional)
- Audio effects include pitch shifting, speed variation, tone adjustment, and intensity smoothing

### 📝 Mood-Based Text Enhancement
- Text is transformed using context-aware emotional filters
- Auto-embeds emojis, punctuation styling, and intensity markers based on mood
- Supports tones like: Friendly, Funny, Sarcastic, Melancholic, and Formal

### 📷 Emotion-Altered Image Expressions
- Upload a face image
- Generate subtle facial changes (smile, frown, raised eyebrows) reflecting selected emotion
- Built using OpenCV and PIL for facial feature mapping and overlay

---

## 🎯 Use Cases

| Scenario | Application |
|----------|-------------|
| 🤖 AI Chatbots | Deliver emotionally consistent responses |
| 🧑‍🏫 E-learning | Improve student engagement with expressive voice/text |
| 🎮 Gaming | Add emotional tones in multiplayer or NPC voice messages |
| 🧠 Mental Health Apps | Visualize tone for mood tracking and journaling |
| 🎨 Creative Messaging | Enhance voice notes, status messages, and visual content |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React.js, HTML, CSS, Bootstrap |
| **Backend** | Flask (Python) |
| **Audio Processing** | Librosa, pydub |
| **Image Processing** | OpenCV, PIL |
| **Design** | Figma |
| **AI / ML Modules** | FrontFace, Harracade Classifier (custom emotion pipeline) |

---

## 📸 Screenshots

> _Screenshots and demo visuals go here. Add your assets to the `/screenshots` directory and replace image links._

| Text Converter | Voice Transformation | Image Expression Modifier |
|----------------|----------------------|----------------------------|
| ![Text Demo](screenshots/text-demo.png) | ![Voice Demo](screenshots/voice-demo.gif) | ![Image Demo](screenshots/image-demo.gif) |

---

## 🔍 Sample Workflow

### 🔊 Voice to Emotion  
1. User records or uploads voice  
2. Chooses an emotion filter (e.g., Sad)  
3. Output: Emotionally adjusted audio in real-time

### 📝 Text Emotion Rendering  
1. User types a message  
2. System auto-detects or user selects emotion  
3. Transformed output with visual + textual emotion cues

### 📷 Image Face Modifier  
1. User uploads a selfie  
2. Chooses an emotional tone  
3. Output: Subtly altered face with emotion-specific features

---

## 📂 Project Structure

```bash
FeelSpeak/
├── backend/              # Flask server with APIs for processing
├── frontend/             # React app for user interface
├── assets/               # Audio/image demo assets
├── models/               # Pretrained emotion classifiers and filters
├── static/               # CSS files and static assets
├── screenshots/          # UI demo images and GIFs
└── README.md
