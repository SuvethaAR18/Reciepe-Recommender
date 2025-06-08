# tamil_nadu_recipe_generator.py

import streamlit as st
import pandas as pd
import pyttsx3
import speech_recognition as sr
import threading
import os
from model import RecipeChatbot

# --- CACHED RESOURCES ---
@st.cache_data
def load_data():
    return pd.read_excel("Reciepe dataset final.xlsx")

@st.cache_resource
def init_tts_engine():
    return pyttsx3.init()

@st.cache_resource
def get_chatbot():
    return RecipeChatbot()

# --- USER DATABASE ---
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN/SIGNUP PAGE ---
def login_signup_page():
    st.markdown("""
        <style>
        .main { background-color: #fff8e1; }
        .title { color: #ff6f00; font-size: 36px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>🍛 Tamil Nadu Recipe Generator</div>", unsafe_allow_html=True)
    st.subheader("👤 Login or Create Account")

    option = st.radio("Select Option", ["Login", "Sign Up"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success("✅ Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials!")
    else:
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.warning("⚠️ Username already exists")
            else:
                st.session_state.users[username] = password
                st.success("🎉 Account created! Please login.")

# --- MAIN APP ---
def main_app():
    st.set_page_config(page_title="Food Reccomedation", page_icon="🍛", layout="wide")
    df = load_data()
    engine = init_tts_engine()
    bot = get_chatbot()

    speak_lock = threading.Lock()
    speak_thread = None

    def speak(text):
        nonlocal speak_thread

        def _speak_text(t):
            with speak_lock:
                engine.stop()
                engine.say(t)
                engine.runAndWait()

        if speak_thread and speak_thread.is_alive():
            engine.stop()
            speak_thread.join()

        speak_thread = threading.Thread(target=_speak_text, args=(text,))
        speak_thread.start()

    def listen():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Please speak now")
            audio = r.listen(source)
        try:
            query = r.recognize_google(audio)
            st.success(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            st.error("😕 Sorry, I didn’t understand.")
        except sr.RequestError:
            st.error("⚠️ Could not request results.")
        return ""

    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/3/38/Tamil_Nadu_Logo.svg", width=100)
    st.sidebar.title("🍽️ Menu")
    tab = st.sidebar.radio("Navigate", ["Home", "Search", "Random", "ChatBot", "Smart Tools", "Category", "Upload Recipe", "Menu", "Logout"])

    if tab == "Home":
        st.title("🏠 Home - Featured Recipes")
        for idx, row in df.sample(3).iterrows():
            with st.container():
                st.subheader(f"🍲 {row['Recipe Name']}")
                st.write(f"*Ingredients:* {row['Ingredients'][:100]}...")
                st.write(f"*Procedure:* {row['Procedure'][:100]}...")

    elif tab == "Search":
        st.title("🔍 Search for a Dish")
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("Enter Recipe Name")
        with col2:
            if st.button("🎤 Speak"):
                search = listen()

        if search:
            matches = df[df['Recipe Name'].str.contains(search, case=False, na=False)]
            if not matches.empty:
                for idx, row in matches.iterrows():
                    st.subheader(row['Recipe Name'])
                    st.write(row['Ingredients'])
                    st.write(row['Procedure'])
                    if st.button(f"🔈 Read {row['Recipe Name']}", key=f"search_read_{idx}"):
                        speak(f"{row['Recipe Name']}. Ingredients: {row['Ingredients']}. Procedure: {row['Procedure']}")
            else:
                st.warning("No matching dish found!")

    elif tab == "ChatBot":
        st.title("🤖 Chat with Recipe Recommendation Bot")

        if "bot" not in st.session_state:
            st.session_state.bot = RecipeChatbot()

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for message in st.session_state.messages:
            st.chat_message(message["role"]).markdown(message["content"])

        user_input = st.chat_input("What would you like to cook today?")
        if user_input:
            st.chat_message("user").markdown(user_input)
            bot_response = st.session_state.bot.predict(user_input)
            st.chat_message("assistant").markdown(bot_response)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            speak(bot_response)

        st.sidebar.header("Teach me new recipes!")
        new_input = st.sidebar.text_input("New question/input:")
        new_output = st.sidebar.text_input("New recipe suggestion/output:")

        if st.sidebar.button("Learn New Recipe"):
            if new_input and new_output:
                st.session_state.bot.learn(new_input, new_output)
                st.sidebar.success("Learned new recipe successfully!")
            else:
                st.sidebar.error("Please provide both input and output!")

    elif tab == "Random":
        st.subheader("✨ Try a Random or Category-Based Recipe")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎲 Random Recipe"):
                recipe = df.sample(1).iloc[0]
                st.session_state.selected_recipe = recipe

        if 'selected_recipe' in st.session_state:
            recipe = st.session_state.selected_recipe
            st.header(f"🍽️ {recipe['Recipe Name']}")
            image_path = f"images/{recipe['Recipe Name']}.jpg"

            if os.path.exists(image_path):
                st.image(image_path, width=400)
            else:
                st.warning("📷 Image not found.")

            st.subheader("📝 Ingredients")
            st.write(recipe.get('Ingredients', 'Not available'))
            if st.button("🔈 Speak Ingredients"):
                speak(recipe.get('Ingredients', 'Not available'))

            st.subheader("👨‍🍳 Step-by-Step Procedure")
            steps = recipe.get('Procedure', '').split(". ")
            for i, step in enumerate(steps, 1):
                if step.strip():
                    st.markdown(f"*Step {i}:* {step}")
                    
            with st.expander("📌 More Details"):
                extra_info = [
                    f"Ingredients: {recipe.get('Ingredients', 'N/A')}",
                    f"Hours to Cook: {recipe.get('Hours to Cook', 'N/A')}",
                    f"Category: {recipe.get('Category', 'N/A')}",
                    f"Cuisine Type: {recipe.get('Cuisine Type', 'N/A')}"
                ]
                for info in extra_info:
                    st.markdown(f"- {info}")

    elif tab == "Smart Tools":
        st.title("🛍️ Smart Tools")
        st.subheader("🛒 Shopping List")
        if 'selected_recipe' in st.session_state:
            ingredients = st.session_state.selected_recipe.get('Ingredients', '')
            for item in [x.strip() for x in ingredients.split(",") if x.strip()]:
                st.checkbox(item)
        else:
            st.info("Select a recipe from any tab to generate a list.")

        st.subheader("📅 Meal Planner")
        if 'meal_plan' not in st.session_state:
            st.session_state.meal_plan = {day: "" for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}

        day = st.selectbox("Select Day", list(st.session_state.meal_plan.keys()))
        plan = st.text_input(f"Meal for {day}")
        if st.button("Save Plan"):
            st.session_state.meal_plan[day] = plan
            st.success(f"Saved: {day} → {plan}")

        st.subheader("📅 Weekly Meal Calendar")
        cols = st.columns(7)
        for idx, col in enumerate(cols):
            with col:
                d = list(st.session_state.meal_plan.keys())[idx]
                st.markdown(f"### {d}")
                val = st.text_input("", st.session_state.meal_plan[d], key=f"meal_{d}")
                st.session_state.meal_plan[d] = val

    elif tab == "Category":
        st.title("📂 Browse by Category")
        category = st.selectbox("Choose a Category", sorted(df['Category'].dropna().unique()), key="category_selectbox")
        if category:
            filtered = df[df['Category'].str.contains(category, case=False, na=False)]
            if not filtered.empty:
                for idx, row in filtered.iterrows():
                    with st.expander(f"🍽️ {row['Recipe Name']}"):
                        if st.button(f"📖 View {row['Recipe Name']}", key=f"view_cat_{idx}"):
                            st.session_state.selected_recipe = row

    elif tab == "Upload Recipe":
        st.title("📤 Upload Your Recipe")
        with st.form("upload_form"):
            dish = st.text_input("Recipe Name")
            ingredients = st.text_area("Ingredients (comma separated)")
            procedure = st.text_area("Cooking Procedure")
            category = st.text_input("Category")
            time_taken = st.number_input("Time Taken (mins)", min_value=1, value=30)
            serves = st.number_input("Serves", min_value=1, value=2)
            spice_level = st.selectbox("Spice Level", ["Mild", "Medium", "Spicy"])
            dietary_info = st.selectbox("Dietary Info", ["Veg", "Non-Veg", "Vegan"])
            cooking_method = st.text_input("Cooking Method")
            submitted = st.form_submit_button("Submit")

            if submitted:
                new_recipe = {
                    "Recipe Name": dish,
                    "Ingredients": ingredients,
                    "Procedure": procedure,
                    "Category": category,
                    "Time Taken (mins)": time_taken,
                    "Quantity": "",
                    "Serves": serves,
                    "Spice Level": spice_level,
                    "Dietary Info": dietary_info,
                    "Cooking Method": cooking_method,
                    "Meal Type": ""
                }
                df.loc[len(df)] = new_recipe
                df.to_excel("new creating.xlsx", index=False)
                st.success(f"✅ {dish} has been added!")

    elif tab == "Menu":
        st.title("📋 Full Menu of Recipes")
        for _, row in df.iterrows():
            st.markdown(f"- {row['Recipe Name']}")

    elif tab == "Logout":
        st.title("🔒 Logged Out Successfully")
        st.session_state.logged_in = False
        st.experimental_rerun()

# --- RUN ---
if not st.session_state.logged_in:
    login_signup_page()
else:
    main_app()
