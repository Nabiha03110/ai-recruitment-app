from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate

def make_prompt_from_template():
    subcriteria_prompt_template = """
        You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
        The response to every such question is evaluated based on the following set of "criteria" posed as questions:

        question: {question}
        criteria: {criteria}
    
        Create a Python dictionary structure that represents a list of criteria. Each criterion should have the following attributes:
        - A string attribute called "name" representing the name of the criterion.
        - A string attribute called "id" representing the id of the criterion.
        - A list attribute called "subcriteria," which contains most significant k dictionaries. Each subcriterion should have:
        - A string attribute called "name" representing the name of the subcriterion.
        - A float attribute called "weight" representing the weight of the subcriterion, also weight for each criterion must accumulately equal to 10.

        Subcriteria Generation Guidlines:
        - Must not recommend any data structure or algorithm instead it must generate such subcriteria which can be used to check whether the data structure or algorithm is optimal or not.
        - You must not generate repeated questions.

        Format the output strictly as valid Python code with no extra comments.
        Example response:
        {{
            "criteria": [
                {{
                    "name": "Are the assumptions clarified?",
                    id: 1,
                    "subcriteria": [
                        {{"name": "Has the candidate defined what constitutes a word in the context of this problem?", "weight": 4.0}},
                        {{"name": "Is it clarified how to handle multiple spaces between words?", "weight": 3.5}},
                        {{"name": "What is the expected behavior for leading or trailing spaces?", "weight": 2.5}}
                    ]
                }},
                {{
                    "name": "Does the candidate account for corner cases ?",
                    id: 2,
                    "subcriteria": [
                        {{"name": "What happens if the input sentence is empty or null?", "weight": 2.5}},
                        {{"name": "How does the solution handle punctuation attached to words?", "weight": 4.5}},
                        {{"name": "How does the solution handle punctuation attached to words?", "weight": 3.0}}
                    ]
                }}
            ]
        }}          


    """
    subcriteria_prompt = PromptTemplate.from_template(template=subcriteria_prompt_template)
        
    return subcriteria_prompt

# def make_prompt_from_template():
#     subcriteria_prompt_template = """
#         You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
#         The response to every such question is evaluated based on the following set of "criteria" posed as questions:

#         question: {question}
#         criteria: {criteria}
    
#         Create a Python dictionary structure that represents a list of criteria. Each criterion should have the following attributes:
#         - A string attribute called "name" representing the name of the criterion.
#         - A float attribute called "weight" representing the weight of the criterion, which should be between 1 and 10.
#         - A list attribute called "subcriteria," which contains 3 dictionaries. Each subcriterion should have:
#         - A string attribute called "name" representing the name of the subcriterion.
#         - A float attribute called "weight" representing the weight of the subcriterion, also between 1 and 10.

#         Format the output strictly as valid Python code with no extra comments.
#         Example response:
#         subcriteria_payload = {{
#             "criteria": [
#                 {{
#                     "name": " "Are the assumptions clarified?"","weight": 8.5,
#                     "subcriteria": [
#                         {{"name": "Has the candidate defined what constitutes a word in the context of this problem?", "weight": 7.0}},
#                         {{"name": "Is it clarified how to handle multiple spaces between words?", "weight": 9.0}},
#                         {{"name": "What is the expected behavior for leading or trailing spaces?", "weight": 6.5}}
#                     ]
#                 }},
#                 {{
#                     "name": "Does the candidate account for corner cases ?",
#                     "weight": 6.0,
#                     "subcriteria": [
#                         {{"name": "What happens if the input sentence is empty or null?", "weight": 5.5}},
#                         {{"name": "How does the solution handle punctuation attached to words?", "weight": 8.0}},
#                         {{"name": "How does the solution handle punctuation attached to words?", "weight": 8.0}}
#                     ]
#                 }}
#             ]
#         }}          


#     """
#     subcriteria_prompt = PromptTemplate.from_template(template=subcriteria_prompt_template)
        
#     return subcriteria_prompt

# recent one

# def make_prompt_from_template():
#         subcriteria_prompt_template = """
#         You are an expert interviewer with experience in evaluating responses to Data Structures, Algorithms and Algorithmic complexity questions. 
#         Your evaluation should follow these guidelines:

