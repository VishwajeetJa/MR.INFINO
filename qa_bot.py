import os
import requests
import json
import pyttsx3
import threading
import cv2
import time
import re
from textblob import TextBlob



MISTRAL_API_KEY = "Ozl4D71u7MFsdFiAIPEcLnkr5kdAVJ2h"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


class VoiceManager:
    """Handles text-to-speech synthesis and state."""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.is_speaking = False

    def speak_in_thread(self, text):
        """Internal method to run TTS in a separate thread."""
        self.is_speaking = True
        self.engine.say(text)
        self.engine.runAndWait()
        self.is_speaking = False

    def speak(self, text):
        """Starts speaking the given text in a non-blocking way."""
        if self.is_speaking:
            self.stop()
        
        thread = threading.Thread(target=self.speak_in_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def stop(self):
        """Stops the TTS engine."""
        self.engine.stop()
        self.is_speaking = False


class VideoManager:
    """Handles loading and displaying video frames for the animation."""
    def __init__(self):
        
        self.video_paths = {
            'base': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\BaseSimulation.mp4",
            'positive': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\comma.mp4", # Add paths for emotion videos
            'negative': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\fullstop.mp4",
            'neutral': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\questionmark.mp4",
            ',': r"C:\path\to\your\comma.mp4",
            '.': r"C:\path\to\your\fullstop.mp4",
            '?': r"C:\path\to\your\questionmark.mp4",
        }
        self.captures = {}
        self.current_emotion = "neutral"

    def initialize_videos(self):
        """Loads all video files into memory. Returns False if base video fails."""
        print("🎬 Initializing videos...")
        for key, path in self.video_paths.items():
            if not os.path.exists(path):
                print(f"⚠️ Missing video file: {key} at {path}")
                continue
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                self.captures[key] = cap
            else:
                print(f"❌ Failed to open video: {key}")
        
        if 'base' not in self.captures:
            print("\nCRITICAL ERROR: The 'base' video failed to load. The animation cannot start.")
            return False
        return True

    def get_current_frame(self):
        """Gets the next frame from the currently active emotion video."""
        active_capture = self.captures.get(self.current_emotion, self.captures['base'])
        ret, frame = active_capture.read()
        if not ret:
            active_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = active_capture.read()
        return ret, frame

    def play_punctuation_video(self, symbol):
        """Shows a single frame of a punctuation video."""
        if symbol in self.captures:
            ret, frame = self.captures[symbol].read()
            if ret:
                cv2.imshow("AI Assistant", frame)
            self.captures[symbol].set(cv2.CAP_PROP_POS_FRAMES, 0) # Rewind

    def release_all(self):
        """Releases all video resources."""
        for cap in self.captures.values():
            cap.release()


def analyze_script(script):
    """Analyzes text to determine sentence structure and emotion."""
    sentences = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    analysis = []
    for sentence in sentences:
        blob = TextBlob(sentence)
        sentiment = blob.sentiment.polarity
        emotion = "neutral"
        if sentiment > 0.3:
            emotion = "positive"
        elif sentiment < -0.3:
            emotion = "negative"
        analysis.append({'text': sentence, 'emotion': emotion})
    return analysis


def get_answer_from_mistral(question):
    """Sends a question to the Mistral AI API and returns the answer."""
    if not MISTRAL_API_KEY or "YOUR_MISTRAL_API_KEY" in MISTRAL_API_KEY:
        return "API Key not configured. Please paste your Mistral API key into the script."
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's questions clearly and concisely."},
            {"role": "user", "content": question}
        ]
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"API Error: {e}")
        return "Sorry, I'm having trouble connecting to the AI service right now."


def start_interactive_qa_with_animation():
    """Runs the main interactive Q&A loop with video animation."""
    print("\n" + "=" * 60)
    print("💬 DYNAMIC AI Q&A SESSION WITH ANIMATION 👱")
    print("   (Type 'quit' to exit)")
    print("=" * 60)
    
    voice_manager = VoiceManager()
    video_manager = VideoManager()

    if not video_manager.initialize_videos():
        return

    while True:
        user_question = input("\nYour Question: ")
        if user_question.lower().strip() == 'quit':
            print("👋 Exiting Q&A session. Goodbye!")
            break
        if not user_question.strip():
            continue

        print("\n🤖 Thinking...")
        answer_text = get_answer_from_mistral(user_question)
        print(f"\n🤖 Answer: {answer_text}")
        
        
        analysis = analyze_script(answer_text)
        full_answer_text = " ".join([s['text'] for s in analysis])
        
        voice_manager.speak(full_answer_text)
        
        sentence_index = 0
        try:
            while voice_manager.is_speaking:
                if sentence_index < len(analysis):
                    current_emotion = analysis[sentence_index]['emotion']
                    video_manager.current_emotion = current_emotion
                
                ret, frame = video_manager.get_current_frame()
                if ret:
                    cv2.imshow("AI Assistant", frame)

                
                if not voice_manager.engine.isBusy():
                    sentence_index +=1

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    voice_manager.stop()
                    break
                
                time.sleep(0.05) 
        finally:
            cv2.destroyAllWindows()

    video_manager.release_all()


if __name__ == "__main__":
    start_interactive_qa_with_animation()
