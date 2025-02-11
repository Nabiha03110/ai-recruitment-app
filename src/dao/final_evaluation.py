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
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import FinalEvaluationNotFoundException,InterviewNotFoundException
import uvicorn
from src.schemas.dao.schema import FinalEvaluationRequest,FinalEvaluationResponse
# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Endpoint to retrieve a specific final evaluation JSON by final evaluation ID
@app.get("/final_evaluation_json/{final_evaluation_id}", response_model=FinalEvaluationResponse)
async def get_final_evaluation(final_evaluation_id: int):
    """
    Retrieve a specific final evaluation JSON by ID.

    Args:
        final_evaluation_id (int): Unique identifier for the final evaluation

    Returns:
        FinalEvaluationResponse: Details of the final evaluation

    Raises:
        Exception: 404 for Evaluation_JSON not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to fetch final evaluation JSON details from final_evaluations table
                query = """
                    SELECT final_evaluation_id, interview_id, final_evaluation_json, final_feedback
                    FROM final_evaluation
                    WHERE final_evaluation_id = %s
                """
                result = execute_query(conn, query, (final_evaluation_id,), fetch_one=True)
                
                # Raise 404 error if no matching record is found
                if not result:
                    raise FinalEvaluationNotFoundException(final_evaluation_id)
                
                # Return the final evaluation JSON response with retrieved details
                return FinalEvaluationResponse(
                    final_evaluation_id=result[0],
                    interview_id=result[1],
                    final_evaluation_json=result[2],
                    final_feedback=result[3]
                )
            except Exception as e:
                # Log any unexpected errors during evaluation JSON retrieval
                logger.error(f"Error retrieving Evaluation JSON: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to update an existing final evaluation JSON
@app.put("/final_evaluation_json/{final_evaluation_id}", response_model=FinalEvaluationResponse)
async def update_final_evaluation(final_evaluation_id: int, evaluation_request: FinalEvaluationRequest):
    """
    Update an existing final evaluation JSON.

    Args:
        final_evaluation_id (int): ID of the evaluation to update
        evaluation_json_request (FinalEvaluationRequest): New evaluation data

    Returns:
        FinalEvaluationResponse: Updated evaluation details

    Raises:
        Exception: 404 for Evaluation_JSON not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if evaluation exists
                check_query = """
                    SELECT final_evaluation_id FROM final_evaluation 
                    WHERE final_evaluation_id = %s
                """
                exists = execute_query(conn, check_query, (final_evaluation_id,), fetch_one=True)
                if not exists:
                    raise FinalEvaluationNotFoundException(final_evaluation_id)
                
                # Prepare update query with optional fields
                update_fields = []
                update_params = []
                if evaluation_request.final_evaluation_json is not None:
                    update_fields.append("final_evaluation_json = %s")
                    update_params.append(evaluation_request.final_evaluation_json)
                if evaluation_request.final_feedback is not None:
                    update_fields.append("final_feedback = %s")
                    update_params.append(evaluation_request.final_feedback)
                if not update_fields:
                    raise Exception("No update fields provided")
                update_params.append(final_evaluation_id)

                # Execute the update query
                update_query = f"""
                    UPDATE final_evaluation
                    SET {', '.join(update_fields)}
                    WHERE final_evaluation_id = %s
                    RETURNING final_evaluation_id, interview_id, final_evaluation_json, final_feedback
                """
                updated_record = execute_query(
                    conn, 
                    update_query, 
                    update_params, 
                    fetch_one=True,
                    commit=True
                )
                
                return FinalEvaluationResponse(
                    final_evaluation_id=updated_record[0],
                    interview_id=updated_record[1],
                    final_evaluation_json=updated_record[2],
                    final_feedback=updated_record[3]
                )
            except Exception as e:
                logger.error(f"Error updating final evaluation: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
# Endpoint to add a new final evaluation JSON for a specific interview
@app.post("/final_evaluation_json", response_model=FinalEvaluationResponse)
async def add_final_evaluation(interview_id: int, evaluation_json_request: FinalEvaluationRequest):
    """
    Add a new final evaluation JSON for a specific interview.

    Args:
        interview_id (int): ID of the interview
        evaluation_json_request (FinalEvaluationRequest): Evaluation data

    Returns:
        FinalEvaluationResponse: Created evaluation details

    Raises:
        Exception: 404 for Evaluation_JSON not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            # Check if an existing evaluation for the interview has a null evaluation JSON
            check_query = """
                SELECT user_id FROM Interview
                WHERE interview_id = %s
            """
            check_interview = execute_query(conn, check_query, (interview_id,), fetch_one=True)
            
            if not check_query:
                raise InterviewNotFoundException
                # Update existing evaluation with the new evaluation JSON
            add_final_evaluation_query = """
                INSERT INTO Final_Evaluation(interview_id,final_evaluation_json,final_feedback)
                VALUES(%s, %s, %s)
                RETURNING final_evaluation_id, interview_id, final_evaluation_json,final_feedback
            """
            result = execute_query(
                conn,
                add_final_evaluation_query,
                (interview_id, evaluation_json_request.final_evaluation_json, evaluation_json_request.final_feedback),
                fetch_one=True,
                commit=True
            )
            return FinalEvaluationResponse(
                final_evaluation_id=result[0],
                interview_id=result[1],
                final_evaluation_json=result[2],
                final_feedback=result[3]
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to delete a final evaluation JSON by final evaluation ID
@app.delete("/final_evaluation_json/{final_evaluation_id}")
async def delete_final_evaluation(final_evaluation_id: int):
    """
    Delete a final evaluation JSON by ID.

    Args:
        final_evaluation_id (int): ID of the evaluation to delete

    Returns:
        dict: Success message
    Raises:
        Exception: 404 for Evaluation_JSON not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to delete record and return deleted record's ID
                delete_query = """
                    DELETE FROM final_evaluation 
                    WHERE final_evaluation_id = %s 
                    RETURNING final_evaluation_id
                """
                deleted_feedback = execute_query(
                    conn, 
                    delete_query, 
                    (final_evaluation_id,), 
                    fetch_one=True,
                    commit=True
                )
                
                # Raise 404 error if no record was deleted
                if not deleted_feedback:
                    raise FinalEvaluationNotFoundException(final_evaluation_id)
                
                # Return success message
                return {"message": "Final Evaluation JSON deleted successfully"}
            except Exception as e:
                # Log any unexpected errors during evaluation JSON deletion
                logger.error(f"Error deleting Final Evaluation JSON : {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9100)