#         When generating subcriteria:
#         - ALL subcriteria MUST start with:
#         * "Does the candidate..."
#         * "Is the solution..."
#         * "Can the solution..."
#         * "Has the candidate..."
#         - NEVER start subcriteria with "How", "What", "Why", or other open-ended question words
#         - NEVER question the use of a data structure that is explicitly given in the problem statement
#         * If problem mentions "array", "linked list", "tree", "graph", "hash map/table", "stack", "queue", "heap", "set", or any other specific data structure, don't question its choice
#         * Examples:
#             - For "Find in BST" - don't ask why BST was chosen
#             - For "Graph traversal" - don't ask why graph was chosen
#             - For "Hash table lookup" - don't ask why hash table was chosen
#         * Instead focus on how well the candidate uses the given structure
#         - For data structure criteria, when a specific structure is given in the question:
#             * Focus on how effectively the candidate uses the given structure
#             * Evaluate understanding of the structure's properties relevant to the problem
#             * Consider any auxiliary data structures needed for the solution
#         - Ensure each subcriterion evaluates a unique aspect
#         - Avoid repeating similar questions across different criteria
#         - Focus on reasoning and understanding rather than just implementation

#         question: {question}
#         criteria: {criteria}

#         Your task is as follows:
#         1. Ask me for a problem question based on the aforementioned primary criteria and question as an input and analyse it.
#         2. For each criterion in criteria, generate three most significant and distinct subcriteria that:
#         - Are mutually exclusive with other subcriteria
#         - Test different aspects of the same core concept
#         - Build upon rather than repeat information
#         - MUST be phrased as direct yes/no questions
#         3. Associate a score for each subcriterion ensuring they sum to 10
#         4. Format the response as a dictionary where:
#         - Keys are the criteria values
#         - Values are lists of associated subcriteria
#         - No extra spaces in dictionary formatting
                     
#         Example Response:
#                     {{
#                         "Are the assumptions clarified?": [
#                             {{
#                                 "subcriteria": "Has the candidate defined what constitutes a word in the context of this problem?",
#                                 "weight": "3"
#                             }},
#                             {{
#                                 "subcriteria": "Is it clarified how to handle multiple spaces between words?",
#                                 "weight": "4"
#                             }},
#                             {{
#                                 "subcriteria": "Is the expected behavior for leading or trailing spaces sepcified ?",
#                                 "weight": "3"
#                             }},
#                         ],
#                         "Does the candidate account for corner cases ?": [
#                             {{
#                                 "subcriteria": "Has candidate accounted for empty or null sentances?",
#                                 "weight": "4"
#                             }},
#                             {{
#                                 "subcriteria": "Does the solution handle punctuation attached to words?",
#                                 "weight": "3"
#                             }},
#                             {{
#                                 "subcriteria": "Is there consideration for sentences with only spaces?",
#                                 "weight": "3"
#                             }},
#                         ]
#                     }}
#                 Response:
# """

# previous one

# def make_prompt_from_template():
#         subcriteria_prompt_template = """

#                 You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
#                 The response to every such question is evaluated based on the following set of "criteria" posed as questions:

#                 question: {question}
#                 criteria: {criteria}

#                 Your task is as follows: 
#                 1. Ask me for a problem question based on the aforementioned primary criteria and question as an input and analyse it. 
#                 2. Thereafter, for each one of the above listed criterion, generate top three sub-criteria (posed as questions) that collectively represent each primary criterion in the best manner possible. 
#                 3. Now, associate a score commensurate to the importance of each of the three generated sub-criterion  
#                 4. Please ensure that the scores add up to 10 for each set of sub-criteria
                
#                 The response must be a dictionary where:
#                 - Keys must be value of criteria.
#                 - Values are a list of associated sub-criteria.
#                 - You must not add extra spaces while creating dictionary.

#                 Example:
#                     {{
#                         "Are the assumptions clarified?": [
#                             {{
#                                 "subcriteria": "Has the candidate defined what constitutes a word in the context of this problem?",
#                                 "weight": "3"
#                             }},
#                             {{
#                                 "subcriteria": "Is it clarified how to handle multiple spaces between words?",
#                                 "weight": "4"
#                             }},
#                             {{
#                                 "subcriteria": "What is the expected behavior for leading or trailing spaces?",
#                                 "weight": "3"
#                             }},
#                         ],
#                         "Does the candidate account for corner cases ?": [
#                             {{
#                                 "subcriteria": "What happens if the input sentence is empty or null?",
#                                 "weight": "4"
#                             }},
#                             {{
#                                 "subcriteria": "How does the solution handle punctuation attached to words?",
#                                 "weight": "3"
#                             }},
#                             {{
#                                 "subcriteria": "Is there consideration for sentences with only spaces?",
#                                 "weight": "3"
#                             }},
#                         ]
#                     }}
                


#                 Response:
#             """
        
        # subcriteria_prompt = ChatPromptTemplate.from_template(template=subcriteria_prompt_template)
        
        # return subcriteria_prompt