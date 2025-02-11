import streamlit as st
import requests
import json
import pandas as pd  # Import Pandas for table formatting

# App Title
st.set_page_config(page_title='NOHA - AI', page_icon='🤖', layout='wide')
st.title('🤖 NOHA - AI Interview Assistant')

# User Information
user_id = 4
question_type_id = 1
question_id = 13

# Initialize session state variables
if "final_score" not in st.session_state:
    st.session_state['final_score'] = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question" not in st.session_state:
    st.session_state.question = None
if "response" not in st.session_state:
    st.session_state.response = None
if "evaluation_results" not in st.session_state:
    st.session_state['evaluation_results'] = None  # Ensure None instead of "Nothing"

# Define Custom CSS Styles
st.markdown("""
    <style>
        .chat-container {
            padding: 15px;
            border-radius: 10px;
            max-height: 500px;
            overflow-y: auto;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .message-box {
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #007BFF;
            color: white;
            text-align: right;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #f0f0f0;
            color: black;
            text-align: left;
            margin-right: auto;
        }
        .start-btn-container {
            text-align: center;
            margin-bottom: 15px;
        }
        .start-btn {
            background-color: #28a745;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            width: 100%;
        }
        .start-btn:hover {
            background-color: #218838;
        }
        .score-box {
            background-color: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #007BFF;
            font-size: 24px;
            font-weight: bold;
        }
        /* Fix input field width to match messages box */
        .chat-input-container {
            width: 60%;
            max-width: 600px;  /* Ensures it doesn't stretch too much */
            margin: auto;
            padding-top: 10px;
        }
        /* Adjust Streamlit's chat input width */
        [data-testid="stChatInput"] {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Layout: Chat on Left, Final Score on Right
col1, col2 = st.columns([3, 1])

with col1:
    # Move start button above the chat history
    with st.container():
        start_button = st.button("🚀 Start Interview", key="start_interview", use_container_width=True)

    st.markdown("### 💬 Chat History")  # Chat history heading now below the button

    # Wrap chat history in a box
    with st.container():
        for message in st.session_state.messages:
            role_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(
                f"<div class='message-box {role_class}'>{message['content']}</div>",
                unsafe_allow_html=True
            )

    if start_button:
        url = "http://127.0.0.1:8000/begin_interview"
        headers = {"Content-Type": "application/json"}

        body = {
            "user_id": user_id,
            "question_type_id": question_type_id,
            "question_id": question_id,
            "question": None,
            "chat_history": st.session_state.chat_history,
            "interview_id": 0,
            "candidate_answer": None
        }

        res = requests.post(url, headers=headers, json=body)
        if res:
            response = res.json()
            final_response = response["data"]
            st.session_state['interview_id'] = final_response['interview_id']

            # Ensure greeting message appears immediately
            greeting_message = final_response['greeting']
            if greeting_message:
                st.session_state.messages.append({'role': 'assistant', 'content': greeting_message})
                st.session_state.chat_history.append({'greeting': greeting_message})
            
            st.session_state.response = response  

        st.rerun()  # Refresh UI to show greeting immediately

# Ensure chat input is always at the bottom and has fixed width
st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
candidate_answer = st.chat_input("✍️ Enter Your Answer")  # This stays at the bottom
st.markdown("</div>", unsafe_allow_html=True)

if candidate_answer:
    st.session_state.messages.append({'role': 'user', 'content': candidate_answer})
    st.session_state.chat_history[-1]['answer'] = candidate_answer

    try:
        url = "http://127.0.0.1:8000/begin_interview"
        headers = {"Content-Type": "application/json"}

        body = {
            "user_id": user_id,
            "question_type_id": question_type_id,
            "question_id": question_id,
            "chat_history": st.session_state['chat_history'],
            "interview_id": st.session_state['interview_id'],
            "question": st.session_state['question'] if st.session_state['question'] else None,
            "candidate_answer": candidate_answer
        }

        res = requests.post(url, headers=headers, json=body)
        if res:
            response = res.json()['data']
            st.session_state.response = response  

        if 'question' in response:
            final_response = response['question']
            st.session_state['question'] = final_response
            st.session_state.messages.append({'role': 'assistant', 'content': final_response})
            st.session_state.chat_history.append({'question': final_response})

        elif isinstance(response, dict):
            hint_message = f"**💡 Hint:** {response['hint']}"
            st.session_state.chat_history.append({'role': 'assistant', 'content': hint_message})
            st.session_state.messages.append({'role': 'assistant', 'content': hint_message})

            st.session_state['final_score'] = response['evaluation']['final_score']

            if 'evaluation_results' in response['evaluation']:
                evaluation_results = [
                    {"Subcriteria": k, "Weight": v[0], "Score": v[1]}
                    for k, v in response['evaluation']['evaluation_results'].items()
                ]
                st.session_state['evaluation_results'] = pd.DataFrame(evaluation_results)
            else:
                st.session_state['evaluation_results'] = None

        else:
            st.session_state.messages.append({'role': 'assistant', 'content': "⚠️ Error in generating response"})

    except Exception as ex:
        error_msg = f"❌ Error: {ex}"
        st.session_state.messages.append({'role': 'assistant', 'content': error_msg})

    st.rerun()

with col2:
    st.markdown("### 🏆 Final Score")
    st.markdown(f"<div class='score-box'>{st.session_state['final_score']}</div>", unsafe_allow_html=True)

    criteria_scores = "0"
    if st.session_state.response and "evaluation" in st.session_state.response and "criteria_score" in st.session_state.response["evaluation"]:
        criteria_scores = ', '.join(map(str, st.session_state.response["evaluation"]["criteria_score"]))

    st.markdown("### 📈 Criteria Scores")
    st.markdown(f"<div class='score-box'>{criteria_scores}</div>", unsafe_allow_html=True)

    st.markdown("### 📊 Evaluation Results")

    if (
        isinstance(st.session_state['evaluation_results'], pd.DataFrame) and
        not st.session_state['evaluation_results'].empty
    ):
        st.dataframe(st.session_state['evaluation_results'], height=220, use_container_width=True)  # Reduced height
    else:
        st.markdown("No evaluation results available.")
