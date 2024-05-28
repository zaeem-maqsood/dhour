import logging

logger = logging.getLogger("custom_logger")


def who_called_me():
    import inspect

    # Get the current stack
    stack = inspect.stack()
    # The first entry is the current function, the second entry is the caller
    caller_frame = stack[2]
    # Get the name of the function that called this one
    function_name = caller_frame.function
    # Optionally, you can also access the filename and line number
    file_name = caller_frame.filename
    line_number = caller_frame.lineno
    print(f"Called by {function_name} in {file_name} on line {line_number}")
    logger.info(f"Called by {function_name} in {file_name} on line {line_number}")
