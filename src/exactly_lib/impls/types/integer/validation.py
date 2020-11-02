from exactly_lib.common.report_rendering import text_docs
from exactly_lib.impls.exception.validation_error_exception import ValidationErrorException
from exactly_lib.impls.types.integer.evaluate_integer import NotAnIntegerException, python_evaluate
from exactly_lib.util.str_ import str_constructor


def evaluate(py_expr: str) -> int:
    """
    :raises ValidationErrorException
    :return: Evaluated value
    """
    try:
        return python_evaluate(py_expr)
    except NotAnIntegerException as ex:
        py_ex_str = (
            ''
            if ex.python_exception_message is None
            else
            '\n\nPython evaluation error:\n' + ex.python_exception_message
        )
        msg = text_docs.single_pre_formatted_line_object(
            str_constructor.FormatPositional(
                'Value must be an integer: `{}\'{}',
                ex.value_string,
                py_ex_str)
        )
        raise ValidationErrorException(msg)
