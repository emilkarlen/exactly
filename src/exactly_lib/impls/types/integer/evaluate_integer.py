from typing import Optional


class NotAnIntegerException(Exception):
    def __init__(self,
                 value_string: str,
                 python_exception_message: Optional[str] = None):
        self.value_string = value_string
        self.python_exception_message = python_exception_message


def python_evaluate(s: str) -> int:
    """
    :raises NotAnIntegerException
    """
    try:
        val = eval(s)
        if isinstance(val, int):
            return val
        else:
            raise NotAnIntegerException(s)
    except SyntaxError as ex:
        raise NotAnIntegerException(s, ex.msg)
    except ValueError as ex:
        raise NotAnIntegerException(s, str(ex))
    except TypeError as ex:
        raise NotAnIntegerException(s, str(ex))
    except NameError as ex:
        raise NotAnIntegerException(s, str(ex))
