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
from src.dao.exceptions import UserNotFoundException
from src.schemas.dao.schema import UserRequest,UserResponse

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/user-service/{user_id}", response_model=UserResponse)
async def get_user_metadata(user_id: int):
    """
    Retrieve user information by ID.
    
    Args:
        user_id (int): ID of the user to retrieve
        
    Returns:
        UserResponse: User details
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                user_fetch_query = "SELECT user_id, name FROM Users WHERE user_id = %s"
                # user = execute_query(
                #     conn,
                #     "SELECT user_id, name FROM Users WHERE user_id = %s",
                #     (user_id,)
                # )
                user = cur.execute(user_fetch_query, (user_id,))
                user = cur.fetchone()
                
                if not user:
                    raise UserNotFoundException(user_id)
                         
            return {"user_id": user[0], "name": user[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e


@app.post("/user-service", response_model=UserResponse)
async def add_user(name: str):
    """
    Create a new user.
    
    Args:
        name (str): Name of the user to create
        
    Returns:
        UserResponse: Created user details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:
            
            cur_query = "INSERT INTO Users ( name) VALUES ( %s) RETURNING user_id, name"
            user = execute_query(
                conn,
                cur_query,
                (name,),
                commit=True
            )
            
            return {"user_id": user[0], "name": user[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/user-service/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserRequest):
    """
    Update an existing user's information.
    
    Args:
        user_id (int): ID of the user to update
        user (UserRequest): Updated user information
        
    Returns:
        UserResponse: Updated user details
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = "UPDATE Users SET name = %s WHERE user_id = %s RETURNING user_id, name"
            updated_user = execute_query(
                conn,
                update_query,
                (user.name, user_id),
                commit=True
            )
            
            if not updated_user:
                raise UserNotFoundException(user_id)
            
            return {"user_id": updated_user[0], "name": updated_user[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/user-service/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    """
    Delete a user by ID.
    
    Args:
        user_id (int): ID of the user to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM Users WHERE user_id = %s RETURNING user_id"
            deleted_user = execute_query(
                conn,
                delete_query,
                (user_id,),
                commit=True
            )
            
            if not deleted_user:
                raise UserNotFoundException(user_id)
            
            return {"message": "User deleted successfully"}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9093)
