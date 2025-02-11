import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# App Title
st.set_page_config(page_title='Bar Riser', page_icon='🤖', layout='wide')
st.title('🤖 Bar Riser - AI Interview Assistant')

# User Information
user_id = 4
question_type_id = 1
question_id = 13

# Initialize session state variables
if "final_score" not in st.session_state:
    st.session_state['final_score'] = 0
if "final_score_history" not in st.session_state:
    st.session_state['final_score_history'] = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question" not in st.session_state:
    st.session_state.question = None
if "response" not in st.session_state:
    st.session_state.response = None
if "evaluation_results" not in st.session_state:
    st.session_state['evaluation_results'] = None
if "criteria_score_history" not in st.session_state:
    st.session_state['criteria_score_history'] = []

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
            max-width: 75%;
            font-size: 18px;
            font-weight: bold;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #40dec7;
            color: black;
            text-align: left;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #d59253;
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
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            width: 100%;
            font-size: 48px;
        }
        .start-btn:hover {
            background-color: #218838;
        }
        .score-box {
            background-color: #e8f4f8;
            padding: 8px;
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

# Layout: Chat on Left, Final Score & Criteria Score on Right
col1, col2 = st.columns([3, 1])

with col1:
    start_button = st.button("🚀 Start Interview", key="start_interview", use_container_width=True)
    st.markdown("### 💬 Chat History")

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
            response = res.json()["data"]
            st.session_state['interview_id'] = response['interview_id']
            greeting_message = response.get('greeting', "")
            if greeting_message:
                st.session_state.messages.append({'role': 'assistant', 'content': greeting_message})
                st.session_state.chat_history.append({'greeting': greeting_message})
        st.rerun()

st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
candidate_answer = st.chat_input("✍️ Enter Your Answer")
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
            "question": st.session_state.get('question', None),
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
            st.session_state['final_score_history'].append(st.session_state['final_score'])

            # Store criteria scores (always 7)
            if 'criteria_score' in response['evaluation']:
                st.session_state['criteria_score_history'].append(response['evaluation']['criteria_score'])

            if 'evaluation_results' in response['evaluation']:
                evaluation_results = [
                    {"Subcriteria": k, "Weight": v[0], "Score": v[1]}
                    for k, v in response['evaluation']['evaluation_results'].items()
                ]
                st.session_state['evaluation_results'] = pd.DataFrame(evaluation_results)

        else:
            st.session_state.messages.append({'role': 'assistant', 'content': "⚠️ Error in generating response"})

    except Exception as ex:
        error_msg = f"❌ Error: {ex}"
        st.session_state.messages.append({'role': 'assistant', 'content': error_msg})
    
    st.rerun()

with col2:
    st.markdown("### 🏆 Final Score Trend")
    if st.session_state['final_score_history']:
        fig, ax = plt.subplots()
        ax.plot(st.session_state['final_score_history'], marker='o', linestyle='-', color='b')
        ax.set_title("Final Score Over Time")
        ax.set_xlabel("Attempts")
        ax.set_ylabel("Score")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.markdown("<div class='score-box'>Final Score Not Available.</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Criteria Score Trend")
    if st.session_state['criteria_score_history']:
        criteria_df = pd.DataFrame(st.session_state['criteria_score_history'])
        criteria_df.columns = [f"Criteria {i+1}" for i in range(7)]
        criteria_df["Attempt"] = range(1, len(criteria_df) + 1)

        fig2, ax2 = plt.subplots()
        for col in criteria_df.columns[:-1]:  # Exclude "Attempt"
            ax2.plot(criteria_df["Attempt"], criteria_df[col], marker='o', linestyle='-')

        ax2.set_title("Criteria Score Over Attempts")
        ax2.set_xlabel("Attempts")
        ax2.set_ylabel("Score")
        ax2.legend(criteria_df.columns[:-1], loc="upper right")
        ax2.grid(True)
        st.pyplot(fig2)
    else:
        st.markdown("<div class='score-box'>No criteria score data available.</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📈 Evaluation Results")
    if isinstance(st.session_state['evaluation_results'], pd.DataFrame) and not st.session_state['evaluation_results'].empty:
        st.dataframe(st.session_state['evaluation_results'], height=220, use_container_width=True)
    else:
        st.markdown("<div class='score-box'>No evaluation results available.</div>", unsafe_allow_html=True)
