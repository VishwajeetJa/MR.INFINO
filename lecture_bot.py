import cv2
import os
import time
import requests
import json
import re
from textblob import TextBlob
import pyttsx3
import threading
import PyPDF2



MISTRAL_API_KEY = "esexNZUdsokW1Yku6ePzkJ8hRIuPCcUh"


class VoiceManager:
    """Manages Text-to-Speech functionality."""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.is_speaking = False
        self.stop_requested = False
        
    def setup_voice(self):
        """Setup voice properties like accent, rate, and volume."""
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            if 'indian' in voice.name.lower() or 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 120)  
        self.engine.setProperty('volume', 0.9) 
        
    def speak_entire_script(self, full_script_text):
        """Speak the entire script as one continuous text in a separate thread."""
        self.stop_requested = False
        self.is_speaking = True
        
        def speak():
            print("🔊 Starting to speak ENTIRE script...")
            self.engine.say(full_script_text)
            self.engine.runAndWait()
            self.is_speaking = False
            print("🔊 Finished speaking entire script")
            
        thread = threading.Thread(target=speak)
        thread.daemon = True
        thread.start()
        
    def stop_speaking(self):
        """Stop the current speech immediately."""
        self.engine.stop()
        self.is_speaking = False
        self.stop_requested = True


def extract_text_from_pdf(pdf_path):
    """Extracts text content from a given PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return None

def generate_lecture_script_with_mistral(raw_content):
    """Uses Mistral AI to generate a complete lecture script from raw content."""
    
    prompt = f"""
    TASK: Create an engaging 10-minute university lecture script based on the following raw content.
    
    RAW CONTENT:
    {raw_content[:4000]} # Using a slice to avoid exceeding token limits
    
    REQUIREMENTS:
    - Duration: Approximately 10 minutes (should be around 1000-1500 words).
    - Structure: A clear introduction, 3-4 main educational points with detailed examples, and a concise conclusion.
    - Engagement: Include real-world examples and case studies directly related to the content.
    - Tone: Add appropriate educational humor and engaging elements suitable for university students.
    - Style: Maintain a conversational yet professional teaching style.
    - Flow: Ensure a logical progression of ideas with clear, easy-to-understand explanations.
    - Formatting: Use natural punctuation for speech delivery (commas, periods, question marks).
    - Overall: The final script should be professional, educational, and entertaining.
    
    Create a complete lecture script that expands on the raw content, making it engaging and suitable for a university-level audience.
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-medium",  
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        print("🔄 Calling Mistral AI API...")
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            script = result['choices'][0]['message']['content']
            print("✅ Script generated successfully with Mistral AI!")
            return script.strip()
        else:
            print(f"❌ Mistral API Error: {response.status_code}")
            print(f"🔧 Response: {response.text}")
            
            
            if response.status_code == 429:
                print("🔄 Trying with mistral-small model...")
                payload["model"] = "mistral-small"
                response = requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    script = result['choices'][0]['message']['content']
                    print("✅ Script generated successfully with mistral-small!")
                    return script.strip()
            
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Mistral API timeout - server took too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Mistral API connection error - check your internet connection.")
        return None
    except Exception as e:
        print(f"❌ Mistral API call failed: {e}")
        return None


def analyze_script(script):
    """Analyzes the script for emotions, punctuation, and video transitions."""
    
    analysis = {
        'sentences': [],
        'punctuation': [],
        'emotions': [],
        'video_transitions': []
    }
    
    
    sentences = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    for i, sentence in enumerate(sentences):
        
        blob = TextBlob(sentence)
        sentiment = blob.sentiment.polarity
        
        
        if sentiment > 0.3:
            emotion = "positive"
        elif sentiment < -0.3:
            emotion = "negative" 
        else:
            emotion = "neutral"
        
        
        sentence_punct = [char for char in sentence if char in [',', '.', '?', '!']]
        
        analysis['sentences'].append({
            'text': sentence,
            'sentiment': sentiment,
            'emotion': emotion,
            'length': len(sentence)
        })
        analysis['punctuation'].extend(sentence_punct)
        analysis['emotions'].append(emotion)
    
    return analysis, script


