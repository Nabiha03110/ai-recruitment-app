from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional
import os
import asyncpg
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
import httpx
from typing import List, Optional
from src.dao.question import get_question_metadata
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import ChatHistoryNotFoundException,InterviewNotFoundException,QuestionNotFoundException
from src.schemas.dao.schema import ChatHistoryRequest,ChatHistoryResponse
import time

# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def refine_chat_history(chat_history):
    refined_chat_history = []
    for row in chat_history:
        refined_chat_history.append({
            row[2]: row[0],     # turn_input_type: turn_input
            "answer": row[1]     # turn_output
        })
    return refined_chat_history


# Initialize FastAPI application for creating chat history service endpoints
app = FastAPI()

# @app.get("/chat_history", response_model=list[dict])
# async def get_chat_history(interview_id: int):
#     """
#     Retrieve the complete chat history for a specific interview, including questions and answers.
    
#     Args:
#         interview_id (int): The unique identifier of the interview.
    
#     Returns:
#         list[dict]: A list of dictionaries containing the chat history, where each dictionary
#                    contains:
#                    - question (str): The interview question
#                    - answer (str): The candidate's answer
    
#     Raises:
#         Exception: If there's an error retrieving the chat history
#         DatabaseConnectionError: If database connection fails
#         DatabaseQueryError: If there's an error executing the query
#         DatabaseOperationError: If there's an error with database operations
#     """
#     try:
#         with get_db_connection() as conn:
#             try:
#                 interview_check_query="SELECT interview_id FROM interview WHERE interview_id = %s"
#                 interview=execute_query(conn,interview_check_query,(interview_id,))
#                 if not interview:
#                     raise InterviewNotFoundException
#                 chat_history_query = """
#                     SELECT turn_input, turn_output,turn_input_type
#                     FROM chat_history
#                     WHERE interview_id = %s
#                 """
#                 result = execute_query(conn, chat_history_query, (interview_id,), fetch_one=False)
                
#                 if not result:
#                     return []
                
#                 refined_chat_history = await refine_chat_history(result)
#                 return refined_chat_history
#             except Exception as e:
#                 logger.error(f"Error retrieving Chat History: {e}")
#                 raise Exception(f"Error retrieving Chat History: {e}")
#     except DatabaseConnectionError as e:
#         raise e
#     except DatabaseQueryError as e:
#         raise e
#     except DatabaseOperationError as e:
#         raise e

@app.get("/chat_history", response_model=list[dict])
async def get_chat_history(interview_id: int, question_id: int, turn_input_type: bool = False):
    """
    Retrieve the complete chat history for a specific interview, including questions and answers.
    
    Args:
        interview_id (int): The unique identifier of the interview.
        question_id (int): The unique identifier of the question.
        turn_input_type (bool): Optional flag to filter based on input type (default is False).
    
    Returns:
        list[dict]: A list of dictionaries containing the chat history, where each dictionary
                    contains:
                    - question (str): The interview question
                    - answer (str): The candidate's answer
    
    Raises:
        InterviewNotFoundException: If the interview is not found in the database.
        DatabaseConnectionError: If database connection fails.
        DatabaseQueryError: If there's an error executing the query.
        DatabaseOperationError: If there's an error with database operations.
    """
    try:
        async with get_db_connection() as conn:
            try:
                # Check if interview exists in the database
                interview_check_query = "SELECT EXISTS (SELECT 1 FROM interview WHERE interview_id = $1)"
                interview_exists = await conn.fetchval(interview_check_query, interview_id)

                if not interview_exists:
                    raise InterviewNotFoundException(f"Interview with ID {interview_id} not found")

                # Query to retrieve chat history
                chat_history_query = """
                    SELECT turn_input, turn_output, turn_input_type
                    FROM chat_history
                    WHERE interview_id = $1 AND question_id = $2
                """
                # interview_id = 1
                # question_id = 10
                result = await conn.fetch(chat_history_query, interview_id, question_id)

                if not result:
                    return []

                # Process the result into a refined chat history
                refined_chat_history = await refine_chat_history(result)
                return refined_chat_history

            except Exception as e:
                logger.error(f"Error retrieving chat history for interview {interview_id}, question {question_id}: {e}")
                raise DatabaseQueryError("Error retrieving chat history from the database.")
                
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError("Failed to connect to the database.")
    
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Database query error: {e}")
        raise DatabaseQueryError("Error executing the database query.")
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise DatabaseOperationError("An unexpected error occurred during database operation.")


