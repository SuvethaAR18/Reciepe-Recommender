import os
import pickle
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier

class RecipeChatbot:
    def __init__(self, data_path="Reciepe Recommendation dataset final.xlsx", model_path="chatbot_model.pkl"):
        self.data_path = data_path
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer()
        self.model = KNeighborsClassifier(n_neighbors=3)
        self.inputs = []
        self.outputs = []

        self.load_data()

        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train()

    def load_data(self):
        df = pd.read_excel(self.data_path)
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
        print("Columns loaded:", df.columns.tolist())  # Optional debug
        df.fillna("", inplace=True)
        self.df = df

        # Combine features for better matching
        self.inputs = (
            df['Ingredients'].astype(str) + " " +
            df['CuisineType'].astype(str) + " " +
            df['HourstoCook'].astype(str) + " hours"
        ).tolist()

        self.outputs = [self.format_response(row) for _, row in df.iterrows()]

    def format_response(self, row):
        return (
            f"🍽️ **Recipe Name**: {row['RecipeName']}\n"
            f"🕒 **Hours to Cook**: {row['HourstoCook']}\n"
            f"🔥 **Method**: {row['CookingMethod']}\n"
            f"📂 **Category**: {row['Category']}\n"
            f"🌍 **Cuisine**: {row['CuisineType']}\n"
            f"📜 **Procedure**:\n{row['Procedure']}"
        )

    def train(self):
        if not self.inputs:
            return
        X = self.vectorizer.fit_transform(self.inputs)
        self.model.fit(X, self.outputs)
        self.save_model()

    def save_model(self):
        with open(self.model_path, "wb") as f:
            pickle.dump((self.vectorizer, self.model, self.inputs, self.outputs), f)

    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.vectorizer, self.model, self.inputs, self.outputs = pickle.load(f)

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)  # Keep letters and numbers
        return text

    def predict(self, user_input):
        if not self.inputs:
            return "I'm still learning. Please teach me some recipes!"

        cleaned_input = self.clean_text(user_input)
        if not cleaned_input.strip():
            return "Please enter some ingredients, cuisine type, or time."

        query = ' '.join(cleaned_input.split())
        X = self.vectorizer.transform([query])

        distances, indices = self.model.kneighbors(X, n_neighbors=1)

        # Threshold distance: adjust for better/worse matching
        if distances[0][0] > 1.0:
            return "Sorry, I couldn't find a matching recipe for your request."

        return self.model.predict(X)[0]

# Example usage
if __name__ == "__main__":
    chatbot = RecipeChatbot()
    while True:
        user_input = input("\nTell me what ingredients, cuisine or time you want (or type 'exit' to quit):\n> ")
        if user_input.lower() == "exit":
            print("Goodbye! Happy cooking! 🍳")
            break
        response = chatbot.predict(user_input)
        print("\nHere's a recipe you might like:\n")
        print(response)
