# 🛡️ MailGuard — AI Spam Mail Detection

MailGuard is an AI-powered spam mail detection web application that analyzes email messages and determines whether they are **SPAM** or **NOT SPAM**.

The project combines a machine learning model with a Flask-based web interface to provide fast, understandable, and interactive spam detection.

## ✨ Features

- 📧 Spam and legitimate mail classification
- 🧠 TF-IDF based text feature extraction
- 🤖 Multinomial Naive Bayes classification
- 📊 Prediction confidence score
- 🔍 Spam detection indicators
- 📏 Message length and word count analysis
- 🕘 Recent scan history
- 💾 Local browser-based scan history
- 🌐 Interactive Flask web interface
- ⚡ Real-time message analysis
- 📱 Responsive user interface
- 🔄 Analyze multiple messages easily

## 🧠 Machine Learning Pipeline

```text
Email Message
     ↓
Text Cleaning
     ↓
TF-IDF Feature Extraction
     ↓
Multinomial Naive Bayes
     ↓
Spam / Not Spam
     ↓
Confidence & Detection Insights