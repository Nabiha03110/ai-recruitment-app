from langchain_core.prompts import ChatPromptTemplate


def make_prompt_from_template():
    hint_generator_prompt_str = """
       You are an expert interviewer specialized in generating hints for answers to questions.
        Given the chat_history and evaluation_results, you must generate a hint for the most recent question asked in chat_history based on the recent answer, whose evaluation results are given.
        The hint must be directed towards only one criterion (consisting of 3 sub-criteria) and guide the candidate toward the optimal solution by suggesting a specific approach to improve or solve it.
        question : {question}
        chat_history: {chat_history}
        evaluation_results: {evaluation_results}

        The hint must be concise, focused, and actionable, specifying the best approach for the optimal solution.
        Do not mention the perks of using it.

        Example:
        You should try implementing the solution using an adjacency list approach to optimize the detection process for both directed and undirected graphs.

        Response:
    """
    
    hint_generator_prompt = ChatPromptTemplate.from_template(template=hint_generator_prompt_str)
    
    return hint_generator_prompt