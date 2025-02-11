from fastapi import FastAPI , Depends
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
from src.dao.exceptions import OrganizationNotFoundException
from src.schemas.dao.schema import OrganizationRequest,OrganizationResponse

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/organization/{organization_id}", response_model=OrganizationResponse)
async def get_organization_metadata(organization_id: int):
    """
    Retrieve organization information by ID.
    
    Args:
        organization_id (int): ID of the organization to retrieve
        
    Returns:
        OrganizationResponse: organization details
        
    Raises:
        Exception: 404 if organization not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            get_organization_query="SELECT organization_id, organization FROM organization WHERE organization_id = %s"
            organization = execute_query(conn,get_organization_query,(organization_id,))
            if not organization:
                raise OrganizationNotFoundException(organization_id)
            return {"organization_id": organization[0], "organization": organization[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e


@app.post("/organization-service", response_model=OrganizationResponse)
async def add_organization(organization: str):
    """
    Create a new organization.
    
    Args:
        organization (str): Name of the organization to create
        
    Returns:
        OrganizationResponse: Created organization details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:
            cur_query = "INSERT INTO organization (organization) VALUES ( %s) RETURNING organization_id, organization"
            organization = execute_query(conn,cur_query,(organization,),commit=True)
            return {"organization_id": organization[0], "organization": organization[1]}    
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/organization-service/{organization_id}", response_model=OrganizationResponse)
async def update_organization(organization_id: int, organization: OrganizationRequest):
    """
    Update an existing organization's information.
    
    Args:
        organization_id (int): ID of the organization to update
        organization (OrganizationRequest): Updated organization information
        
    Returns:
        OrganizationResponse: Updated organization details
        
    Raises:
        Exception: 404 if organization not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = "UPDATE organization SET organization = %s WHERE organization_id = %s RETURNING organization_id, organization"
            updated_organization = execute_query(conn,update_query,(organization.organization, organization_id),commit=True)
            if not updated_organization:
                raise OrganizationNotFoundException(organization_id)         
            return {"organization_id": updated_organization[0], "organization": updated_organization[1]} 
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/organization-service/{organization_id}", response_model=dict)
async def delete_organization(organization_id: int):
    """
    Delete a organization by ID.
    
    Args:
        organization_id (int): ID of the organization to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if organization not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM organization WHERE organization_id = %s RETURNING organization_id"
            deleted_organization = execute_query(
                conn,
                delete_query,
                (organization_id,),
                commit=True
            )
            
            if not deleted_organization:
                raise OrganizationNotFoundException(organization_id)
            
            return {"message": "organization deleted successfully"}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9093)
