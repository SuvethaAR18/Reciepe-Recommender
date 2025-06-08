import streamlit as st
from model import RecipeChatbot

st.set_page_config(page_title="Recipe Recommendation Bot", page_icon="🍽️")
st.title("🍽️ Recipe Recommendation Chatbot")

# Load the chatbot
bot = RecipeChatbot()

# Chat History
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# User input
user_input = st.chat_input("What would you like to cook today?")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)

    # Predict bot response
    bot_response = bot.predict(user_input)
    st.chat_message("assistant").markdown(bot_response)

    # Store in session
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Allow learning new recipes
st.sidebar.header("Teach me new recipes!")
new_input = st.sidebar.text_input("New question/input:")
new_output = st.sidebar.text_input("New recipe suggestion/output:")

if st.sidebar.button("Learn New Recipe"):
    if new_input and new_output:
        bot.learn(new_input, new_output)
        st.sidebar.success("Learned new recipe successfully!")
    else:
        st.sidebar.error("Please provide both input and output!")
