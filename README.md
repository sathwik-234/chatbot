# TalentScout: AI Hiring Assistant Chatbot

TalentScout is an interactive, conversational AI chatbot designed to conduct initial technical screenings for job candidates. Built with Python, Streamlit, and Google's Gemini API, it moves beyond traditional forms and offers a seamless, engaging chat experience for the entire process, from gathering candidate information to asking personalized technical questions.


## 🌟 Key Features

-   **Fully Conversational Interface**: No more forms! Candidates provide their details and answer questions within a single, continuous chat window.
-   **Dynamic Question Generation**: Leverages the Google Gemini API to generate relevant technical questions based on the candidate's specific role, tech stack, and experience level.
-   **Interactive Q&A**: The chatbot provides conversational acknowledgements and transitions after each answer, making the screening feel natural and interactive.
-   **Graceful Exit**: Candidates can type `exit` or `quit` at any point during the conversation to end the session smoothly.
-   **Session State Management**: Intelligently uses Streamlit's session state to manage the entire conversation flow, from info collection to the technical interview, completion, or early exit.
-   **Complete Chat Summary**: Upon completion, a full summary of the conversation, including the information provided and all questions and answers, is displayed.

## ⚙️ Technology Stack

-   **Language**: Python 3.8+
-   **Framework**: Streamlit
-   **AI Model**: Google Generative AI (Gemini 1.5 Flash)
-   **Dependencies**: `google-generativeai`, `python-dotenv`

## 📁 File Structure

```
.
├── hiring_assistant_chatbot.py   # Main Streamlit application script
├── requirements.txt              # Project dependencies
├── .env                          # Environment variables (API key)
└── README.md                     # This file
```

## 🤖 How It Works

The application operates as a state machine, managed by `st.session_state`. The main states are:

1.  **`collecting_info_chat`**: The initial state where the chatbot conversationally asks for the candidate's details (name, email, position, etc.). Each piece of information is stored, and the chatbot asks for the next until all fields are collected.
2.  **`interview`**: Once information is collected, the app transitions to the interview state.
    -   It makes a single API call to the Gemini model, sending the candidate's profile to generate a list of 5 personalized technical questions.
    -   It then asks these questions one by one, waiting for the user's answer in the chat.
    -   After each answer, it makes another API call to generate a brief, neutral "bridge" comment, making the flow feel interactive.
3.  **`completed`**: After the last question is answered, the state changes to `completed`, showing a success message and a full transcript of the entire conversation.
4.  **`ended`**: If the user types `exit` or `quit` at any point, the state changes to `ended`, which gracefully concludes the session and shows the conversation up to that point.

## 💬 Demo Conversation Flow

```
🤖 TalentScout: Hi there! I'm TalentScout, your AI hiring assistant. To begin, what's your full name?
👤 You: Jane Doe
🤖 TalentScout: Thanks, Jane! Could you please provide your email address?
👤 You: jane.doe@email.com
... (continues for all details) ...
🤖 TalentScout: Great, thank you! I have all your details:
               - Name: Jane Doe
               - Email: jane.doe@email.com
               ...
               We're ready to start the technical screening now. I'll generate some questions based on your profile.
... (spinner appears) ...
🤖 TalentScout: **Question 1/5 [Easy]:** What is the difference between a list and a tuple in Python?

               (Suggested time: 30 seconds)
👤 You: A list is mutable, meaning its contents can be changed, while a tuple is immutable.
🤖 TalentScout: Got it. Let's move to the next point.
🤖 TalentScout: **Question 2/5 [Medium]:** Can you explain the concept of the Virtual DOM in React?

               (Suggested time: 60 seconds)
👤 You: exit
🤖 TalentScout: Okay, ending the interview as requested. Thank you for your time.
```
