from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import QuestionNotFoundException,QuestionTypeNotFoundException
from src.schemas.dao.schema import QuestionResponse,QuestionRequest
import asyncpg
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

@app.get("/question-service/{question_id}", response_model=QuestionResponse)
async def get_question_metadata(question_id: int):
    """
    Retrieve a question by its ID.
    
    Args:
        question_id (int): ID of the question to retrieve
    
    Returns:
        QuestionResponse: Question details
        
    Raises:
        Exception: 404 if question not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question, question_type, question_type_id 
                FROM Question
                WHERE question_id = %s
            """
            question = execute_query(conn, question_query, (question_id,))
            
            if not question:
                logger.erro(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
                
            return {
                "question_id": question[0],
                "question": question[1],
                "question_type": question[2],
                "question_type_id": question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/question-service")
async def get_initial_question_metadata():
    try:
        with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question,question_type_id FROM question
                WHERE question_id != 0
                ORDER BY RANDOM()
                LIMIT 1;
            """
            question = execute_query(conn, question_query)
                
            return {
                "question_id": question[0],
                "question": question[1],
                "question_type_id": question[2]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
    
# @app.get("/question-service")
# async def get_question_metadata_by_type(question_type_id):
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor() as cur:
#                 question_query = """
#                     SELECT question_id, question FROM question
#                     WHERE question_type_id = %s
#                     ORDER BY question_id ASC
#                 """
#                 # question_list = execute_query(conn, question_query, (question_type_id,), fetch_one = False)
#                 question_list = cur.execute(question_query, (question_type_id,))
#                 question_list = cur.fetchall()
#             return question_list
#     except DatabaseConnectionError as e:
#         raise e
#     except DatabaseQueryError as e:
#         raise e
#     except DatabaseOperationError as e:
#         raise e
@app.get("/question-service")
async def get_question(question_id: int):
    try:
        async with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question FROM question
                WHERE question_id = $1
            """
            # Execute the query using asyncpg
            question_row = await conn.fetchrow(question_query, question_id)

            return question_row["question"]
    except Exception as e:
        print(f"Error fetching questions: {e}")
        raise Exception(f"Failed to retrieve questions: {str(e)}")

@app.get("/question-service")
async def get_question_metadata_by_type(question_type_id: int):
    try:
        async with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question FROM question
                WHERE question_type_id = $1
                ORDER BY question_id ASC
            """
            # Execute the query using asyncpg
            question_list = await conn.fetch(question_query, question_type_id)
            return question_list
    except Exception as e:
        print(f"Error fetching questions: {e}")
        raise Exception(f"Failed to retrieve questions: {str(e)}")




@app.post("/question-service", response_model=QuestionResponse)
async def add_question(question: str, question_type_id: int, complexity: int):
    """
    Create a new question.
    
    Args:
        question (QuestionRequest): Question details for creation
    
    Returns:
        QuestionResponse: Created question details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:     
            question_type_query="SELECT question_type FROM question_type WHERE question_type_id = %s"
            question_type=execute_query(conn,question_type_query,(question_type_id,))[0]

            insert_query = """
                INSERT INTO Question (question, question_type, question_type_id,complexity)
                VALUES (%s, %s, %s, %s)
                RETURNING question_id, question, question_type, question_type_id,complexity
            """
            new_question = execute_query(
                conn, 
                insert_query, 
                (question, question_type, question_type_id,complexity,), 
                commit=True
            )
            
            return {
                "question_id": new_question[0],
                "question": new_question[1],
                "question_type": new_question[2],
                "question_type_id": new_question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/question-service/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionRequest, question_type_id: int):
    """
    Update an existing question by its ID.
    
    Args:
        question_id (int): ID of the question to update
        question (QuestionRequest): Updated question details
        question_type_id (int): New question type ID
    
    Returns:
        QuestionResponse: Updated question details
        
    Raises:
        Exception: 404 if question not found, 400 if no update fields provided,
                      503 for connection issues, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            verify_type_query = "SELECT question_type FROM Question WHERE question_type_id = %s LIMIT 1"
            existing_type = execute_query(conn, verify_type_query, (question_type_id,))
            
            if not existing_type:
                logger.error(f"Question type with ID {question_type_id} not found in the database ")
                raise QuestionTypeNotFoundException(question_type_id)
            
            update_fields = []
            params = []
            
            if question.question is not None:
                update_fields.append("question = %s")
                params.append(question.question)
            
            update_fields.append("question_type_id = %s")
            params.append(question_type_id)
            
            if question.question_type is not None:
                update_fields.append("question_type = %s")
                params.append(question.question_type)
            
            if not update_fields:
                logger.error(f"Empty update fields provided to update_question")
                raise Exception("No update fields provided")
            
            update_query = f"""
                UPDATE Question
                SET {', '.join(update_fields)}
                WHERE question_id = %s
                RETURNING question_id, question, question_type, question_type_id
            """
            params.append(question_id)
            
            updated_question = execute_query(
                conn, 
                update_query, 
                tuple(params), 
                commit=True
            )
            
            if not updated_question:
                logger.error(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
            return {
                "question_id": updated_question[0],
                "question": updated_question[1],
                "question_type": updated_question[2],
                "question_type_id": updated_question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/question-service/{question_id}", response_model=dict)
async def delete_question(question_id: int):
    """
    Delete a question by its ID.
    
    Args:
        question_id (int): ID of the question to delete
    
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if question not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM Question WHERE question_id = %s RETURNING question_id"
            deleted_question = execute_query(
                conn, 
                delete_query, 
                (question_id,), 
                commit=True
            )
            
            if not deleted_question:
                logger.error(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
            return {"message": "Question deleted successfully"}

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9095)