import streamlit as st
import requests
import json

st.title('NOHA - AI')

user_id = 4
question_type_id = 1
question_id = 13

if "final_score" not in st.session_state:
    st.session_state['final_score'] = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "question" not in st.session_state:
    st.session_state.question = None

chat_btn = st.button("Start Interview")

if chat_btn:
    url = "http://127.0.0.1:8000/begin_interview"
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "user_id": user_id,
        "question_type_id": question_type_id,
        "question_id": question_id,
        "question": None,
        "chat_history": st.session_state.chat_history,
        "interview_id": 0,
        "candidate_answer": None
    }

    res = requests.post(url, headers=headers, data=json.dumps(body))
    if res:
        response = res.json()
        final_response = response["data"]
        st.session_state['interview_id'] = final_response['interview_id']
        st.session_state.messages.append({'role': 'assistant', 'content': final_response['greeting']})
        st.session_state.chat_history.append({'greeting': final_response['greeting']})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

candidate_answer = st.chat_input("Enter Your Answer")

if candidate_answer:
        
    if candidate_answer != None:
        with st.chat_message("user"):
            st.markdown(candidate_answer)

        st.session_state.messages.append({'role': 'user', 'content': candidate_answer})
        st.session_state.chat_history[-1]['answer'] = candidate_answer

    try:
        url = "http://127.0.0.1:8000/begin_interview"
        headers = {
            "Content-Type": "application/json"
        }

        if st.session_state['question'] == None:
            body = {
                "user_id": 4,
                "question_type_id": 1,
                "question_id": 13,
                "chat_history": st.session_state['chat_history'],
                "interview_id": st.session_state['interview_id'],
                "candidate_answer": candidate_answer
            }
        else:
            body = {
                "user_id": 4,
                "question_type_id": 1,
                "question_id": 13,
                "chat_history": st.session_state['chat_history'],
                "interview_id": st.session_state['interview_id'],
                "question": st.session_state['question'],
                "candidate_answer": candidate_answer
            }


        res = requests.post(url, headers=headers, json=body)
        if res:
            response = res.json()
            response = response['data']

        if 'question' in response.keys():
            final_response = response['question']
            st.session_state['question'] = response['question']

            with st.chat_message("assistant"):
                st.markdown(final_response)

            st.session_state.messages.append({'role': 'assistant', 'content': final_response})
            st.session_state.chat_history.append({'question': final_response})

        elif type(response) == dict:
            formatted_response = "**Evaluation Results:**\n\n"
            for i, result in enumerate(response['evaluation']['evaluation_results'], 1):
                formatted_response += f"{result}: {response['evaluation']['evaluation_results'][result][0]} , {response['evaluation']['evaluation_results'][result][1]}\n\n"

            formatted_response += f"**Criteria Scores:**\n\n{response['evaluation']['criteria_score']}\n\n"
            formatted_response += f"**Final Score:**\n\n{response['evaluation']['final_score']}\n\n"
            formatted_response += f"**Hint:**\n\n{response['hint']}"

            st.session_state.chat_history.append({f"{response['hint_type']}": f"{response['hint']}"})

            with st.chat_message("assistant"):
                st.markdown(formatted_response)

            st.session_state.messages.append({'role': 'assistant', 'content': formatted_response})

        else:
            final_response = "Error in generating response"
            with st.chat_message("assistant"):
                st.markdown(final_response)

            st.session_state.messages.append({'role': 'assistant', 'content': final_response})

    except Exception as ex:
        final_response = f"Error in generating response: {ex}"
        with st.chat_message("assistant"):
            st.markdown(final_response)

        st.session_state.messages.append({'role': 'assistant', 'content': final_response})