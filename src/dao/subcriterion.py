from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Optional, Union
import os
import time
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import uvicorn
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import QuestionNotFoundException,SubcriterionNotFoundException
from src.dao.criterion_payload import Criterion,SubCriterion
from src.schemas.dao.schema import SubcriteriaResponse,SubcriteriaRequest,SubcriteriaUpdate
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Pydantic Models with Documentation

app = FastAPI()

@app.get("/subcriteria/{subcriterion_id}", response_model=SubcriteriaResponse)
async def get_subcriterion(subcriterion_id: int):
    """
    Retrieve a subcriterion by ID.
    Args:
        subcriterion_id (int): ID of the subcriterion to retrieve
    Returns:
        SubcriteriaResponse: subcriterion details
    Raises:
        Exception: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            query = """
                SELECT subcriterion_id, subcriteria, criterion_id, question_id
                FROM Subcriterion
                WHERE subcriterion_id = %s
            """
            category = execute_query(conn, query, (subcriterion_id,))
            if not category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {
                "subcriterion_id": category[0],
                "subcriteria": category[1],
                "criterion_id": category[2],
                "question_id": category[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# @app.get("/subcriteria")
# async def fetch_subcriteria(question_id: int):
#     try:
#         with get_db_connection() as conn:
#             check_question_query = "SELECT question FROM Question WHERE question_id = %s"
#             question = execute_query(conn, check_question_query, (question_id,))
            
#             if not question:
#                 raise QuestionNotFoundException(question_id)
#             query = """
#                 SELECT 
#                     Criterion.criterion,
#                     Subcriterion.subcriterion,
#                     Subcriterion.weight
#                 FROM Subcriterion
#                 JOIN Criterion ON Criterion.criterion_id = Subcriterion.criterion_id
#                 WHERE Subcriterion.question_id = %s
#             """
#             results = execute_query(conn, query, (question_id,), fetch_one=False)
            
#             if not results:
#                 return {}

#             criteria_dict = {}
            
#             for criterion_name, subcriterion_name, weight in results:
#                 if criterion_name not in criteria_dict:
#                     criteria_dict[criterion_name] = Criterion(criterion_name)
                
#                 subcriterion = SubCriterion(subcriterion_name, float(weight))
#                 criteria_dict[criterion_name].add_subcriterion(subcriterion)

#             return {
#                 name: [{"subcriterion": sub.name, "weight": sub.weight} 
#                       for sub in criterion.subcriteria]
#                 for name, criterion in criteria_dict.items()
#             }

#     except DatabaseConnectionError as e:
#         raise e
#     except DatabaseQueryError as e:
#         raise e
#     except DatabaseOperationError as e:
#         raise e

@app.get("/subcriteria")
async def fetch_subcriteria(question_id: int):
    try:
        async with get_db_connection() as conn:
            # check_question_query = "SELECT EXISTS (SELECT 1 FROM Question WHERE question_id = $1)"
            # question_exists = await conn.fetchval(check_question_query, question_id)
            
            # if not question_exists:
            #     raise QuestionNotFoundException(f"Question with ID {question_id} not found.")
            query = """
                SELECT 
                    Criterion.criterion,
                    Subcriterion.subcriterion,
                    Subcriterion.weight
                FROM Subcriterion
                JOIN Criterion ON Criterion.criterion_id = Subcriterion.criterion_id
                WHERE Subcriterion.question_id = $1
            """
            results = await conn.fetch(query, question_id)
            
            if not results:
                return {}
            
            start_time = time.time()

            criteria_map = {}
            for record in results:
                criterion = record["criterion"]
                subcriterion = record["subcriterion"]
                weight = float(record["weight"])

                if criterion not in criteria_map:
                    criteria_map[criterion] = {"subcriteria": []}
                criteria_map[criterion]["subcriteria"].append({"name": subcriterion, "weight": weight})

            # Build final structure
            result = {"criteria": [{"name": name, "subcriteria": value["subcriteria"]} for name, value in criteria_map.items()]}

            execution_time = time.time() - start_time
            logger.info(f"Processed in {execution_time:.2f} seconds")

            return result

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# @app.post("/subcriteria/batch_insert")
# async def batch_insert_subcriteria(question_id: int, criteria_subcriteria_weight_map):
#     ds_criterion_to_id_map = {
#         "Are the assumptions clarified?": 1,
#         "Does the candidate account for corner cases ?": 2,
#         "Does the candidate choose the appropriate data structure for the problem?": 3,
#         "Does the candidate select a suitable algorithm for the task?": 4,
#         "Does the solution proposed by the candidate have optimal time complexity?": 5,
#         "Does the solution proposed by the candidate have optimal space complexity?": 6,
#         "Does the proposed solution handle generic use cases?": 7
#     }
    
