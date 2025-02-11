import src.utils as utils
import src.services.llm as llm
from src.services.llm.prompts.solution_hint_prompt import make_prompt_from_template
from src.services.llm.llm_service import get_chain

# Initialize logger
logger = utils.get_logger(__name__)

async def generate_hint(input_request):
    try:
        chat_history = input_request.chat_history
        evaluation_results = input_request.evaluation_results
        question = input_request.question

        hint_generator_prompt = make_prompt_from_template()
        hint_generator_chain = get_chain(prompt = hint_generator_prompt)
        llm_response = await hint_generator_chain.ainvoke({"question": question,"chat_history": chat_history, "evaluation_results": evaluation_results})

        return llm_response.content

    except Exception as ex:
        logger.critical(f"Unexpected error in hint generation process: {ex}")
        raise Exception(f"Unexpected error in hint generation process: {ex}")