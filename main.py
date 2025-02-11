
# """Main module for initializing the FastAPI application."""

# import uvicorn
# from fastapi import FastAPI
# import src.api.endpoints as endpoints

# # Initialize the FastAPI application
# app = FastAPI()

# # Include the router
# app.include_router(endpoints.router)

# def main():
#     """Run the FastAPI application."""
#     uvicorn.run(app, host="127.0.0.1", port=8000)

# if __name__ == "__main__":
#     main()
"""Main module for initializing the FastAPI application."""

import uvicorn
from fastapi import FastAPI
import src.api.endpoints as endpoints
from contextlib import asynccontextmanager
from src.dao.utils.db_utils import init_pool, close_pool
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    try:
        logger.info("Initializing the database connection pool.")
        await init_pool()
    except Exception as e:
        logger.error(f"Error initializing database connection pool: {str(e)}")
        raise e

    yield  # The application runs while this generator is suspended

    try:
        logger.info("Closing the database connection pool.")
        await close_pool()
    except Exception as e:
        logger.error(f"Error closing database connection pool: {str(e)}")
        raise e

# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)

# Include the router
app.include_router(endpoints.router)

def main():
    """Run the FastAPI application."""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()