#     try:
#         with get_db_connection() as conn:
#             # Check if question exists
#             check_question_query = "SELECT question FROM Question WHERE question_id = %s"
#             question = execute_query(conn, check_question_query, (question_id,))
            
#             if not question:
#                 raise QuestionNotFoundException(question_id)

#             values_to_insert = []
            
#             # Iterate through each criterion and its subcriteria
#             for criterion, subcriteria_weight_list in criteria_subcriteria_weight_map.items():
#                 criterion_id = ds_criterion_to_id_map.get(criterion)
                
#                 for subcriterion_weight in subcriteria_weight_list:
#                     values_to_insert.append((
#                         subcriterion_weight['subcriteria'],
#                         criterion_id,
#                         question_id,
#                         float(subcriterion_weight['weight'])  # Convert string weight to float
#                     ))
#             if values_to_insert:
#                 # Use execute_values for batch insert
#                 insert_query = """
#                     INSERT INTO subcriterion (subcriterion, criterion_id, question_id, weight)
#                     VALUES %s
#                     RETURNING subcriterion_id
#                 """
                
#                 cursor = conn.cursor()
#                 execute_values(
#                     cursor,
#                     insert_query,
#                     values_to_insert,
#                     template="(%s, %s, %s, %s)"
#                 )
#                 conn.commit()
#                 cursor.close()
                
#                 return {"status": "success", "message": f"Successfully inserted {len(values_to_insert)} subcriteria"}

#     except DatabaseConnectionError as e:
#         raise e
#     except DatabaseQueryError as e:
#         raise e
#     except DatabaseOperationError as e:
#         raise e

@app.post("/subcriteria/batch_insert")
async def batch_insert_subcriteria(question_id: int, criteria_subcriteria_weight_map):
    """
    Batch insert subcriteria for a given question ID.

    Args:
        question_id (int): The ID of the question.
        criteria_subcriteria_weight_map (dict): A dictionary containing criteria and their subcriteria with weights.

    Returns:
        dict: A status message indicating the success of the operation.

    Raises:
        QuestionNotFoundException: If the specified question does not exist.
        Exception: For any unexpected errors during the operation.
    """
    try:
        async with get_db_connection() as conn:
            # Check if question exists
            check_question_query = "SELECT question FROM Question WHERE question_id = $1"
            question = await conn.fetchval(check_question_query, question_id)

            if not question:
                raise QuestionNotFoundException(f"Question with ID {question_id} not found.")

            values_to_insert = []
            for criterion in criteria_subcriteria_weight_map['criteria']:
                criterion_id = criterion['id']
                for subcriterion in criterion['subcriteria']:
                    values_to_insert.append((
                        subcriterion['name'],
                        criterion_id,
                        question_id,
                        subcriterion['weight']
                    ))

            if values_to_insert:
                # Batch insert using asyncpg's executemany
                insert_query = """
                    INSERT INTO subcriterion (subcriterion, criterion_id, question_id, weight)
                    VALUES ($1, $2, $3, $4)
                """
                await conn.executemany(insert_query, values_to_insert)
                
                return {"status": "success", "message": f"Successfully inserted {len(values_to_insert)} subcriteria"}

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/subcriteria/{subcriterion_id}", response_model=SubcriteriaResponse)
async def update_subcriterion(subcriterion_id: int, update_data: SubcriteriaUpdate):
    """
    Update an existing subcriterion.
    Args:
        subcriterion_id (int): ID of the subcriterion to update
        update_data (SubcriteriaUpdate): New data for the subcriterion
    Returns:
        SubcriteriaResponse: Updated subcriterion details
    Raises:
        Exception: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = """
                UPDATE Subcriterion
                SET subcriterion = %s
                WHERE subcriterion_id = %s
                RETURNING subcriterion_id, subcriterion, criterion_id, question_id
            """
            updated_category = execute_query(
                conn,
                update_query,
                (update_data.subcriteria, subcriterion_id),
                commit=True
            )
            if not updated_category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {
                "subcriterion_id": updated_category[0],
                "subcriteria": updated_category[1],
                "criterion_id": updated_category[2],
                "question_id": updated_category[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
@app.delete("/subcriteria/{subcriterion_id}", response_model=dict)
async def delete_subcriterion(subcriterion_id: int):
    """
    Delete a subcriterion by ID.
    Args:
        subcriterion_id (int): ID of the subcriterion to delete
    Returns:
        dict: Success message
    Raises:
        Exception: 404 if subcriterion not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = """
                DELETE FROM Subcriterion
                WHERE subcriterion_id = %s
                RETURNING subcriterion_id
            """
            deleted_category = execute_query(
                conn,
                delete_query,
                (subcriterion_id,),
                commit=True
            )
            if not deleted_category:
                raise SubcriterionNotFoundException('subcriterion_id',subcriterion_id)
            return {"message": "subcriterion deleted successfully"}
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9092)