class VideoManager:
    """Handles loading, playing, and managing video files for the simulation."""
    def __init__(self):
        
        self.video_paths = {
            'base': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\BaseSimulation.mp4",
            ',': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\comma.mp4", 
            '.': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\fullstop.mp4",
            '?': r"C:\Users\acer\Desktop\CEP Project Modeule\BaseSimulation\questionmark.mp4",
            'positive': r"C:\path\to\your\positive_expression.mp4",
            'negative': r"C:\path\to\your\negative_expression.mp4",
            'neutral': r"C:\path\to\your\neutral_expression.mp4"
        }
        
        self.captures = {}
        self.current_emotion = "neutral"
        
    def initialize_videos(self):
        """Initializes all video captures with detailed debugging."""
        print("🎬 Initializing videos with detailed logs...")
    
        for key, path in self.video_paths.items():
            print(f"\n--- Checking for '{key}' ---")
            print(f"Attempting to use path: {path}")
            
            
            if not os.path.exists(path):
                print(f"⚠️ ERROR: File does NOT exist at this path.")
                continue  
                
            
            cap = cv2.VideoCapture(path)
            
            
            if cap.isOpened():
                self.captures[key] = cap
                print(f"✅ SUCCESS: Video '{key}' loaded successfully.")
            else:
                print(f"❌ FAILED: OpenCV could not open '{key}'.")
                print("   This usually means the video file is corrupted, uses an unsupported format (codec), or there's a permissions issue.")
    
        
        if 'base' not in self.captures:
            print("\nCRITICAL ERROR: The 'base' video failed to load. The animation cannot start.")
            return False
            
        return True
    
    def play_expression_video(self, emotion):
        """Switches the current expression video if it has changed."""
        if emotion in self.captures and emotion != self.current_emotion:
            print(f"🎭 Switching to {emotion} expression")
            self.current_emotion = emotion
            return True
        return False
    
    def play_punctuation_video(self, symbol):
        """Plays a punctuation animation in a non-blocking way."""
        if symbol in self.captures:
            
            cap = self.captures[symbol]
            current_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
            ret, frame = cap.read()
            if ret:
                cv2.imshow("AI Lecture", frame)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos)
            return True
        return False
    
    def get_base_frame(self):
        """Gets the next frame from the base video, looping if necessary."""
        if 'base' in self.captures:
            ret, frame = self.captures['base'].read()
            if not ret: 
                self.captures['base'].set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.captures['base'].read()
            return ret, frame
        return False, None
    
    def release_all(self):
        """Releases all video capture resources."""
        for cap in self.captures.values():
            cap.release()


