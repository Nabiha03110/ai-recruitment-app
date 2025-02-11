"""
This module implements the functionality for evaluating answers based on predefined criteria, 
including calculating scores using weighted averages, and storing results in a database.
"""

import json
from src import utils
from  src.utils import interview_computation
from src.services.llm.prompts import answer_evaluator_prompt
import src.services.llm as llm
from src import dao
import time

# Initialize logger
logger = utils.get_logger(__name__)

# async def evaluate_answer(question_id, question, interview_id, candidate_answer):
#     """
#     Orchestrates the evaluation process for a given query.
    
#     Args:
#         input (GenerateEvaluation): The request body containing the evaluation details.
#             - question_id (int): The unique identifier of the question to be evaluated.
#             - question (str): The text of the question.
#             - interview_id (int): The unique identifier of the interview session.
#             - answer (str): The candidate's answer to be evaluated.
    
#     Returns:
#         dict: A response containing the evaluation results.
#     """
#     try:

#         evaluation_criteria = await dao.fetch_subcriteria(question_id)
#         chat_history = await dao.get_chat_history(interview_id)

#         llm_inputs = []
#         subcriteria_weights = []
#         # criteria_scores = []
#         evaluation_results = []

#         assessment_payload_ready_for_computation = {}

#         for criterion in evaluation_criteria.keys():
#             llm_inputs.append({"question": question, "answer": candidate_answer, "chat_history": chat_history, "subcriteria": evaluation_criteria[criterion]})
#             # llm_inputs.append({"question": question, "answer": candidate_answer, "chat_history": chat_history, "subcriteria": evaluation_criteria[criterion],"eval_distribution":eval_distribution})
#             subcriteria_weights.append([int(subcriterion['weight']) for subcriterion in evaluation_criteria[criterion]])
#             ### rmsbegin: added code here to populate the assessment_payload
#             subcriterion_question_weight_list = evaluation_criteria[criterion]
#             for elem in subcriterion_question_weight_list:
#                 subcriterion_question = elem["subcriterion"]
#                 subcriterion_weight = elem["weight"]
#                 assessment_payload_ready_for_computation[subcriterion_question] = [subcriterion_weight]
#             ### rmsend: assessment_payload is ready with foll. format {"question1":[3.0]}

#         evaluation_prompt = answer_evaluator_prompt.make_prompt_from_template()
#         evaluation_llm = llm.get_openai_model(model = "gpt-4o-mini")
#         evaluation_chain = evaluation_prompt | evaluation_llm
#         llm_response = await evaluation_chain.abatch(llm_inputs)
#         logger.info(f"LLM RESPONSE FOR ANSWER EVALUATOR : {llm_response}")
        
#         for criterion_result, criterion_weights in zip(llm_response, subcriteria_weights):     
#             if "json" in criterion_result.content:
#                 str1=criterion_result.content.replace("```json\n", "")
#                 str2=str1.replace("```", "")
#                 evaluation_results.append(json.loads(str2))
#             else:
#                 evaluation_results.append(json.loads(criterion_result.content))
#             #evaluation_results.append(json.loads(criterion_result.content))
#             # subcriteria_score = (json.loads(criterion_result.content)).values()
#             # criteria_scores.append(score_subcriteria(criterion_weights, subcriteria_score))
           

#         ### rmsbegin: code below appends the candidate score against to each dictionary item in the existing list containg weight
#         for evaluation_dict_item in evaluation_results:
#             for key in evaluation_dict_item.keys():
#                 assessment_payload_ready_for_computation[key].append(evaluation_dict_item[key])  # appending score to the weight  

#         # total_score_count = sum(criteria_scores)
#         # final_score = round(total_score_count / len(evaluation_criteria.keys()), 2)

#         # print(assessment_payload_ready_for_computation)
#         return (interview_computation.compute_turn_score_interim(assessment_payload_ready_for_computation))

        
    
