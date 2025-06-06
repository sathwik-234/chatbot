# hiring_assistant_chatbot.py

import streamlit as st
import os
import time
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-flash-latest"
model = genai.GenerativeModel(MODEL_NAME)

INFO_FIELDS_ORDERED = [
    {"key": "name", "prompt": "Hi there! I'm TalentScout, your AI hiring assistant. To begin, what's your full name?", "validation": None},
    {"key": "email", "prompt": "Thanks, {name}! Could you please provide your email address?", "validation": "email"},
    {"key": "position", "prompt": "Got it. And what position are you applying for?"},
    {"key": "tech_stack", "prompt": "Great. What's your primary tech stack? Please list the key technologies, separated by commas (e.g., Python, React, Docker, SQL)."},
    {"key": "phone", "prompt": "What's a good phone number to reach you at?", "validation": "phone"},
    {"key": "years_of_experience", "prompt": "How many years of relevant professional experience do you have?", "validation": "number"},
    {"key": "location", "prompt": "And finally, what's your current location (e.g., City, Country)?"}
]

# --- Helper Functions ---
def add_timer_hint_to_question(question_text, question_number_for_display, total_questions):
    difficulty_marker = ""
    cleaned_question_text = question_text
    if question_text.startswith("[") and "]" in question_text:
        potential_marker = question_text.split("]", 1)[0] + "]"
        if any(diff_level in potential_marker.lower() for diff_level in ["[easy]", "[medium]", "[hard]"]):
            difficulty_marker = potential_marker
            cleaned_question_text = question_text.replace(difficulty_marker, "").strip()

    if not difficulty_marker:
        if "[easy]" in question_text.lower(): difficulty_marker = "[Easy]"
        elif "[medium]" in question_text.lower(): difficulty_marker = "[Medium]"
        elif "[hard]" in question_text.lower(): difficulty_marker = "[Hard]"
        # If still no marker, cleaned_question_text remains as is

    if "[easy]" in difficulty_marker.lower(): timer_suggestion = 300
    elif "[medium]" in difficulty_marker.lower(): timer_suggestion = 600
    elif "[hard]" in difficulty_marker.lower(): timer_suggestion = 900
    else: timer_suggestion = 600

    return f"**Question {question_number_for_display}/{total_questions} {difficulty_marker}:** {cleaned_question_text.strip()}\n\n*(Suggested time: {timer_suggestion} seconds)*"


def generate_ai_bridge(candidate_info, question_asked, user_answer, current_q_idx_0_based, total_questions):
    is_last_question = (current_q_idx_0_based == total_questions - 1)
    transition_phrase = "Let's move to the next point."
    if is_last_question:
        transition_phrase = "That covers the set of questions I had for this section. Thank you!"

    prompt_text = f"""
    You are TalentScout, a friendly and professional AI technical interviewer.
    The candidate is {candidate_info.get('name', 'the candidate')}.
    They were asked: "{question_asked}"
    They answered: "{user_answer}"

    Briefly acknowledge their answer in a conversational, encouraging, and neutral way (1 short sentence).
    Do not evaluate the correctness of the answer.
    Then, add the following phrase: "{transition_phrase}"

    Example acknowledgement: "Thanks for sharing that."
    Combine your acknowledgement with the provided transition phrase.
    If it's the last question, your response should feel conclusive.
    """
    try:
        with st.spinner("🤖 Thinking..."):
            response = model.generate_content(prompt_text)
            return response.text.strip()
    except Exception as e:
        st.warning(f"Minor issue generating AI bridge: {e}. Moving on.")
        return f"Okay. {transition_phrase}"

def initialize_session_state():
    if 'app_state' not in st.session_state:
        st.session_state.app_state = 'collecting_info_chat'
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    if 'collected_info' not in st.session_state:
        st.session_state.collected_info = {}
    if 'info_collection_field_index' not in st.session_state:
        st.session_state.info_collection_field_index = 0
    if 'initial_questions' not in st.session_state:
        st.session_state.initial_questions = []
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

initialize_session_state()

# ====================================
st.title("🤖 TalentScout Hiring Assistant")


