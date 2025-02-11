from langchain_core.prompts import ChatPromptTemplate

def hint_prompt_template():
    prompt = """
    You are a technical interviewer reviewing a candidate's response. Analyze the chat history and their answer evaluation to provide an insightful hint.

    Input:
    chat_history: {chat_history}  # This includes the question and the conversation history.
    answer_evaluation: {answer_evaluation}

    Instructions:
    1. Review the chat_history to understand what has already been discussed, including the question.
    2. Analyze the answer_evaluation to identify areas where the candidate could improve.
    3. Generate a hint that:
       - Encourages deeper technical discussion.
       - Builds upon previously discussed concepts from the chat_history.
       - Helps assess multiple aspects indirectly.
       - Avoids leading the candidate directly to the answer or providing explicit hints.
       - Prompts the candidate to think critically about implications, trade-offs, or optimizations.

    Return:
    A single hint that indirectly helps evaluate areas of improvement or clarification without explicitly addressing them.

    Example:
    Input:
    chat_history: [
        "Question: Reverse a linked list",
        "I would use three pointers: prev, current, and next",
        "The solution would modify the original list in-place"
    ]
    answer_evaluation: {{
        "sub_criteria": [
            {{"Is it clear what type of linked list is being reversed?": "3"}},
            {{"Are there any specific constraints?": "4"}}
        ]
    }}

    Output:
    How would your approach need to be modified if we needed to maintain a reference to both ends of the list throughout the process?
    """

    hint_prompt=ChatPromptTemplate.from_template(template=prompt)
    return hint_prompt