#     except Exception as ex:
#         logger.critical(f"Unexpected error in evaluation process: {ex}")
#         raise Exception(f"Unexpected error in evaluation process: {ex}")


async def evaluate_answer(question_id, question, interview_id, chat_history, evaluation_criteria):
    """
    Orchestrates the evaluation process for a given query.
    
    Args:
        input (GenerateEvaluation): The request body containing the evaluation details.
            - question_id (int): The unique identifier of the question to be evaluated.
            - question (str): The text of the question.
            - interview_id (int): The unique identifier of the interview session.
            - answer (str): The candidate's answer to be evaluated.
    
    Returns:
        dict: A response containing the evaluation results.
    """
    try:
        llm_inputs = []
        subcriteria_weights = []
        evaluation_results = []

        assessment_payload_ready_for_computation = {}

        start_time = time.time()

        for criterion in evaluation_criteria['criteria']:
            llm_inputs.append({"question": question, "chat_history": chat_history, "criterion": criterion})
            subcriteria_weights.append([int(subcriterion['weight']) for subcriterion in criterion['subcriteria']])
            ### rmsbegin: added code here to populate the assessment_payload
            for elem in criterion['subcriteria']:
                subcriterion_question = elem['name']
                subcriterion_weight = elem['weight']
                assessment_payload_ready_for_computation[subcriterion_question] = [subcriterion_weight]
            ### rmsend: assessment_payload is ready with foll. format {"question1":[3.0]}

        execution_time = time.time() - start_time
        logger.info(f"LLM Input Loop:- Processed in {execution_time:.2f} seconds")

        evaluation_prompt = answer_evaluator_prompt.make_prompt_from_template()
        evaluation_llm = llm.get_openai_model(model = "gpt-4o-mini")
        evaluation_chain = evaluation_prompt | evaluation_llm
        logger.info("GENERATING LLM RESPONSE FOR ANSWER EVALUATOR")
        start_time = time.time()
        llm_response = await evaluation_chain.abatch(llm_inputs)
        execution_time = time.time() - start_time
        logger.info(f"LLM Response:- Processed in {execution_time:.2f} seconds")
        logger.info(f"LLM RESPONSE FOR ANSWER EVALUATOR : {llm_response}")

        start_time = time.time()
        
        for criterion_result, criterion_weights in zip(llm_response, subcriteria_weights):     
            evaluation_results.append(json.loads(utils.clean_response(criterion_result.content)))

            for subcriteria_results in evaluation_results[-1]['subcriteria']:
                assessment_payload_ready_for_computation[subcriteria_results['name']].append(subcriteria_results['score'])  # appending score to the weight
              
        execution_time = time.time() - start_time
        logger.info(f"Assesment Payload Loop:- Processed in {execution_time:.2f} seconds")

        start_time = time.time()
        
        criterion_score_list, final_score = interview_computation.compute_turn_score_interim(assessment_payload_ready_for_computation)

        execution_time = time.time() - start_time
        logger.info(f"Interim Score:- Processed in {execution_time:.2f} seconds")

        start_time = time.time()
        
        # await dao.add_question_evaluation(interview_id, question_id, final_score, json.dumps(assessment_payload_ready_for_computation))

        execution_time = time.time() - start_time
        logger.info(f"Add Evaluation:- Processed in {execution_time:.2f} seconds")
        
        return {
            'evaluation_results': assessment_payload_ready_for_computation,
            'criteria_score': criterion_score_list,
            'final_score': final_score
        }
    
    except Exception as ex:
        logger.critical(f"Unexpected error in evaluation process: {ex}")
        raise Exception(f"Unexpected error in evaluation process: {ex}")


def score_subcriteria(criterion_weights, subcriteria_score):
    total_weight = sum(criterion_weights)
    weighted_score = sum(weight * int(score) for weight, score in zip(criterion_weights, subcriteria_score))
    criterion_score = (round((weighted_score / total_weight), 2) if total_weight != 0 else 0)/10.0
    criterion_score=round(criterion_score,2)
    return criterion_score