# INFO COLLECTION
if st.session_state.app_state == 'collecting_info_chat':
    current_field_idx = st.session_state.info_collection_field_index

    if not st.session_state.chat_history:
        first_field_data = INFO_FIELDS_ORDERED[0]
        st.session_state.chat_history.append({"role": "assistant", "content": first_field_data["prompt"]})
        st.session_state.info_collection_field_index = 0
        st.session_state.collected_info = {}
        st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    if current_field_idx < len(INFO_FIELDS_ORDERED):
        field_to_collect = INFO_FIELDS_ORDERED[current_field_idx]
        prompt_key_for_input = field_to_collect['key'].replace('_', ' ')

        if user_response := st.chat_input(f"Your {prompt_key_for_input}... (or type 'exit' to quit)", key=f"collect_info_{field_to_collect['key']}"):
            if user_response.lower() in ["exit", "quit", "stop"]:
                st.session_state.chat_history.append({"role": "user", "content": user_response})
                st.session_state.chat_history.append({"role": "assistant", "content": "Okay, ending the session as requested. Goodbye!"})
                st.session_state.app_state = 'ended'
                st.rerun()
            else:
                st.session_state.chat_history.append({"role": "user", "content": user_response})
                valid_input = True
                processed_response = user_response

                if field_to_collect.get("validation") == "number":
                    try:
                        num_val = int(user_response)
                        if not (0 <= num_val <= 70):
                            st.session_state.chat_history.append({"role": "assistant", "content": "That doesn't seem like a valid number of years. Please provide a number (e.g., 5)."})
                            valid_input = False
                        else:
                            processed_response = num_val
                    except ValueError:
                        st.session_state.chat_history.append({"role": "assistant", "content": "Please enter the number of years as a numeric value (e.g., '5')."})
                        valid_input = False
                elif field_to_collect.get("validation") == "email":
                    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                    if not re.match(email_regex, user_response):
                        st.session_state.chat_history.append({"role": "assistant", "content": "That doesn't look like a valid email address. Please try again."})
                        valid_input = False
                    else:
                        processed_response = user_response.strip().lower()
                elif field_to_collect.get("validation") == "phone":
                    phone_regex = r"^\+?[1-9]\d{1,14}$"
                    if not re.match(phone_regex, user_response):
                        st.session_state.chat_history.append({"role": "assistant", "content": "That doesn't look like a valid phone number. Please try again."})
                        valid_input = False
                    else:
                        processed_response = user_response.strip()
                else:
                    processed_response = user_response.strip()
                
                if valid_input:
                    st.session_state.collected_info[field_to_collect['key']] = processed_response
                    next_field_idx = current_field_idx + 1
                    st.session_state.info_collection_field_index = next_field_idx

                    if next_field_idx < len(INFO_FIELDS_ORDERED):
                        next_field_data = INFO_FIELDS_ORDERED[next_field_idx]
                        prompt_text = next_field_data["prompt"]
                        if "{name}" in prompt_text and "name" in st.session_state.collected_info:
                            prompt_text = prompt_text.format(name=st.session_state.collected_info["name"].split()[0])
                        st.session_state.chat_history.append({"role": "assistant", "content": prompt_text})
                    else:
                        st.session_state.candidate_info = st.session_state.collected_info.copy()
                        details_summary = "\n".join([f"- **{key.replace('_', ' ').title()}:** {value}" for key, value in st.session_state.candidate_info.items()])
                        ai_summary_message = f"Great, thank you! I have all your details:\n{details_summary}\n\nWe're ready to start the technical screening now. I'll generate some questions based on your profile."
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_summary_message})
                        st.session_state.app_state = 'interview'
                        st.session_state.initial_questions = []
                        st.session_state.question_index = 0
                st.rerun()

# TECHNICAL INTERVIEW

