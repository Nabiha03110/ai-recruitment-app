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
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import CriterionNotFoundException
from src.schemas.dao.schema import CriteriaRequest,CriteriaResponse
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/criteria/{criterion_id}", response_model=CriteriaResponse)
async def fetch_criterion(criterion_id: int):
    """
    Retrieves a criteria by ID

    Args:
        criterion_id (int): ID of the criteria to retrieve
    
    Returns:
        CriteriaResponse:criteria Details
    
    Raises:
        Exception: 404 if criteria not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Query to fetch the criteria by ID
                criteria = execute_query(
                    conn,
                    "SELECT criterion_id, criterion, question_type_id FROM Criterion WHERE criterion_id = %s",
                    (criterion_id,)
                )
                if not criteria:
                    raise CriterionNotFoundException('criterion_id',criterion_id)  # Handle not found
                # Return the criteria details
                return {"criterion_id": criteria[0], "": criteria[1], "question_type_id": criteria[2]}
            except Exception as e:
                logger.error(f"Error retrieving criteria: {e}")  # Log errors
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/criteria")
async def fetch_criteria(question_type_id: int):
    """
    Retrieve all criteria for a given question type ID.

    Args:
        question_type_id (int): ID of the question type to retrieve criteria for.

    Returns:
        dict: A dictionary where keys are criterion IDs and values are criteria descriptions.

    Raises:
        CriterionNotFoundException: If no criteria are found for the given question_type_id.
        DatabaseConnectionError: If there is an issue with the database connection.
        Exception: For any other unexpected errors.
    """
    try:
        async with get_db_connection() as conn:
            try:
                # Query to fetch all criteria associated with the question type
                query = """
                    SELECT criterion_id, criterion
                    FROM Criterion 
                    WHERE question_type_id = $1
                """
                criteria = await conn.fetch(query, question_type_id)

                if not criteria:
                    raise CriterionNotFoundException('question_type_id',question_type_id)
                
                criteria = {criterion["criterion_id"]:criterion["criterion"] for criterion in criteria}
                return criteria
            
            except Exception as e:
                logger.error(f"Error retrieving criteria for question_type_id {question_type_id}: {e}")
                raise Exception(f"Error retrieving criteria for question_type_id {question_type_id}: {e}")

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/criteria", response_model=CriteriaResponse)
async def add_criteria(criterion: CriteriaRequest, question_type_id: int):
    """
    Add a new metric criteria to the database.
    
    Args:
        criterion (CriteriaRequest) : New data for criteria
        question_type_id (int): ID of the question type to add criteria for
    Returns: 
        CriteriaResponse:Added criteria details

    Raises: 
        Exception: 400 for validation errors, 503 for connection issues,
                      500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Insert the new criteria into the database
                cur_query = """
                    INSERT INTO Criterion (criterion, question_type_id) 
                    VALUES (%s, %s) 
                    RETURNING criterion_id, criterion, question_type_id
                """
                criteria = execute_query(
                    conn,
                    cur_query,
                    (criterion.criterion, question_type_id),
                    commit=True
                )
                # Return the newly created criteria details
                return {
                    "criterion_id": criteria[0],
                    "criterion": criteria[1],
                    "question_type_id": criteria[2]
                }
            except Exception as e:
                logger.error(f"Error adding criteria: {e}")  # Log errors
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/criteria/{criterion_id}", response_model=CriteriaResponse)
async def update_criteria(criterion_id: int, criteria: CriteriaRequest):
    """
    Update an existing criteria.
    
    Args:
        criterion_id (int): ID of the criteria to update
        criteria (CriteriaRequest): New data for the criteria
        
    Returns:
        criteriaResponse: Updated criteria details
        
    Raises:
        Exception: 404 if criteria not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Update the metric criteria in the database
                update_query = "UPDATE Criterion SET criterion = %s WHERE criterion_id = %s RETURNING criterion_id, criterion, question_type_id"
                updated_criteria = execute_query(
                    conn,
                    update_query,
                    (criteria.criterion, criterion_id),
                    commit=True
                )
                if not updated_criteria:
                    raise CriterionNotFoundException('criterion_id',criterion_id)
                # Return the updated criteria details
                return {"criterion_id": updated_criteria[0], "criterion": updated_criteria[1], "question_type_id": updated_criteria[2]}
            except Exception as e:
                logger.error(f"Error updating metric criteria: {e}")  # Log errors
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/criteria/{criterion_id}", response_model=dict)
async def delete_criteria(criterion_id: int):
    """
    Delete a subcriteria by ID.
    
    Args:
        criterion_id (int): ID of the subcriteria to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if criteria not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try: 
        with get_db_connection() as conn:
            try:
                # Delete the criteria from the database
                delete_query = "DELETE FROM Criterion WHERE criterion_id = %s RETURNING criterion_id"
                deleted_criteria = execute_query(
                    conn,
                    delete_query,
                    (criterion_id,),
                    commit=True
                )
                if not deleted_criteria:
                    raise CriterionNotFoundException('criterion_id',criterion_id)
                # Return success message
                return {"message": "criteria deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting criteria: {e}")  # Log errors
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9091)