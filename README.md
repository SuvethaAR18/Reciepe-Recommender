# Reciepe-Recommender
A voice-enabled, AI-powered recipe discovery platform to preserve and promote traditional Tamil cuisine. Built with Streamlit, the application integrates voice recognition, text-to-speech, and a K-Nearest Neighbors (KNN) based chatbot for intelligent and interactive culinary exploration.

# Features
1) Voice-Based Recipe Search: Search for recipes using voice commands in English or Tamil.
2) Intelligent KNN Chatbot: Get recipe recommendations based on ingredients, preferences, and queries.
3) Text-to-Speech: Listen to step-by-step cooking instructions — ideal for hands-free cooking.
4) Streamlit Interface: Clean and interactive web UI with real-time response.
5) Multi-language Support: Supports Tamil and English for input and output.
6) Ingredient-Based Recipe Suggestions: Discover what you can cook using available ingredients.
7) Smart Meal Planner: Generate meal plans and shopping lists with ease.
8) Cultural Insights & User Contributions: Learn about traditional dishes and share your own recipes.

# Objective
To preserve the culinary heritage of Tamil Nadu through an accessible, intelligent platform. The app uses voice interaction, machine learning, and multilingual support to help users explore, learn, and share recipes while promoting cultural inclusivity and ease of use.

# Technologies Used
Component	Technology
Frontend/UI	Streamlit (Python)
Machine Learning	K-Nearest Neighbors (KNN)
Voice Recognition	SpeechRecognition Library
Text-to-Speech	pyttsx3 / gTTS
Dataset Handling	Pandas / CSV
Language Support	Googletrans (for Tamil-English)
Image Rendering	PIL / OpenCV

# How to Run the Project
Step 1: Clone the repository

Step 2: 
bash
Copy code
git clone 
cd reciepechatbot_app
Install dependencies

Step 3:
bash
Copy code
pip install -r requirements.txt
Run the app

Step 4:
bash
Copy code
streamlit run app.py
