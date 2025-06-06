# hiring_assistant_chatbot.py

import streamlit as st
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0

st.title("🤖 TalentScout Hiring Assistant")
st.write("Welcome! I’ll guide you through technical screening based on your tech stack.")

# Check for redirection values from form
query_params = st.experimental_get_query_params()

name = query_params.get("name", [""])[0]
email = query_params.get("email", [""])[0]
position = query_params.get("position", [""])[0]
tech_stack = query_params.get("tech_stack", [""])[0]

if name and email and position and tech_stack:
    st.write(f"👋 Hi {name}, let's begin your technical assessment for the {position} position!")

    if not st.session_state.questions:
        prompt = f"""
        You are a technical interviewer. The candidate has experience with the following tech stack: {tech_stack}.
        Generate 3-5 technical questions that assess their proficiency in each technology listed.
        Label each question with a difficulty level (easy/medium/hard).
        """

        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            content = response.text
            questions = [q.strip() for q in content.strip().split("\n") if q.strip()]
            st.session_state.questions = questions

        except Exception as e:
            st.error(f"Error generating questions: {e}")

    if st.session_state.questions:
        idx = st.session_state.question_index
        if idx < len(st.session_state.questions):
            current_question = st.session_state.questions[idx]
            st.subheader(f"Question {idx+1}:")
            st.write(current_question)

            if "easy" in current_question.lower():
                timer_duration = 30
            elif "medium" in current_question.lower():
                timer_duration = 60
            else:
                timer_duration = 90

            st.info(f"⏳ You have {timer_duration} seconds to answer.")
            time.sleep(timer_duration)

            answer = st.text_area("Your Answer")
            if st.button("Submit Answer"):
                st.session_state.conversation.append({"question": current_question, "answer": answer})
                st.session_state.question_index += 1
                st.experimental_rerun()
        else:
            st.success("🎉 You've completed the technical round. Thank you!")
else:
    st.warning("Please fill the application form first before starting the technical assessment.")

# Exit keyword detection
user_exit_input = st.text_input("Type 'exit' to end the conversation")
if user_exit_input.lower() in ["exit", "quit", "stop"]:
    st.write("👋 Thank you! The conversation has ended.")
