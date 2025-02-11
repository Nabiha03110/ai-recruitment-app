import logging

# def get_logger(name: str) -> logging.Logger:
#     """Configures and returns a logger instance.

#     Args:
#         name: Name of the logger (usually `__name__`).

#     Returns:
#         logging.Logger: Configured logger instance.
#     """
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)

#     formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

#     file_handler = logging.FileHandler('noha_ai_prototype.log')
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)

#     return logger


def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger instance.

    Args:
        name: Name of the logger (usually __name__).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove all existing handlers from the logger
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler('noha_ai_prototype.log')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    logger.propagate = False
    
    return logger