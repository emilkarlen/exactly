class NotAnIntegerException(Exception):
    def __init__(self, value_string: str):
        self.value_string = value_string


def python_evaluate(s: str) -> int:
    try:
        val = eval(s)
        if isinstance(val, int):
            return val
        else:
            raise NotAnIntegerException(s)
    except SyntaxError:
        raise NotAnIntegerException(s)
    except ValueError:
        raise NotAnIntegerException(s)
    except TypeError:
        raise NotAnIntegerException(s)
    except NameError:
        raise NotAnIntegerException(s)