def get_user_input():
    """Gets input from the user, either as raw text or from a PDF file."""
    print("\n📥 Choose input method:")
    print("1. Enter raw text")
    print("2. Upload PDF file")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📝 Enter your raw text content (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and len(lines) > 0:
                break
            lines.append(line)
        content = "\n".join(lines)
        if len(content.strip()) < 50:
            print("❌ Please provide more content (at least 50 characters).")
            return None
        return content
    
    elif choice == "2":
        pdf_path = input("Enter PDF file path: ").strip()
        if os.path.exists(pdf_path):
            text = extract_text_from_pdf(pdf_path)
            if text and len(text.strip()) > 50:
                print(f"✅ PDF extracted successfully! ({len(text)} characters)")
                return text
            else:
                print("❌ Failed to extract meaningful text from PDF.")
                return None
        else:
            print("❌ PDF file not found at the specified path.")
            return None
    else:
        print("❌ Invalid choice. Please enter 1 or 2.")
        return None


def run_lecture_simulation():
    """Main function to run the complete lecture simulation."""
    
    
    voice_manager = VoiceManager()
    
    print("=" * 60)
    print("🎓 AI LECTURE SIMULATION SYSTEM (MISTRAL AI)")
    print("=" * 60)
    
    
    raw_content = get_user_input()
    if not raw_content:
        print("❌ No valid content provided. Exiting.")
        return
    
    
    print("\n🤖 Generating enhanced lecture script with Mistral AI...")
    print(f"📊 Input content length: {len(raw_content)} characters")
    
    enhanced_script = generate_lecture_script_with_mistral(raw_content)
    
    if not enhanced_script:
        print("❌ Failed to generate script with Mistral AI.")
        print("💡 Possible solutions:")
        print("   - Check your MISTRAL_API_KEY at the top of the script.")
        print("   - Check your internet connection.")
        print("   - The API might be busy; try again later.")
        print("   - Ensure you have sufficient API credits.")
        return
    
    print("\n📜 ENHANCED LECTURE SCRIPT:")
    print("=" * 60)
    print(enhanced_script)
    print("=" * 60)
    
    
    print("\n🔍 Analyzing script for expressions and punctuation...")
    analysis, original_script = analyze_script(enhanced_script)
    
    print(f"📊 Analysis Results:")
    print(f"   - Sentences: {len(analysis['sentences'])}")
    print(f"   - Punctuation marks: {len(analysis['punctuation'])}")
    print(f"   - Emotional range detected: {set(analysis['emotions'])}")
    
    
    video_manager = VideoManager()
    if not video_manager.initialize_videos():
        print("❌ Failed to initialize videos. Check the file paths in the VideoManager class.")
        return
    
    
    print("\n🎤 Starting CONTINUOUS voice for ENTIRE script...")
    voice_manager.speak_entire_script(original_script)
    
    
    print("\n🎬 Starting animation...")
    print("💡 Press 'q' in the video window to quit")
    
    sentence_index = 0
    char_index = 0
    animation_speed = 0.08  
    
    try:
        while voice_manager.is_speaking or sentence_index < len(analysis['sentences']):
            
            if sentence_index < len(analysis['sentences']):
                current_sentence = analysis['sentences'][sentence_index]
                current_emotion = current_sentence['emotion']
                
                
                if char_index == 0:
                    print(f"\n🎯 Sentence {sentence_index + 1}/{len(analysis['sentences'])}")
                    print(f"   Emotion: {current_emotion}")
                    print(f"   Text: {current_sentence['text'][:80]}...")
                
                
                video_manager.play_expression_video(current_emotion)
                
                
                ret, frame = video_manager.get_base_frame()
                if ret:
                    cv2.imshow("AI Lecture", frame)
                
                
                if char_index < len(current_sentence['text']):
                    current_char = current_sentence['text'][char_index]
                    if current_char in [',', '.', '?', '!']:
                        print(f"   🔹 Punctuation: '{current_char}'")
                        video_manager.play_punctuation_video(current_char)
                
                char_index += 1
                
                
                if char_index >= len(current_sentence['text']):
                    sentence_index += 1
                    char_index = 0
                    time.sleep(0.3)  
            
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                voice_manager.stop_speaking()
                break
            
            time.sleep(animation_speed)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation interrupted by user.")
    
    finally:
        
        voice_manager.stop_speaking()
        video_manager.release_all()
        cv2.destroyAllWindows()
        print("\n✅ Lecture simulation completed!")
        
        
        print("\n📈 SIMULATION SUMMARY:")
        print(f"   - Input content: {len(raw_content)} characters")
        print(f"   - Generated script: {len(enhanced_script)} characters")
        print(f"   - Sentences animated: {sentence_index}/{len(analysis['sentences'])}")
        print(f"   - Voice completed: {'Yes' if not voice_manager.is_speaking else 'No'}")


if __name__ == "__main__":
    run_lecture_simulation()

