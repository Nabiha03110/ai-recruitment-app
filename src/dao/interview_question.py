from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
from src.dao.exceptions import QuestionEvaluationNotFoundException,QuestionNotFoundException,InterviewNotFoundException
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/interview-questions")
async def add_interview_question(interview_id: int, question_id: int):
    """
    Endpoint to add a question to an interview.

    Args:
        interview_id: ID of the interview.
        question_id: ID of the question.

    Returns:
        Success message if the question is added.

    Raises:
        Exception: 404 for interview/question not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if the interview exists
                interview_check_query = "SELECT user_id FROM Interview WHERE interview_id = %s"
                interview_exists = execute_query(conn, interview_check_query, (interview_id,))[0]
                
                # Check if the question exists
                question_check_query = "SELECT question FROM Question WHERE question_id = %s"
                question_exists = execute_query(conn, question_check_query, (question_id,))[0]
                
                if not interview_exists:
                    raise InterviewNotFoundException(interview_id)
                
                if not question_exists:
                    raise QuestionNotFoundException(question_id)
                
                # Insert the interview question into the database
                insert_query = """
                    INSERT INTO Interview_Question (interview_id, question_id) 
                    VALUES (%s, %s)
                """
                execute_query(
                    conn, 
                    insert_query, 
                    (interview_id, question_id), 
                    commit=True
                )
                
                return {"message": "Interview question added successfully"}
            except Exception as e:
                logger.error(f"Error adding interview question: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/interview-questions/{interview_id}")
async def get_interview_questions(interview_id: int):
    """
    Endpoint to retrieve all questions for a specific interview.

    Args:
        interview_id: ID of the interview.

    Returns:
        List of question IDs.

    Raises:
        Exception: 404 for interview not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if the interview exists
                interview_check_query = "SELECT user_id FROM Interview WHERE interview_id = %s"
                interview_exists = execute_query(conn, interview_check_query, (interview_id,))[0]
                
                if not interview_exists:
                    logger.error(f"Interview with ID {interview_id} not found in the database")
                    raise InterviewNotFoundException(interview_id)
                # Retrieve all associated questions
                query = """
                    SELECT question_id 
                    FROM Interview_Question 
                    WHERE interview_id = %s
                """
                questions = execute_query(
                    conn, 
                    query, 
                    (interview_id,), 
                    fetch_one=False
                )
                return {"question_id": [q[0] for q in questions]}
            except Exception as e:
                logger.error(f"Error retrieving interview questions: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/interview-questions")
async def update_interview_question(current_interview_id: int,current_question_id: int,new_question_id: int):
    """
    Endpoint to update a question in an interview.

    Args:
        current_interview_id: ID of the interview.
        current_question_id: Current ID of the question.
        new_question_id: New ID of the question to update to.

    Returns:
        Success message if the update is successful.

    Raises:
        Exception: 404 for question not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if the new question exists
                question_check_query = "SELECT question FROM Question WHERE question_id = %s"
                question_exists = execute_query(conn, question_check_query, (new_question_id,))[0]
                
                if not question_exists:
                    logger.error(f"Question with ID {current_question_id} not found in the database")
                    raise InterviewQuestionNotFoundException(current_question_id,current_interview_id)
                
                # Update the question in the database
                update_query = """
                    UPDATE Interview_Question 
                    SET question_id = %s 
                    WHERE interview_id = %s AND question_id = %s
                """
                execute_query(
                    conn, 
                    update_query, 
                    (new_question_id, current_interview_id, current_question_id), 
                    commit=True
                )
                
                return {"message": "Interview question updated successfully"}
            except Exception as e:
                logger.error(f"Error updating interview question: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/interview-questions")
async def delete_interview_question(interview_id: int, question_id: int):
    """
    Endpoint to delete a specific question from an interview.

    Args:
        interview_id: ID of the interview.
        question_id: ID of the question.

    Returns:
        Success message if the question is deleted.
    
    Raises:
        Exception: 404 for interview question not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Delete the specific question from the interview
                delete_query = """
                    DELETE FROM Interview_Question 
                    WHERE interview_id = %s AND question_id = %s
                    RETURNING interview_id, question_id
                """
                deleted_question = execute_query(
                    conn, 
                    delete_query, 
                    (interview_id, question_id), 
                    fetch_one=True,
                    commit=True
                )
                
                if not deleted_question:
                    logger.error(f"Interview question with {question_id} not found for interview ID {interview_id}")
                    raise InterviewQuestionNotFoundException(question_id,interview_id)
                
                return {"message": "Interview question deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting interview question: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9098)