from typing import Any, Dict, List
from src.dao.criterion import fetch_criteria
from src.dao.subcriterion import batch_insert_subcriteria, fetch_subcriteria
from src.schemas.endpoints.schema import GenerateSubCriteriaRequest
from src.utils.logger import get_logger
from src.services.llm.prompts import subcriteria_generator_prompt
from src.services.llm import llm_service
import src.utils as utils
import json
import time


# Initialize logger using get_logger
logger = get_logger(__name__)


async def generate_subcriteria(question, question_id, question_type_id) -> Dict[str, List[Dict[str, Any]]]:
    """Handles the process of generating sub-criteria for a given question.

    Args:
        input_request: Object containing:
            - question_id: Unique ID for database insertion
            - question: Text for generating relevant sub-criteria
            - question_type_id (int): The identifier representing the type of question .


    Returns:
        Dict containing generated sub-criteria under 'evaluation_subcriteria' key

    Raises:
        Exception: For any processing errors
    """

    start_time = time.time()
    # Fetch existing sub-criteria from the database
    subcriteria_payload = await fetch_subcriteria(question_id)
    print(f"Fetch Subcriteria: {time.time() - start_time}")
    if subcriteria_payload:
        logger.info("Sub-criteria found in the database for question ID: %s", question_id)
        return subcriteria_payload
    # If no sub-criteria found, generate them using LLM
    else:

        logger.info("Generating sub-criteria for question ID: %s", question_id)
        criteria = await fetch_criteria(question_type_id)
        # print(f"72. {time.time() - start_time}")
        logger.info("Retrieved criteria for question type ID: %s", question_type_id)

        try:
            llm_inputs_dict = {'question': question, 'criteria': criteria }
            subcriteria_prompt = subcriteria_generator_prompt.make_prompt_from_template()
            llm_model = llm_service.get_openai_model(model = "gpt-4o-mini")
            subcriteria_generator_chain = (subcriteria_prompt | llm_model)
            subcriteria_payload = await subcriteria_generator_chain.ainvoke(llm_inputs_dict)
            # print(f"73. {time.time() - start_time}")
            subcriteria_payload = json.loads(utils.clean_response(subcriteria_payload.content))
            # print(f"74. {time.time() - start_time}")
            logger.info("Successfully generated subcriteria from llm")

        except (json.JSONDecodeError, AttributeError) as parse_err:
            logger.critical("Failed to parse LLM response: %s", parse_err)
            raise ValueError(f"Error parsing LLM response: {parse_err}") from parse_err
        except Exception as ex:
            logger.critical("Chain invocation failed: %s", ex)
            raise ex
        await batch_insert_subcriteria(question_id, subcriteria_payload)
        # print(f"75. {time.time() - start_time}")
        logger.info("Sub-criteria inserted into the database for question ID: %s", question_id)
        return subcriteria_payload


   






