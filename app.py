from flask import Flask, render_template, request, jsonify
import pickle
import re
import numpy as np
from collections import Counter


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# LOAD TRAINED MODEL
# ==========================================

print("Loading spam detection model...")

with open(
    "model/spam_model.pkl",
    "rb"
) as file:

    model_data = pickle.load(file)


vocabulary = model_data["vocabulary"]

idf = model_data["idf"]

log_spam_prior = model_data[
    "log_spam_prior"
]

log_ham_prior = model_data[
    "log_ham_prior"
]

log_spam_word_probability = model_data[
    "log_spam_word_probability"
]

log_ham_word_probability = model_data[
    "log_ham_word_probability"
]


print("Model loaded successfully!")


# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text):

    text = str(text).lower()

    # Replace URLs
    text = re.sub(
        r"http\S+|www\S+|https\S+",
        " URL ",
        text
    )

    # Keep letters, numbers and spaces
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ==========================================
# CREATE TF-IDF FEATURES
# ==========================================

def create_features(message):

    message = clean_text(message)

    features = np.zeros(
        len(vocabulary),
        dtype=np.float32
    )

    words = message.split()

    word_frequency = Counter(words)

    total_words = len(words)

    if total_words == 0:
        return features


    for word, count in word_frequency.items():

        if word in vocabulary:

            index = vocabulary[word]

            tf = count / total_words

            features[index] = (
                tf * idf[word]
            )


    return features


# ==========================================
# SPAM INDICATOR ANALYSIS
# ==========================================

def analyze_indicators(message):

    indicators = []

    lower_message = message.lower()


    # URL detection
    if re.search(
        r"http\S+|www\S+|https\S+",
        message,
        re.IGNORECASE
    ):

        indicators.append(
            "Contains external links"
        )


    # Money / financial language
    money_words = [
        "money",
        "cash",
        "prize",
        "reward",
        "won",
        "winner",
        "free",
        "bonus",
        "offer",
        "credit",
        "loan",
        "profit"
    ]

    if any(
        word in lower_message
        for word in money_words
    ):

        indicators.append(
            "Promotional or financial language"
        )


    # Urgency
    urgency_words = [
        "urgent",
        "immediately",
        "act now",
        "limited time",
        "hurry",
        "today",
        "expires",
        "claim now"
    ]

    if any(
        word in lower_message
        for word in urgency_words
    ):

        indicators.append(
            "Urgency-based language"
        )


    # Prize / winning language
    prize_words = [
        "congratulations",
        "you have won",
        "selected",
        "lucky winner",
        "claim your prize"
    ]

    if any(
        word in lower_message
        for word in prize_words
    ):

        indicators.append(
            "Prize or winning claim"
        )


    # Phone number
    if re.search(
        r"\+?\d[\d\s\-]{7,}\d",
        message
    ):

        indicators.append(
            "Contains a phone number"
        )


    # Excessive capital letters
    letters = [
        char
        for char in message
        if char.isalpha()
    ]

    if len(letters) > 10:

        uppercase_count = sum(
            char.isupper()
            for char in message
        )

        uppercase_ratio = (
            uppercase_count
            /
            len(letters)
        )

        if uppercase_ratio > 0.45:

            indicators.append(
                "Unusually high use of capital letters"
            )


    # Exclamation marks
    if message.count("!") >= 3:

        indicators.append(
            "Excessive exclamation marks"
        )


    # Default
    if not indicators:

        indicators.append(
            "No obvious spam indicators detected"
        )


    return indicators


# ==========================================
# PREDICTION
# ==========================================

def predict_message(message):

    features = create_features(
        message
    )


    spam_score = (
        np.dot(
            features,
            log_spam_word_probability
        )
        +
        log_spam_prior
    )


    ham_score = (
        np.dot(
            features,
            log_ham_word_probability
        )
        +
        log_ham_prior
    )


    # Convert scores into probabilities

    max_score = max(
        spam_score,
        ham_score
    )


    spam_exp = np.exp(
        spam_score - max_score
    )

    ham_exp = np.exp(
        ham_score - max_score
    )


    total = (
        spam_exp
        +
        ham_exp
    )


    spam_probability = (
        spam_exp
        /
        total
    )


    ham_probability = (
        ham_exp
        /
        total
    )


    if spam_probability > ham_probability:

        prediction = "SPAM"

        confidence = (
            spam_probability * 100
        )

    else:

        prediction = "NOT SPAM"

        confidence = (
            ham_probability * 100
        )


    return (
        prediction,
        float(confidence)
    )


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# PREDICTION API
# ==========================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "No message received."
        }), 400


    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({
            "error":
                "Please enter an email message."
        }), 400


    # Run prediction

    prediction, confidence = (
        predict_message(message)
    )


    # Analyze message characteristics

    indicators = analyze_indicators(
        message
    )


    # Calculate word count

    cleaned_message = clean_text(
        message
    )

    word_count = len(
        cleaned_message.split()
    )


    return jsonify({

        "prediction":
            prediction,

        "confidence":
            round(
                float(confidence),
                2
            ),

        "message_length":
            int(len(message)),

        "word_count":
            int(word_count),

        "indicators":
            indicators

    })


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "MAILGUARD SPAM DETECTION"
    )

    print(
        "=========================================="
    )

    print(
        "Server starting..."
    )

    app.run(
        debug=True
    )