@app.put("/chat_history/{chat_history_turn_id}", response_model=ChatHistoryResponse)
async def update_candidate_answer(chat_history_turn_id: int, chat_history_request: ChatHistoryRequest):
    """
    Update an existing chat history in the chat history.
    
    Args:
        chat_history_turn_id (int): The unique identifier of the chat history entry to update.
        chat_history_request (ChatHistoryRequest): The new answer details, must be 2-500 characters.
    
    Returns:
        ChatHistoryResponse: The updated chat history details.
    
    Raises:
        Exception (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            # Check existence
            check_query = "SELECT chat_history_turn_id FROM chat_history WHERE chat_history_turn_id = %s"
            exists = execute_query(conn, check_query, (chat_history_turn_id,), fetch_one=True)
            if not exists:
                raise ChatHistoryNotFoundException(chat_history_turn_id)

            # Build dynamic update
            update_fields = []
            update_params = []
            if chat_history_request.turn_input is not None:
                update_fields.append("turn_input = %s")
                update_params.append(chat_history_request.turn_input)
            if chat_history_request.turn_output is not None:
                update_fields.append("turn_output = %s")
                update_params.append(chat_history_request.turn_output)
            if chat_history_request.turn_input_type is not None:
                update_fields.append("turn_input_type = %s")
                update_params.append(chat_history_request.turn_input_type)
            
            if not update_fields:
                raise Exception("No update fields provided")
            
            update_params.append(chat_history_turn_id)

            update_query = f"""
                UPDATE chat_history
                SET {', '.join(update_fields)}
                WHERE chat_history_turn_id = %s
                RETURNING chat_history_turn_id, question_id, interview_id, turn_input, turn_output, turn_input_type
            """
            updated_record = execute_query(
                conn, 
                update_query, 
                update_params, 
                fetch_one=True,
                commit=True
            )
            
            return ChatHistoryResponse(
                chat_history_turn_id=updated_record[0],
                question_id=updated_record[1],
                interview_id=updated_record[2],
                turn_input=updated_record[3],
                turn_output=updated_record[4],
                turn_input_type=updated_record[5],
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
    
@app.put("/chat_history/update_answer", response_model=dict)
async def update_last_candidate_answer(interview_id: int, candidate_answer: str):
    """
    Update the candidate answer in the last row for a specific interview.

    Args:
        interview_id (int): The unique identifier of the interview.
        candidate_answer (str): The candidate's answer to the question, must be 2-500 characters.
        pool (Pool): The database connection pool.

    Returns:
        bool: True if the candidate answer is successfully updated, False otherwise.

    Raises:
        ValueError: If the candidate answer is invalid (not 2-500 characters).
        InterviewNotFoundException: If the interview does not exist.
        Exception: If there's an error updating the chat history.
    """
    # start_time = time.time()
    # Validate the candidate_answer length
    if not (2 <= len(candidate_answer) <= 1000):
        raise ValueError("Candidate answer must be between 2 and 1000 characters.")
    # print(f"A. {time.time() - start_time}")

    try:
        async with get_db_connection() as conn:
            # Check if the interview exists
            # print(f"B. {time.time() - start_time}")
            # interview_check_query = "SELECT interview_id FROM interview WHERE interview_id = $1"
            # interview = await conn.fetchval(interview_check_query, interview_id)
            # print(f"C. {time.time() - start_time}")
            # if not interview:
            #     raise InterviewNotFoundException(f"Interview with ID {interview_id} not found.")

            # Update the candidate answer for the last row of the interview
            update_query = """
                UPDATE chat_history
                SET turn_output = $1
                WHERE chat_history_turn_id = (
                    SELECT chat_history_turn_id
                    FROM chat_history
                    WHERE interview_id = $2
                    ORDER BY chat_history_turn_id DESC
                    LIMIT 1
                )
                RETURNING chat_history_turn_id
            """
            # Execute the update query and fetch the updated row
            result = await conn.fetchval(update_query, candidate_answer, interview_id)
            # print(f"D. {time.time() - start_time}")

            if result:
                return True  # Data is successfully inserted/updated
            else:
                return False
            
    except ValueError as e:
        raise e
    except InterviewNotFoundException as e:
        raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")

@app.post("/chat_history", response_model=dict)
async def add_chat_history(interview_id: int, question_id: int, turn_input: str, turn_output: str, turn_input_type: str):
    """
    Add a new chat history for a specific interview and question.

    Args:
        interview_id (int): The unique identifier of the interview.
        question_id (int): The unique identifier of the question being answered.
        turn_input (str): The input provided by the candidate.
        turn_output (str): The output generated by the system.
        turn_input_type (str): The type of input (e.g., text, audio).

    Returns:
        bool: True if the chat history was successfully added to the database.

    Raises:
        DatabaseConnectionError: If there is an issue with the database connection.
        DatabaseQueryError: If there is an error executing the query.
        DatabaseOperationError: If there is a database operation error.
    """
    try:
        async with get_db_connection() as conn:
            # Insert the new chat history into the database
            insert_query = """
                INSERT INTO chat_history (interview_id, question_id, turn_input, turn_output, turn_input_type)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING chat_history_turn_id
            """
            result = await conn.fetchval(insert_query, interview_id, question_id, turn_input, turn_output, turn_input_type)

            if result:
                return True
            else:
                raise DatabaseOperationError("Failed to insert chat history")
    except DatabaseConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise e
    except DatabaseQueryError as e:
        logger.error(f"Database query error: {e}")
        raise e
    except DatabaseOperationError as e:
        logger.error(f"Database operation error: {e}")
        raise e



@app.delete("/chat_history/{interview_id}")
async def delete_chat_history(interview_id: int):
    """
    Delete a specific chat history from the chat history.
    
    Args:
        interview_id (int): The unique identifier of the interview chat history entry to delete.
    
    Returns:
        dict: A message confirming successful deletion:
            {"message": "chat history deleted successfully"}
    
    Raises:
        Exception (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                delete_query = """
                    DELETE FROM chat_history 
                    WHERE interview_id = %s 
                    RETURNING interview_id
                """
                deleted_feedback = execute_query(
                    conn, 
                    delete_query, 
                    (interview_id,), 
                    fetch_one=True,
                    commit=True
                )
                
                if not deleted_feedback:
                    raise InterviewNotFoundException(interview_id)
                
                return {"message": "chat history deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting chat history : {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9094)