elif st.session_state.app_state == 'interview':
    info = st.session_state.candidate_info
    
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    if not st.session_state.initial_questions:
        if not info:
            st.error("Candidate information is missing. Please restart.")
            if st.button("Restart"):
                for key_to_del in list(st.session_state.keys()): del st.session_state[key_to_del]
                st.rerun()
            st.stop()

        prompt_q_gen = f"""
        You are an expert technical interviewer.
        The candidate is applying for a {info.get('position', 'technical')} role and has experience with: {info.get('tech_stack', 'various technologies')}.
        The candidate has {info.get('years_of_experience', 'some')} years of experience.
        Generate a list of exactly 3 technical questions.
        Prefix each question with its difficulty level: [Easy], [Medium], or [Hard].
        Output only the questions, each on a new line.
        """
        try:
            with st.spinner("Generating personalized technical questions..."):
                time.sleep(1)
                response = model.generate_content(prompt_q_gen)
                content = response.text
                questions = [q.strip() for q in content.strip().split("\n") if q.strip() and ("[" in q and "]" in q)]

                if not questions or len(questions) < 1:
                    st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I had trouble generating the questions. Let's try that again in a moment."})
                    if st.button("Try generating questions again"):
                         st.session_state.initial_questions = []
                         st.rerun()
                    st.stop()
                
                st.session_state.initial_questions = questions
                first_q_text = add_timer_hint_to_question(
                    st.session_state.initial_questions[0], 1, len(st.session_state.initial_questions)
                )
                st.session_state.chat_history.append({"role": "assistant", "content": first_q_text})
                st.session_state.question_index = 0
                st.rerun()
        except Exception as e:
            st.error(f"An error occurred while generating questions: {e}")
            st.session_state.chat_history.append({"role": "assistant", "content": f"An error occurred: {e}. Please try starting a new session if this persists."})
            if st.button("Start New Session"):
                for key_to_del in list(st.session_state.keys()): del st.session_state[key_to_del]
                st.rerun()
            st.stop()

    if st.session_state.initial_questions and \
       st.session_state.question_index >= len(st.session_state.initial_questions) and \
       st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant" and \
       "That covers the set of questions" in st.session_state.chat_history[-1]["content"]:
        st.session_state.app_state = 'completed'
        time.sleep(1)
        st.rerun()

    if st.session_state.app_state == 'interview' and st.session_state.initial_questions and \
       st.session_state.question_index < len(st.session_state.initial_questions):
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
            if user_response := st.chat_input("Your answer... (or type 'exit' to quit)", key=f"answer_q_{st.session_state.question_index}"):
                if user_response.lower() in ["exit", "quit", "stop"]:
                    st.session_state.chat_history.append({"role": "user", "content": user_response})
                    st.session_state.chat_history.append({"role": "assistant", "content": "Okay, ending the interview as requested. Thank you for your time."})
                    st.session_state.app_state = 'ended'
                    st.rerun()
                else:
                    st.session_state.chat_history.append({"role": "user", "content": user_response})
                    current_q_text_raw = st.session_state.initial_questions[st.session_state.question_index]

                    ai_bridge_text = generate_ai_bridge(
                        info, current_q_text_raw, user_response,
                        st.session_state.question_index, len(st.session_state.initial_questions)
                    )
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_bridge_text})
                    st.session_state.question_index += 1

                    if st.session_state.question_index < len(st.session_state.initial_questions):
                        next_q_text_formatted = add_timer_hint_to_question(
                            st.session_state.initial_questions[st.session_state.question_index],
                            st.session_state.question_index + 1, len(st.session_state.initial_questions)
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": next_q_text_formatted})
                    st.rerun()

# VIEW 3: COMPLETION

elif st.session_state.app_state == 'completed':
    st.success("🎉 You've completed the technical screening. Thank you!")
    st.balloons()
    st.write("### Full Conversation Summary:")
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
        if message != st.session_state.chat_history[-1]:
             st.divider()
    
    st.write("---")
    st.write("### Structured Candidate Information:")
    final_info = st.session_state.get('candidate_info', {})
    if final_info:
        for key, value in final_info.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    else:
        st.write("No structured candidate information was finalized (session may have ended early).")

    if st.button("Start New Session"):
        for key_to_del in list(st.session_state.keys()):
            del st.session_state[key_to_del]
        st.rerun()

# VIEW 4: CONVERSATION ENDED MANUALLY
elif st.session_state.app_state == 'ended':
    st.info("👋 The session was ended. Thank you for your time!")
    
    user_name = None
    # Try to get name from finalized candidate_info first
    if 'candidate_info' in st.session_state and st.session_state.candidate_info and st.session_state.candidate_info.get("name"):
        user_name = st.session_state.candidate_info["name"]
    # Fallback to collected_info if candidate_info isn't populated (e.g., exited during info collection)
    elif 'collected_info' in st.session_state and st.session_state.collected_info and st.session_state.collected_info.get("name"):
        user_name = st.session_state.collected_info["name"]
    
    if user_name:
        st.write(f"Goodbye, {user_name.split()[0]}!") # Use first name
    else:
        st.write("Goodbye!") # Generic if no name was captured
    
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.write("### Conversation Log (up to exit):")
        for message in st.session_state.chat_history:
            with st.chat_message(name=message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
            if message != st.session_state.chat_history[-1]:
                 st.divider()

    if st.button("Start New Session"):
        for key_to_del in list(st.session_state.keys()):
            del st.session_state[key_to_del]
        st.rerun()