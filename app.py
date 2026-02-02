from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
import re
from textblob import TextBlob
import google.genai as genai
import wikipedia
import random

# Using your existing keys from the project
MISTRAL_API_KEY = "YOUR API KEY" 
GEMINI_API_KEY = "YOUR API KEY" 
MISTRAL_API_URL = "YOU API KEY URL"

app = Flask(__name__)
CORS(app)

def analyze_script(script):
    """Analyzes text for sentiment/emotions for animation."""
    sentences = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    analysis = []
    for sentence in sentences:
        blob = TextBlob(sentence)
        sentiment = blob.sentiment.polarity
        emotion = "neutral"
        if sentiment > 0.3: emotion = "positive"
        elif sentiment < -0.3: emotion = "negative"
        analysis.append({'text': sentence, 'emotion': emotion})
    return analysis

@app.route('/ask', methods=['POST'])
def ask_question():
    user_question = request.json.get('question')
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": user_question}]}
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        answer_text = response.json()['choices'][0]['message']['content'].strip()
        return jsonify({"full_answer": answer_text, "analysis": analyze_script(answer_text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-lecture', methods=['POST'])
def generate_lecture():
    raw_content = request.json.get('content')
    prompt = f"Create an engaging university lecture script based on:\n\n{raw_content[:4000]}"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-medium", "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        script = response.json()['choices'][0]['message']['content'].strip()
        return jsonify({"full_answer": script, "analysis": analyze_script(script)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/solve-numerical', methods=['POST'])
def solve_numerical():
    problem_text = request.json.get('problem')
    prompt = f"Solve this problem step-by-step in plain text. No LaTeX.\n\n{problem_text}"
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        solution = "".join([p.text for p in response.candidates[0].content.parts]).strip()
        return jsonify({"solution": solution})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- INTEGRATED CODE EXPLAINER ---
@app.route('/explain-code', methods=['POST'])
def explain_code():
    data = request.json
    code = data.get('code')
    lang = data.get('language')
    prompt = f"Explain this {lang} code line-by-line for a student:\n\n{code}"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        explanation = response.json()['choices'][0]['message']['content'].strip()
        return jsonify({"explanation": explanation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- FIXED QUIZ GENERATOR ---
@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    topic = request.json.get('topic')
    num = int(request.json.get('num', 5))
    
    try:
        # Search for the most relevant page first to avoid Disambiguation errors
        search_results = wikipedia.search(topic)
        if not search_results:
            return jsonify({"error": "Topic not found on Wikipedia. Try a broader term."}), 404
        
        page_title = search_results[0]
        content = wikipedia.summary(page_title, sentences=15)
        
        # Extract keywords (6+ characters)
        words = re.findall(r'\b\w{6,}\b', content)
        keywords = list(set(words))
        random.shuffle(keywords)
        
        if len(keywords) < 2:
            return jsonify({"error": "Not enough content to generate a quiz. Try a different topic."}), 400

        quiz_data = []
        for i in range(min(num, len(keywords))):
            answer = keywords[i]
            # Find sentence containing the keyword
            sentence = next((s for s in content.split('.') if answer in s), None)
            
            if sentence:
                question = sentence.replace(answer, "_______")
                # Ensure distractors pool is safe
                distract_pool = [w for w in keywords if w.lower() != answer.lower()]
                k_val = min(3, len(distract_pool))
                
                distractors = random.sample(distract_pool, k=k_val)
                options = distractors + [answer]
                random.shuffle(options)
                
                quiz_data.append({
                    "question": question.strip() + ".",
                    "options": options,
                    "answer": answer
                })
        
        return jsonify({"quiz": quiz_data})
        
    except wikipedia.exceptions.DisambiguationError as e:
        return jsonify({"error": f"Too many results. Did you mean: {', '.join(e.options[:3])}?"}), 400
    except Exception as e:
        print(f"Quiz Error: {e}")
        return jsonify({"error": "Could not generate quiz. Check your internet connection or topic."}), 500

if __name__ == "__main__":
    app.run(debug=True)
