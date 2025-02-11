"""Interview router module for handling interview-related API endpoints.

This module provides FastAPI router endpoints for generating sub-criteria and
evaluating answers in the interview process.
"""
import uvicorn
import json
from fastapi import FastAPI
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.schemas.endpoints.schema import GenerateSubCriteriaRequest,EvaluateAnswerRequest, GenerateHintRequest,StartInterviewRequest
from src.services.workflows import subcriteria_generator,answer_evaluator
from src.utils.logger import get_logger
from typing import List
from src.utils.response_helper import decorate_response
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool,init_pool
from src.dao.question import get_question_metadata
from src.dao.exceptions import QuestionNotFoundException,InterviewNotFoundException
from src.services.workflows.candidate_greeter import generate_greeting
from src.services.workflows import answer_evaluator
from src.services.workflows.solution_hint_generator import generate_hint
from src.services.workflows import hint_generator
from test.simulate_candidate_response import simulate_candidate_response
from src.dao.chat_history import get_chat_history
from src.dao.interview import get_interview_metadata, add_interview
from src.dao.chat_history import add_chat_history, update_last_candidate_answer
from src.dao.question import get_initial_question_metadata,get_question_metadata
from src.dao.chat_history import delete_chat_history
from src.dao.question import add_question, get_question_metadata_by_type, get_question
import time
from asyncio import gather
from src import dao

import asyncio
# Initialize logger

logger = get_logger(__name__)

# Initialize the router
router = APIRouter(tags=["Execute Interview"])

app=FastAPI()

