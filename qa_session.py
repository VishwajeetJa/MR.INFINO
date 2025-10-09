from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize a Flask application
app = Flask(__name__)
# Enable CORS
CORS(app) 

# --- Your Knowledge Base ---
qa_database = {
    "difference ai ml dl": """
    Artificial Intelligence is the broad field. Machine Learning is a subset of AI that learns from data. Deep Learning is a subset of Machine Learning using complex neural networks.
    """,
    "types of machine learning": """
    The three main types are Supervised, Unsupervised, and Reinforcement Learning.
    """,
    "neural network": """
    A Neural Network is a computational model inspired by the human brain, consisting of interconnected nodes, or neurons, organized in layers.
    """,
    "neuron": """
    A neuron is the basic processing unit in a Neural Network. It receives inputs, processes them, and passes an output signal to other neurons.
    """,
    "cnn": """
    A Convolutional Neural Network, or CNN, is a type of deep neural network specialized for processing visual data like images.
    """,
    "rnn": """
    A Recurrent Neural Network, or RNN, is a type of neural network designed for sequential data, like text or time-series data, using an internal memory loop.
    """,
    "train": """
    Training is the process of teaching a network by showing it data. It involves making a prediction, calculating the error, and adjusting the network's internal weights to reduce that error.
    """,
    "overfitting": """
    Overfitting happens when a model learns the training data too well, including its noise. It performs poorly on new, unseen data because it can't generalize.
    """
}

# --- API Endpoint ---
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    user_question = data.get("question", "").lower()

    # Find the text answer from your database
    text_answer = "Sorry, I don't have a direct answer for that. Please try asking in a different way."
    for keyword, answer in qa_database.items():
        if keyword in user_question:
            text_answer = answer.strip()
            break
            
    # Return the simple text answer in a JSON object
    return jsonify({"answer": text_answer})

# --- Start the Application ---
if __name__ == "__main__":
    app.run(debug=True)