@router.get("/greeter-service")
async def greet_candidate(user_id: int):
    try:
        user_name, interview_id = await add_interview(user_id)
        greeting_response=await generate_greeting(user_name)
        return decorate_response(True,greeting_response)
    except Exception as e:
        logger.critical("Failed to generate candidate greeting: %s", e)
        return decorate_response(
            False,
            "Failed to generate candidate greeting",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/generate_subcriteria", status_code=status.HTTP_200_OK)
async def generate_subcriteria(input_request: GenerateSubCriteriaRequest) -> JSONResponse:
    """Generates sub-criteria based on the given question.

    Args:
        input_request: Request object containing:
            - question_id: Unique ID for database insertion
            - question: Content used to generate sub-criteria.
            - question_type_id (int): The identifier representing the type of question .


    Returns:
        JSONResponse containing:
            - succeeded: Operation success status
            - message: Generated sub-criteria or error message
            - httpStatusCode: HTTP status code.
    """
    try:
        # Extract necessary attributes from the input request
        question = input_request.question
        question_id = input_request.question_id
        question_type_id = input_request.question_type_id
        logger.info("Started generating sub-criteria for question ID: %s", question_id)

    except AttributeError as attr_err:
        logger.error("Input object missing required attributes: %s", attr_err)
        raise Exception(f"Input object missing required attributes: {attr_err}") from attr_err
    
    try:
        subcriteria = await subcriteria_generator.generate_subcriteria(question, question_id, question_type_id)
        logger.info("Successfully generated sub-criteria: %s", subcriteria)
        return decorate_response(True, subcriteria)

    except Exception as ex:
        logger.critical("Failed to generate sub-criteria: %s", ex)
        return decorate_response(
            False,
            "Failed to generate sub-criteria",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/evaluate_answer", status_code=status.HTTP_200_OK)
async def evaluate_answer(input_request: EvaluateAnswerRequest) -> JSONResponse:
    """Evaluates an answer based on provided criteria.

    Args:
        evaluation_request_input: Request object containing evaluation details

    Returns:
        JSONResponse containing:
            - succeeded: Operation success status
            - message: Evaluation results or error message
            - httpStatusCode: HTTP status code
    """
    try:
        question_id = input_request.question_id
        question = input_request.question
        interview_id = input_request.interview_id
        candidate_answer = input_request.answer
        eval_distribution = input_request.eval_distribution
    except AttributeError as attr_err:
        logger.critical(f"Input object missing required attributes: {attr_err}")
        raise AttributeError(f"Input object missing required attributes: {attr_err}") from attr_err
    try:
        response = await answer_evaluator.evaluate_answer(question_id, question, interview_id, candidate_answer, eval_distribution)
        logger.info("Successfully evaluated answer")
        # return decorate_response(True, response)
        return response
    
    except Exception as ex:
        logger.critical("Failed to evaluate answer: %s", ex)
        return decorate_response(False,"Failed to evaluate answer",status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/generate_hint")
# remodel takes input chat_history and answer_evaluation
async def generate_hint(chat_history,answer_evaluation,hint_count):
    try:
        hint = await hint_generator.generate_hint(chat_history,answer_evaluation,hint_count)
        return decorate_response(True,hint)
    except Exception as e:
        logger.critical("Failed to generate hint: %s", e)
        return decorate_response(
            False,
            "Failed to generate hint",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/generate_solution_hint", status_code=status.HTTP_200_OK)
async def generate_solution_hint(input_request: GenerateHintRequest) -> JSONResponse:
    """Evaluates an answer based on provided criteria.

    Args:
        evaluation_request_input: Request object containing evaluation details

    Returns:
        JSONResponse containing:
            - succeeded: Operation success status
            - message: Evaluation results or error message
            - httpStatusCode: HTTP status code
    """
    try:
        response = await generate_hint(input_request)
        logger.info("Successfully generated hint")
        return decorate_response(True, response)
    
    except Exception as ex:
        logger.critical("Failed to generate hint: %s", ex)
        return decorate_response(False,"Failed to generate hint",status.HTTP_500_INTERNAL_SERVER_ERROR)
#add question complexity
@router.post("/onboard_question",status_code=status.HTTP_200_OK)
async def onboard_question(question: str, question_type_id: int ,complexity: int):
    question_metadata=await add_question(question,question_type_id,complexity)
    question_id=question_metadata['question_id']
    question=question_metadata['question']
    question_type_id=question_metadata['question_type_id']
    subcriteria_payload={
        'question_id': question_id,
        'question': question,
        'question_type_id': question_type_id
    }
    subcriteria_request=GenerateSubCriteriaRequest(**subcriteria_payload)
    subcriteria=await generate_subcriteria(subcriteria_request)
    return {
        "question_metadata": question_metadata,
        "subcriteria": subcriteria
    }

@router.post("/onboard_multiple_questions", status_code=status.HTTP_200_OK)
async def onboard_multiple_questions(questions: List[dict]):
    """
    Onboard multiple questions in a single request.

    Args:
        questions: A list of dictionaries, where each dictionary contains:
            - question: The question text.
            - question_type_id: The type ID of the question.
            - complexity: The complexity level of the question.

    Returns:
        JSONResponse containing:
            - succeeded: Operation success status.
            - message: List of onboarded questions or error message.
            - httpStatusCode: HTTP status code.
    """
    try:
        results = []
        for question_data in questions:
            question = question_data.get("question")
            question_type_id = question_data.get("question_type_id")
            complexity = question_data.get("complexity")
            
            # if not all([question, question_type_id, complexity]):
            #     raise ValueError("Missing required fields in one or more questions.")
            
            result = await onboard_question(question, question_type_id, complexity)
            results.append(result)
        
        logger.info("Successfully onboarded multiple questions")
        return decorate_response(True, results)
    
    except Exception as ex:
        logger.critical("Failed to onboard multiple questions: %s", ex)
        return decorate_response(
            False,
            "Failed to onboard multiple questions",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
#condcut interview
@router.post("/conduct_interview", status_code=status.HTTP_200_OK)
async def conduct_interview(interview_id) :
    hint_count=[0,0,0,0,0]
    initial_eval_distribution=[0,0,0,0,0,0,0]
    # if len(chat_history) == 0: call greeter  
    # use dao calls for interview_question for question_id, interview for user_id/name, chat_history for turn_input/output
    # call greeting and generate greeting
    # call chat_history.add_chat_history and write the first turn to the database
    # get answers from the user and update chat_history (answer_evaluator)
    # pass the answer to the answer evaluator and generate scores 
    # pass the scores and the updated chat history to hint generator
    # get the generated hint and update chat history
    # repeat the loop from step no.3 until the average interview score crosses the predefined threshold
    # if the interview score crossed the threshold, call the reporting api and generate the report
    # for now assuming that question_id = 1
    
    chat_history= await get_chat_history(interview_id)
    if chat_history:
        await delete_chat_history(interview_id)
    chat_history= await get_chat_history(interview_id)    
    if not chat_history:
        question_id=0

        interview_metadata=await get_interview_metadata(interview_id)
        user_id=interview_metadata.user_id
        greeting_response = await greet_candidate(user_id)

        greeting_response_body = greeting_response.body.decode()
        greeting_response_data = json.loads(greeting_response_body)
        
        greeting = greeting_response_data["message"]
        simulated_candidate_greeting_response="Hey I am ready let's begin the interview"
        #check whether the candidate is readfy for interview by a logic
        added_chat_history_data=await add_chat_history(interview_id, question_id, greeting, simulated_candidate_greeting_response,'greeting')

    #initial_question_metadata=await get_initial_question_metadata()
    initial_question_metadata=await get_question_metadata(10)
    initial_question=initial_question_metadata['question']

    
    ##################################################################################################
    # subcriteria_weight_list_norm=[]
    # for key,value in subcriteria.items():
    #     subcriterion_weight_list=subcriteria['key'][0]
    #     for dict_el in subcriterion_weight_list:
    #         subcriteria_weight_list_norm.append(dict_el['weight'])
    # logger.info(f"SUBCRITERIA NORM {subcriteria_weight_list_norm}")
    ##################################################################################################
    
    #candidate_response=await simulate_candidate_response(initial_question_metadata['question_id'])
    candidate_response=input(f"Answer for question ,  : ")
    added_chat_history=await add_chat_history(interview_id,initial_question_metadata['question_id'],initial_question,candidate_response,'question')
    
    answer_evaluation_payload={
        "question_id":initial_question_metadata['question_id'],
        "question":initial_question,
        "interview_id":interview_id,
        "answer":candidate_response,
        "eval_distribution":initial_eval_distribution
    }
    #logger.info(f"ANSWER EVALUATION PAYLOAD : {answer_evaluation_payload}")
    answer_evaluation_request=EvaluateAnswerRequest(**answer_evaluation_payload)
    answer_evaluation=await evaluate_answer(answer_evaluation_request)
    chat_history=await get_chat_history(interview_id)
    logger.info(f"HINT GENERATOR PAYLOAD : {chat_history} {answer_evaluation} {hint_count}")
    while(answer_evaluation['final_score']<9.5):
        hint_response=await generate_hint(chat_history,answer_evaluation,hint_count)
        hint_response_body = hint_response.body.decode()
        hint_response_data = json.loads(hint_response_body)
        hint = hint_response_data["message"]
        
        logger.info("\n################################################################################")  
        logger.info("\n######################################## CHAT HISTORY ####################")
        for dict_el in chat_history:
            for key, value in dict_el.items():
                logger.info(f"\t[{key}]: {value}")
        logger.info("\n######################################### ASSESSMENT ####################")
        for dict_el in answer_evaluation["evaluation_results"]:
            for key, value in dict_el.items():
                logger.info(f"\t{key}: [{value}]")
        logger.info(f"\n########################## CRITERIA LEVEL SCORES: {answer_evaluation['criteria_scores']}")
        logger.info(f"\n############################### FINAL SCORE: {answer_evaluation['final_score']}")
        logger.info(f"\n########################### HINT: {hint}")
        #candidate_response=await simulate_candidate_response(initial_question_metadata['question_id'])
        candidate_response=input("Enter your answer : " )
        added_chat_history=await add_chat_history(interview_id,initial_question_metadata['question_id'],hint,candidate_response,'hint_question')
        answer_evaluation_payload={
        "question_id":initial_question_metadata['question_id'],
        "question":initial_question,
        "interview_id":interview_id,
        "answer":candidate_response,
        "eval_distribution":initial_eval_distribution
    }
        #logger.info(f"ANSWER EVALUATION PAYLOAD : {answer_evaluation_payload}")
        answer_evaluation_request=EvaluateAnswerRequest(**answer_evaluation_payload)
        answer_evaluation=await evaluate_answer(answer_evaluation_request)
        chat_history=await get_chat_history(interview_id)
        logger.info(f"\n############################### UPDATED SCORE {len(chat_history)}: {answer_evaluation['final_score']} ")


@router.post("/start_interview", status_code=status.HTTP_200_OK)
async def start_interview(  user_id: int, question_type_id: int, interview_id: int = None, next_question_id: int = 0, candidate_answer: str = None):
    start_time = time.time()
    logger.info("################################# START OF INTERVIEW #########################################")
    if not connection_pool:
        await init_pool()
        print(f"Connection Pool: {time.time() - start_time}")
    question_list = await get_question_metadata_by_type(question_type_id)
    print(f"Question List: {time.time() - start_time}")
    logger.info("################################################################################")
    logger.info(f"QUESTION LIST {question_list}")

    question_id = question_list[next_question_id +12][0]
    question = question_list[next_question_id +12][1]
    if next_question_id == 0 and interview_id == None:
        username, interview_id = await add_interview(user_id)
        print(f"Add Interview: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"INTERVIEW ID {interview_id}")

    chat_history = await get_chat_history(interview_id, question_id)
    print(f"Get Chat History: {time.time() - start_time}")
    logger.info("################################################################################")
    logger.info(f"CHAT HISTORY {chat_history}")

    if len(chat_history) == 0 and candidate_answer == None:
        greeting_response = await generate_greeting(username)
        print(f"Generate Greeting: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"GREETING {greeting_response}")

        await add_chat_history(interview_id, question_id, greeting_response, candidate_answer, 'greeting')
        logger.info("Successfully added chat history")

        print(f"Add Chat History: {time.time() - start_time}")

        return decorate_response(True, {'interview_id': interview_id, 'greeting': greeting_response})
    
    elif len(chat_history) == 1 and candidate_answer != None:
        await update_last_candidate_answer(interview_id, candidate_answer)
        print(f"Update Last Candidate Answer: {time.time() - start_time}")
        logger.info("Successfully updated last candidate answer")

        subcriteria = await subcriteria_generator.generate_subcriteria(question, question_id, question_type_id)
        print(f"Generate Subcriteria: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"SUBCRITERIA {subcriteria}")

        await add_chat_history(interview_id, question_id, question, None, 'question')
        logger.info("Successfully added chat history")

        print(f"Add Chat History: {time.time() - start_time}")

        return decorate_response(True, question)
    
    elif len(chat_history) >= 2 and candidate_answer != None:
        await update_last_candidate_answer(interview_id, candidate_answer)
        print(f"Update Last Candidate Answer: {time.time() - start_time}") # 2.29 sec
        logger.info("Successfully updated last candidate answer")

        evaluation = await answer_evaluator.evaluate_answer(question_id, question, interview_id, candidate_answer) # 7.3 sec
        print(f"Evaluate Answer: {time.time() - start_time}") # 9.6 sec
        logger.info("################################################################################")
        logger.info(f"EVALUATION {evaluation}")
        
        chat_history = await get_chat_history(interview_id, question_id)
        print(f"Get Chat History: {time.time() - start_time}") # 10.45 sec
        logger.info("################################################################################")
        logger.info(f"CHAT HISTORY {chat_history}")

        if evaluation['final_score'] < 7:
            hint_type, hint = await hint_generator.generate_hint(chat_history, evaluation)
            print(f"Generate Hint: {time.time() - start_time}") # 10.46 sec
            logger.info("################################################################################")
            logger.info(f"HINT {hint}")

            await add_chat_history(interview_id, question_id, hint, None, hint_type)
            print(f"Add Chat History: {time.time() - start_time}") # 11.60 sec
            logger.info("Successfully added chat history")
        else:
            hint = None

        if hint == None or hint == "Thank you for going through all the hints. You should now have everything you need to write the code for this problem." or evaluation['final_score'] >= 7:
            next_question_id += 1
        else:
            pass
        
        print(f"Hint Generated: {time.time() - start_time}") # 11.60 sec
        return decorate_response(True, {'evaluation': evaluation, 'hint': hint, 'next_question_bit': next_question_id})


@router.post("/start_interview", status_code=status.HTTP_200_OK)
async def start_interview(user_id: int, question_type_id: int, interview_id: int = None, next_question_id: int = 0, candidate_answer: str = None):
    start_time = time.time()
    logger.info("################################# START OF INTERVIEW #########################################")
    if not connection_pool:
        await init_pool()
        print(f"Connection Pool: {time.time() - start_time}")
    question_list = await get_question_metadata_by_type(question_type_id)
    print(f"Question List: {time.time() - start_time}")
    logger.info("################################################################################")
    logger.info(f"QUESTION LIST {question_list}")

    question_id = question_list[next_question_id +12][0]
    question = question_list[next_question_id +12][1]
    if next_question_id == 0 and interview_id == None:
        username, interview_id = await add_interview(user_id)
        print(f"Add Interview: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"INTERVIEW ID {interview_id}")

    chat_history = await get_chat_history(interview_id, question_id)
    print(f"Get Chat History: {time.time() - start_time}")
    logger.info("################################################################################")
    logger.info(f"CHAT HISTORY {chat_history}")

    if len(chat_history) == 0 and candidate_answer == None:
        greeting_response = await generate_greeting(username)
        print(f"Generate Greeting: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"GREETING {greeting_response}")

        await add_chat_history(interview_id, question_id, greeting_response, candidate_answer, 'greeting')
        logger.info("Successfully added chat history")

        print(f"Add Chat History: {time.time() - start_time}")

        return decorate_response(True, {'interview_id': interview_id, 'greeting': greeting_response})
    
    elif len(chat_history) == 1 and candidate_answer != None:
        await update_last_candidate_answer(interview_id, candidate_answer)
        print(f"Update Last Candidate Answer: {time.time() - start_time}")
        logger.info("Successfully updated last candidate answer")

        subcriteria = await subcriteria_generator.generate_subcriteria(question, question_id, question_type_id)
        print(f"Generate Subcriteria: {time.time() - start_time}")
        logger.info("################################################################################")
        logger.info(f"SUBCRITERIA {subcriteria}")

        await add_chat_history(interview_id, question_id, question, None, 'question')
        logger.info("Successfully added chat history")

        print(f"Add Chat History: {time.time() - start_time}")

        return decorate_response(True, question)
    
    elif len(chat_history) >= 2 and candidate_answer != None:
        await update_last_candidate_answer(interview_id, candidate_answer)
        print(f"Update Last Candidate Answer: {time.time() - start_time}") # 2.29 sec
        logger.info("Successfully updated last candidate answer")

        evaluation = await answer_evaluator.evaluate_answer(question_id, question, interview_id, candidate_answer) # 7.3 sec
        print(f"Evaluate Answer: {time.time() - start_time}") # 9.6 sec
        logger.info("################################################################################")
        logger.info(f"EVALUATION {evaluation}")
        
        chat_history = await get_chat_history(interview_id, question_id)
        print(f"Get Chat History: {time.time() - start_time}") # 10.45 sec
        logger.info("################################################################################")
        logger.info(f"CHAT HISTORY {chat_history}")

        if evaluation['final_score'] < 7:
            hint_type, hint = await hint_generator.generate_hint(chat_history, evaluation)
            print(f"Generate Hint: {time.time() - start_time}") # 10.46 sec
            logger.info("################################################################################")
            logger.info(f"HINT {hint}")

            await add_chat_history(interview_id, question_id, hint, None, hint_type)
            print(f"Add Chat History: {time.time() - start_time}") # 11.60 sec
            logger.info("Successfully added chat history")
        else:
            hint = None

        if hint == None or hint == "Thank you for going through all the hints. You should now have everything you need to write the code for this problem." or evaluation['final_score'] >= 7:
            next_question_id += 1
        else:
            pass
        
        print(f"Hint Generated: {time.time() - start_time}") # 11.60 sec
        return decorate_response(True, {'evaluation': evaluation, 'hint': hint, 'next_question_bit': next_question_id})


@router.post("/begin_interview", status_code=status.HTTP_200_OK)
async def begin_interview(input_request: StartInterviewRequest):
    try:
        # Extracting input attributes
        question_id = input_request.question_id
        user_id = input_request.user_id
        candidate_answer = input_request.candidate_answer
        chat_history = input_request.chat_history
        question_type_id = input_request.question_type_id
        interview_id = input_request.interview_id
        question = input_request.question
    except AttributeError as attr_err:
        logger.critical(f"Input object missing required attributes: {attr_err}")
        return decorate_response(
            succeeded=False,
            message=f"Missing required attributes: {attr_err}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    start_time = time.time()
    logger.info("################################# START OF INTERVIEW #########################################")
    try:
        # Process the interview logic
        if len(chat_history) == 0 and not candidate_answer:
            if not interview_id:
                user_name, interview_id = await add_interview(user_id)
            
            greeting_response = await generate_greeting(user_name)
            logger.info(f"Greeting generated: {greeting_response}")

            await add_chat_history(interview_id, question_id, greeting_response, candidate_answer, "greeting")
            logger.info("Chat history added successfully.")

            execution_time = time.time() - start_time
            logger.info(f"Processed in {execution_time:.2f} seconds")

            return decorate_response(succeeded=True, message="Interview started successfully.", data={"interview_id": interview_id, "greeting": greeting_response}, status_code=status.HTTP_200_OK)
        
        elif len(chat_history) == 1 and candidate_answer is not None:
            tasks = []

            # Add the task for getting the question if `question_id` exists
            if question_id:
                tasks.append(get_question(question_id))
            else:
                tasks.append(None)  # Placeholder to maintain order

            # Add the task for updating the last candidate answer
            tasks.append(update_last_candidate_answer(interview_id, candidate_answer))

            # Execute the tasks concurrently
            results = await gather(*tasks, return_exceptions=True)
            
            # Handle `get_question` result
            question = results[0] if isinstance(results[0], str) else None
            if isinstance(results[0], Exception):
                logger.error(f"Error fetching question: {results[0]}")
                raise results[0]

            # Handle `update_last_candidate_answer` result
            update_success = results[1]
            if isinstance(update_success, Exception):
                logger.error(f"Error updating last candidate answer: {update_success}")
                raise update_success
            elif not update_success:
                logger.warning("Candidate answer update failed. No rows were updated.")
                return decorate_response(
                    succeeded=False,
                    message="Failed to update candidate answer.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            logger.info("Successfully updated last candidate answer.")

            # Generate or Fetch SubCriteria
            # subcriteria = await subcriteria_generator.generate_subcriteria(question, question_id, question_type_id)
            # logger.info("################################################################################")
            # logger.info(f"SUBCRITERIA {subcriteria}")

            # Add chat history
            chat_history_result = await add_chat_history(interview_id, question_id, question, None, "question")
            if chat_history_result:
                logger.info("Successfully added chat history.")
            else:
                logger.warning("Failed to add chat history.")
                return decorate_response(
                    succeeded=False,
                    message="Failed to add chat history.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            execution_time = time.time() - start_time
            logger.info(f"Processed in {execution_time:.2f} seconds")
            
            return decorate_response(succeeded=True, message="Next question fetched successfully.", data={"question": question}, status_code=status.HTTP_200_OK)
        
        elif len(chat_history) >= 2 and candidate_answer is not None:
            # Concurrently update the last candidate answer and evaluate the answer
            start_time_02 = time.time()
            update_candidate_answer = update_last_candidate_answer(interview_id, candidate_answer)
            fetch_evaluation_criteria_task = dao.fetch_subcriteria(question_id)

            update_success, evaluation_criteria = await gather(update_candidate_answer, fetch_evaluation_criteria_task)

            if isinstance(update_success, Exception):
                logger.error(f"Error updating last candidate answer: {update_success}")
                return decorate_response(
                    succeeded=False,
                    message="Failed to update candidate answer.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            execution_time = time.time() - start_time_02
            logger.info(f"Update Answer and Fetch Subcriteria:- Processed in {execution_time:.2f} seconds")
            
            evaluation = await answer_evaluator.evaluate_answer(question_id, question, interview_id, chat_history, evaluation_criteria)

            logger.info("Successfully updated last candidate answer")

            logger.info("################################################################################")
            logger.info(f"EVALUATION {evaluation}")

            if evaluation['final_score'] < 7:
                generate_hint_task = hint_generator.generate_hint(chat_history, evaluation)
                add_evaluation_task = dao.add_question_evaluation(interview_id, question_id, evaluation['final_score'], json.dumps(evaluation['evaluation_results']))
                
                generate_hint_response, add_evaluation_success = await gather(generate_hint_task, add_evaluation_task)
                hint_type = generate_hint_response['hint_type']
                hint = generate_hint_response['hint']

                if isinstance(add_evaluation_success, Exception):
                    logger.error(f"Error adding evaluation results: {add_evaluation_success}")
                    return decorate_response(
                        succeeded=False,
                        message="Failed to add evaluation results.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
            
                logger.info("################################################################################")
                logger.info(f"HINT {hint}")
                
            else:
                await dao.add_question_evaluation(interview_id, question_id, evaluation['final_score'], json.dumps(evaluation['evaluation_results']))

                hint = "Great! Now that you've identified the right approach to solve this problem, get ready to start writing the code now."
                hint_type = "score_exceeded"

            await add_chat_history(interview_id, question_id, hint, None, hint_type)
            logger.info("Successfully added chat history")
            
            execution_time = time.time() - start_time
            logger.info(f"Processed in {execution_time:.2f} seconds")

            return decorate_response(succeeded=True, message="Evaluation and Hint Generated Successfully.", data={'evaluation': evaluation, 'hint': hint, 'hint_type': hint_type}, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Error during processing interview step: {e}")
        return decorate_response(
            succeeded=False,
            message="An error occurred while processing the interview step.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

            


    

    



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9030)